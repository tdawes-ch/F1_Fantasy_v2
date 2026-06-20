from config.config import DB_PATH
from database.management import connection
from datetime import datetime

def get_last_scraped(url: str) -> datetime:
    """Gets the most recent timestamp for when a specific URL was scraped using the scrape_log table

    Args:
        url (str): The URL to be checked

    Returns:
        datetime: The most recent datetime 
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT last_scraped
                            FROM scrape_log
                           WHERE url = ?
                           ORDER BY id DESC;
                        """,(url,)
                            )
        last_scraped = cursor.fetchone()
    return last_scraped[0]

def get_scraped_races(year: int) -> int:
    """Gets the number that sits in the scraped_races column for a specific year

    Args:
        year (int): The F1 season year

    Returns:
        int: The number that sits in the scraped_races column for that year
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT scraped_races
                            FROM scrape_seasons
                           WHERE year = ?;
                        """,(year,)
                            )
        scraped_races = cursor.fetchone()
    return int(scraped_races[0])