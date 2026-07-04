"""
This extracts the session date from:

https://www.formula1.com/en/results/2026/races/1279/australia/race-result


"""
from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from config.config import DB_PATH
from database.management import connection
from datetime import datetime

def _extract_prices(soup: BeautifulSoup) -> dict:
    # Sets classes found in f1 site. Stupid arbitrary names, let's hope they don't change
    div_class = "si-stats__list-grid"
    results = {}

    for div in soup.find_all("div", class_ = div_class):
        li = div.find_all("li")
        if not li:
            raise ValueError(f"Could not find list (li) in div: {div_class}")
        for row in li:
            print(row.text)
            
    if results:
        return results # this is a dictionary of each session and its url
    else:
        raise LookupError("Couldn't extract date information")

def write_prices_to_db(from_date: str, to_date: str, url: str):
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        UPDATE scrape_race_weekends
                            SET from_date = ?, to_date = ?
                         WHERE url = ?;
                        """,
                        (from_date, to_date, url)
                        )

def run(html: BeautifulSoup, url: str):
    results = _extract_prices(soup=html)
    write_prices_to_db(from_date=results["from_date"], to_date=results["to_date"], url=url)

def test(url:str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    print(_extract_prices(soup))

def _get_test_urls(start_year:int, end_year:int) -> list:
    urls = []
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT url
                          FROM scrape_race_weekends
                         WHERE year BETWEEN ? AND ?;
                        """,
                        (start_year, end_year)
                        )
        output = cursor.fetchall()

    if output:
        for url in output:
            urls.append(url[0])
    return urls    

def run_update(start_year:int, end_year:int) -> None:
    urls = _get_test_urls(start_year, end_year)
    for url in urls:
        print(url)
        response = requests.get(url)
        race_html = BeautifulSoup(response.text, "html.parser")
        run(race_html, url)

test(r"https://fantasy.formula1.com/en/statistics/details")
#run_update(1950,2026)