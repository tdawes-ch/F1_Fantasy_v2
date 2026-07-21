from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from config.config import DB_PATH, FANTASY_PROCESSED_DIR
from database.management import connection
from datetime import datetime
from toolbox import processing
from pathlib import Path
import json
from toolbox import file_management as fm
from pprint import pprint

def _extract_prices(json_data: dict, year: int, round: int) -> list:
    """Extracts just the price information from the raw database tables (`fantasy_raw_driver_data`, `fantasy_raw_constructor_data`)
    and returns the price information in the format:
    [ID type (`driver_id`/`constructor_id`), actual ID value (e.g. `lewis_hamilton`), price value]

    Args:
        json_data (dict): Raw JSON data
        year (int): _description_
        round (int): _description_

    Raises:
        ValueError: _description_

    Returns:
        list: _description_
    """    
    price_info = []
    for data in json_data["Data"]["Value"]:
        match data["PositionName"]:
            case "DRIVER":
                table_name = "fantasy_raw_driver_data"
                id = [processing.create_driver_id(fname=data["FirstName"], lname=data["LastName"]), "driver_id"]
            case "CONSTRUCTOR":
                table_name = "fantasy_raw_constructor_data"
                id = [processing.create_constructor_id(constructor_name=data["DisplayName"]), "constructor_id"]
            case _:
                raise ValueError(f"Unknown value for 'PositionName': {data['PositionName']}")
        
        query = f"""SELECT {id[1]}, value FROM {table_name} WHERE {id[1]} = "{id[0]}" AND year = {year} AND round = {round};"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query)
            output = cursor.fetchone()
        
        if output:
            price_info.append([id[1], output[0], float(output[1])])

    return price_info

def _add_fantasy_data_to_db(json_data: dict, year: int, round: int):
    """Internal function to add raw fantasy data to the database. For each JSON field, there is a matching column.

    Args:
        json_data (dict): The raw JSON data
        year (int): The year
        round (int): The round

    Raises:
        ValueError: Unknown value for `'PositionName'` in the JSON data
    """    
    for data in json_data["Data"]["Value"]:
        match data["PositionName"]:
            case "DRIVER":
                table_name = "fantasy_raw_driver_data"
                id = [processing.create_driver_id(fname=data["FirstName"],lname=data["LastName"]), 
                      "driver_id"]
                query = f"""INSERT INTO {table_name} (driver_id, year, round)
                            VALUES ("{id[0]}", {year}, {round}) 
                            ON CONFLICT (driver_id, year, round) DO NOTHING;"""
            case "CONSTRUCTOR":
                table_name = "fantasy_raw_constructor_data"
                id = [processing.create_constructor_id(constructor_name=data["DisplayName"]), "constructor_id"]
                query = f"""INSERT INTO {table_name} (constructor_id, year, round)
                            VALUES ("{id[0]}", {year}, {round}) 
                            ON CONFLICT (constructor_id, year, round) DO NOTHING;"""
            case _:
                raise ValueError(f"Unknown value for 'PositionName': {data["PositionName"]}")
        # add driver id and date
        with connection.get_db(DB_PATH) as conn: # type: ignore
            cursor = conn.cursor()
            cursor.execute(query)

        for value in data:
            if "ppints" in value.lower(): # stupid spelling mistakes in the f1 data
                columnname = value.lower().replace("ppints","points")
            elif "higest" in value.lower():
                columnname = value.lower().replace("higest","highest")
            else:
                columnname = value.lower()
            
            query = f"""UPDATE {table_name} 
                        SET {columnname} = {"NULL" if isinstance(data[value],str) and data[value] == ""
                                            else (f'"{data[value]}"' if isinstance(data[value], (str, dict, list)) 
                                                  else data[value])} 
                        WHERE {id[1]} = "{id[0]}"
                        AND year = {year}
                        AND round = {round};"""
            with connection.get_db(DB_PATH) as conn:  # type: ignore
                cursor = conn.cursor()
                cursor.execute(query)

def _add_price_data(price_data: list, year: int, round: int):
    """Internal function to add price data to the database. Adds to either `fantasy_driver_prices` or `fantasy_constructor_prices` table.

    Args:
        price_data (list): The list of price data, in the format: [ID type (`driver_id`/`constructor_id`), actual ID value (e.g. lewis_hamilton), price value]
        year (int): The year
        round (int): The round

    Raises:
        ValueError: An incorrect ID type has been entered (neither `driver_id` or `constructor_id`)
    """    
    for data in price_data:
        match data[0]:
            case "driver_id":
                table_name = "fantasy_driver_prices"
            case "constructor_id":
                table_name = "fantasy_constructor_prices"
            case _:
                raise ValueError(f"Incorrect ID type: {data[0]}")
        query = f"""INSERT INTO {table_name} ({data[0]}, price, year, round) 
                    VALUES (?, ?, ?, ?) 
                    ON CONFLICT({data[0]}, year, round) 
                    DO UPDATE SET
                    price = excluded.price;"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query, 
                           (data[1], 
                            int(data[2] * 1_000_000), 
                            year, 
                            round)
                            )

