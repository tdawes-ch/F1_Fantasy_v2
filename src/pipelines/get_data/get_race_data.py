'''
We will loop through each season e.g. 2020. Following is pseudocode:

for year in season:
    if flag = 'CSV':
        get filepath to csv (processed/<year>/<year>.csv)
        open csv using toolbox.file_management.load_csv
        get urls to -> urls []
    elif flag = 'DB'
        query scrape_race_weekends for urls where year = year
        export into urls []
    # once urls are collected:
    send urls to race_scraper? (yes)
    races are now all scraped, can then use the same urls to get other race data (or run that inside race_scraper)

And then we can go through each session. Similar format to this 
'''
from pathlib import Path
from config.config import PROCESSED_DATA_DIR
from toolbox import file_management as fm
from config.config import DB_PATH
from database.management import connection
from scraping import race_scraper
from processing.extraction import extract_circuit_name, extract_sessions
from rich.progress import Progress

def _get_race_name_from_db(url: str) -> str:
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT race_name
                            FROM scrape_race_weekends
                           WHERE url = ? ;
                        """, (url,)
        )
        race_name = cursor.fetchone()

    return race_name[0]

def _get_filepath_to_csv(year: int) -> Path:
    return PROCESSED_DATA_DIR / str(year) / f"{year}.csv"

def _get_urls_from_csv(path_to_csv: Path) -> list[str]:
    csvfile = fm.load_csv(csv_path=path_to_csv)
    urls = []
    for row in csvfile:
        urls.append(row["url"])
    return urls

def _get_urls_from_db(year: int) -> list[str]:
    urls = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT url
                            FROM scrape_race_weekends
                           WHERE year = ? ;
                        """, (str(year),)
        )
        output = cursor.fetchall()
 
    for row in output:
        urls.append(row[0])

    return urls

def _get_filepath_to_html_from_url(url: str) -> Path:
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT filepath
                            FROM scrape_race_weekends
                           WHERE url = ? ;
                        """, (url,)
        )
        filepath = Path(cursor.fetchone()[0])
    
    if filepath == None:
        raise ValueError(f"Filepath doesn't exist in database for url: {url}")

    return filepath

def run(start_year: int, end_year: int, progress: Progress, flag: str='db'):
    """
    This will get all race data. 
    It will loop through each race URL, get the race_id, then:
    1. Scrape the race pages (https://www.formula1.com/en/results/2026/races/1287/barcelona-catalunya/race-result)
        a.  update scraped_seasons.scraped_races number
    2. Call extract_circuit_name
    3. Call extract_sessions
    4. Loop through sessions
    5. Needs to updated 
    based on the url found in either the csv. 
    """
    # setup progress bar
    num_seasons = end_year + 1 - start_year
    extraction_task = progress.add_task(f"[bold magenta]{start_year}:[/bold magenta]", total=num_seasons)

    # go through each year
    for year in range(start_year, end_year+1):
        ## progress bars
        progress.update(extraction_task,description=f"[bold magenta]Current year: {year}[/bold magenta][bright_cyan] Getting race URLs...[/bright_cyan]")

        # get the urls to pass through
        if flag.lower() == 'db':
            urls = _get_urls_from_db(year)
        elif flag.lower() == 'csv':
            urls = _get_urls_from_csv(_get_filepath_to_csv(year))
        else:
            raise ValueError(f"Unexpected flag value: '{flag}'. Expected 'db' or 'csv'.")
        
        progress.update(extraction_task,description=f"[bright_cyan]Current season: [/bright_cyan][bold magenta]{year}[/bold magenta]")

        processing_task = progress.add_task(f"↳ [bold magenta]{year}: [/bold magenta]", total=None)

        # scrape all races
        race_scraper.download_races(urls, year, progress)
        progress.update(processing_task, total=len(urls))
        # get more specific race information 8520
        ## for each race, get filepath to html, do extraction things

        for race_url in urls:
            race_name = _get_race_name_from_db(url=race_url)
            padded_race = f"{race_name:<20}"

            progress.update(processing_task, description=f"↳ [bold magenta]{year}: [/bold magenta][purple]{padded_race}[/purple][cyan]          Getting HTML Path...[/cyan]")
            path_to_html = _get_filepath_to_html_from_url(url=race_url)
            progress.update(processing_task, description=f"↳ [bold magenta]{year}: [/bold magenta][purple]{padded_race}[/purple][cyan]               Reading HTML...[/cyan]")
            race_html = fm.load_html_file(filepath=path_to_html)

            progress.update(processing_task, description=f"↳ [bold magenta]{year}: [/bold magenta][purple]{padded_race}[/purple][cyan] Extracting circuit details...[/cyan]")
            extract_circuit_name.run(html=race_html, url=race_url)

            progress.update(processing_task, description=f"↳ [bold magenta]{year}: [/bold magenta][purple]{padded_race}[/purple][cyan]        Extracting sessions...[/cyan]")
            extract_sessions.run(html=race_html, url=race_url, year=year)
            progress.advance(processing_task)
        
        progress.update(processing_task, description=f"↳ [bold magenta]{year}: [/bold magenta][green]All race data extracted[/green]")

        progress.advance(extraction_task)      
    progress.update(extraction_task,description=f"[bright_green]Data from races in {start_year} -> {end_year} extracted![/bright_green]")