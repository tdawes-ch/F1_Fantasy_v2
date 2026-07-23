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
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, Optional
import logging
from pathlib import Path
import sqlite3
import sys
from rich.progress import Progress
from rich import print

# adding logging in case i use it in the future...
logger = logging.getLogger(__name__)

@dataclass
class CheckResult:
    name: str
    description: str
    passed: bool = False
    critical: bool = True  # If True, a failure should halt the entire app
    error: Optional[Exception] = None
    
class SetupChecker:
    def __init__(self):
        # Format: (machine_name, UI_display_name, is_critical_bool, function_to_run) <- TY Gemini!
        self.checks = [("locations", "Config Locations", True, self._run_locations_check),
                       ("files", "Config Files", True, self._run_files_check),
                       ("db", "Database Validity", True, self._run_db_check),
                       ("db_data", "Database Data", False, self._run_db_data_check),
                       ("random_db_path", "Database Paths", False, self._run_db_path_check),
                       ("network", "Network Connection", False, self._run_network_check)
                       ]
        # list of all results from the checks:
        self.results: List[CheckResult] = []
        # used internally for tracking locations ans files:
        self._missing_locations = []
        self._missing_files = []
        self._db_tables = []

    def run_all(self, on_progress_step: Callable[[str], None]) -> Tuple[List[CheckResult], bool]:
        # takes in the function to update the CLI (on_progress_step) 
        # outputs the list of all checks, followed by True/False if the checks are OK or not

        self.results = [] # resets list in case this is run multiple times
        system_healthy = True # assumes everything is ok. Only a failed check will make it False

        # loop through each check to be completed
        for key, description, critical, check_func in self.checks:
            # 1. function for updating the CLI with the description
            on_progress_step(description)

            # 2. Create CheckResult datatpye
            result = CheckResult(name=key, description=description, critical=critical)
            """ Example:
                    name: locations <- set
                    description: Config Locations <- set
                    passed: False <- default
                    critical: True <- set
                    error: None <- default
            """

            #3. Run the check function associated with the check.
            try:
                check_func()
                result.passed = True
                logger.info(f"Setup Check PASSED: {description}")
            except Exception as e:
                # if fail:
                result.error = e
                result.passed = False
                logger.error(f"Setup Check FAILED: {description} - Error: {e}")

                if critical:
                    system_healthy = False
            
            # 4. add results to self variable
            self.results.append(result)
        
        # returns all results of checks, and if the system is healthy or not.
        return self.results, system_healthy

    def _run_locations_check(self):
        # ("locations", "Config Locations", True, self._run_locations_check)
        self._missing_locations = []
        self._missing_files = []

        for var_name, filepath in TRACKED_LOCATIONS.items():
            if filepath.suffix: # If it's a file
                if not fm.check_location(filepath, flag='file'):
                    self._missing_files.append([var_name, filepath])
            else: # it's a directory
                if not fm.check_location(filepath, flag='dir'):
                    self._missing_locations.append([var_name, filepath])
        
        if self._missing_locations:
            for _, filepath in self._missing_locations:
                fm.create_path(dir_path=filepath)


    def _run_files_check(self):
        # ("files", "Config Files", True, self._run_files_check)
        """Validates that all necessary files exist within those locations."""
        # This relies on the execution of _run_locations_check right before it
        if self._missing_files:
            readable_errors = [f"{var_name} ({path})" for var_name, path in self._missing_files]
            raise FileNotFoundError(f"Missing required files: {', '.join(readable_errors)}")

    def _run_db_check(self):
        #("db", "Database Validity", True, self._run_db_check)
        if not fm.check_location(filepath=DB_PATH, flag='file'):
            raise FileNotFoundError(f"Database file not found at: {DB_PATH}. Must've been an error when initialising.")

        with connection.get_db(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name 
                  FROM sqlite_master 
                 WHERE type='table' AND name NOT LIKE 'sqlite_%';
            """)
            # Store tables on the class instance so the data check can reuse 
            self._db_tables = cursor.fetchall()

        if not self._db_tables:
            raise ValueError("Database structure missing: No tables found.")
        
    def _run_db_data_check(self):
        # ("db_data", "Database Data", False, self._run_db_data_check)
        if not self._db_tables:
            raise ValueError("Cannot verify data because database tables are missing.")
        
        has_data = False
        with connection.get_db(db_path=DB_PATH) as conn:
            cursor = conn.cursor()
            for table_name in self._db_tables:
                cursor.execute(f"SELECT 1 FROM [{table_name[0]}] LIMIT 1;")
                if cursor.fetchone() is not None:
                    has_data = True
                    break # found data! No need to check other tables
            
        if not has_data:
            raise ValueError("Database is empty: Tables exist but contain no rows.")

    def _run_db_path_check(self):
        # ("random_db_path", "Database Paths", False, self._run_db_path_check)
        # As other checks are critical, no need to check for db_path
        with connection.get_db(DB_PATH) as conn: # type: ignore
            cursor = conn.cursor()
            try:
                cursor.execute("""
                                SELECT filepath
                                FROM scrape_log;
                                """
                                )
                random_path = cursor.fetchone()
            except sqlite3.OperationalError:
                raise ValueError("Could not read from 'scrape_log' table. Does it exist?")

        if not random_path or not random_path[0]:
            # no data, or nothing exists in the column:
            raise ValueError("No records found in 'scrape_log' to verify file system paths.")

        path_from_db = Path(random_path[0])
        if not fm.check_location(filepath=path_from_db, flag="file"):
            raise FileNotFoundError(f"File '{path_from_db}' from database log missing on disk.")

    def _run_network_check(self):
        connection_ok, connection_error = network.test_outbound_connection() # quick ping
        if not connection_ok:
            raise connection_error or Exception(f"Quick connection test failed.")
        
        url = "https://www.formula1.com/"
        connection_ok, connection_error = network.test_outbound_connection(url) # quick ping
        if not connection_ok:
            raise connection_error or Exception(f"Connection test failed for '{url}'")
        
    def did_check_pass(self, check_name: str) -> Tuple[bool, Exception | None]:
        """
        Queries the status of a specific check by its name ID.
        
        Args:
            check_name (str): The unique string key of the check (e.g., 'network')
            "locations", "files", "db", "db_data", "random_db_path", "network"
            
        Returns:
            bool: True if the check ran and passed, False otherwise.
        """
        # "locations", "files", "db", "db_data", "random_db_path", "network"
        for result in self.results:
            if result.name == check_name:
                return result.passed, result.error
        return False, None


#######################################
'''
TESTING BELOW (AI GENERATED):
'''
def test():
    checker = SetupChecker()

    print("Starting system diagnostics...")

    # Initialize the Rich progress bar library context manager
    with Progress() as progress:
        # Create a new progress task line. Total matches the amount of checks we registered.
        task_id = progress.add_task("[cyan]Initializing...", total=len(checker.checks))
        
        # -----------------------------------------------------------------
        # CALLBACK FUNCTION DEFINITION
        # -----------------------------------------------------------------
        # This function acts as a bridge. We give this function to the Checker.
        # When the Checker runs a check, it runs this function, allowing main.py
        # to manage its own UI updates cleanly.
        def update_ui(description: str):
            progress.update(task_id, description=f"Checking: [yellow]{description}[/yellow]")
            progress.advance(task_id) # Increments progress bar by 1
        # -----------------------------------------------------------------

        # Execute the check pipeline, passing the UI callback function inward.
        # It returns our rich custom data structures.
        results, system_healthy = checker.run_all(on_progress_step=update_ui)

    # Context manager closed. The progress bar is finished animating.
    # Now, we parse our custom data types to print out a clean summary report.
    print("\n--- Diagnostic Report ---")
    
    for r in results:
        # Evaluate properties directly using the clear variable names on our custom data type
        status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        importance = "(Critical)" if r.critical else "(Optional)"
        
        print(f"{status} {r.description} {importance}")
        
        # If an error object was caught and stored inside the data type, print its message out
        if r.error:
            print(f"   └── Error Details: {r.error}")

    # Act decisively on the overarching system health status flag
    if not system_healthy:
        print("\n[CRITICAL] Application failed to start due to missing requirements. See logs above.")
        sys.exit(1) # Kill the script immediately with an error exit code
        
    print("\n[SUCCESS] System checks passed. Launching application...")
    # ... Your main app code/server start goes here ...
