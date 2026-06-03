"""
This extracts the circuit name from:

https://www.formula1.com/en/results/2026/races/1279/australia/race-result


"""
from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from pathlib import Path, PurePosixPath

def _extract_circuit(soup: BeautifulSoup, url: str) -> list[dict]:
    # url must be something like "https://www.formula1.com/en/results/2026/races/1279/australia/race-result" 
    # (output from scrape_race_weekends.url in db)

    # Sets classes found in f1 site. Stupid names, let's hope they don't change
    div_class = "flex flex-col gap-px-6 text-text-3"
    p_class = "typography-module_body-xs-semibold__Fyfwn"

    results = []

    for div in soup.find_all("div", class_ = div_class):
        for p in div.find_all("p", class_ = p_class):
            circuit, city = p.get_text().split(",")
            results.append({
                "circuit": circuit.strip(),
                "city": city.strip()
            })
    return results # this is a dictionary of each session and its url

def write_results_to_db(results, race_id):
    pass 

url = "https://www.formula1.com/en/results/2026/races/1286/monaco/race-result"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

print(_extract_circuit(soup,url))