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
from urllib.parse import urlparse

class ScraperError(Exception):
    # Base exception for scraper errors
    pass


class InvalidUrlError(ScraperError):
    # something up with the url
    pass


class FetchError(ScraperError):
    # url is okay, but something wrong with website. Not code 200 OK
    pass

class FileWriteError(ScraperError):
    # something up when writing the file
    pass

class FilepathError(Exception):
    pass

def validate_url(url: str):
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


def validate_output(path):
    ...

def download_html(url):
    html = requests.get(url)

    return 
    ...

def save_html(content, path):
    ...

def html_scraper(url, output_path):
    if not True:
        # isn't a valid url
        pass
    else: 
        # is a valid url
        if not validate_output(output_path):
            # output path isn't valid
            pass
        else:
            # output path is valid
            pass
    if url.raise_for_status() != None:
        # log url fail
        quit()
    else:
        validate_output(output_path)
    
    html = download_html(url)
    prettified_html = html.prettify()
    save_html(prettified_html, output_path)

try:
    validate_url("http://grnignaigndpag.com")
except ScraperError as e:
    print(e)

#response = requests.get(url.format(fyear=2020))
#print(response.text[:10])
#print(response.raise_for_status()==None)