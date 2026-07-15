from bones import scraper_toolbox
from pathlib import Path

url = r"https://fantasy.formula1.com/en/game-rules"
output_path = Path(r"C:\Users\thoma\OneDrive\Documents\Python\F1_Fantasy_v2\data\fantasy\raw\2026\rules\rules.html")
scraper_toolbox.html_scraper(url, output_path)