import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

url = "https://www.formula1.com/en/results/2025/races"
soup = BeautifulSoup(requests.get(url).text, "html.parser")

results = []

for li in soup.find_all("li", class_="DropdownMenu-module_dropdown-item__T0Pcm"):
    a = li.find("a")
    if not a:
        continue

    href = a.get("href")
    if not href:
        continue

    spans = a.find_all("span")

    if len(spans) < 2:
        continue  # skip incomplete items

    info = spans[1].get_text(strip=True)

    # final validation
    if not info:
        continue

    results.append({
        "link": urljoin(url, href),
        "info": info
    })

# ---- WRITE TO CSV ----

output_file = r"C:\Users\thoma\OneDrive\Documents\Python\F1_Fantasy_v2\testing\code\processing\outputs\list_extraction_output.csv"

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["link", "info"])
    writer.writeheader()
    writer.writerows(results)

print(f"Saved {len(results)} rows to {output_file}")