import json
from pprint import pp


with open(file="data/fantasy/raw/2026/07-07.json",mode="r",encoding="utf-8") as json_data:
    loaded_json = json.load(json_data)

pp(loaded_json)
