import pymongo.collection
from flask import Flask, render_template
from flask import request
import requests
import conf
import re
import pymongo
import gridfs
import base64

PARAMS = {
    "api_key": conf.api_token
}

TURBO_PARAMS = {
    "api_key": conf.api_token,
    "significant": 0,
    "game_mode": 23
}

app = Flask(__name__, static_folder="static")


@app.route('/')
def home():
    return render_template("home.html", id_error=False)


@app.route('/', methods=["POST"])
def post_id():
    account_id = request.form["id"]

    if account_id == "master":
        account_id = conf.master_id

    if not re.search(r'^[0-9]+$', account_id):
        return render_template("home.html", id_error=True)

    # get username & user avatar
    name_response = requests.get(f"https://api.opendota.com/api/players/{account_id}", params=PARAMS)
    if name_response.status_code != 200:
        return render_template("home.html", id_error=True)

    try:
        player_name = name_response.json()["profile"]["personaname"]
        player_img = name_response.json()["profile"]["avatarfull"]
    except KeyError:
        return render_template("home.html", id_error=True)

    # get normals matches
    wl_response = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl", params=PARAMS)
    if wl_response.status_code != 200:
        return render_template("home.html", id_error=True)

    normal_wins = wl_response.json()["win"]
    normal_lose = wl_response.json()["lose"]

    # get turbo matches
    turbo_wl_response = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl", params=TURBO_PARAMS)
    if turbo_wl_response.status_code != 200:
        return render_template("home.html", id_error=True)

    turbo_wins = turbo_wl_response.json()["win"]
    turbo_lose = turbo_wl_response.json()["lose"]

    # pre save user data
    user_stats = {
        "name": player_name,
        "avatar": player_img,
        "normal_wins": normal_wins,
        "normal_lose": normal_lose,
        "normal_wr": round(normal_wins / (normal_wins + normal_lose) * 100, 2),
        "turbo_wins": turbo_wins,
        "turbo_lose": turbo_lose,
        "turbo_wr": round(turbo_wins / (turbo_lose + turbo_wins) * 100, 2)
    }

    # get all heroes id & localized_name
    all_heroes_response = requests.get("https://api.opendota.com/api/heroes", params=PARAMS)
    if all_heroes_response.status_code != 200:
        return render_template("home.html", id_error=True)

    id_name_heroes_data = {}

    for hero in all_heroes_response.json():
        id_name_heroes_data[str(hero["id"])] = hero["localized_name"]

    # get best 20 account heroes
    response_heroes = requests.get(f"https://api.opendota.com/api/players/{account_id}/heroes", params=PARAMS)
    if response_heroes.status_code != 200:
        return render_template("home.html", id_error=True)

    best_twenty_heroes = response_heroes.json()[:20]

    db_client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/?authMechanism=DEFAULT")
    current_db = db_client["dota_api"]
    fs = gridfs.GridFS(current_db, collection="heroes_images")

    # pre save 20 account heroes
    heroes_stats = []
    for hero in best_twenty_heroes:
        bimage = fs.get(int(hero["hero_id"])).read()

        hero_stats = {
            "hero_id": hero["hero_id"],
            "hero_name": id_name_heroes_data[hero["hero_id"]],
            "hero_img_decoded": base64.b64encode(bimage).decode('utf-8'),
            "games": hero["games"],
            "wins": hero["win"],
            "losses": hero["games"] - hero["win"],
            "winrate": round(hero["win"] / hero["games"] * 100, 2)
        }
        heroes_stats.append(hero_stats)

    # mongo_data = {
    #     "_id": account_id,
    #     "user_stats": user_stats,
    #     "heroes_stats": heroes_stats
    # }
    #
    # profile_img = requests.get(
    #     url=str(user_stats["avatar"]),
    #     stream=True).content
    #
    # db_client = pymongo.MongoClient("mongodb://mongo:mongo@localhost:27017/?authMechanism=DEFAULT")
    # current_db = db_client["dota_api"]
    # web_collection = current_db["web"]
    # # ins_result = web_collection.insert_one(mongo_data)
    # fs = gridfs.GridFS(current_db, collection="profile_images")
    # # a = fs.put(profile_img, filename="profile", _id=account_id)
    #
    # fs = gridfs.GridFS(current_db, collection="heroes_images")
    # for hero in best_twenty_heroes:
    #     bimage = fs.get(int(hero["hero_id"])).read()
    #     img_encoded = base64.b64encode(bimage)

    return render_template("info.html", id=account_id, user_stats=user_stats, heroes_stats=heroes_stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
