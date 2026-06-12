"""
This will have various checks to see the status of the current setup.

1, Check if f1.db exists (and a query)
2, Checks if config locations and files exist
3, Checks if a random filepath in the database exists
4, Checks network with a ping to url

"""
import toolbox.file_management as fm
from toolbox import network
from config.config import DB_PATH, TRACKED_LOCATIONS
from database.management import connection
from pathlib import Path
from rich.progress import Progress

def _check_db(path_to_db: Path):
    if fm.check_location(filepath=path_to_db, flag='file'):
        with connection.get_db(path_to_db) as conn: # type: ignore
            cursor = conn.cursor()
            cursor.execute("""
                            SELECT name 
                              FROM sqlite_master 
                             WHERE type='table' AND name NOT LIKE 'sqlite_%';
                            """
                            )
            tables = cursor.fetchall()

            # If no tables exist at all, raise an error
            if not tables:
                raise ValueError("Database is empty: No user tables found.")
            
            # 2. Check if at least ONE table contains data
            has_data = False
            for (table_name,) in tables:
                cursor.execute(f"SELECT 1 FROM [{table_name}] LIMIT 1;")
                if cursor.fetchone() is not None:
                    has_data = True
                    break # found data! No need to check other tables.
                
            if not has_data:
                raise ValueError("Database is empty: Tables exist but contain no rows.")
                
            return True

    else:
        raise ValueError(f"Database not found in: {path_to_db}")
    
def _check_path_in_database(path_to_db: Path):
    with connection.get_db(path_to_db) as conn: # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT filepath
                          FROM scrape_log;
                        """
                        )
        random_path = cursor.fetchone()[0]

    if random_path:
        if fm.check_location(filepath=random_path, flag="file"):
            return True
        else:
            raise ValueError(f"Couldn't open path ({random_path}) collected from database")
    else:
        raise ValueError(f"Couldn't find ")
    
def _check_config_locations(locations: dict):
    missing_locations = []
    missing_files = []

    for var_name, filepath in locations.items():
        if filepath.suffix:
            flag = 'file'
            if not fm.check_location(filepath, flag):
                missing_files.append({
                    var_name: str(filepath)
                })
        else:
            flag = 'dir'
            if not fm.check_location(filepath, flag):
                missing_locations.append({
                    "variable": var_name,
                    "filepath": str(filepath)
                })

    return missing_locations, missing_files

def _create_config_locations(locations: list[dict]):
    for location in locations:
        fm.create_path(location["filepath"])


def do_checks(progress: Progress, task_id) -> tuple:
    checks = {
        "locations": False,
        "files": False,
        "db": False,
        "random_db_path": False,
        "network": False
    }
    errors = []

    progress.update(task_id, 
                    description=f"Performing check: [yellow]locations and files[/yellow]", 
                    total=len(checks),
                    completed=0
    )

    ## check locations and files
    missing_locations, missing_files = _check_config_locations(TRACKED_LOCATIONS)
    if missing_locations:
        try:
            _create_config_locations(missing_locations)
        except OSError as e:
            errors.append(e)

    checks["locations"] = True
    progress.advance(task_id)

    if not missing_files:
        checks["files"] = True
    progress.advance(task_id)

    ## check database
    progress.update(task_id, description=f"Performing check: [yellow]database[/yellow]")
    try:
        valid_db = _check_db(DB_PATH)
        checks["db"] = True
    except ValueError as e:
        valid_db = False
        errors.append(e)
    progress.advance(task_id)

    
    ## check random path in database
    progress.update(task_id, description=f"Performing check: [yellow]database path[/yellow]")
    if valid_db:
        try:
            checks["random_db_path"] = _check_path_in_database(DB_PATH)
        except ValueError as e:
            errors.append(e)
    progress.advance(task_id)

    ## network check
    progress.update(task_id, description=f"Performing check: [yellow]network connection[/yellow]")
    connection_ok, connection_error = network.test_outbound_connection()
    if connection_ok:
        checks["network"] = True
    else:
        errors.append(connection_error)
    progress.advance(task_id)

    return checks, errors