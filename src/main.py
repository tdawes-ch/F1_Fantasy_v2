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
from pipelines import setup_checker, online_mode
from interface.progress_manager import get_progress_bar
from rich.console import Console
from rich import print
from interface import prompts
from pipelines.get_data import get_all_races, get_all_results, get_race_data, get_session_data, get_fantasy_prices
from processing.migration import scrape_to_race
import sys
from logging_utils.logger_config import setup_logging
from toolbox import network
from datetime import datetime
from datetime import datetime
from pipelines import offline_mode, online_mode

# setting up console thing
console = Console()

def _def_check_offline_mode(results: list):
    pass

def main():
    offline_only = False
    start_time = datetime.now()
    print(f"[b]Start Time:[/b] {start_time}")
    # setup logs
    setup_logging()

    prompts.print_welcome_message()
    
    ## do the setup and checks
    console.print(f"[b]Running initialisation checks:[/b]")
    checker = setup_checker.SetupChecker()
    with get_progress_bar() as setup_progress:
        # Set up the database!!
        db_task = setup_progress.add_task("Initialising database...", total=None)

        try:
            init_db.init_db(db_path=DB_PATH)
            setup_progress.remove_task(db_task)
        except Exception as e:
            setup_progress.remove_task(db_task)
            print(f"\n[b i]Error occurred when setting up database:[/b i][red]\n{e}[/red]")

    
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
        ## Checks are now complete!

    if not all_passed:
        prompts.checker_summary(results, system_healthy)
        # need a way of checking individual errors to determine what to do next.
        # check network
        # if network not ok
            # if no data in table,
                # need data!!
            # else show limits of data (e.g. only got data from x to y years)
    network_check, network_error = checker.did_check_pass("network")    
    offline_only = not(network_check)

    if not(offline_only):
        console.print("Network test passed! 🎉")
        do_check = prompts.ask_options(question="[b]Run speedtest?[/b]",
                                       options=["Yes", "No"])
        if do_check == 1:
        # Network Status:
            console.print("\n[b]Running network test:[/b]")
            with get_progress_bar() as network_test:
                network_task = network_test.add_task("Running network speedtest...", total=1)
                stats = network.avg_download_speed(attempts=10)
                if stats["error"] is None:
                    network_test.update(network_task, description=f"[green]Speedtest complete.[/green]",completed=1)
                else:
                    network_test.update(network_task, description=f"[yellow]Changing server and re-running...[/yellow]")
                    stats = network.run_speedtest()
                    if stats["error"] is None:
                        network_test.update(network_task, description=f"[green]Speedtest complete.[/green]",completed=1)
                    else:
                        network_test.update(network_task, description=f"[red]Speedtest complete.[/red]")
            prompts.network_status(stats)
    else:
        prompts.announce_offline_mode(network_error)

    offline_mode.run() if offline_only else online_mode.run()  
            
    start_year, end_year = prompts.get_valid_years()
    online_mode.run_scraping(start_year, end_year)
    
    # here marks the end of all scraping ^ now onto processing v

    with get_progress_bar() as migration_progress:
        console.print(f"[b]\nCopying data from scraped tables to race tables:[/b]")
        scrape_to_race.migrate_all(progress=migration_progress, db_path=DB_PATH, update=False)

    with get_progress_bar() as results_progress:
        console.print(f"[b]\nCollecting results from sessions:[/b]")
        get_all_results.run(start_year, end_year, results_progress)

    end_time = datetime.now()
    message = f"\n[b]End Time:[/b] {end_time}"
    print()
    print("="*40)
    print(message)
    print(f"\n[b]Time to process {end_year-start_year+1} seasons:[/b] {end_time-start_time}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # This block catches the Ctrl+C instantly
        console.print("\n\n[bold red]🛑  Program cancelled by user (Ctrl+C).[/bold red]")
        console.print("[yellow]⚠️   Disconnecting from DB and exiting...[/yellow]")
        
        # Cleanly terminate the Python process with exit code 0 (Success/Clean Exit)
        sys.exit(0)