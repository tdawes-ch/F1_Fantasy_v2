import requests

# You pinpoint exactly the session and driver you want via URL queries
url = "https://api.openf1.org/v1/car_data?driver_number=1&session_key=9161"
response = requests.get(url).json()

# You get a raw list of chronological data points
for data_point in response[:50]:
    print(f"Time: {data_point['date']} | Speed: {data_point['speed']} km/h")