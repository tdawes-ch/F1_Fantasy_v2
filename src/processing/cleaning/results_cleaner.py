'''
this takes in a results table (from extract_results) and will do the following:

- Create driver info and populate appropriate tables
- Create constructor information and populate appropriate tables
- Populate results
'''
from pprint import pp
from toolbox import file_management as fm
from config.config import DB_PATH
from database.management import connection

def _insert_driver_details(driver_id: str, fname: str, lname: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_drivers (driver_id,
                                                  forename,
                                                  surname
                                                 )
                        VALUES (?, ?, ?)
                        ON CONFLICT (driver_id) DO NOTHING;
                        """,
                        (driver_id,
                         fname,
                         lname
                         )
                        )

def _insert_driver_number(driver_id: str, driver_number: int, year: int):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_driver_number_history (driver_id,
                                                                number,
                                                                season
                                                                )
                        VALUES (?, ?, ?)
                        ON CONFLICT (driver_id, season) DO NOTHING;
                        """,
                        (driver_id,
                         driver_number,
                         year
                         )
                        )

def _insert_driver_code(driver_id: str, driver_code: int, year: int):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_driver_code_history (driver_id,
                                                              code,
                                                              season
                                                             )
                        VALUES (?, ?, ?)
                        ON CONFLICT (driver_id, season) DO NOTHING;
                        """,
                        (driver_id,
                         driver_code,
                         year
                         )
                        )
        
def _insert_constructor_details(constructor_id: str, team: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_constructors (constructor_id,
                                                       name
                                                      )
                        VALUES (?, ?)
                        ON CONFLICT (constructor_id) DO NOTHING;
                        """,
                        (constructor_id,
                         team
                         )
                        )
        
def _insert_driver_constructor_link(driver_id: str, constructor_id: str, year: int):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_driver_constructor_history (driver_id,
                                                                     constructor_id,
                                                                     season
                                                                    )
                        VALUES (?, ?, ?)
                        ON CONFLICT (driver_id, constructor_id, season) DO NOTHING;
                        """,
                        (driver_id,
                         constructor_id,
                         year
                         )
                        )

def _driver_processing(results: list[dict], year: int):
    headers = fm.get_headers(results)
    required = {"Driver","Team","No."}

    if not required.issubset(set(headers)): # checks if there are the appropriate driver headers
        raise ValueError(f"Expected driver detail headings not found ({required})")

    for result in results:
        driver, team, number = result["Driver"], result["Team"], result["No."]
        if len(driver) != 3:
            raise ValueError(f"Expected three items under driver (fname, lname, code), got {len(driver)}: {driver}")
        driver_id = f"{driver[0]}_{driver[1]}".lower()
        # driver db additions
        _insert_driver_details(driver_id, fname=driver[0], lname=driver[1])
        _insert_driver_number(driver_id, number, year)
        _insert_driver_code(driver_id, driver_code=driver[2], year=year)
        constructor_id = "_".join(name for name in team.lower().split(" "))
        # constructor db additions
        _insert_constructor_details(constructor_id, team)
        _insert_driver_constructor_link(driver_id, constructor_id, year)

def _results_processing(year: int, 
                        race_id: int, 
                        session_name: str, 
                        results: list[dict], 
                        url: str):
    print(results)

def run(year: int, 
        race_id: int, 
        session_name: str, 
        results: list[dict], 
        url: str): 
    #pp(results)
    _driver_processing(results,year)
    _results_processing(year, race_id, session_name, results, url)
