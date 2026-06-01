from bs4 import BeautifulSoup
from pathlib import Path
import csv

def load_html_file(html_path: Path | str) -> BeautifulSoup:
    html_path = Path(html_path)
    # opens an html file as beautifulsoup
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {path.name} in {path.parent}")

    if html_path.suffix.lower() != ".html":
        raise FileNotFoundError("File must be a .html file")

    with open(html_path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f, "html.parser")
    

def write_to_csv(data: list[dict], csv_path: Path | str, headers: list[str]):
    csv_path = Path(csv_path)
    # writes a file to csv given data, a filepath, and headers
    if csv_path.suffix.lower() != ".csv":
        raise Exception("File must be a .csv file")
    
    # ensure output directory exists
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
