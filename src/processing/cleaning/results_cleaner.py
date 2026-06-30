'''
this takes in a results table (from extract_results) and will do the following:

- Create driver info and populate appropriate tables
- Create constructor information and populate appropriate tables
- Populate results
'''
from pprint import pp
from toolbox import file_management as fm
from toolbox import database_query
from toolbox import processing 
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
        
def _insert_constructor_details(constructor_id: str | None, team: str | None):
    if constructor_id and team:
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
        
def _insert_driver_constructor_link(driver_id: str, constructor_id: str | None, year: int):
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
        
def _validate_team(team_name: str, driver_id: str, year: int):
    if team_name:
        return team_name
    else:
        new_team_name = database_query.get_driver_team_name_for_year(driver_id, year)
        if new_team_name:
            return new_team_name
        else:
            return None

def _driver_processing(results: list[dict], year: int):
    headers = fm.get_headers(results)
    required = {"Driver","Team","No."}

    if not required.issubset(set(headers)): # checks if there are the appropriate driver headers
        raise ValueError(f"Expected driver detail headings not found ({required})")

    for result in results:
        driver, team, number = result["Driver"], result["Team"], result["No."]
        if len(driver) != 3:
            raise ValueError(f"Expected three items under driver (fname, lname, code), got {len(driver)}: {driver}")
        driver_id = processing.create_driver_id(fname=driver[0], lname=driver[1])
        validated_team_name = _validate_team(team_name=team, driver_id=driver_id, year=year)
        if validated_team_name:
            constructor_id = "_".join(name for name in validated_team_name.lower().split(" "))
        else:
            constructor_id = None
        # driver db additions
        _insert_driver_details(driver_id, fname=driver[0], lname=driver[1])
        _insert_driver_number(driver_id, number, year)
        _insert_driver_code(driver_id, driver_code=driver[2], year=year)
    
        # constructor db additions
        _insert_constructor_details(constructor_id, validated_team_name)
        _insert_driver_constructor_link(driver_id, constructor_id, year)

