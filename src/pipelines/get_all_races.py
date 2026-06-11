from processing.extraction import extract_circuit_name, extract_all_races, extract_sessions
from toolbox import network
from scraping import season_scraper
from database import init_db
from database.management import connection as con
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from pathlib import Path

def _create_csv_path(dir: Path, year: int) -> Path:
    return dir / str(year) / f"{year}.csv"

def _create_html_path(dir: Path, year: int) -> Path:
    return dir / str(year) / f"{year}.html"

def get_all_races(start_year: int, end_year: int, base_url):
    # this is network dependent, compartmentalises it so I can test it 
    # without scraping EVERYTHING and wasting bandwidth
    season_scraper.download_years(base_url, start_year, end_year)

    for year in range(start_year,end_year+1):
        html_path = _create_html_path(dir=RAW_DATA_DIR, year=year)
        csv_path = _create_csv_path(dir=PROCESSED_DATA_DIR, year=year)
        extract_all_races.extract_season_races(html_path,csv_path,base_url) # gets all
        # At this point, we've got season data and basic race data in the scraped tables. We now need more indepth race info