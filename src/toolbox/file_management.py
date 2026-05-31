from bs4 import BeautifulSoup
from pathlib import Path
import csv

def load_html_file(html_path: str) -> BeautifulSoup:
    # opens an html file as beautifulsoup
    path = Path(html_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path.name} in {path.parent}")

    if path.suffix.lower() != ".html":
        raise FileNotFoundError("File must be a .html file")

    with open(path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f, "html.parser")
    

def write_to_csv(data: list[dict], csv_path: str, headers: list[str]):
    # writes a file to csv given data, a filepath, and headers
    path = Path(csv_path)

    if path.suffix.lower() != ".csv":
        raise Exception("File must be a .csv file")
    
    # ensure output directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
