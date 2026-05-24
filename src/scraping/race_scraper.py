"""
finds each race from the output csvs of season_cleaner.py

Goes through each .csv in year folder in: (is this optimal?)
data/sessions/raw/<year>
e.g.:
data/sessions/raw/2025/2025.csv
data/sessions/raw/2026/2026.csv

These are in the format:
race_url, race_id, grand prix, date, laps, time

We will go to the first race in the list. 
We can get the list of all races.
This will get added to logs (data/logs/seasons.csv)

We will then get a list of all sessions for the weekend.

We will scrape each race_url and go to /race-result
e.g.:
https://www.formula1.com/en/results/2026/races/1287/barcelona-catalunya/race-result

"""