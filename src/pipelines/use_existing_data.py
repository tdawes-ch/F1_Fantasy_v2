"""This is the file to manage the use of existing data. It will:
1. Generate a summary of existing data in the database,
2. Cross check scraped data tables and `race` tables to see if there is any potential data missing.
3. Check current logged filepaths. See if they can be used to enrich missing data
4. Check unlogged filepaths and add them to the scrape_log table in database (use file creation date)
    a. essentially run processing again against all of these
5. See if unlogged filepaths can be used to enrich data
"""