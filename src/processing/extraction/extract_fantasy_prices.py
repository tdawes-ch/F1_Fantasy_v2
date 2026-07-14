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

def _extract_prices(json_data: dict, date: str) -> list:
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
        
        query = f"""SELECT {id[1]}, value FROM {table_name} WHERE {id[1]} = "{id[0]}" AND date = "{date}";"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query)
            output = cursor.fetchone()
        
        if output:
            price_info.append([id[1], output[0], float(output[1])])

    return price_info

def _add_fantasy_data_to_db(json_data: dict, date: str):
    for data in json_data["Data"]["Value"]:
        match data["PositionName"]:
            case "DRIVER":
                table_name = "fantasy_raw_driver_data"
                id = [processing.create_driver_id(fname=data["FirstName"],lname=data["LastName"]), "driver_id"]
                query = f"""INSERT INTO {table_name} (driver_id, date)
                            VALUES ("{id[0]}","{date}") 
                            ON CONFLICT (driver_id, date) DO NOTHING;"""
            case "CONSTRUCTOR":
                table_name = "fantasy_raw_constructor_data"
                id = [processing.create_constructor_id(constructor_name=data["DisplayName"]), "constructor_id"]
                query = f"""INSERT INTO {table_name} (constructor_id, date)
                            VALUES ("{id[0]}","{date}") 
                            ON CONFLICT (constructor_id, date) DO NOTHING;"""
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
                        AND date = "{date}";"""
            with connection.get_db(DB_PATH) as conn:  # type: ignore
                cursor = conn.cursor()
                cursor.execute(query)

def _add_price_data(price_data: list, date: str):
    for data in price_data:
        match data[0]:
            case "driver_id":
                table_name = "fantasy_driver_prices"
            case "constructor_id":
                table_name = "fantasy_constructor_prices"
            case _:
                raise ValueError(f"Incorrect table name: {data[0]}")
        query = f"""INSERT INTO {table_name} ({data[0]} ,price, date) 
                    VALUES (?, ?, ?) 
                    ON CONFLICT({data[0]}, date) 
                    DO UPDATE SET
                    price = excluded.price;"""
        with connection.get_db(DB_PATH) as conn:  # type: ignore
            cursor = conn.cursor()
            cursor.execute(query, (data[1], int(data[2] * 1_000_000), date))

def _create_csv_path(date: str, driver_or_constructor: str) -> Path:
    match driver_or_constructor:
        case "d" | "driver":
            identifier = "drivers"
        case "c" | "constructor":
            identifier = "constructors"
        case _:
            raise ValueError(f"Incorrect value for 'driver_or_constructor'. Expected 'd', 'c', 'driver', or 'constructor'. Got: '{driver_or_constructor}'")
    year, month, day = date.split("-")
    return FANTASY_PROCESSED_DIR / year / month / day / f"{identifier}.csv"

def _write_price_data_to_csv(price_data: list, date: str):
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
    
    driver_csv_path, constructor_csv_path = _create_csv_path(date, "driver"), _create_csv_path(date, "constructor")
    fm.write_to_csv(data=driver_prices, 
                    csv_path=driver_csv_path,
                    headers=fm.get_headers(driver_prices))
    fm.write_to_csv(data=constructor_prices, 
                    csv_path=constructor_csv_path,
                    headers=fm.get_headers(constructor_prices))

def run(json_data: dict, date: str) -> bool:
    try:
        _add_fantasy_data_to_db(json_data, date)
        price_data = _extract_prices(json_data, date)
        _add_price_data(price_data, date)
        _write_price_data_to_csv(price_data, date)
        return True
    except:
        return False

def test(url: str):
    response = requests.get(url)
    json_data = response.json()
    date = "2026-07-05"
    _add_fantasy_data_to_db(json_data, date)
    price_data = _extract_prices(json_data, date)
    _add_price_data(price_data, date)

def test_local(json_path: str, date: str):
    with open(file=json_path,mode="r",encoding="utf-8") as json_data:
        loaded_json = json.load(json_data)
    price_data = _extract_prices(loaded_json, date)
    _write_price_data_to_csv(price_data, date)
    
#test_local(json_path="data/fantasy/raw/2026/07-05.json", date="2026-07-05")
#test(r"https://fantasy.formula1.com/feeds/drivers/9_en.json")
#run_update(1950,2026)