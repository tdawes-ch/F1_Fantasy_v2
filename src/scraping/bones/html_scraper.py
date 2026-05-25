'''
Each file within this folder will use html scraper. It'll take the following parameters:
def html_scraper(url, output):

where url is a string to a website
and output is a filepath for the .html to be saved
'''
from bs4 import BeautifulSoup
import validators
import requests

def validate_url(url): # obsolete
    ...

def validate_output(path):
    ...

def download_html(url):
    ...

def save_html(content, path):
    ...

def html_scraper(url, output):
    if response.raise_for_status() != None:
        log
    validate_url(url)
    validate_output(output)
    
    html = download_html(url)
    save_html(html, output)

url = "https://www.formula1.com/en/results/{fyear}/races"
response = requests.get(url.format(fyear=2020))
print(response.text[:10])
print(response.raise_for_status()==None)