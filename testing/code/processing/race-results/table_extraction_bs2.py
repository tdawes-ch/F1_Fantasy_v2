import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.formula1.com/en/results/2026/races"
soup = BeautifulSoup(requests.get(url).text, "html.parser")

table = soup.find("table")

headers = [th.text.strip() for th in table.find_all("th")]

rows = []
for tr in table.find_all("tr")[1:]:
    cells = [td.text.strip() for td in tr.find_all("td")]
    if cells:
        rows.append(cells)

df = pd.DataFrame(rows, columns=headers)
print(df)