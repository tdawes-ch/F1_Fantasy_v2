# scrape page
# extract data
# write to db
from scraping import fantasy_price_scraper
from config.config import FANTASY_RAW_DIR, FANTASY_PROCESSED_DIR
from toolbox import database_query
from interface import prompts
from pathlib import Path
from toolbox import file_management as fm
from processing.extraction import extract_fantasy_prices

BASE_URL = r"https://fantasy.formula1.com/en/statistics/details"

def _do_we_need_to_scrape(recent_file: str, directory: Path, latest_race: dict):
    # check if the most recent price information is after the most recent race.
    # If yes, don't bother. If no, return true. If no file, return true also
    file_date = f"{directory.name}-{recent_file.split(".")[0]}"
    if file_date < latest_race["to_date"]:
        return True
    else:
        return False
    
def _do_we_need_to_process() -> bool:
    # check if there are results in the database. If no, we need to process. If there are results, we check if they relate to the 
    return True
        
def run():
    recent_file, directory = fantasy_price_scraper.get_latest_file(directory=FANTASY_RAW_DIR)
    latest_race = database_query.get_recent_race(table_name="scrape_race_weekends", n_races_ago=0)
    if not recent_file or not latest_race: # if there isn't a file, get it
        fantasy_price_scraper.run(url=BASE_URL)
    else:
        if _do_we_need_to_scrape(recent_file, directory, latest_race):
            fantasy_price_scraper.run(url=BASE_URL)
        else: # do options
            if prompts.scrape_anyway(message=f"\n{recent_file} already exists in '{directory}'"):
                fantasy_price_scraper.run(url=BASE_URL)
    recent_file, directory = fantasy_price_scraper.get_latest_file(directory=FANTASY_RAW_DIR)
    if recent_file:
        file_date = f"{directory.name}-{recent_file.split(".")[0]}"
        # check if we need to process
        if _do_we_need_to_process():
            json_data = fm.load_json_file(directory / recent_file)
            extract_fantasy_prices.run(json_data, file_date)
            
def test():
    run()

test()