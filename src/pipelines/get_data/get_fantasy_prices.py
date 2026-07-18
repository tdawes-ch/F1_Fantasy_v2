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
from pprint import pprint, pp
from datetime import datetime

BASE_URL = "https://fantasy.formula1.com/feeds/drivers/{fround}_en.json"

def _do_we_need_to_scrape(recent_file: str, directory: Path, round: int, year: int):
    # check if the recent file matches the info of the recent race
    dir_year = int(directory.name)
    file_round = int(recent_file.split(".")[0])
    if dir_year == year and file_round == round:
        return True
    else:
        return False
    
def _do_we_need_previous(year: int, round: int):
    for i in range(round):
        print(i)
    
def _do_we_need_to_process(round: int, year: int = int(datetime.now().strftime("%Y"))) -> bool:
    """Internal function to check if the file needs to be processed by checking if there's any data for 'year' and 'round' in _any_ of the fantasy tables

    Args:
        year (int): The year, usually the current year
        round (int): The round

    Returns:
        bool: True if we do need to process data for 'file_date', False, if we don't (data is already there)
    """    
    # check if there are results in the database. If no, we need to process. If there are results, we check if they relate to the
    tables = ["fantasy_constructor_prices",
              "fantasy_driver_prices",
              "fantasy_raw_constructor_data",
              "fantasy_raw_driver_data"]
    for table in tables:
        query = f"""SELECT * FROM {table} WHERE year = {year} and round = {round};"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query)
            output = cursor.fetchall()
        if not output:
            return True
    return False

def _update_fantasy_scraping(round: int, year: int = int(datetime.now().strftime("%Y"))):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE fantasy_scraping
                             SET is_processed = 1
                           WHERE year = ? 
                             AND round = ?;
                        """, 
                        (year, round))
        
def _make_url(recent_race: dict) -> str:
    return f"https://fantasy.formula1.com/feeds/drivers/{recent_race["round"]+1}_en.json"

"""       
def run1():
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
    if recent_file:
        file_date = f"{directory.name}-{recent_file.split(".")[0]}"
        # check if we need to process
        if _do_we_need_to_process(file_date):
            json_data = fm.load_json_file(directory / recent_file)
            if extract_fantasy_prices.run(json_data, file_date):
                _update_fantasy_scraping(file_date)
"""

def run():
    # We need to: first check if the most recent results are collected
    recent_race = database_query.get_recent_race(table_name="scrape_race_weekends", n_races_ago=0)
    if not recent_race:
        return
    year, round = recent_race["season"], recent_race["round"]
    if _do_we_need_to_process(round, year):
        ""
        recent_file, directory = fantasy_price_scraper.get_latest_file(directory=FANTASY_RAW_DIR)
        if recent_file:
            if _do_we_need_to_scrape(recent_file, directory, round, year):
                for i in range(round):
                    print(f"scraping: {i} '{BASE_URL.format(fround = i)}'")
                #fantasy_price_scraper.run()
            else:
                print("we need to process whats here")
        else:
            print("we should scrape")

            
def test():
    run()

test()