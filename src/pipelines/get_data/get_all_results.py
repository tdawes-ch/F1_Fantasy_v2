'''
Not 100% sure yet on how this will work but it will call the relevant results functions
in processing/extraction/extract_results.py
'''
from bs4 import BeautifulSoup
from toolbox import file_management as fm
from toolbox import database_query
from database.management import connection
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
            "session_type":row[0].strip(),
            "url":row[1].strip(),
            "filepath":row[2].strip()
        })
    
    return sessions

def _make_output_path(year, race_name, session_type) -> Path:
    session = "_".join(session_name for session_name in session_type.lower().split(" "))
    return PROCESSED_DATA_DIR / str(year) / race_name / f"{session}.csv"

def run(start_year: int, end_year: int):
    # setup progress bar
    num_seasons = end_year + 1 - start_year
    #year_task = progress.add_task(f"[bold magenta]{start_year}:[/bold magenta]", total=num_seasons)

    for year in range(start_year, end_year+1):
        # get race_ids
        race_ids = database_query.get_race_ids(year=year, has_sessions=True)
        for race_id in race_ids:
            session_data = _get_session_info(race_id=race_id)
            for session in session_data:
                session_html = fm.load_html_file(filepath=session["filepath"])
                session_results = extract_results.get_results(soup=session_html)
                race_name = database_query.get_race_name(race_id)
                output_path = _make_output_path(year, race_name, session["session_type"])
                fm.write_to_csv(data=session_results,
                                csv_path=output_path,
                                headers=fm.get_headers(session_results))
                results_cleaner.run(session_results)
                
def test():
    run(2026,2026)

test()