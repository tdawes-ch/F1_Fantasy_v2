''' 
manages connection to db
'''
import sqlite3
from pathlib import Path

def get_connection(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # allows column-name access
    return conn