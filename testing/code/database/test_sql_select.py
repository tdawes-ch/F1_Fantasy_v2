from config.config import DB_PATH
from database.management import connection

with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT DISTINCT(race_name)
                            FROM scrape_race_weekends
                           WHERE race_id = 1045;
                        """)
        output = cursor.fetchall()
 
for row in output:
    print(row[0])