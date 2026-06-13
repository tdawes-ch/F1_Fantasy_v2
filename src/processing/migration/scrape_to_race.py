"""
File to migrate data from the scraped tables to the race tables.
"""
from config.config import DB_PATH
from database.management import connection
from rich.progress import Progress
from pathlib import Path
# format is [schema_to_schema_table] e.g. races_to_scrape_sessions
# scrape_race_weekends -> race_races

def scrape_to_race_races(db_path: Path):
    migration_data = {}
    # get data from scrape_race_weekends
    with connection.get_db(db_path) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT race_id, race_name, circuit, city, year, round
                          FROM scrape_race_weekends;
                       """)
        results = cursor.fetchall()
        for row in results:
            # save data to dictionary
            migration_data = {
                "race_id":row[0],
                "name":row[1],
                "circuit":row[2],
                "city":row[3],
                "season":row[4],
                "round":row[5]
                }
            # write data to race_races
            cursor.execute("""
                            INSERT INTO race_races (race_id, name, circuit, city, season, round)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT(race_id) DO NOTHING;
                        """,
                        (migration_data["race_id"],
                         migration_data["name"],
                         migration_data["circuit"],
                         migration_data["city"],
                         migration_data["season"],
                         migration_data["round"])
                        )

def scrape_to_race_sessions(db_path: Path):
    migration_data = {}
    # get data from scrape_race_weekends
    with connection.get_db(db_path) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT session_id, race_id, session_type
                          FROM scrape_sessions;
                       """)
        results = cursor.fetchall()
        for row in results:
            # save data to dictionary
            migration_data = {
                "session_id":row[0], # session ID should be something meaningful (race_id + session_type?)
                "race_id":row[1],
                "session_type":row[2]
                # also need to get the date of the session from somewhere
                }
            # write data to race_races
            cursor.execute(
                        """
                        INSERT INTO race_sessions (session_id, race_id, session_type)
                        VALUES (?, ?, ?)
                        ON CONFLICT(session_id) DO NOTHING;
                        """,
                        (migration_data["session_id"],
                         migration_data["race_id"],
                         migration_data["session_type"]
                        )
                        )
            
def scrape_to_race_seasons(db_path: Path):
    migration_data = {}
    # get data from scrape_race_weekends
    with connection.get_db(db_path) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT year, expected_races, scraped_races
                          FROM scrape_seasons;
                       """)
        results = cursor.fetchall()
        for row in results:
            # save data to dictionary
            migration_data = {
                "year":row[0],
                "expected_races":row[1],
                "scraped_races":row[2]
                }
            # write data to race_races
            cursor.execute("""
                            INSERT INTO race_seasons (season, total_sessions, actual_sessions)
                            VALUES (?, ?, ?)
                            ON CONFLICT(season) DO NOTHING;
                        """,
                        (migration_data["year"],
                         migration_data["expected_races"],
                         migration_data["scraped_races"]
                        )
                        )

def migrate_all(progress: Progress, db_path: Path = DB_PATH):
    migration_task = progress.add_task(description=f"",total=3)
    # runs all migration sql scripts (this will run on setup)

    task_description = "Copying [blue]Seasion Data[/blue]..."
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_seasons(db_path)
    progress.advance(migration_task)

    task_description = "Copying [blue]Race Data[/blue]..."
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_races(db_path)
    progress.advance(migration_task)

    task_description = "Copying [blue]Session Data...[/blue]"
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_sessions(db_path)
    progress.advance(migration_task)


    progress.update(migration_task, description=f"[green]✓ Data copied to [i b]race[/i b] tables[/green]")