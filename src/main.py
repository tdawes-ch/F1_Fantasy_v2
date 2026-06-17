"""
get html data for year -> 
extract races for each year -> 
get html data for each session in each weekend (log too) -> 
convert html data into csv -> 
put csv into database -> 
perform calculations for f1 fantasy team.
"""
from database import init_db
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_PATH
from pipelines import get_all_races, get_race_data, get_session_data, get_all_results, setup_checker
from interface.progress_manager import get_progress_bar
from rich.console import Console
from interface import prompts
from processing.migration import scrape_to_race
import sys
from logging_utils.logger_config import setup_logging

# setting up console thing
console = Console()
# set up logger file

def main():
    # setup logs
    setup_logging()

    prompts.print_welcome_message()
    
    ## do the setup and checks
    console.print(f"[b]Running initialisation checks:[/b]")
    checker = setup_checker.SetupChecker()
    with get_progress_bar() as setup_progress:
        # Set up the database!!
        db_task = setup_progress.add_task("Initialising database...", total=None)
        init_db.init_db(db_path=DB_PATH)
        setup_progress.remove_task(db_task)

        # Now do checks
        setup_task = setup_progress.add_task("Running setup checks...",total=len(checker.checks))

        # this gets passed into SetupChecker.run_all()
        def update_ui(description: str):
            setup_progress.update(setup_task, description=f"Checking: [yellow]{description}[/yellow]")
            setup_progress.advance(setup_task)

        results, system_healthy = checker.run_all(on_progress_step=update_ui)
        all_passed = all(r.passed for r in checker.results)

        if all_passed and system_healthy:
            setup_progress.update(setup_task, description=f"[green]Checks complete.[/green]")
        elif not system_healthy:
            setup_progress.update(setup_task, description=f"[red]Checks complete.[/red]")
        else:
            setup_progress.update(setup_task, description=f"[yellow]Checks complete.[/yellow]")

    if not all_passed:
        prompts.checker_summary(results, system_healthy)
            
    base_url = "https://www.formula1.com/en/results/{fyear}/races"
    print()

    start_year, end_year = prompts.get_valid_years()
    num_seasons = end_year + 1 - start_year
    
    console.print(f"\nPreparing to scrape {num_seasons} season(s)...\n")
    # get races from each year
    with get_progress_bar() as year_progress:
        console.print(f"Getting and processing the {num_seasons} season overview page(s):")
        get_all_races.run(start_year,end_year,base_url,year_progress)

    
    # get the race html and extract info
    with get_progress_bar() as race_progress:
        console.print(f"\nGetting and processing individual races:")
        get_race_data.run(start_year,end_year,race_progress,flag='db')

    with get_progress_bar() as session_progress:
        console.print(f"\nGetting and processing individual race sessions:")
        # get_session_data.run(start_year,end_year,session_progress)

    with get_progress_bar() as migration_progress:
        console.print(f"\nCopying data from scraped tables to race tables:")
        scrape_to_race.migrate_all(progress=migration_progress)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # This block catches the Ctrl+C instantly
        console.print("\n\n[bold red]🛑  Program cancelled by user (Ctrl+C).[/bold red]")
        console.print("[yellow]⚠️   Disconnecting from DB and exiting...[/yellow]")
        
        # Explicitly close any global resources here if needed (e.g., db.close())
        
        # Cleanly terminate the Python process with exit code 0 (Success/Clean Exit)
        sys.exit(0)