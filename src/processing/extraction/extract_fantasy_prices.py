from bs4 import BeautifulSoup
import requests # for testing
from urllib.parse import urljoin
from config.config import DB_PATH
from database.management import connection
from datetime import datetime

def _extract_prices(json_data):
    pass

def run(json_data: dict, url: str):
    pass

def test(url: str):
    response = requests.get(url)
    json_data = response.json()

test(r"https://fantasy.formula1.com/feeds/drivers/9_en.json")
#run_update(1950,2026)