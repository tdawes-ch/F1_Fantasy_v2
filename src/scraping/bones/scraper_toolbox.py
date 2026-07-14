'''
Each file within this folder will use html scraper. It'll take the following parameters:
def html_scraper(url, output):

where url is a string to a website
and output is a filepath for the .html to be saved

must:
1. get url, check if it's valid (validators)
2. Validate filepath somehow. 
3. If both are valid, will try and get data. 200 OK is good (not 200 ok then quit and submit error)
4. If it's 200 OK, convert text output to prettified HTML
'''
from bs4 import BeautifulSoup
import validators
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from database.management import connection
from config.config import DB_PATH, RAW_DATA_DIR
from scraping.bones.errors import (ScraperError, InvalidUrlError, FetchError, FileWriteError, FilepathError)
import json

def validate_url(url: str) -> str:
    """Checks whether the URL is a valid URL or not. Use:
    - checked_url = validate_url(url=url)

    Args:
        url (str): The URL to be checked

    Raises:
        InvalidUrlError: URL is missing scheme (http/https)
        InvalidUrlError: URL is missing domain
        InvalidUrlError: Invalid URL formats

    Returns:
        str: the same URL
    """
    if not validators.url(url):
        parsed = urlparse(url)
        error_type = "InvalidUrlError"
        if not parsed.scheme:
            raise InvalidUrlError(f"{error_type}: URL is missing scheme (http/https)")
        elif not parsed.netloc:
            raise InvalidUrlError(f"{error_type}: URL is missing domain")
        else:
            raise InvalidUrlError(f"{error_type}: Invalid URL format")
    else:
        return url


def validate_output(filepath: Path, suffix: str = ".html") -> Path:
    """Makes sure that the output path is correct (contains a filename and the file has the correct suffix)

    Args:
        filepath (Path): Path to the file
        suffix (str): Suffix of the file, e.g. .html, .json

    Raises:
        FilepathError: Output path must include a filename
        FilepathError: Unsupported output file type (not .html, or .json)

    Returns:
        Path: The original path
    """
    path = Path(filepath)

    if not path.name:
        raise FilepathError("Output path must include a filename")

    if path.suffix.lower() != suffix.lower():
        raise FilepathError(f"Unsupported output file type (not {suffix})")

    return path


