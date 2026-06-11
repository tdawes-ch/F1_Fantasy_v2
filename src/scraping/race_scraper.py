"""
Copied structure from season_scraper

download_races gets called, with a list of urls and the season year as the parameter

1. 
"""

from pathlib import Path, PurePosixPath
import datetime
from scraping.bones import html_scraper_toolbox as scraper
from config.config import RAW_DATA_DIR, LOG_DATA_DIR, DB_PATH
import toolbox.file_management as fm
import toolbox.extract_race_id as get_id
from database.management import connection
from rich.console import Console
from rich.live import Live
from rich.console import Group
from rich.text import Text
from rich.progress import (
    Progress, 
    BarColumn, 
    TaskProgressColumn, 
    TimeRemainingColumn, 
    MofNCompleteColumn
)


def create_path(year: int, url: str, race_name: str) -> Path:
    # takes url, turns it into /2020/<race_name>
    path = RAW_DATA_DIR /  str(year) / race_name / "race_results.html"
    return path

def get_race_name(url: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT race_name
                            FROM scrape_race_weekends
                           WHERE url = ? ;
                        """,(url, )
                            )
        race_name = cursor.fetchone()
    return race_name[0]

def write_to_db(url: str):
    # writes the scraper update to the database
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_race_weekends
                             SET scraped = 1
                           WHERE url = ?;
                        """,(url, )
                            )
        # could also insert to scrape_sessions for race results, but will do that elsewhere
    
def download_races(urls: list[str], year: int):
    for url in urls:
        race_name = get_race_name(url)
        output_path = create_path(year, url, race_name)
        scraper.html_scraper(url, output_path)
        write_to_db(url)