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


def _create_path(year: int, url: str, race_name: str, file_name: str) -> Path:
    # takes url, turns it into /2020/<race_name>/
    path = RAW_DATA_DIR /  str(year) / race_name / f"{file_name}.html"
    return path

def _get_race_name(url: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT race_name
                            FROM scrape_race_weekends
                           WHERE url = ? ;
                        """,(url, )
                            )
        race_name = cursor.fetchone()
    return race_name[0]


def _write_to_scrape_sessions(url: str, year:int, race_id: int, filepath: Path):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        UPDATE scrape_sessions
                        SET filepath = ?
                        WHERE url = ?
                        """,
                        (race_id, 
                         year,
                         "Race Results",
                         url,
                         str(filepath),
                         1,
                         database_query.get_last_scraped(url)
                            )
                        )
        
def _write_to_scrape_seasons(year: int):
    # update scraped sessions value
    pass

def _update_scraped_sessions(year:int):
    ############ work on this
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        # update scrape_race_weekends
        cursor.execute("""
                        UPDATE scrape_seasons
                           SET scraped_races = (SELECT COUNT(*)
                                                  FROM scrape_race_weekends
                                                 WHERE has_sessions
                        """
        )
    
def download_sessions(urls: list[str], year: int, race_id: int, progress: Progress):
    ## progresss bar
    download_task = progress.add_task(f"  ↳ Downloading URL: ", total=len(urls))

    if urls:
        _write_to_scrape_seasons(year) # sets has_races to 1
        for url in urls:
            short_url = f"f1.com/.../{url.split('/races/')[-1]}"
            progress.update(download_task, description=f"  ↳ Downloading URL: [grey11]{short_url:<50}[/grey11]")

            race_name = _get_race_name(url)
            output_path = _create_path(year, url, race_name, file_name)
            scraper.html_scraper(url, output_path)
            _write_to_scrape_weekends(url, output_path)

            progress.advance(download_task)
            
        progress.remove_task(download_task)
    else:
        return