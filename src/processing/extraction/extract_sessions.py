"""
This extracts sessions, given the race weekend url in:
"""
# data\sessions\raw\<year>\<year>.html
"""
Sessions:
Practice 0 (called warm up in some years)
Practice 1
Practice 2 (non-sprint weekend)
Practice 3 (non-sprint weekend)
sprint-qualifying (sprint weekend)
sprint-grid (sprint weekend)
sprint (sprint weekend)
qualifying
starting-grid
pit-stop-summary
fastest-laps
race-results

"""
from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from pathlib import Path, PurePosixPath

def _extract_items(soup: BeautifulSoup, url: str) -> list[dict]:
    # url must be something like "https://www.formula1.com/en/results/2026/races/1279/australia/race-result" 
    # (output from scrape_race_weekends.url in db)

    # 1. turn "https://www.formula1.com/en/results/2026/races/1279/australia/race-result" into "/en/results/2026/races/1279/australia/race-result"
    base_url = url.replace("https://www.formula1.com","")
    # 2. Turn into path, get parent (removes race-result) e.g. "/en/results/2026/races/1279/australia"
    base_url = str(PurePosixPath(base_url).parent).lower()

    # Sets classes found in f1 site. Stupid names, let's hope they don't change
    list_class = "DropdownMenu-module_dropdown-item__T0Pcm"
    a_link_class = "DropdownMenuItem-module_dropdown-menu-item__6Y3-v typography-module_body-s-semibold__O2lOH"

    results = []

    # 3. Go through each list item
    for li in soup.find_all("li", class_ = list_class):
        # 3.a. go through each link (a) within the list
        for a in li.find_all("a", class_ = a_link_class):
            # 3.a.i. check if the link is relevant to this race
            if base_url not in (str(a["href"]).lower()):
                continue
            # 3.a.ii. check if the text is within the <a> and not a <title> block.
            elif not a.find("title"):
                results.append({
                    "url": urljoin("https://www.formula1.com", a["href"]), # type: ignore
                    "session_name": a.get_text(),
                                })
    return results # this is a dictionary of each session and its url

def write_to_db(results, year):
    pass 

url = "https://www.formula1.com/en/results/2026/races/1279/australia/race-result"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

print(_extract_items(soup,url))