"""
Copied structure from season_scraper

download_races gets called, with a list of urls and the season year as the parameter

1. 
"""

from pathlib import Path
from scraping.bones import html_scraper_toolbox as scraper
from config.config import RAW_DATA_DIR, DB_PATH
from toolbox import extract_race_id, database_query
from database.management import connection
from rich.progress import Progress
import datetime


def _create_path(year: int, url: str, race_name: str) -> Path:
    # takes url, turns it into /2020/<race_name>
    path = RAW_DATA_DIR /  str(year) / race_name / "race_results.html"
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

def _write_to_scrape_weekends(url: str, output_path: Path):
    # writes the scraper update to the database
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_race_weekends
                             SET scraped = 1, filepath = ?, last_scraped = ?
                           WHERE url = ?;
                        """,(str(output_path), 
                             database_query.get_last_scraped(url),
                             url)
                            )
        # could also insert to scrape_sessions for race results, but will do that elsewhere

def _write_to_scrape_seasons(year:int):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_seasons
                             SET has_races = 1
                           WHERE year = ?;
                        """,(str(year),)
        )

def _write_to_scrape_sessions(url: str, year:int, filepath: Path):
    race_id = extract_race_id.from_db(data=url, flag="url")
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO scrape_sessions (session_id, race_id, year, session_type, url, filepath, scraped, last_scraped)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(url) DO UPDATE SET
                            last_scraped = EXCLUDED.last_scraped;
                        """,
                        (int(f"{race_id}000"),
                         race_id, 
                         year,
                         "Race Results",
                         url,
                         str(filepath),
                         1,
                         database_query.get_last_scraped(url)
                            )
                        )
    
def download_races(urls: list[str], year: int, progress: Progress):
    ## progresss bar
    download_task = progress.add_task(f"  ↳ Downloading URL: ", total=len(urls))

    if urls:
        _write_to_scrape_seasons(year) # sets has_races to 1
        for url in urls:
            short_url = f"f1.com/.../{url.split('/races/')[-1]}"
            task_message = f"{short_url:<40}"
            progress.update(download_task, description=f"  ↳ Downloading URL: [grey11]{task_message}[/grey11]")

            race_name = _get_race_name(url)
            output_path = _create_path(year, url, race_name)
            scraper.html_scraper(url, output_path)

            task_message = f"{"Writing to database...":<40}"
            progress.update(download_task, description=f"  ↳ Downloading URL: [grey11]{task_message}[/grey11]")
            _write_to_scrape_weekends(url, output_path)
            _write_to_scrape_sessions(url, year, output_path)

            progress.advance(download_task)
            
        progress.remove_task(download_task)
    else:
        return