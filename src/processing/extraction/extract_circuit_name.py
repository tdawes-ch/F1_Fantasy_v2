"""
This extracts the circuit name from:

https://www.formula1.com/en/results/2026/races/1279/australia/race-result


"""
from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from pathlib import Path, PurePosixPath
from config.config import DB_PATH

def _extract_circuit(soup: BeautifulSoup) -> list[dict]:
    # Sets classes found in f1 site. Stupid arbitrary names, let's hope they don't change
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

def write_circuit_to_db(results: list[dict], race_id: int):
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        for result in results:
            cursor.execute("""
                            UPDATE ;
                            """,
                            ()
                            )
    pass 

def main():
    pass

def test():
    url = "https://www.formula1.com/en/results/2026/races/1286/monaco/race-result"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    print(_extract_circuit(soup))