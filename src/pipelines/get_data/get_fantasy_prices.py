# scrape page
# extract data
# write to db
from scraping import fantasy_price_scraper
from config.config import FANTASY_RAW_DIR, FANTASY_PROCESSED_DIR, DB_PATH
from toolbox import database_query
from interface import prompts
from pathlib import Path
from toolbox import file_management as fm
from processing.extraction import extract_fantasy_prices
from database.management import connection
from pprint import pprint

BASE_URL = r"https://fantasy.formula1.com/feeds/drivers/9_en.json"

def _do_we_need_to_scrape(recent_file: str, directory: Path, latest_race: dict):
    # check if the most recent price information is after the most recent race.
    # If yes, don't bother. If no, return true. If no file, return true also
    file_date = f"{directory.name}-{recent_file.split(".")[0]}"
    if file_date < latest_race["to_date"]:
        return True
    else:
        return False
    
def _do_we_need_to_process(file_date: str) -> bool:
    """Internal function to check if the file needs to be processed by checking if there's any data for 'file_date' in _any_ of the fantasy tables

    Args:
        file_date (str): The file date, YYYY-MM-DD

    Returns:
        bool: True if we do need to process data for 'file_date', False, if we don't (data is already there)
    """    
    # check if there are results in the database. If no, we need to process. If there are results, we check if they relate to the
    tables = ["fantasy_constructor_prices",
              "fantasy_driver_prices",
              "fantasy_raw_constructor_data",
              "fantasy_raw_driver_data"]
    for table in tables:
        query = f"""SELECT * FROM {table} WHERE date = "{file_date}";"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query)
            output = cursor.fetchall()
        if not output:
            return True
    return False

def _update_fantasy_scraping(file_date: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE fantasy_scraping
                             SET is_processed = 1
                           WHERE date = ? ;
                        """, 
                        (file_date,))
        
def _make_url(recent_race: dict) -> str:
    return f"https://fantasy.formula1.com/feeds/drivers/{recent_race["round"]+1}_en.json"
        
def run():
    recent_file, directory = fantasy_price_scraper.get_latest_file(directory=FANTASY_RAW_DIR)
    latest_race = database_query.get_recent_race(table_name="scrape_race_weekends", n_races_ago=0)
    if not recent_file or not latest_race: # if there isn't a file, get it
        fantasy_price_scraper.run(url=BASE_URL)
    else:
        if _do_we_need_to_scrape(recent_file, directory, latest_race):
            fantasy_price_scraper.run(url=BASE_URL)
        else: # do options
            if prompts.scrape_anyway(message=f"\n'{recent_file}' already exists in '{directory}'"):
                fantasy_price_scraper.run(url=BASE_URL)
    recent_file, directory = fantasy_price_scraper.get_latest_file(directory=FANTASY_RAW_DIR)
    if recent_file:
        file_date = f"{directory.name}-{recent_file.split(".")[0]}"
        # check if we need to process
        if _do_we_need_to_process(file_date):
            json_data = fm.load_json_file(directory / recent_file)
            if extract_fantasy_prices.run(json_data, file_date):
                _update_fantasy_scraping(file_date)
            
def test():
    run()