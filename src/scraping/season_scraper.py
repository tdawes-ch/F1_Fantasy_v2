"""
Goes through each season:
https://www.formula1.com/en/results/{fyear}/races (format(fyear = year))
given a start year, end year (default start = 1950, default end = this year)

Gets:
- html page prettified by beautifulsoup.prettify()

Outputs html page into:
data/sessions/raw/<year>/<year>.html
"""
import requests
from pathlib import Path
import datetime
import scraping.bones as bones


def download_years(start_year: int = 2000, end_year: int = int(datetime.datetime.now().strftime("%Y"))):
    url = "https://www.formula1.com/en/results/{fyear}/races"
    ...

def download_race_pages( output_folder: str, url: str, start_year: int = 2000, end_year: int = int(datetime.datetime.now().strftime("%Y")) ):
    for year in range(start_year, end_year + 1):
        print(year)

        print(f"Downloading {year}...")

        response = requests.get(url)
        response.raise_for_status()

        # Prettify
        html = BeautifulSoup(response.text, "html.parser")
        prettified_html = html.prettify()

        # Create folder if not exists
        folder = Path(f"data/raw/{year}")
        folder.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = folder / f"{year}_races.html"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(prettified_html)

        print(f"Saved to {file_path}")