'''
Stuck on the pipeline for this a bit :/
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
    for url in urls[]:
        output_path = x
        scrape
        extract_circuit_name
        extract_sessions

And then we can go through each session. Similar format to this 
'''

def _get_urls_from_csv ():
    pass

def _get_urls_from_db():
    pass

def get_race_data(flag: str='db'):
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
    pass