def fetch_url(url: str) -> str:
    """Uses the requests module to get the HTML text from the URL

    Args:
        url (str): The URL to be pinged for data

    Raises:
        FetchError: Invalid URL format (missing schema like http:// or https://)
        FetchError: Invalid URL provided
        TimeoutError: Request timed out
        ConnectionError: Failed to connect to the server
        RuntimeError: HTTP error
        RuntimeError: Catches unexpected errors

    Returns:
        str: Returns pure HTML text
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    except requests.exceptions.MissingSchema:
        raise FetchError("Invalid URL format (missing schema like http:// or https://)")

    except requests.exceptions.InvalidURL:
        raise FetchError("Invalid URL provided")

    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out")

    except requests.exceptions.ConnectionError:
        raise ConnectionError("Failed to connect to the server")

    except requests.exceptions.HTTPError as e:
        # This covers non-200 responses after raise_for_status()
        raise RuntimeError(f"HTTP error occurred: {e}")

    except requests.exceptions.RequestException as e:
        # Catch-all for anything requests can throw
        raise RuntimeError(f"Unexpected request error: {e}")
    

def fetch_json(url: str) -> str:
    """Uses the requests module to get the HTML text from the URL

    Args:
        url (str): The URL to be pinged for data

    Raises:
        FetchError: Invalid URL format (missing schema like http:// or https://)
        FetchError: Invalid URL provided
        TimeoutError: Request timed out
        ConnectionError: Failed to connect to the server
        RuntimeError: HTTP error
        RuntimeError: Catches unexpected errors

    Returns:
        str: Returns pure HTML text
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.MissingSchema:
        raise FetchError("Invalid URL format (missing schema like http:// or https://)")

    except requests.exceptions.InvalidURL:
        raise FetchError("Invalid URL provided")

    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out")

    except requests.exceptions.ConnectionError:
        raise ConnectionError("Failed to connect to the server")

    except requests.exceptions.HTTPError as e:
        # This covers non-200 responses after raise_for_status()
        raise RuntimeError(f"HTTP error occurred: {e}")
    
    except requests.exceptions.JSONDecodeError as e:
        raise RuntimeError(f"JSON Decoder error: {e}")
    
    except requests.exceptions.InvalidJSONError as e:
        raise RuntimeError(f"Invalid JSON error: {e}")

    except requests.exceptions.RequestException as e:
        # Catch-all for anything requests can throw
        raise RuntimeError(f"Unexpected request error: {e}")


def save_html(html: str, output_path: Path = RAW_DATA_DIR):
    """Saves the HTML text to a .html file defined by 'output_path'

    Args:
        html (str): Raw HTML string of text (usually from html.prettify() )
        output_path (Path, optional): _description_. Defaults to RAW_DATA_DIR (the raw data directory defined in .env).
    """
    path = validate_output(filepath=output_path, suffix=".html")
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")

    tmp_path.write_text(html, encoding="utf-8")
    tmp_path.replace(path)

def save_json(json_data: str, output_path: Path = RAW_DATA_DIR):
    """Saves the JSON to a .json file defined by 'output_path'

    Args:
        json (str): JSON data
        output_path (Path, optional): _description_. Defaults to RAW_DATA_DIR (the raw data directory defined in .env).
    """
    path = validate_output(filepath=output_path, suffix=".json")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        # indent=4 adds clean spacing, sort_keys is optional but keeps it organized
        json.dump(json_data, f, indent=4, ensure_ascii=False, sort_keys=True)

def log_to_db(url: str, output_path: Path, status: None | str = None) -> datetime:
    """All scraped URLs will be logged in the 'scrape_log' table. It will log the URL and the path to the associated HTML file.

    Args:
        url (str): The URL getting scraped
        output_path (Path): The output path of the HTML
    """    
    current_time = datetime.now()
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO scrape_log (url, filepath, last_scraped, status)
                        VALUES (?, ?, ?, ?);
                        """,
                        (url, str(output_path), current_time, None)
                        )
    return current_time

def update_db(url: str, output_path: Path, time: datetime, status: str):
    """This updates the status of the scraped URL, depending on how the network is. If it's F, it's flagged as something that should be retried
    Args:
        url (str): The URL getting scraped
        output_path (Path): The output path of the HTML
        time (datetime): The time of the original insert
        status (str): The flag ("C" = confirmed, "F" = failed. Maybe more to come)
    """    
    current_time = datetime.now()
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        UPDATE scrape_log SET status = ? 
                        WHERE url = ? 
                        AND filepath = ?
                        AND last_scraped = ?;
                        """,
                        (status, url, str(output_path), time)
                        )
    return current_time

def html_scraper(url: str, output_path: Path):
    """Given a URL and a filepath, this function will download the HTML data, prettify it, save it, and log the action to the database.

    Args:
        url (str): URL to be scraped
        output_path (Path): The path for the HTML file that the scraped data will be saved into
    """
    checked_url = validate_url(url) # is a valid url 
    current_time = log_to_db(checked_url, output_path)
    try:
        html = BeautifulSoup(fetch_url(checked_url),"html.parser")
        prettified_html = html.prettify()
        save_html(prettified_html, output_path)
        update_db(checked_url, output_path, current_time, status="C")
    except Exception as e:
        update_db(checked_url, output_path, current_time, status="F")
        raise Exception(e)

def json_scraper(url: str, output_path: Path):
    checked_url = validate_url(url) # is a valid url 
    current_time = log_to_db(checked_url, output_path)
    try:
        json = fetch_json(checked_url)
        save_json(json, output_path)
        update_db(checked_url, output_path, current_time, status="C")
    except Exception as e:
        update_db(checked_url, output_path, current_time, status="F")
        raise Exception(e)