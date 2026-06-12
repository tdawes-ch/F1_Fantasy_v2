from config.config import DB_PATH
from database.management import connection
import datetime

def get_last_scraped(url: str):
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute("""SELECT last_scraped
                            FROM scrape_log
                           WHERE url = ?
                           ORDER BY id DESC;
                        """,(url,)
                            )
        last_scraped = cursor.fetchone()
    return last_scraped[0]

def get_something():
    pass