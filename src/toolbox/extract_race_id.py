from pathlib import PurePosixPath
from urllib.parse import urlparse
from database.management import connection
from config.config import DB_PATH

""" 
this gets the race id from the url e.g.:
- https://www.formula1.com/en/results/2026/races/1279/australia/race-result
becomes
- 1279

"""

def from_url(url: str) -> int | None:
    """Takes in a URL and returns the race ID from the URL e.g.:
    - Input: https://www.formula1.com/en/results/2026/races/1279/australia/practice/1
    - Output: Race ID: 1279

    Args:
        url (str): The URL to be processed

    Returns:
        int | None: The race ID value
    """
    path = PurePosixPath(urlparse(url).path)
    try:
        races_index = path.parts.index('races')
        race_id = path.parts[races_index + 1]
        return int(race_id)
    except ValueError:
        print("'races' not found in URL structure")
        race_id = None # None is essentially NULL
        return race_id
    
def from_db(data: str | list[int], flag:str) -> int:
    """Finds the race ID from the database from either a URL or a combination of round and year.

    Args:
        data (str | list[int]): The data to be processed. Depends on the flag
        flag (str): The method to get the race ID (from url or year & round)
            e.g.: "year,round"
                  "url"

    Raises:
        ValueError: Incorrect flag
        ValueError: Incorrect list passed for round,year
        ValueError: Unknown error for data and flag

    Returns:
        int: the race ID
    """    
    valid_flag = ("year,round", "url")
    flag = flag.lower().strip()

    if flag not in valid_flag:
        raise ValueError(f"Incorrect flag passed into extract_race_id.from_db(): {flag}")
    elif flag == valid_flag[0] and isinstance(data, list): ## year,round
        if len(data) != 2:
            raise ValueError(f"Incorrect list passed for round,year extract_race_id.from_db(): {data}. Expected [int,int]")
        else:
            with connection.get_db(DB_PATH) as conn:  # type: ignore
                cursor = conn.cursor()
                cursor.execute("""SELECT race_id
                                    FROM scrape_race_weekends
                                WHERE year = ? 
                                  AND round = ?;
                                """,(data[0], data[1])
                                    )
                race_id = cursor.fetchone()
            return int(race_id[0])
    elif flag == "url":
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute("""SELECT race_id
                                FROM scrape_race_weekends
                            WHERE url = ? ;
                            """,(data, )
                                )
            race_id = cursor.fetchone()
        return int(race_id[0])
    else:
        raise ValueError("Unknown error occurred in extract_race_id.from_db() for values:/n - data: {data} /n - flag: {flag}")