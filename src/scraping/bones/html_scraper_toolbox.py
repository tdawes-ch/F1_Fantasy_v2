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
from pathlib import Path
from urllib.parse import urlparse
from scraping.bones.errors import (ScraperError, InvalidUrlError, FetchError, FileWriteError, FilepathError)


def validate_url(url: str) -> str:
    # uses validators and urllib.parse.urlparse to validate
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
    path = Path(filepath)

    if not path.name:
        raise FilepathError("Output path must include a filename")

    if path.suffix.lower() not in {".html"}:
        raise FilepathError("Unsupported output file type")

    return path


def fetch_url(url: str) -> str:
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


def save_html(html, output_path):
    path = validate_output(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = path.with_suffix(path.suffix + ".tmp")

    tmp_path.write_text(html, encoding="utf-8")
    tmp_path.replace(path)


def html_scraper(url, output_path):
    validate_url(url) # is a valid url 
    print(url)
    html = BeautifulSoup(fetch_url(url),"html.parser")
    prettified_html = html.prettify()
    save_html(prettified_html, output_path)