import requests

# Just swapping the base URL out keeps everything else identical!
url = "https://api.jolpi.ca/ergast/f1/current/last/results.json"

response = requests.get(url)
data = response.json()

# Digging down works exactly the same way
race_data = data["MRData"]["RaceTable"]["Races"][0]
print(f"Latest Race: {race_data['raceName']}")