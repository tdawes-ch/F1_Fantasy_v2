'''
goes through each session in:

data/sessions/processed/<year>/<weekend>/sessions.csv

that isn't called race-result (this was collected in race_scraper)

Downloads html into: 
data/sessions/processed/<year>/<weekend>/<session_name>
e.g.:
data/sessions/processed/2026/canada/race-result

'''

"""
Copied structure from season_scraper

download_races gets called, with a list of urls and the season year as the parameter

1. 
"""

from pathlib import Path
from scraping.bones import html_scraper_toolbox as scraper
from config.config import RAW_DATA_DIR, DB_PATH
import toolbox.file_management as fm
from toolbox import extract_race_id, database_query
from database.management import connection
from rich.progress import Progress


def _create_path(year: int, race_name: str, file_name: str) -> Path:
    """
    takes url, turns it into /2020/<race_name>/<session_type>.html
    """
    path = RAW_DATA_DIR /  str(year) / race_name / f"{file_name}.html"
    return path

def _create_filename(url: str) -> str:
    """
    takes url, turns it into .html relative to the session type
    e.g. Practice 1 -> practice_1
    """
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT session_type
                          FROM scrape_sessions
                         WHERE url = ? ;
                       """,
                       (url,
                       )
                      )
        output = cursor.fetchone()[0].strip() # bad idea to not strip the output lol
    return f"{"_".join(session_name for session_name in output.lower().split(" "))}.html"

def _get_race_name(url: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT srw.race_name
                          FROM scrape_race_weekends srw
                          LEFT JOIN scrape_sessions ss ON srw.race_id = ss.race_id
                         WHERE ss.url = ?;
                        """,
                        (url, )
                            )
        race_name = cursor.fetchone()
    return race_name[0]

def _write_to_scrape_sessions(url: str, filepath: Path):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        UPDATE scrape_sessions
                           SET filepath = ?,
                               scraped = 1,
                               last_scraped = ?
                        WHERE url = ? ;
                        """,
                        (str(filepath), 
                         database_query.get_last_scraped(url),
                         url
                            )
                        )

def download_sessions(urls: list[str], year: int, race_id: int, progress: Progress):
    """
    Args:
    - urls: a list of session urls for a set race weekend
    - year: the year being processed
    - race_id: the race ID of the race weekend
    - progress: the progress bar
    """
    ## progresss bar
    download_task = progress.add_task(f"  ↳ Downloading URL: ", total=len(urls))

    if urls:
        for session_url in urls: # essentially, for session in race
            session_filename = _create_filename(url=session_url)
            short_url = f"f1.com/.../{session_url.split('/races/')[-1]}"
            progress.update(download_task, description=f"  ↳ Downloading URL: [grey11]{short_url:<50}[/grey11]")

            race_name = _get_race_name(url=session_url) # get race name
            output_path = _create_path(year=year, race_name=race_name, file_name=session_filename) # create output path for .html
            scraper.html_scraper(session_url, output_path) # send url to be scraped

            _write_to_scrape_sessions(session_url, output_path) # write to scrape sessions table
            progress.advance(download_task)

        progress.remove_task(download_task)
    else:
        return