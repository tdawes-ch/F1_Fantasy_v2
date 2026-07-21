from scraping.bones import scraper_toolbox
from config.config import FANTASY_RAW_DIR, DB_PATH
from pathlib import Path
from toolbox import file_management as fm
from datetime import datetime, date
from pprint import pprint
from database.management import connection

def _create_dir_path(directory: Path = FANTASY_RAW_DIR) -> Path:
    return directory / datetime.now().strftime("%Y")

def _create_filename(round: int) -> str:
    # datetime.now().strftime('%m-%d')
    return f"{round}.json"

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

def _add_to_db(filepath: Path | str, url: str, year: int, round: int):
    filepath = str(filepath)
    with connection.get_db(DB_PATH) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        INSERT INTO fantasy_scraping (url, year, round, is_processed, filepath)
                        VALUES(?, ?, ?, ?, ?)
                        ON CONFLICT (url, year, round)
                        DO NOTHING;
                        """,
                        (url, year, round, 0, filepath)
                        )
    
def run(url: str, year: int, round: int) -> None:
    directory = _create_dir_path(directory=FANTASY_RAW_DIR)
    filename = _create_filename(round)
    fullpath = directory / filename
    scraper_toolbox.json_scraper(url=url, output_path=fullpath)
    # date=date.today().strftime("%Y-%m-%d")
    _add_to_db(filepath=fullpath, url=url, year=year, round=round)

#run(r"https://fantasy.formula1.com/feeds/drivers/9_en.json")