def _create_csv_path(year: int, round: int, driver_or_constructor: str) -> Path:
    """Internal function to generate a CSV output path in the form:
    - `FANTASY_PROCESSED_DIR` / `year` / `round` / `identifier`.csv
    - `FANTASY_PROCESSED_DIR` / 2026 / 2 / drivers.csv
    - `FANTASY_PROCESSED_DIR` / 2026 / 2 / constructors.csv

    Args:
        year (int): The year
        round (int): The round
        driver_or_constructor (str): A flag to show either a driver, or a constructor. Options are: ["d", "driver", "c", "constructor"]

    Raises:
        ValueError: Invalid value for `driver_or_constructor`

    Returns:
        Path: The output CSV path, including filename
    """
    match driver_or_constructor:
        case "d" | "driver":
            identifier = "drivers"
        case "c" | "constructor":
            identifier = "constructors"
        case _:
            raise ValueError(f"Incorrect value for 'driver_or_constructor'. Expected 'd', 'c', 'driver', or 'constructor'. Got: '{driver_or_constructor}'")
    return FANTASY_PROCESSED_DIR / str(year) / str(round) / f"{identifier}.csv"

def _write_price_data_to_csv(price_data: list, year: int, round: int):
    """From a list of price data, we write the ID (`constructor_id`/`driver_id`) and price to a CSV file.

    Args:
        price_data (list): The price information.
        year (int): The year
        round (int): The round

    Raises:
        ValueError: ID format is incorrect (isn't `driver_id` or `constructor_id`)
    """
    if price_data:
        if price_data[0][0] in ["driver_id", "constructor_id"]:
            pass
        else:
            raise ValueError(f"Incorrect format for price_data. Expected either 'driver_id' or 'constructor_id', got {price_data[0]}")
    
    driver_prices, constructor_prices = [], []
    for data in price_data:
        match data[0]:
            case "driver_id":
                driver_prices.append({"driver_id": data[1],
                                     "price": float(data[2]) * 1_000_000})
            case "constructor_id":
                constructor_prices.append({"construcor_id": data[1],
                                          "price": float(data[2]) * 1_000_000})
    
    driver_csv_path, constructor_csv_path = _create_csv_path(year, round, "driver"), _create_csv_path(year, round, "constructor")
    fm.write_to_csv(data=driver_prices, 
                    csv_path=driver_csv_path,
                    headers=fm.get_headers(driver_prices))
    fm.write_to_csv(data=constructor_prices, 
                    csv_path=constructor_csv_path,
                    headers=fm.get_headers(constructor_prices))

def run(json_data: dict, year: int, round: int) -> bool:
    """Runs the full pipeline for extracting information from the JSON data to writing to both a CSV and the database.

    Args:
        json_data (dict): The raw JSON data
        year (int): The year
        round (int): The round

    Returns:
        bool: True if successful, False if not.
    """
    try:
        _add_fantasy_data_to_db(json_data, year, round)
        price_data = _extract_prices(json_data, year, round)
        _add_price_data(price_data, year, round)
        _write_price_data_to_csv(price_data, year, round)
        return True
    except:
        return False

def test(url: str):
    response = requests.get(url)
    json_data = response.json()
    year = 2026
    round = 5
    _add_fantasy_data_to_db(json_data, year, round)
    price_data = _extract_prices(json_data, year, round)
    _add_price_data(price_data, year, round)

def test_local(json_path: str, year: int, round: int):
    with open(file=json_path,mode="r",encoding="utf-8") as json_data:
        loaded_json = json.load(json_data)
    price_data = _extract_prices(loaded_json, year, round)
    _write_price_data_to_csv(price_data, year, round)
    
#test_local(json_path="data/fantasy/raw/2026/07-05.json", date="2026-07-05")
#test(r"https://fantasy.formula1.com/feeds/drivers/9_en.json")
#run_update(1950,2026)