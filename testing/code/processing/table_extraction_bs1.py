import requests
from bs4 import BeautifulSoup

url = "https://www.formula1.com/en/results/2026/races"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")  # or use class/id selectors
rows = table.find_all("tr")

data = []

for row in rows:
    cols = row.find_all(["td", "th"])
    cols = [col.get_text(strip=True) for col in cols]
    data.append(cols)

print(data)