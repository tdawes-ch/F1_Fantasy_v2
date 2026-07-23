from interface import prompts

# separate file for offline functions?

## first check the database. Return list of years and their current status e.g. 2020, has all results; 2021, only partial results

def check_for_db_data(start_year: int, end_year: int) -> bool:
    return True

# If there's no data, check for html or csv files?
def check_for_csv_data(start_year: int, end_year: int) -> bool:
    return True

def run():
    offline_options = ["Continue with existing data",
                       "Quit"]
    user_choice = prompts.ask_options(options=offline_options, 
                                      question="How would you like to continue?",
                                      confirm=True)
    match user_choice:
        case 1:
            print("gonna check existing data")
        case 2:
            print("gonna quit")
        case _:
            raise ValueError("Unknown choice from prompts.ask_options. Unsure on how this happened...")
    
    
    # present options: 1. check existing data, 2. scrape [overwrite, add]
    pass

## if there's literally nothing, then we should quit
## if there's sufficient data, we can do some processing, but idk what yet
