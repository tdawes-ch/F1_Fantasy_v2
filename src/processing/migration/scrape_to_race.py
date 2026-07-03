"""
File to migrate data from the scraped tables to the race tables.
"""
from config.config import DB_PATH
from database.management import connection
from rich.progress import Progress
from pathlib import Path
# format is [schema_to_schema_table] e.g. races_to_scrape_sessions
# scrape_race_weekends -> race_races

def scrape_to_race_races(db_path: Path, update: bool):
    migration_data = {}
    # get data from scrape_race_weekends
    with connection.get_db(db_path) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT race_id, race_name, circuit, city, year, round, from_date, to_date
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
                "round":row[5],
                "from_date":row[6],
                "to_date":row[6]
                }
            # write data to race_races
            if update:
                cursor.execute("""
                                INSERT INTO race_races (race_id, name, circuit, city, season, round, from_date, to_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(race_id)
                                DO UPDATE SET
                                name = excluded.name,
                                circuit = excluded.circuit,
                                city = excluded.city,
                                season = excluded.season,
                                round = excluded.round,
                                from_date = excluded.from_date,
                                to_date= excluded.to_date;
                            """,
                            (migration_data["race_id"],
                            migration_data["name"],
                            migration_data["circuit"],
                            migration_data["city"],
                            migration_data["season"],
                            migration_data["round"],
                            migration_data["from_date"],
                            migration_data["to_date"])
                            )
            else:
                cursor.execute("""
                                INSERT INTO race_races (race_id, name, circuit, city, season, round, from_date, to_date)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(race_id) DO NOTHING;
                            """,
                            (migration_data["race_id"],
                            migration_data["name"],
                            migration_data["circuit"],
                            migration_data["city"],
                            migration_data["season"],
                            migration_data["round"],
                            migration_data["from_date"],
                            migration_data["to_date"])
                            )

def scrape_to_race_sessions(db_path: Path, update: bool):
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
            # write data to race_sessions
            if update:
                cursor.execute(
                            """
                            INSERT INTO race_sessions (session_id, race_id, session_type)
                            VALUES (?, ?, ?)
                            ON CONFLICT(session_id) 
                            DO UPDATE SET
                            session_type = excluded.session_type,
                            race_id = excluded.race_id;
                            """,
                            (migration_data["session_id"],
                            migration_data["race_id"],
                            migration_data["session_type"]
                            )
                            )
            else:
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
            
def scrape_to_race_seasons(db_path: Path, update: bool) -> None:
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
            # write data to race_seasons
            if update:
                cursor.execute("""
                               INSERT INTO race_seasons (season, total_sessions, actual_sessions)
                               VALUES (?, ?, ?)
                               ON CONFLICT(season)
                               DO UPDATE SET
                               total_sessions = excluded.total_sessions,
                               actual_sessions = excluded.actual_sessions
                               ;
                               """,
                               (migration_data["year"],
                                migration_data["expected_races"],
                                migration_data["scraped_races"]
                               )
                              )
            else: 
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

def migrate_all(progress: Progress, db_path: Path = DB_PATH, update: bool = True):
    migration_task = progress.add_task(description=f"",total=3)
    # runs all migration sql scripts (this will run on setup)

    task_description = "Copying [blue]Seasion Data[/blue]..."
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_seasons(db_path, update)
    progress.advance(migration_task)

    task_description = "Copying [blue]Race Data[/blue]..."
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_races(db_path, update)
    progress.advance(migration_task)

    task_description = "Copying [blue]Session Data...[/blue]"
    progress.update(migration_task,description=f"{task_description:<30}")
    scrape_to_race_sessions(db_path, update)
    progress.advance(migration_task)


    progress.update(migration_task, description=f"[green]✓ Data copied to [i b]race[/i b] tables[/green]")

from interface.progress_manager import get_progress_bar

def do_migration():
    with get_progress_bar() as progress:
        migrate_all(progress, DB_PATH)

def do_update():
    with get_progress_bar() as progress:
        migrate_all(progress, DB_PATH, update=True)

#do_migration()
#do_update()