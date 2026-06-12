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