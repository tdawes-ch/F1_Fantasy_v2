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
from database.management import connection

def create_path(year: int, url: str) -> Path:
    # takes url, turns it into /2020/<race_name>
    return Path(url)

def get_race_name():
    race_name = ''
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO race_weekends;
                        """,()
                            )
    pass

def write_to_db(year, url, output_path):
    # writes the scraper update to the database
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO race_weekends;
                        """,()
                            )
    
def download_races(urls: list[str],
                   year: int
                   ):
    for url in urls:
        output_path = create_path(year, url) # path
        scraper.html_scraper(url, output_path)
        write_to_db(year, url, output_path)

