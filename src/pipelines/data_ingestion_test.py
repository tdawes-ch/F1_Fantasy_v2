from processing.extraction import extract_all_races
from scraping import season_scraper
from database import init_db
from database.management import connection as con
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

init_db.init_db() # goes in main

base_url = "https://www.formula1.com/en/results/{fyear}/races"
start_year = 2020
end_year = 2026

season_scraper.download_years(base_url, start_year, end_year)

for year in range(start_year,end_year+1):
    html_path = RAW_DATA_DIR / str(year) / f"{year}.html"
    csv_path = PROCESSED_DATA_DIR / str(year) / f"{year}.csv"
    extract_all_races.extract_season_races(html_path,csv_path,base_url)