'''
Not 100% sure yet on how this will work but it will call the relevant results functions
in processing/extraction/extract_results.py
'''
from bs4 import BeautifulSoup
from toolbox import file_management as fm
from toolbox import database_query
from database.management import connection
from interface.progress_manager import get_progress_bar
from pprint import pprint
from config.config import DB_PATH, PROCESSED_DATA_DIR
from rich.progress import Progress
from processing.extraction import extract_results
from processing.cleaning import results_cleaner
from pathlib import Path

""" 

We need to go through each year from start to end,
    Go through each race weekend,
        Go through each session:
            - Collect results -> extract_results.get_race_results()
            - Create filepath and write to CSV?
            - Clean results
            - Write results to database
"""
def _get_session_info(race_id: int) -> list[dict]:
    """Internal function to get session information from the database

    Args:
        race_id (int): _description_

    Returns:
        list[dict]: The session information in the form: 
                    {"session_name": (name of the session)
                     "url": (url of the session results page)
                     "filepath": (filepath to the saved HTML)}
    """    
    sessions = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT session_type, url, filepath
                            FROM scrape_sessions
                           WHERE race_id = ?;
                        """,(race_id,)
                            )
        output = cursor.fetchall()
    
    for row in output:
        sessions.append({
            "session_name":row[0].strip(),
            "url":row[1].strip(),
            "filepath":row[2].strip()
        })
    
    return sessions

def _make_output_path(year: int, race_name: str, session_name: str) -> Path:
    """Internal tool to create output path to CSV results

    Args:
        year (_type_): The year of the F1 season
        race_name (_type_): The name of the race
        session_name (_type_): The name of the session

    Returns:
        Path: The path/to/the/results.csv
    """
    session = "_".join(name for name in session_name.lower().split(" "))
    return PROCESSED_DATA_DIR / str(year) / race_name / f"{session}.csv"

def _update_scrape_sessions_table(url: str) -> None:
    """Updates the 'has_data' column in the 'scrape_sessions' table to signify that data has been collected

    Args:
        url (str): The URL of the session results page
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""UPDATE scrape_sessions
                             SET has_data = 1 
                           WHERE url = ?;
                        """,(url,)
                            )
        output = cursor.fetchall()

def run(start_year: int, end_year: int, progress: Progress) -> None:
    # setup progress bar
    num_seasons = end_year + 1 - start_year
    processing_task = progress.add_task(f"[bold magenta]Current year: {start_year}[/bold magenta]", total=num_seasons)
    tasks = []

    for year in range(start_year, end_year+1):
        progress.update(processing_task, description=f"[bold magenta]Current year: {year}[/bold magenta]")

        # get race_ids
        race_ids = database_query.get_race_ids(year=year, has_sessions=True)
        year_task = progress.add_task(f"└ Getting sessions", total=len(race_ids))
        tasks.append(year_task)

        for race_id in race_ids:
            race_name = database_query.get_race_name(race_id)
            progress.update(year_task, description=f"└ Getting sessions for [b]{race_name}[b]")
            session_data = _get_session_info(race_id=race_id)
            
            for session in session_data:
                progress.update(year_task, description=f"└ Processing results for [b]{race_name}:\n  - [dim]{session["session_name"]}[/dim][b]")
                session_html = fm.load_html_file(filepath=session["filepath"])
                session_results = extract_results.get_results(soup=session_html)
            
                if not race_name or not session_results: # so pylance won't have a fit
                    continue 
                
                output_path = _make_output_path(year, race_name, session["session_name"])
                fm.write_to_csv(data=session_results,
                                csv_path=output_path,
                                headers=fm.get_headers(session_results))
                
                results_cleaner.run(year,
                                    race_id,
                                    session_name=session["session_name"],
                                    results=session_results,
                                    url=session["url"])
                
                _update_scrape_sessions_table(url=session["url"])

            progress.advance(year_task)
        
        if year == end_year:
            pipe = "└"
        else:
            pipe = "├"

        progress.update(year_task, description=f"{pipe} [green][b]{year}:[/b] All session results processed.[/green]")
        progress.advance(processing_task)

    # clean up tasks
    for task_id in tasks:
        progress.remove_task(task_id)

    progress.update(processing_task, description=f"[green]✓ Data from sessions in {start_year} -> {end_year} extracted[/green]")

def test():
    with get_progress_bar() as migration_progress:
        run(2026,2026,migration_progress)

#test()