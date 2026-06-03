from pathlib import PurePosixPath
from urllib.parse import urlparse

""" 
this gets the race id from the url e.g.:
- https://www.formula1.com/en/results/2026/races/1279/australia/race-result
becomes
- 1279

"""

def from_url(url: str) -> int | None:
    path = PurePosixPath(urlparse(url).path)
    try:
        races_index = path.parts.index('races')
        race_id = path.parts[races_index + 1]
        return int(race_id)
    except ValueError:
        print("'races' not found in URL structure")
        race_id = None # None is essentially NULL
        return race_id
    
def from_db():
    # maybe a tool needed to extract a race id given some parameters. Will use SQL
    pass