# scrape page
# extract data
# write to db
from scraping import fantasy_price_scraper
from config.config import FANTASY_RAW_DIR, FANTASY_PROCESSED_DIR, DB_PATH
from toolbox import database_query
from pathlib import Path
from toolbox import file_management as fm
from processing.extraction import extract_fantasy_prices
from database.management import connection
from pprint import pprint, pp
from interface.progress_manager import get_progress_bar
from datetime import datetime
from rich.progress import Progress

BASE_URL = "https://fantasy.formula1.com/feeds/drivers/{fround}_en.json"

def _do_we_need_to_scrape(recent_file: str, directory: Path, round: int, year: int) -> bool:
    """Checks recent race data against the most recent file to see if we need to scrape. This is currently not in use.

    Args:
        recent_file (str): The filename of the most recent json file
        directory (Path): The directory to the file
        round (int): The most recent round in the database
        year (int): The most recent year in the database

    Returns:
        bool: True if we need to scrape, False if we don't
    """
    # check if the recent file matches the info of the recent race
    dir_year = int(directory.name)
    file_round = int(recent_file.split(".")[0])
    if dir_year == year and file_round == round:
        return False
    else:
        return True
    
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
    """Updates the `fantasy_scraping` table in the database. It sets `is_processed` to 1 instead of 0 to symbolise that the fantasy data is now properly processed.

    Args:
        round (int): The round
        year (int, optional): The year. Defaults to `int(datetime.now().strftime("%Y"))`, the current year.
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE fantasy_scraping
                             SET is_processed = 1
                           WHERE year = ? 
                             AND round = ?;
                        """, 
                        (year, round))
        
def _make_url(recent_race: dict) -> str:
    """Internal function that makes the URL to the JSON data, given recent race information. Currently unused.

    Args:
        recent_race (dict): The most recent race information, as a dictionary.

    Returns:
        str: The formatted URL
    """    
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
def _load_and_process_data(path_to_json: Path,
                          year: int,
                          round: int):
    """Internal function that loads fantasy price data from a JSON path, and then passes that to `extract_fantasy_prices.run()`
    to extract and write the cleaned data to CSVs and the database.

    Args:
        path_to_json (Path): The path to the JSON file.
        year (int): The year
        round (int): The round
    """
    fantasy_price_json = fm.load_json_file(filepath=path_to_json)
    extract_fantasy_prices.run(json_data=fantasy_price_json,
                                year=year,
                                round=round)

def run(progress: Progress):
    """The full pipeline of checking for existing JSON data, checking whether it's been processed or not, and scraping and processing based
    on how the checks have played out. 

    Args:
        progress (Progress): The progress bar instance
    """    
    fantasy_data_task = progress.add_task(description=f"[bold magenta]Getting info from recent race...[/bold magenta]")
    recent_race = database_query.get_recent_race(table_name="scrape_race_weekends", n_races_ago=0)
    if not recent_race:
        progress.update(task_id=fantasy_data_task,
                        description=f"[bold yellow]No recent race data.[/bold yellow]")
        return
    
    year, round = recent_race["season"], recent_race["round"]
    progress.update(task_id=fantasy_data_task,
                    description=f"[bold magenta]{year}, round {0}:[/bold magenta]", 
                    total=round+1)

    for i in range(1, round + 2): # round + 2 instead of + 1 because price data is shown for the next race before the next race has started.
        progress.update(task_id=fantasy_data_task,
                        description=f"[bold magenta]{year}, round {i}:[/bold magenta] Checking for existing .json...")
        fantasy_data_path = FANTASY_RAW_DIR / str(year) / f"{i}.json"
        if not fm.check_location(filepath=fantasy_data_path): # flag="file"
            progress.update(task_id=fantasy_data_task,
                            description=f"[bold magenta]{year}, round {i}:[/bold magenta] .json not found, downloading...")
            fantasy_price_scraper.run(url=BASE_URL.format(fround = i),
                                      year=year,
                                      round=i)
        
        progress.update(task_id=fantasy_data_task,
                        description=f"[bold magenta]{year}, round {i}:[/bold magenta] Checking for processed .json data...")
        if _do_we_need_to_process(round=i, year=year):
            progress.update(task_id=fantasy_data_task,
                            description=f"[bold magenta]{year}, round {i}:[/bold magenta] Loading and processing .json...")
            _load_and_process_data(path_to_json=fantasy_data_path,
                                   year=year,
                                   round=i)
            _update_fantasy_scraping(round=i, year=year)

        progress.advance(task_id=fantasy_data_task)
    progress.update(task_id=fantasy_data_task,
                    description=f"[green]✓ Fantasy price data for rounds {1} -> {round+1} extracted[/green]")
    
            
            
def test():
    with get_progress_bar() as fantasy_data_progress:
        run(fantasy_data_progress)

#test()