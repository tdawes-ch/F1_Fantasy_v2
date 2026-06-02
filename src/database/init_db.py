from database.management.connection import get_db
from pathlib import Path
from config.config import DB_PATH

def init_db():
    with open(DB_PATH.parent / "schema.sql", "r") as f:
        schema = f.read()

    with get_db(DB_PATH) as conn:
        conn.executescript(schema)