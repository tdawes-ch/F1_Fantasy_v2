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
from config.config import RAW_DATA_DIR, DB_PATH
import toolbox.file_management as fm
from database.management import connection
from rich.progress import Progress


# 1. Check if years.csv exists, create file if it doesn't

def create_path(year: int) -> Path:
    path = Path(RAW_DATA_DIR) / str(year) / f"{str(year)}.html"
    return path

def write_to_db(year, url, output_path):
    # writes the scraper update to the database
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO scrape_seasons (year, url, filepath, scraped, last_scraped)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(year) DO UPDATE 
                            SET filepath = EXCLUDED.filepath,
                                scraped = EXCLUDED.scraped,
                                last_scraped = EXCLUDED.last_scraped;
                        """,(year,
                            url,
                            str(output_path),
                            1,
                            datetime.datetime.now())
                            )
    
def download_years(progress: Progress,
                   base_url: str = "https://www.formula1.com/en/results/{fyear}/races",
                   start_year: int = 1950,
                   end_year: int = int(datetime.datetime.now().strftime("%Y")),
                   ):
    num_seasons = end_year + 1 - start_year
    # setup progress bar
    download_task = progress.add_task(f"Downloading season: [bold magenta]{start_year}[/bold magenta]", total=num_seasons)

    for year in range(start_year, end_year+1):
        # update bar
        progress.update(download_task, description=f"Downloading season: [bold magenta]{year}[/bold magenta]")
        # create values
        url = base_url.format(fyear = year)
        output_path = create_path(year) # path
        # scrape html
        scraper.html_scraper(url, output_path)
        # write to database
        write_to_db(year, url, output_path)
        # add 1++
        progress.advance(download_task)

    progress.update(download_task, description=f"[green]✓ Seasons ({start_year} -> {end_year}) downloaded[/green]")