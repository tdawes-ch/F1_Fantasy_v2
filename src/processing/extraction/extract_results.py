'''
Not 100% sure yet on how this will work but it will call the relevant results functions
in processing/extraction/extract_results.py
'''
from bs4 import BeautifulSoup
from toolbox import file_management as fm
from database.management import connection
from pprint import pprint
from config.config import DB_PATH

def get_results(soup: BeautifulSoup) -> list[dict] | None:
    """Extracts a table of results from the F1 results HTML page. Should work for all session types

    Args:
        soup (BeautifulSoup): Raw HTML data

    Returns:
        list[dict]: The table of results in the format of a list of dictionaries
    """
    headers = []
    table_data = []

    table = soup.find("table", class_ = "Table-module_table__cKsW2")
    if not table:
        raise ValueError("Couldn't find table within HTML data")

    thead = table.find("thead")
    tbody = table.find("tbody")
    if not thead or not tbody:
        raise ValueError("Couldn't find table data within HTML table") 
    
    for heading in thead.find_all("th"):
        headers.append(heading.get_text(strip=True))
        
    for row in tbody.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) != len(headers):
            return None
        else:
            row_values = []
            for column in columns:
                # there is a span in driver name as there is FNAME, LNAME, SHORT (Lewis, Hamilton, HAM)
                # there is also a span in constructors in newer sessions as there is the team logo

                spans = column.find_all("span", recursive=False) # first get all spans 
                if not spans: # if there aren't any spans, just add whatever data there is
                    row_values.append(column.get_text(strip=True)) # just add the text
                else: # if there are spans, check them
                    # row_values.append([data.get_text(strip=True) for data in sub_span])
                    for span in spans:
                        data = []
                        if span.strings:
                            for string in span.strings:
                                if not string.isspace():
                                    data.append(string.strip())
                        if len(data) == 1:
                            row_values.append(data[0])
                        else:
                            row_values.append(data)

            row_dict = dict(zip(headers,row_values))
            table_data.append(row_dict)

    return table_data


def test():
    with connection.get_db(DB_PATH) as conn:  # type: ignore
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT url, filepath
            FROM scrape_sessions
            WHERE race_id = ?;
            """,
            (1047,)
        )
        output = cursor.fetchall()

    sessions = []
    for row in output:
        url = row[0]
        filepath = row[1]
        sessions.append((url, filepath))

    for session in sessions:
        html = fm.load_html_file(filepath=session[1])
        results = get_results(soup=html)
        #print(session[0])
        #pprint(results)

#test()