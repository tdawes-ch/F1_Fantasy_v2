from scraping.bones import html_scraper_toolbox
from config.config import FANTASY_RAW_DIR
from pathlib import Path
from toolbox import file_management as fm
from datetime import datetime, date
from pprint import pprint
from database.management import connection

def _create_dir_path(directory: Path = FANTASY_RAW_DIR) -> Path:
    return directory / datetime.now().strftime("%Y")

def _create_filename() -> str:
    return f"{datetime.now().strftime('%m-%d')}.html"

def get_latest_file(directory: Path = FANTASY_RAW_DIR) -> tuple[str | None, Path]:
    """Gets the most recent file in the directory by sorting alphabetically (as these files will be named mm_dd.html)

    Args:
        directory (Path, optional): The directory to be searched. Defaults to FANTASY_RAW_DIR.

    Returns:
        tuple[str | None, Path]: The most recent filename, followed by the directory it's in.
    """
    latest_folder = sorted([folder.name for folder in directory.iterdir() if folder.is_dir()], reverse=True)
    if latest_folder:
        latest_folder = latest_folder[0]
    else:
        return None, directory

    files = sorted([file.name for file in Path(directory / latest_folder).iterdir() if file.is_file()], reverse=True)
    if files:
        return files[0], Path(directory / latest_folder)
    else:
        return None, directory

def _add_to_db(filepath: Path | str, url: str, date: str):
    filepath = str(filepath)
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO fantasy_scraping (url, date, is_processed, filepath)
                        VALUES(?, ?, ?, ?)
                        ON CONFLICT (url, date)
                        DO NOTHING;
                        """,
                        (url, date, 0, filepath)
                        )
    
def run(url: str) -> None:
    directory = _create_dir_path(directory=FANTASY_RAW_DIR)
    filename = _create_filename()
    fullpath = directory / filename
    html_scraper_toolbox.html_scraper(url=url, output_path=fullpath)
    _add_to_db(filepath=fullpath, url=url, date=date.today().strftime("%Y-%m-%d"))