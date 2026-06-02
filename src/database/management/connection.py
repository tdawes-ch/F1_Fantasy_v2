''' 
manages connection to db
'''
import sqlite3
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def get_db(db_path: str):
    """Provides a transactional scope around a series of operations."""
    conn = sqlite3.connect(db_path)
    # Optional: Converts row results into dictionary-like objects
    conn.row_factory = sqlite3.Row 
    try:
        yield conn
        conn.commit()  # Automatically commits if no errors happen
    except Exception as e:
        conn.rollback() # Automatically rolls back if an error occurs
        raise e
    finally:
        conn.close()   # ALWAYS closes the connection