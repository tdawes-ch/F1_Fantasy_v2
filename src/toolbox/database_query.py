from config.config import DB_PATH
from database.management import connection
from datetime import datetime

def get_last_scraped(url: str) -> datetime | None:
    """Gets the most recent timestamp for when a specific URL was scraped using the scrape_log table

    Args:
        url (str): The URL to be checked

    Returns:
        datetime | None: The most recent datetime. None if not found
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT last_scraped
                            FROM scrape_log
                           WHERE url = ?
                           ORDER BY id DESC;
                        """,(url,)
                            )
        output = cursor.fetchone()
        if output:
            last_scraped = output[0]
        else:
            last_scraped = None
    return last_scraped

def get_scraped_races(year: int) -> int | None:
    """Gets the number that sits in the scraped_races column for a specific year

    Args:
        year (int): The F1 season year

    Returns:
        int | None: The number that sits in the scraped_races column for that year. "None" if none
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT scraped_races
                            FROM scrape_seasons
                           WHERE year = ?;
                        """,(year,)
                            )
        output = cursor.fetchone()
        if output:
            scraped_races = int(output[0])
        else: 
            scraped_races = None
    return scraped_races

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

def get_race_name(race_id: int) -> str | None:
    """Gets the name of a race from a race ID

    Args:
        race_id (int): The race ID

    Returns:
        str | None: The race name, "None" if not found.
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT race_name
                            FROM scrape_race_weekends
                        WHERE race_id = ?;
                        """,(race_id,)
                            )
        output = cursor.fetchone()
        if output:
            race_name = output[0]
        else:
            race_name = None
    return race_name

def get_session_id(url: str) -> int:
    """Gets the name of a session from a URL

    Args:
        url (str): The URL of the session

    Returns:
        int: The session ID
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT session_id
                            FROM scrape_sessions
                           WHERE url = ?;
                        """,(url,)
                            )
        session_id = int(cursor.fetchone()[0])
    return session_id

def get_n_qualy_sessions(session_id: int) -> int | None:
    """Gets the current number of qualifying rounds for a set session_id

    Args:
        session_id (int): The session ID

    Returns:
        int | None: Number of qualifying rounds, "None" if not found.
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT qualifying_round
                            FROM qualifying_times
                           WHERE session_id = ?
                           ORDER BY qualifying_round DESC;
                        """,(session_id,)
                            )
        output = cursor.fetchone()

        if output:
            qualy_session = int(output[0])
        else:
            qualy_session = None
    return qualy_session

def get_driver_team_name_for_year(driver_id: str, year: int) -> str | None:
    """Gets the constructor name for a specific driver and year combination. 
    May not be accurate for years like 2020 for George Russell. Primarily
    used to fix the weird situation in 2008 PIT STOP SUMMARY for German GP
    as Fernando Alonso doesn't have a team name.

    Args:
        driver_id (str): The driver ID

    Returns:
        int | None: Number of qualifying rounds, "None" if not found.
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT rc.name
                            FROM race_drivers rd
                            LEFT JOIN race_driver_constructor_history rdch ON rd.driver_id = rdch.driver_id
                                LEFT JOIN race_constructors rc ON rdch.constructor_id = rc.constructor_id
                           WHERE rd.driver_id = ?
                             AND rdch.season = ?;
                        """,(driver_id.lower(),
                             year)
                            )
        output = cursor.fetchone()

        if output:
            constructor_name = output[0]
        else:
            constructor_name = None
    return constructor_name

def get_fastest_time(session_id: int) -> float | None:
    """Gets the fastest lap time for a given session

    Args:
        session_id (int): the session ID

    Returns:
        float | None: the lap time
    """    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT lap_time
                            FROM lap_times lt
                            LEFT JOIN race_results rr ON lt.session_id = rr.session_id
                                                     AND lt.driver_id = rr.driver_id
                           WHERE rr.pos = 1
                             AND lt.session_id = ?;
                        """,(session_id,))
        output = cursor.fetchone()
    if output:
        if output[0]:
            lap_time = float(output[0])
        else:
            lap_time = None
    else:
        lap_time = None

    return lap_time