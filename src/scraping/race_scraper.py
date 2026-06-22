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
    """Takes a URL and turns it into /2020/<race_name>/race_results.html

    Args:
        year (int): The year of the F1 season e.g. 2020
        url (str): The full URL to the race weekend
        race_name (str): The name of the race

    Returns:
        Path: The full output path to the race HTML file e.g.
            <path_to_project>/2020/<race_name>/race_results.html
    """
    # takes url, turns it into /2020/<race_name>
    path = RAW_DATA_DIR /  str(year) / race_name / "race_results.html"
    return path

def _get_race_name(url: str) -> str:
    """From a given URL, this function calls SQL to get the name of the current race

    Args:
        url (str): The URL to the race results page

    Returns:
        str: The name of the race from the database
    """    
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
    """This function writes data to the 'scrape_race_weekends' table which stores data in the race weekends.
    We update the table to show that the URL has now been scraped and set the column to the filepath to the HTML file

    Args:
        url (str): The URL to the race weekend that is being scraped
        output_path (Path): The output path to the HTML file for the url
    """    
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
    """This function writes data to the 'scrape_seasons' table which stores data pertaining to the whole season.
    We update the table to show that the season contains races

    Args:
        year (int): The year of the F1 season that the race weekend is in
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_seasons
                             SET has_races = 1
                           WHERE year = ?;
                        """,(str(year),)
        )

def _write_to_scrape_sessions(url: str, year:int, filepath: Path):
    """This function writes data to the 'scrape_sessions' table which stores data pertaining to individual sessions.
    We insert:
        - session_id (race_id+000)
        - race_id
        - year
        - session_type (Race Results)
        - url
        - filepath (for the scraped URL)
        - scraped (set to 1 as it's now scraped)
        - last_scraped (timestamp that this URL was last scraped)

    Args:
        url (str): The URL of the race weekend
        year (int): The year of the F1 season that the race weekend is in
        filepath (Path): The filepath to the HTML file associated with the URL
    """    
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
    """Takes in the URLs and the year that's being downloaded and creates the associated data in order to download all URLs and update the database correctly.

    Args:
        urls (list[str]): A list of URLs of all of the races for the year
        year (int): The year being downloaded
        progress (Progress): Inherits the progress bar
    """
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