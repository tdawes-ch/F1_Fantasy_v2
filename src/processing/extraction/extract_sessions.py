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
from toolbox import extract_race_id, database_query
from config.config import DB_PATH
from database.management import connection

def _extract_items(soup: BeautifulSoup, url: str) -> list[dict]:
    """
    From HTML data and the url for that data, we:
    1. Find the list for session information
    2. Append session info (url to session, session name) to results
    3. Return a list of all session info
    """
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


def _write_to_db(results: list[dict], url: str, year: int):
    # must write to scrape_race_weekends (has_sessions)
    race_id = extract_race_id.from_url(url) # get race_id

    if results: # isn't empty
        # write 0 to has_sessions
        has_sessions = 1
    else:
        # write 1 to has_sessions
        has_sessions = 0
        
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        # update scrape_race_weekends
        cursor.execute("""
                        UPDATE scrape_race_weekends
                           SET has_sessions = ?
                         WHERE race_id = ? ;
                        """,
                        (has_sessions, race_id)
                        )
        # update scrape_sessions
        session_id = 1
        for session in results:
            cursor.execute("""
                            INSERT INTO scrape_sessions (session_id, race_id, year, session_type, url)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(session_id) DO NOTHING;
                            """,
                            (int(f"{race_id}{session_id}"),
                            race_id,
                            year,
                            session["session_name"], # session type from results
                            session["url"] # url from results
                            )
                           )
            session_id += 1
            """
            # if there is the fastest laps session, the weekend is complete! +1 to scraped_races
            if session["session_name"].strip() == "Fastest Laps":
                scraped_races = database_query.get_scraped_races(year)
                cursor.execute( # need triple quotes if this gets uncommented
                        UPDATE scrape_seasons
                           SET scraped_races = ?
                         WHERE year = ? ;
                        ,
                        (scraped_races+1, year)
                        )
            """
        # update session_id for race_results
        cursor.execute("""
                        UPDATE scrape_sessions
                           SET session_id = ?
                         WHERE race_id = ?
                           AND session_type = "Race Results";
                       """,
                       (int(f"{race_id}{session_id}"),
                        race_id
                        )
                      )

        
def run(html: BeautifulSoup, url: str, year: int):
    """
    Takes in html data, the url of that data, and the year.
    1. Run _extract_items to get a dict list of sessions
    2. Write the sessions to the database
    """
    sessions = _extract_items(soup=html, url=url)
    _write_to_db(results=sessions, url=url, year=year)

def test(flag: str = "output"):
    url = "https://www.formula1.com/en/results/2026/races/1286/monaco/race-result"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    if flag == "output":
        output = _extract_items(soup,url)
        print(output)
    elif flag == "full":
        run(soup, url, 2026)

# test("output")