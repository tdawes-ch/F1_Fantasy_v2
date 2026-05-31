'''
for the first race we can get the list of all races for the season

save this to log file seasons.csv for total races
'''
import csv
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import toolbox.file_management as fm
from config.config import BASE_URL

CLASS_NAME = "DropdownMenu-module_dropdown-item__T0Pcm"

def _extract_items(soup: BeautifulSoup, base_url: str) -> list[dict]:
    # takes in html in the form of soup, also base_url e.g. "https://www.formula1.com/en/results/2025/races"
    results = []

    for li in soup.find_all("li", class_ = CLASS_NAME):
        # goes through all list data with the set class
        a = li.find("a")
        if not a:
            # if the class doesn't contain a link, not interested
            continue

        href = a.get("href")
        if not href:
            # if the <a> block doesn't contain a href, not interested
            continue

        spans = a.find_all("span")
        if len(spans) < 2:
            # site contains span within a span. Data we're interested in is in the 2nd span. If there isn't a 2nd span, continue
            continue  # skip incomplete items

        info = spans[1].get_text(strip=True) # gets data from 2nd span

        # final validation
        if not info:
            # if it's empty, we're not interested
            continue

        results.append({
            "url": urljoin(base_url, href),
            "race": info,
            "status": ""
        })
        
    return results


def extract_season_races(html_path: str, csv_path: str, base_url: str = ""):
    # takes path to the .html file, output csv path,
    html = fm.load_html_file(html_path)
    results = _extract_items(html,base_url)
    fm.write_to_csv(results, csv_path, ["url", "race", "status"])


try:
    extract_season_races(r"C:\Users\thoma\OneDrive\Documents\Python\F1_Fantasy_v2\data\sessions\raw\2024\2024.html",
                      r"C:\Users\thoma\OneDrive\Documents\Python\F1_Fantasy_v2\data\sessions\processed\2024\2024.csv",
                      BASE_URL)
except FileNotFoundError as e:
    print(e)
