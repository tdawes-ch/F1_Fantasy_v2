from bs4 import BeautifulSoup
from pathlib import Path
import csv
from typing import Literal

def load_html_file(filepath: Path | str) -> BeautifulSoup:
    """Loads an HTML file from a filepath

    Args:
        filepath (Path | str): The path to the HTML file including filename

    Raises:
        FileNotFoundError: Path isn't found
        FileNotFoundError: Isn't a .html file

    Returns:
        BeautifulSoup: The HTML output
    """
    html_path = Path(filepath)
    # opens an html file as beautifulsoup
    if not html_path.exists():
        raise FileNotFoundError(f"File not found: {html_path.name} in {html_path.parent}")

    if html_path.suffix.lower() != ".html":
        raise FileNotFoundError("File must be a .html file")

    with open(html_path, "r", encoding="utf-8") as f:
        return BeautifulSoup(f, "html.parser")
    

def write_to_csv(data: list[dict], csv_path: Path | str, headers: list[str]):
    """Writes data to a CSV file

    Args:
        data (list[dict]): The data for the CSV file, in the form of a list of dictionaries
            e.g.: [{header1: data, header2: data}, {header1: data, header2: data}]
        csv_path (Path | str): Path to the output CSV file, including .csv
        headers (list[str]): Headers of the CSV file as a list of strings
            e.g.: ["header1", "header2"]

    Raises:
        Exception: Filepath isn't to a .csv
    """
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

def load_csv(csv_path: Path | str) -> list[dict]:
    """Loads a csv into a list of dictionaries where the dictionary is in the format {header: data}

    Args:
        csv_path (Path | str): Path to the .csv file

    Raises:
        Exception: Filepath isn't to a .csv

    Returns:
        list[dict]: The data of the CSV file, in the form of a list of dictionaries
            e.g.: [{header1: data, header2: data}, {header1: data, header2: data}]
    """
    csv_path = Path(csv_path)
    if csv_path.suffix.lower() != ".csv":
        raise Exception("File must be a .csv file")
    results = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)
    return results

def create_path(dir_path: Path):
    """Creates a filepath at a set location

    Args:
        dir_path (Path): Path to be created

    Raises:
        OSError: Filepath can't be created
    """
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create directory at {dir_path}. {e}")
    
def check_location(filepath: Path, flag: Literal['dir', 'file'] = 'dir') -> bool:
    """Checks whether a filepath exists for either a directory or file depending on the flag

    Args:
        filepath (Path): The filepath to be checked
        flag (Literal['dir', 'file'], optional): A flag for whether to check for a directory or file. Defaults to 'dir'.

    Raises:
        ValueError: _description_

    Returns:
        bool: _description_
    """
    # Returns True if the filepath exists, False otherwise.
    if flag.lower() == 'dir':
        return Path(filepath).exists()
    elif flag.lower() == 'file':
        return Path(filepath).is_file()
    else:
        raise ValueError(f"Incorrect flag passed to check_path: {flag}")
    
def get_headers(list_dict:list[dict]) -> list[str]:
    """Gets a list of headers from a list of dictionaries, used for CSV processing

    Args:
        list_dict (list[dict]): the data

    Returns:
        list[str]: the headers
    """
    if list_dict:
        headers = list(list_dict[0].keys())
        return headers
    else:
        return []