def _add_qualy_time_to_db(session_id: int, qualy_round: int, driver_id: str, time: str) -> None:
    # get time value. Either null (dnf, dns), or actual time value
    if time[0].isalpha():
        time_value = None
    else:
        time_value = processing.time_to_seconds(time)

    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO qualifying_times (session_id,
                                                      driver_id,
                                                      qualifying_round,
                                                      lap_time)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT (session_id, driver_id, qualifying_round) 
                        DO UPDATE SET 
                        lap_time = excluded.lap_time;
                        """,
                        (session_id,
                         driver_id,
                         qualy_round,
                         time_value
                         )
                        )

def _insert_qualy_time(driver_id: str, session_id: int, result: dict) -> None:
    # get potential time key for dict. If not, it's probably q1,q2,q3 format instead of having separate sessions
    time_key = _get_time_key(result)
    if time_key:
        time_value = result[time_key]
        if time_value.strip() != "":
            # get current round of qualifying
            #qualy_round = database_query.get_n_qualy_sessions(session_id)
            #if qualy_round:
            #    qualy_round += 1
            #else:
            qualy_round = 1
            _add_qualy_time_to_db(session_id, qualy_round, driver_id, time_value)
    else: # q1, q2, q3
        for key in result:
            if key.lower().startswith("q"):
                qualy_round = int(key[1:])
                time_value = result[key]
                if time_value.strip() != "":
                    _add_qualy_time_to_db(session_id, qualy_round, driver_id, time_value)

def _qualy_processing(results: list[dict], session_id: int):
    for qualy_result in results:
        driver_id = processing.create_driver_id(fname=qualy_result["Driver"][0], lname=qualy_result["Driver"][1])
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            # insert into results table
            cursor.execute("""
                           INSERT INTO race_results (session_id,
                                                     driver_id,
                                                     pos)
                           VALUES (?, ?, ?)
                           ON CONFLICT (session_id, driver_id)
                           DO UPDATE SET 
                              pos = excluded.pos,
                              status = excluded.status;
                           """,
                           (session_id,
                            driver_id,
                            qualy_result["Pos."]                            
                           )
                          )
        _insert_qualy_time(driver_id, session_id, qualy_result)

def _get_time_key(data: list[dict] | dict) -> str | None:
    """Internal function to determine what the appropriate dictionary key is to get the time values. Sometimes it's just "Time", sometimes it's "Time / Retired", etc.

    Args:
        data (list[dict] | dict): The data to check. Either a list of dictionaries or just a dictionary

    Returns:
        str | None: Eiter the key name or, if there isn't a key, nothing (None)
    """
    # Get keys from the first dictionary in the list
    if isinstance(data, list):
        if not data:  # Handle empty list
            return None
        target_dict = data[0]
    else:
        target_dict = data
    
    # Find the first key that contains "time" (case-insensitive)
    for key in target_dict.keys():
        if "time" in key.lower():
            if "day" in key.lower(): ## gets rid of it accidentally setting "Time of Day" as the key!!
                continue
            else:
                return key
    return None

def _get_lap_key(data: list[dict] | dict) -> str | None:
    """Internal function to determine what the appropriate dictionary key is to get the lap values. Sometimes it's just "Laps", but better to be safe

    Args:
        data (list[dict] | dict): The data to check. Either a list of dictionaries or just a dictionary

    Returns:
        str | None: Eiter the key name or, if there isn't a key, nothing (None)
    """
    # Get keys from the first dictionary in the list
    if isinstance(data, list):
        if not data:  # Handle empty list
            return None
        target_dict = data[0]
    else:
        target_dict = data
    
    # Find the first key that contains "time" (case-insensitive)
    for key in target_dict.keys():
        if "lap" in key.lower():
            return key
    return None

def _convert_time_result(data: str) -> tuple[float | None, str]:
    if not data:
        time_value = None
        time_type = "STATUS"
    elif data[0].isalpha():
        time_value = None
        time_type = "STATUS"
    elif data[0] == "+" and len(data.split(" ")) == 2:
        time_value = float(data.replace("+","").split(" ")[0]) # +2 Laps -> 2
        time_type = "LAPPED"
    elif data[0] == "+" and len(data.split(" ")) == 1:
        time_value = float(data.replace("+","").replace("s","")) # +1.123s -> 1.123
        time_type = "GAP"
    elif data.find(":"):
        time_value = processing.time_to_seconds(time_str=data) # 1:32.741 -> 92.741
        time_type = "TOTAL"
    elif data.find(".") and data[0] != "+": # 31.410 -> 31.410 but float
        time_value = float(data)
        time_type = "TOTAL"
    else:
        time_value = None
        time_type = "STATUS"
    return time_value, time_type

def _add_lap_result(session_id: int,
                    driver_id: str,
                    position: str,
                    time_data: str | None,
                    is_total: int,
                    lap_info: str | None) -> None:
    # insert into results table
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO race_results (session_id,
                                                  driver_id,
                                                  pos)
                        VALUES (?, ?, ?)
                        ON CONFLICT (session_id, driver_id)
                        DO UPDATE SET pos = excluded.pos;
                        """,
                        (session_id,
                         driver_id,
                         position)
                       )
    # insert into lap_times table
    # get time data
    if time_data:
        time_value, time_type = _convert_time_result(time_data)
    else:
        time_value, time_type = None, "STATUS"

    if time_type == "TOTAL":
        # just add converted time
        lap_time = time_value
    elif time_type == "GAP":
        # calculate full time from total + gap
        total_time = database_query.get_fastest_time(session_id)
        if total_time and time_value:
            lap_time = round(total_time + time_value,3)
        else: # how do i handle no lap time?
            lap_time = None
    else:
        lap_time = None
    
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO lap_times (session_id,
                                               driver_id,
                                               is_total,
                                               lap_number,
                                               lap_time)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT (session_id, driver_id, lap_number)
                        DO UPDATE SET 
                        lap_number = excluded.lap_number,
                        lap_time = excluded.lap_time;
                        """,
                        (session_id,
                         driver_id,
                         is_total,
                         lap_info,
                         lap_time)
                       )

def _pit_stop_processing(results: list[dict], session_id: int):
    lap_key = _get_lap_key(results)
    time_key = _get_time_key(results)
    for pit_stop in results:
        driver_id = processing.create_driver_id(fname=pit_stop["Driver"][0], lname=pit_stop["Driver"][1])
        duration, status = _convert_time_result(pit_stop[time_key])
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute("""
                            INSERT INTO pit_stops (session_id, driver_id, stop_number, lap_number, duration)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT (session_id, driver_id, stop_number)
                            DO UPDATE SET
                            lap_number = excluded.lap_number,
                            duration = excluded.duration;
                           """,
                           (session_id,
                            driver_id,
                            pit_stop["Stops"],
                            pit_stop[lap_key],
                            duration))

def _race_results_processing(results: list[dict], session_id: int):
    time_key = _get_time_key(results)
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        for race_result in results:
            driver_id = processing.create_driver_id(fname=race_result["Driver"][0], lname=race_result["Driver"][1])

            if race_result[time_key][0].isalpha(): # If time is DNF, DNS, etc.
                status = race_result[time_key]
                time_result = None, "STATUS"
            else:
                status = None
                time_result = _convert_time_result(race_result[time_key])

            cursor.execute("""
                           INSERT INTO race_results (session_id,
                                                     driver_id,
                                                     pos,
                                                     points,
                                                     status)
                           VALUES (?, ?, ?, ?, ?)
                           ON CONFLICT (session_id, driver_id)
                           DO UPDATE SET 
                              pos = excluded.pos,
                              points = excluded.points,
                              status = excluded.status;
                           """,
                           (session_id,
                            driver_id,
                            race_result["Pos."],
                            race_result["Pts."],
                            status                             
                           )
                          )
            
            cursor.execute("""
                           INSERT INTO race_duration (session_id,
                                                      driver_id,
                                                      time_type,
                                                      duration,
                                                      n_laps)
                           VALUES (?, ?, ?, ?, ?)
                           ON CONFLICT (session_id, driver_id)
                           DO UPDATE SET 
                              time_type = excluded.time_type,
                              duration = excluded.duration,
                              n_laps = excluded.n_laps;
                           """,
                           (session_id,
                            driver_id,
                            time_result[1],
                            time_result[0],
                            race_result["Laps"]                   
                           )
                          )

def _lap_session_processing(results: list[dict], session_id: int):
    time_key = _get_time_key(results)
    lap_key = _get_lap_key(results)
    for lap_detail in results:
        driver_id = processing.create_driver_id(fname=lap_detail["Driver"][0], lname=lap_detail["Driver"][1])
        if lap_key and time_key:
            lap_info = lap_detail[lap_key]
            time_info = lap_detail[time_key]
        else:
            lap_info = None
            time_info = None
        # add positional result and lap time
        _add_lap_result(session_id=session_id,
                        driver_id=driver_id,
                        position=lap_detail["Pos."],
                        time_data=time_info,
                        is_total=0,
                        lap_info=lap_info)

########################## SWITCHBOARD ##########################
########################## V IMPORTANT ##########################

def _results_switchboard(year: int, 
                         race_id: int, 
                         session_name: str, 
                         results: list[dict], 
                         url: str):
    headers = fm.get_headers(results)
    session_id = database_query.get_session_id(url)
    #print(session_name)
    #pp(headers)

    if "pit" in session_name.lower(): # pit stop summary!
        required = {"Driver", "Team", "Time"}
        if not required.issubset(set(headers)): # checks if there are the appropriate driver headers
            raise ValueError(f"Expected driver detail headings not found ({required})")
        _pit_stop_processing(results, session_id)
    else: # practice, warmup, qualifying, race results, fastest lap, sprint, etc.
        ## Define headers needed
        required = {"Driver", "Team", "Pos."}
        if not required.issubset(set(headers)): # checks if there are the appropriate driver headers
            raise ValueError(f"Expected driver detail headings not found ({required})")
        
        ## headers are there, can then check session deets
        if "qualifying" in session_name.lower(): # qualifying / sprint qualifying
            _qualy_processing(results, session_id)
        elif "race" in session_name.lower() or session_name.lower() == "sprint": # race or sprint race (must be == "sprint" to not catch sprint qualy)
            _race_results_processing(results, session_id)
        elif "warm" in session_name.lower(): # weird warmup sessions before practice was a thing
            _lap_session_processing(results, session_id)
        elif "fastest" in session_name.lower() or "practice" in session_name.lower(): # fastest laps
            _lap_session_processing(results, session_id)
        else: # a session that just has driver and position e.g. starting grid
            pass

def run(year: int, 
        race_id: int, 
        session_name: str, 
        results: list[dict], 
        url: str): 
    #pp(results)
    _driver_processing(results,year)
    _results_switchboard(year, race_id, session_name, results, url)