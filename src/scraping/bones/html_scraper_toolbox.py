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

class ScraperError(Exception):
    # Base exception for scraper errors
    pass


class InvalidURLError(ScraperError):
    # something up with the url
    pass


class FetchError(ScraperError):
    # url is okay, but something wrong with website. Not code 200 OK
    pass


class FileWriteError(ScraperError):
    pass

def validate_url(url): # obsolete
    ...

def validate_output(path):
    ...

def download_html(url):
    html = requests.get(url)

    return 
    ...

def save_html(content, path):
    ...

def html_scraper(url, output_path):
    if not validators.url(url):
        # isn't a valid url
        pass
    else: 
        # is a valid url
        if not validate_output(output_path):
            # output path isn't valid
            pass
        else:
            # output path is valid
            
    

    if response.raise_for_status() != None:
        # log url fail
        quit()
    else:
        validate_output(output_path)
    
    html = download_html(url)
    prettified_html = html.prettify()
    save_html(prettified_html, output_path)

html_scraper("test","test")

#response = requests.get(url.format(fyear=2020))
#print(response.text[:10])
#print(response.raise_for_status()==None)