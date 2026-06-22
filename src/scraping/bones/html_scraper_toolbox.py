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
import datetime
from pathlib import Path
from urllib.parse import urlparse
from database.management import connection
from config.config import DB_PATH, RAW_DATA_DIR
from scraping.bones.errors import (ScraperError, InvalidUrlError, FetchError, FileWriteError, FilepathError)

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


def validate_output(filepath) -> Path:
    """Makes sure that the output path is correct (contains a filename and the file is .HTML)

    Args:
        filepath (_type_): Path to the file

    Raises:
        FilepathError: Output path must include a filename"
        FilepathError: Unsupported output file type (not .html)

    Returns:
        Path: _description_
    """
    path = Path(filepath)

    if not path.name:
        raise FilepathError("Output path must include a filename")

    if path.suffix.lower() not in {".html"}:
        raise FilepathError("Unsupported output file type (not .html")

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


def save_html(html: str, output_path: Path = RAW_DATA_DIR):
    """Saves the HTML text to a .html file defined by 'output_path'

    Args:
        html (str): Raw HTML string of text (usually from html.prettify() )
        output_path (Path, optional): _description_. Defaults to RAW_DATA_DIR (the raw data directory defined in .env).
    """
    path = validate_output(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")

    tmp_path.write_text(html, encoding="utf-8")
    tmp_path.replace(path)

def log_to_db(url: str, output_path: Path):
    """All scraped URLs will be logged in the 'scrape_log' table. It will log the URL and the path to the associated HTML file.

    Args:
        url (str): The URL getting scraped
        output_path (Path): The output path of the HTML
    """    
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO scrape_log (url, filepath, last_scraped)
                        VALUES (?, ?, ?);
                        """,
                        (url, str(output_path), datetime.datetime.now())
                        )

def html_scraper(url: str, output_path: Path):
    """Given a URL and a filepath, this function will download the HTML data, prettify it, save it, and log the action to the database.

    Args:
        url (str): URL to be scraped
        output_path (Path): The path for the HTML file that the scraped data will be saved into
    """
    checked_url = validate_url(url) # is a valid url 
    html = BeautifulSoup(fetch_url(checked_url),"html.parser")
    prettified_html = html.prettify()
    save_html(prettified_html, output_path)
    log_to_db(checked_url, output_path)