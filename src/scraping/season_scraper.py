"""
Goes through each season:
https://www.formula1.com/en/results/{fyear}/races (format(fyear = year))
given a start year, end year (default start = 1950, default end = this year)

Gets:
- html page prettified by beautifulsoup.prettify()

Outputs html page into:
data/sessions/raw/<year>/<year>.html
"""
from pathlib import Path
import datetime
from scraping.bones import html_scraper_toolbox as scraper
from config.config import RAW_DATA_DIR, LOG_DATA_DIR, DB_PATH
import toolbox.file_management as fm
from database.management import connection

# 1. Check if years.csv exists, create file if it doesn't

def create_path(year: int) -> Path:
    path = Path(RAW_DATA_DIR) / str(year) / f"{str(year)}.html"
    return path

def log(url, year, filepath):
    pass
    
def download_years(base_url: str = "https://www.formula1.com/en/results/{fyear}/races",
                   start_year: int = 1950,
                   end_year: int = int(datetime.datetime.now().strftime("%Y"))
                   ):
    for year in range(start_year, end_year+1):
        url = base_url.format(fyear = year)
        scraper.html_scraper(url,create_path(year))
        with connection.get_db(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO scrape_seasons (year, url, scraped, last_scraped)
                              VALUES (?, ?, ?, ?)
                              ON CONFLICT(year) DO UPDATE SET
                                  url = EXCLUDED.url,
                                  scraped = EXCLUDED.scraped,
                                  last_scraped = EXCLUDED.last_scraped;
                           """,(year,
                                url,
                                1,
                                datetime.datetime.now())
                            )