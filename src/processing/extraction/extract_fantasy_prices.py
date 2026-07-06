from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from config.config import DB_PATH
from database.management import connection
from datetime import datetime
from toolbox import processing

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

def run(json_data: dict, date: str):
    _add_fantasy_data_to_db(json_data, date)
    price_data = _extract_prices(json_data, date)
    _add_price_data(price_data, date)

def test(url: str):
    response = requests.get(url)
    json_data = response.json()
    date = "2026-07-05"
    _add_fantasy_data_to_db(json_data, date)
    price_data = _extract_prices(json_data, date)
    _add_price_data(price_data, date)

test(r"https://fantasy.formula1.com/feeds/drivers/9_en.json")
#run_update(1950,2026)