import requests
import pymongo
import gridfs
import conf

params = {
    "api_key": conf.api_token
}
hero_img_request = requests.get("https://api.opendota.com/api/heroStats", params=params)
db_client = pymongo.MongoClient("mongodb://mongo:mongo@mongo:27017/?authMechanism=DEFAULT")
current_db = db_client["dota_api"]
fs = gridfs.GridFS(current_db, collection="heroes_images")

for hero in hero_img_request.json():
    img = requests.get(url="http://cdn.dota2.com" + hero["img"],
                       stream=True).content
    fs.put(img, filename=hero["localized_name"], _id=hero["hero_id"])
