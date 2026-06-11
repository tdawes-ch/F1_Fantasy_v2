"""
get html data for year -> 
extract races for each year -> 
get html data for each session in each weekend (log too) -> 
convert html data into csv -> 
put csv into database -> 
perform calculations for f1 fantasy team.
"""
from toolbox import network
from database import init_db
from database.management import connection as con
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from pipelines import get_all_races, get_race_data, get_all_results

init_db.init_db() # goes in main

base_url = "https://www.formula1.com/en/results/{fyear}/races"
start_year = 2020
end_year = 2026

connection_ok, connection_error = network.test_outbound_connection()

if connection_ok:
    get_all_races.get_all_races(start_year,end_year,base_url)
    get_race_data.get_race_data(start_year,end_year,flag='db')
else:
    print(connection_error)
