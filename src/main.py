"""
get html data for year -> 
extract races for each year -> 
get html data for each session in each weekend (log too) -> 
convert html data into csv -> 
put csv into database -> 
perform calculations for f1 fantasy team.
"""

from config.config import RAW_DATA_DIR
import datetime
from logging_utils import logger

print(RAW_DATA_DIR)

print(datetime.datetime.now().strftime("%Y")) # https://www.w3schools.com/python/python_datetime.asp

logger.runtime()

