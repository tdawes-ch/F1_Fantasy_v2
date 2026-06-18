from processing.extraction import extract_circuit_name, extract_all_races, extract_sessions
from toolbox import network
from scraping import season_scraper
from database import init_db
from database.management import connection as con
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from pathlib import Path
from rich.progress import Progress

def _create_csv_path(dir: Path, year: int) -> Path:
    return dir / str(year) / f"{year}.csv"

def _create_html_path(dir: Path, year: int) -> Path:
    return dir / str(year) / f"{year}.html"

def run(start_year: int, end_year: int, base_url, progress: Progress):
    """
    1. Downloads the year pages
    2. Goes through each year:
        a. Extracts the list of all races and writes to database
    """
    num_seasons = end_year + 1 - start_year
    # scrape the years
    season_scraper.download_years(progress, base_url, start_year, end_year)
    
    # setup progress bar
    extraction_task = progress.add_task(f"Processing season: [bold magenta]{start_year}[/bold magenta]", total=num_seasons)
    # extract all race names and stuff from the html
    for year in range(start_year,end_year+1):
        progress.update(extraction_task, description=f"Processing season: [bold magenta]{year}[/bold magenta]")
        html_path = _create_html_path(dir=RAW_DATA_DIR, year=year)
        csv_path = _create_csv_path(dir=PROCESSED_DATA_DIR, year=year)
        extract_all_races.extract_season_races(html_path,csv_path,base_url) # gets all races
        # At this point, we've got season data and basic race data in the scraped tables. We now need more indepth race info
        progress.advance(extraction_task)

    progress.update(extraction_task, description=f"[green]✓ Race information processed[/green]")