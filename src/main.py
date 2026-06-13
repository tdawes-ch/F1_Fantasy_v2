"""
get html data for year -> 
extract races for each year -> 
get html data for each session in each weekend (log too) -> 
convert html data into csv -> 
put csv into database -> 
perform calculations for f1 fantasy team.
"""
from database import init_db
from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from pipelines import get_all_races, get_race_data, get_session_data, get_all_results, setup_checker
from interface.progress_manager import get_progress_bar
from rich.console import Console
from interface import prompts
from processing.migration import scrape_to_race
import sys

console = Console()

def main():
    prompts.print_welcome_message()

    ## do the setup and checks
    with get_progress_bar() as setup_progress:
        # Set up the database!!
        db_task = setup_progress.add_task("Initialising database", total=None)
        init_db.init_db()
        setup_progress.remove_task(db_task)

        # Now do checks for the following:
        """
            "locations": False,
            "files": False,
            "db": False,
            "random_db_path": False,
            "network": False
        """
        check_task = setup_progress.add_task("Performing check:", total=None)
        all_checks, all_errors = setup_checker.do_checks(setup_progress, task_id=check_task)

        # if checks failed:
        if not all(all_checks.values()):
            # do failed checks stuff
            if not all_checks["db"]:
                if len(all_errors)-1 == 0:
                    setup_progress.update(check_task, description=f"[green]✓ Checks completed.\n[i][b]Note:[/b] Database needs populating.[/i][/green]")
                else:
                    setup_progress.update(check_task, description=f"[red]⚠️   Checks completed, [bold red]{len(all_errors)} error(s).[/bold red][/red]")
            else:
                setup_progress.update(check_task, description=f"[red]⚠️   Checks completed, [bold red]{len(all_errors)} error(s).[/bold red][/red]")
        else:
            setup_progress.update(check_task, description=f"[green]✓ Checks completed[/green]")
    
    if all_errors:
        if all_checks["db"]:
            console.print(f"\n[u]{len(all_errors)} error(s) found:[/u]")
            for error in all_errors:
                console.print(f"- {error}")
            console.print("[b i red]Please rectify errors before running.[/b i red]")
            sys.exit(0)

            
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