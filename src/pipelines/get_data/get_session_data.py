from scraping import session_scraper
from database.management import connection
from pathlib import Path
from rich.progress import Progress
from config.config import DB_PATH

"""
MAIN GOAL IS TO SCRAPE ALL SESSION HTML PAGES

We want to take in a start year and end year and loop through the following:

For each year,
    get a list of race_ids
    loop through each race_id,
        get all session urls where they aren't race results (already scraped)
            NOTE: CAN CHECK IF THE FILEPATH EXISTS IN OTHER VERSIONS
        send urls to download_sessions
"""

def _get_race_ids(year:int) -> list[tuple[int, str]]:
    results = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT race_id, race_name
              FROM scrape_race_weekends
             WHERE year = ? ;
            """,
            (year,)
        )
        output = cursor.fetchall()
    
    for row in output:
        race_id = int(row[0])
        race_name = row[1]
        results.append((race_id, race_name))

    return results


def _get_session_urls(race_id: int) -> list[str]:
    urls = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT url, session_type
              FROM scrape_sessions
             WHERE race_id = ? 
               AND session_type <> 'Race Results';
            """,
            (race_id,)
        )
        output = cursor.fetchall()

    for row in output:
        url = row[0]
        urls.append(url)

    return urls


def run(start_year:int, end_year:int, progress: Progress):
    # setup progress bar
    num_seasons = end_year + 1 - start_year
    year_task = progress.add_task(f"[bold magenta]Current year: {start_year}[/bold magenta]", total=num_seasons)
    tasks = []

    for year in range(start_year, end_year+1):
        progress.update(year_task, description=f"[bold magenta]Current year: {year}[/bold magenta]")
        race_info = _get_race_ids(year)

        race_task = progress.add_task(f"└ Getting sessions", total=len(race_info))
        tasks.append(race_task)
        
        for race_id, race_name in race_info:
            session_urls = _get_session_urls(race_id)
            progress.update(race_task, description=f"└ Getting sessions for [b]{race_name}[b]")
            
            session_scraper.download_sessions(urls=session_urls, year=year, race_id=race_id, progress=progress)
            progress.advance(race_task)

        if year == end_year:
            pipe = "└"
        else:
            pipe = "├"

        progress.update(race_task, description=f"{pipe} [green][b]{year}:[/b] All sessions collected.[/green]")
        progress.advance(year_task)
    
    progress.update(year_task,description=f"[green]Data from sessions in {start_year} -> {end_year} extracted[/green]")
    for task_id in tasks:
        ## cleans up progress bars
        progress.remove_task(task_id)