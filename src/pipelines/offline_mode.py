# separate file for offline functions?

## first check the database. Return list of years and their current status e.g. 2020, has all results; 2021, only partial results

def check_for_db_data(start_year: int, end_year: int) -> bool:
    return True

# If there's no data, check for html or csv files?
def check_for_csv_data(start_year: int, end_year: int) -> bool:
    return True

## if there's literally nothing, then we should quit
## if there's sufficient data, we can do some processing, but idk what yet
