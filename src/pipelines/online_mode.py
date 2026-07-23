# separate file for online functions?
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_PATH
from interface.progress_manager import get_progress_bar
from rich import print
from interface import prompts
from pipelines.get_data import get_all_races, get_all_results, get_race_data, get_session_data, get_fantasy_prices
from logging_utils.logger_config import setup_logging
from datetime import datetime
from datetime import datetime
from rich.console import Console

console = Console()

def run_scraping(start_year, end_year):
    base_url = "https://www.formula1.com/en/results/{fyear}/races"
    print()

    num_seasons = end_year - start_year + 1
    
    # console.print(f"\nPreparing to scrape {num_seasons} season(s)...\n")
    # get races from each year
    with get_progress_bar() as year_progress:
        console.print(f"[b]\nGetting and processing the {num_seasons} season overview page(s):[/b]")
        get_all_races.run_online(start_year,end_year,base_url,year_progress)

    # get the race html and extract info
    with get_progress_bar() as race_progress:
        console.print(f"[b]\nGetting and processing individual races:[/b]")
        get_race_data.run(start_year,end_year,race_progress,flag='db')

    # get session html (e.g. practice 1, qualy, etc.)
    with get_progress_bar() as session_progress:
        console.print(f"[b]\nGetting and processing individual race sessions:[/b]")
        get_session_data.run(start_year, end_year, session_progress)

    # get fantasy json data, but only if the end year is in
    current_year = int(datetime.now().strftime("%Y"))
    if current_year in range(start_year, end_year + 1):
        with get_progress_bar() as fantasy_data_progress:
            console.print(f"[b]\nGetting and processing fantasy data:[/b]")
            get_fantasy_prices.run(fantasy_data_progress)
    else:
        console.print(f"[b]\nSkipping getting fantasy data as current year ({current_year}) is not within range ({start_year} -> {end_year}).[/b]")


# function to get the most recent year
def get_latest_year():
    pass

def run():
    pass