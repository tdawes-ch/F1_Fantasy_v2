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

def get_race_ids(year: int, has_sessions: bool = False) -> list[int]:
    """Gets a list of race IDs for a given year.

    Args:
        year (int): Year of F1 season
        has_sessions (bool, optional): Used to choose whether to get race IDs only for weekends that have sessions or not. Defaults to False.

    Returns:
        list[int]: List of race IDs stored as integers
    """    
    race_ids = []
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        if has_sessions:
            cursor.execute("""
                           SELECT race_id
                             FROM scrape_race_weekends
                            WHERE year = ?
                              AND has_sessions = ?;
                            """,(year,int(has_sessions))
                                )
        else:
            cursor.execute("""
                           SELECT race_id
                             FROM scrape_race_weekends
                            WHERE year = ?;
                            """,(year,)
                                )
        output = cursor.fetchall()
    for row in output:
        race_ids.append(row[0])
    return race_ids

def get_race_name(race_id: int) -> str:
    """Gets the name of a race from a race ID

    Args:
        race_id (int): The race ID

    Returns:
        str: The race name
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT race_name
                            FROM scrape_race_weekends
                        WHERE race_id = ?;
                        """,(race_id,)
                            )
        race_name = cursor.fetchone()[0]
    return race_name
