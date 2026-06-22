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

def _create_path(year: int) -> Path:
    """An internal function used to create the output filepath for the HTML data. It takes in the year and converts it into a full filepath:
    - year -> raw_data_dir/year/year.html
    - 2020 -> raw_data_dir/2020/2020.html

    Args:
        year (int): The year of the season

    Returns:
        Path: The output path for the HTML file
    """
    path = Path(RAW_DATA_DIR) / str(year) / f"{str(year)}.html"
    return path

def _write_to_db(year, url, output_path):
    """An internal function that writes to the 'scrape_seasons' table in the database. It adds the following (if it doesn't already exist):
    - Year
    - URL
    - Filepath
    - Scraped (0 -> 1)
    - Last scraped timestamp

    Args:
        year (_type_): The year of the season
        url (_type_): The URL of the year overview page
        output_path (_type_): The file path to the associated HTML file
    """    
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
    """Given a start and end year, this will loop through each year and download the HTML data for the 
    year summary page, write to a file, and write to the database.

    Args:
        progress (Progress): Inherits the progress bar
        base_url (_type_, optional): The base URL for the F1 year summary pages. Defaults to "https://www.formula1.com/en/results/{fyear}/races".
        start_year (int, optional): The first year to be scraped. Defaults to 1950.
        end_year (int, optional): The last year to be scraped. Defaults to int(datetime.datetime.now().strftime("%Y")) aka this current year.
    """
    num_seasons = end_year + 1 - start_year
    # setup progress bar
    download_task = progress.add_task(f"Downloading season: [bold magenta]{start_year}[/bold magenta]", total=num_seasons)

    for year in range(start_year, end_year+1):
        # update bar
        progress.update(download_task, description=f"Downloading season: [bold magenta]{year}[/bold magenta]")
        # create values
        url = base_url.format(fyear = year)
        output_path = _create_path(year) # path
        # scrape html
        scraper.html_scraper(url, output_path)
        # write to database
        _write_to_db(year, url, output_path)
        # add 1++
        progress.advance(download_task)

    progress.update(download_task, description=f"[green]✓ Seasons ({start_year} -> {end_year}) downloaded[/green]")