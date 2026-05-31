from database.management.connection import get_connection
from pathlib import Path
from config.config import DB_PATH

def init_db():
    conn = get_connection(DB_PATH)

    with open(DB_PATH.parent / "schema.sql", "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()

init_db()