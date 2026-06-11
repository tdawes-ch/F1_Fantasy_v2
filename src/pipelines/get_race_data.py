'''
Stuck on the pipeline for this a bit :/
We will loop through each season e.g. 2020. Following is pseudocode:

for year in season:
    if flag = 'CSV':
        get filepath to csv (processed/<year>/<year>.csv)
        open csv using toolbox.file_management.load_csv
        get urls to -> urls []
    elif flag = 'DB'
        query scrape_race_weekends for urls where year = year
        export into urls []
    # once urls are collected:
    send urls to race_scraper? (yes)
    races are now all scraped, can then use the same urls to get other race data (or run that inside race_scraper)

And then we can go through each session. Similar format to this 
'''
from pathlib import Path
from config.config import PROCESSED_DATA_DIR
from toolbox import file_management as fm
from config.config import DB_PATH
from database.management import connection
from scraping import race_scraper

def _get_filepath_to_csv(year: int) -> Path:
    return PROCESSED_DATA_DIR / str(year) / f"{year}.csv"

def _get_urls_from_csv(path_to_csv: Path) -> list[str]:
    csvfile = fm.load_csv(csv_path=path_to_csv)
    urls = []
    for row in csvfile:
        urls.append(row["url"])
    return urls

def _get_urls_from_db(year: int) -> list[str]:
    urls = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT url
                            FROM scrape_race_weekends
                           WHERE year = ? ;
                        """, (str(year),)
        )
        output = cursor.fetchall()
 
    for row in output:
        urls.append(row[0])

    return urls

def get_race_data(start_year: int, end_year: int, flag: str='db'):
    """
    This will get all race data. 
    It will loop through each race URL, get the race_id, then:
    1. Scrape the race pages (https://www.formula1.com/en/results/2026/races/1287/barcelona-catalunya/race-result)
        a.  update scraped_seasons.scraped_races number
    2. Call extract_circuit_name
    3. Call extract_sessions
    4. Loop through sessions
    5. Needs to updated 
    based on the url found in either the csv. 
    """
    for year in range(start_year, end_year+1):
        # get the urls to pass through
        if flag.lower() == 'db':
            urls = _get_urls_from_db(year)
        elif flag.lower() == 'csv':
            urls = _get_urls_from_csv(_get_filepath_to_csv(year))
        else:
            raise ValueError(f"Unexpected flag value: '{flag}'. Expected 'db' or 'csv'.")
        
        # scrape all races
        race_scraper.download_races(urls, year)

