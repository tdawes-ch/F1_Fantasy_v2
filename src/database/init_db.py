from database.management.connection import get_db
import logging
from pathlib import Path
import sqlite3

# Configure logging to help with debugging
logger = logging.getLogger(__name__)

def init_db(db_path: Path = Path("database/f1.db")):
    schema_path = db_path.parent / "schema.sql"
    
    # 1. Handle File Reading Errors
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = f.read()
    except FileNotFoundError:
        logger.error(f"Database initialization failed: Schema file not found at {schema_path}")
        raise
    except PermissionError:
        logger.error(f"Database initialization failed: Insufficient permissions to read {schema_path}")
        raise
    except Exception as e:
        logger.error(f"Database initialization failed: Unexpected error reading schema file: {e}")
        raise

    # 2. Handle Database Execution Errors
    try:
        with get_db(db_path) as conn:
            conn.executescript(schema)
        logger.info("Database successfully initialized from schema.")
    except sqlite3.OperationalError as e:
        logger.error(f"Database initialization failed: Operational error (check file paths/permissions) - {e}")
        raise
    except sqlite3.DatabaseError as e:
        # Catches syntax errors in schema.sql, corrupt DBs, etc.
        logger.error(f"Database initialization failed: SQL syntax or database execution error - {e}")
        raise
    except Exception as e:
        logger.error(f"Database initialization failed: An unexpected database error occurred: {e}")
        raise