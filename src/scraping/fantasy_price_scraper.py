from scraping.bones import html_scraper_toolbox
from config.config import FANTASY_RAW_DIR
from pathlib import Path
from toolbox import file_management as fm
from datetime import datetime
from pprint import pprint

def _create_dir_path() -> Path:
    return FANTASY_RAW_DIR / datetime.now().strftime("%Y")

def _create_filename() -> str:
    return f"{datetime.now().strftime('%m-%d')}.html"

def get_latest_file(directory: Path = FANTASY_RAW_DIR) -> str | None:
    """Gets the most recent file in the directory by sorting alphabetically (as these files will be named mm_dd.html)

    Args:
        directory (Path, optional): The directory to be searched. Defaults to FANTASY_RAW_DIR.

    Returns:
        str | None: Either the name of the file, or None if one doesn't exist in the directory.
    """
    files = sorted([file.name for file in directory.iterdir() if file.is_file()], reverse=True)
    if files:
        return files[0]
    else:
        return None
    
def run():
    pprint(_create_filename())
    pprint(_create_dir_path())
    print(get_latest_file(FANTASY_RAW_DIR))
    
run()