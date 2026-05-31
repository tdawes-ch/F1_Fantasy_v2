'''
gets the important data from the season html pages
outputs csv.

e.g.:
https://www.formula1.com/en/results/2026/races

this will get:
race_url, race_id, grand prix, date, laps, time (any other info?)

JUST TAKES IN ONE .HTML FILE, ONE OUTPUT CSV. THIS WILL BE LOOPED BY ANOTHER PROGRAM

and write to .csv with the above headers
Outputs csv into:
data/sessions/processed/<year>/<year>.csv
'''
from config.config import PROCESSED_DATA_DIR

