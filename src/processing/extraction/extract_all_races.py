'''
for the first race we can get the list of all races for the season

save this to log file seasons.csv for total races
'''
from bs4 import BeautifulSoup
from pathlib import Path, PurePosixPath
import datetime
from urllib.parse import urljoin, urlparse
from toolbox import extract_race_id
import toolbox.file_management as fm
from config.config import DB_PATH
from database.management import connection

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
            "url": urljoin(base_url, href), # type: ignore
            "race": info,
        })
        
    return results


def extract_season_races(html_path: Path | str, csv_path: Path | str, base_url: str = ""):
    # takes path to the .html file, output csv path, and a base url
    # in case string gets passed through
    html_path = Path(html_path)
    csv_path = Path(csv_path)

    # does stuff for the csv. Can maybe put this in an if statement if I pass through a flag for whether to save CSVs or not.
    html = fm.load_html_file(html_path)
    results = _extract_items(html,base_url)
    fm.write_to_csv(results, csv_path, ["url", "race"])
    
    # does database stuff
    year = html_path.parent.name
    write_results_to_db(results, year)

def write_results_to_db(results, year):
    # do the scrape_seasons update
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_seasons
                          SET expected_races = ?
                          WHERE year = ?
                        """,(len(results),
                             year)
                      )
    # update the other table (scrape_race_weekends)
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        i = 1
        for race in results:
            url = race["url"]
            race_id = extract_race_id.from_url(url)
            cursor.execute("""
                            INSERT INTO scrape_race_weekends (race_id, year, round, race_name, url, scraped)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT(url) DO UPDATE SET
                                race_id = EXCLUDED.race_id,
                                year = EXCLUDED.year,
                                round = EXCLUDED.round,
                                race_name = EXCLUDED.race_name,
                                scraped = EXCLUDED.scraped;
                            """,
                            (race_id, year, i, race["race"], url, 0)
                          )
            i+=1
