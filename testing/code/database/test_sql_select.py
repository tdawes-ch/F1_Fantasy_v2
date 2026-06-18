from config.config import DB_PATH
from database.management import connection

with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT srw.race_name
                          FROM scrape_race_weekends srw
                          LEFT JOIN scrape_sessions ss ON srw.race_id = ss.race_id
                         WHERE ss.url = ?;
                           """,
                           ("https://www.formula1.com/en/results/1999/races/687/australia/practice/2",)
                           )
        output = cursor.fetchall()
 
for row in output:
    print(row[0])