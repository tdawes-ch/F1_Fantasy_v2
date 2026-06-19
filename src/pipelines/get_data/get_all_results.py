'''
Not 100% sure yet on how this will work but it will call the relevant results functions
in processing/extraction/extract_results.py
'''
from bs4 import BeautifulSoup
from toolbox import file_management as fm
from database.management import connection
from pprint import pprint
from config.config import DB_PATH
from rich.progress import Progress
from processing.extraction import extract_results

""" 

We need to go through each year from start to end,
    Go through each race weekend,
        Go through each session:
            - Collect results -> extract_results.get_race_results()
            - Create filepath and write to CSV?
            - Clean results
            - Write results to database
"""

def run(start_year: int, end_year: int, progress: Progress):
    # setup progress bar
    num_seasons = end_year + 1 - start_year
    year_task = progress.add_task(f"[bold magenta]{start_year}:[/bold magenta]", total=num_seasons)

    for year in range(start_year, end_year+1):
        # get race_ids
        for race_id in race_ids:
            
        pass
    pass