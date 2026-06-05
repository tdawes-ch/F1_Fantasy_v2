from processing.extraction import extract_circuit_name, extract_all_races, extract_sessions
from toolbox import network
from scraping import season_scraper
from database import init_db
from database.management import connection as con
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def get_all_races(start_year: int, end_year: int, base_url):
    # this is network dependent, compartmentalises it so I can test it 
    # without scraping EVERYTHING and wasting bandwidth
    season_scraper.download_years(base_url, start_year, end_year)

    for year in range(start_year,end_year+1):
        html_path = RAW_DATA_DIR / str(year) / f"{year}.html"
        csv_path = PROCESSED_DATA_DIR / str(year) / f"{year}.csv"
        extract_all_races.extract_season_races(html_path,csv_path,base_url)
        # At this point, we've got season data and basic race data in the scraped tables. We now need more indepth race info


init_db.init_db() # goes in main

base_url = "https://www.formula1.com/en/results/{fyear}/races"
start_year = 2020
end_year = 2026

connection_ok, connection_error = network.test_outbound_connection()

if connection_ok:
    get_all_races(start_year,end_year,base_url)
else:
    print(connection_error)