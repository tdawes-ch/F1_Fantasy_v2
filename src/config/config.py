import os
from pathlib import Path
from dotenv import load_dotenv

""" 
this would get and set important variables for use later on

from config import VARIABLE_NAME 
from config import FILEPATH_TO_PROJECT
"""

# Load .env file
load_dotenv()

# get base url
BASE_URL = os.getenv("BASE_URL","https://www.formula1.com")

# project route (important for combining filepaths)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# data directories
DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIR", "data/")
RAW_DATA_DIR = PROJECT_ROOT / os.getenv("RAW_DATA_DIR", "data/sessions/raw/")
PROCESSED_DATA_DIR = PROJECT_ROOT / os.getenv("PROCESSED_DATA_DIR", "data/sessions/processed/")
LOG_DATA_DIR = PROJECT_ROOT / os.getenv("LOG_DATA_DIR", "data/logs/processed/")
LOG_DIR = PROJECT_ROOT / os.getenv("LOG_DIR", "data/logs/")

# database paths
DB_PATH = PROJECT_ROOT / os.getenv("DB_PATH", "database/f1.db")