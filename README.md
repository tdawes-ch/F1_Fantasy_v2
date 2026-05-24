# F1 Fantasy Data Engine (v2)

A Python-based data pipeline for scraping, processing, and analysing Formula 1 race data across multiple seasons, particularly for optimising F1 Fantasy choices.

## Features

- Scrapes race weekend data (practice, qualifying, sprint, race)
- Logs all scraping activity
- Stores structured data in SQLite
- Supports SQL-based analytics
- Generates standings and reports
- Creates a list of the best fantasy teams
- Using practice/no fantasy points sessions, it'll calculate who is most likely to perform the best for the current weekend.  

## Pipeline

1. Scrape each season for race information
2. Scrape each race session for each race (quali, sprint, race, etc.)
3. Convert each page into .csv data
4. Import .csv into SQLite database
5. Perform calculations against database to get results, best fantasy team, etc.

## Setup

```bash
pip install -r requirements.txt