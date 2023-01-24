from flask import Flask, render_template
from flask import request
import requests
import conf


app = Flask(__name__, static_folder="static")

account_id = ""


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/', methods=["POST"])
def post_id():
    global account_id
    account_id = request.form["id"]

    if account_id == "master":
        account_id = conf.master_id

    params = {
        "api_key": conf.api_token
    }


    wl_response = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl", params=params)
    normal_wins = wl_response.json()["win"]
    normal_lose = wl_response.json()["lose"]

    name_response = requests.get(f"https://api.opendota.com/api/players/{account_id}", params=params)
    player_name = name_response.json()["profile"]["personaname"]
    player_img = name_response.json()["profile"]["avatarfull"]
    turbo_params = {
        "api_key": conf.api_token,
        "significant": 0,
        "game_mode": 23
    }

    turbo_wl_response = requests.get(
        f"https://api.opendota.com/api/players/{account_id}/wl", params=turbo_params)
    turbo_wins = turbo_wl_response.json()["win"]
    turbo_lose = turbo_wl_response.json()["lose"]

    user_stats = {
        "name": player_name,
        "normal_wins": normal_wins,
        "normal_lose": normal_lose,
        "normal_wr": round(normal_wins / (normal_wins + normal_lose) * 100, 2),
        "turbo_wins": turbo_wins,
        "turbo_lose": turbo_lose,
        "turbo_wr": round(turbo_wins / (turbo_lose + turbo_wins) * 100, 2),
        "avatar": player_img
    }

    all_heroes_response = requests.get("https://api.opendota.com/api/heroes", params=params)
    id_name_heroes_data = {}

    for hero in all_heroes_response.json():
        id_name_heroes_data[str(hero["id"])] = hero["localized_name"]

    response_heroes = requests.get(f"https://api.opendota.com/api/players/{account_id}/heroes", params=params)
    best_twenty_heroes = response_heroes.json()[:20]
    hero_img_request = requests.get("https://api.opendota.com/api/heroStats", params=params).json()
    heroes_data = {}
    for row in hero_img_request:
        heroes_data[str(row["hero_id"])] = ["http://cdn.dota2.com" + row["img"]]

    heroes_stats = {}

    for hero in best_twenty_heroes:
        heroes_stats[id_name_heroes_data[hero["hero_id"]]] = {
            "Games": hero["games"],
            "Wins": hero["win"],
            "Losses": hero["games"] - hero["win"],
            "Winrate": round(hero["win"] / hero["games"] * 100, 2),
            "img": str(heroes_data[hero["hero_id"]])[2:-3]
        }

    return render_template("info.html", id=account_id, user_stats=user_stats, context=heroes_stats)


if __name__ == "__main__":
    app.run()
