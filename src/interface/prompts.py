from datetime import datetime
from rich import print
import os
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt
from config.config import DB_PATH, LOG_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_DIR, FANTASY_PROCESSED_DIR, FANTASY_RAW_DIR  # Assuming these import paths

def print_welcome_message():
    """Prints a welcome message for the program
    """
    print("[b i yellow]========== F1 DATA SCRAPER ==========[/b i yellow]\n")
    _print_small_info()

# more info on paths and stuff
def _print_big_info():
    """Prints the session info to the console in the form of a table. More verbose than print_small_info
    """
    # 1. Initialize table
    table = Table.grid(expand=True)
    table.add_column(style="cyan", justify="left", width=20)   # Category Labels
    table.add_column(style="white", justify="left")            # Variable Data

    # 2. Basic info
    table.add_row("Version:", "v0.0.1")
    table.add_row("Author:", "Thomas Dawes")
    
    table.add_row("", "")  # spacer

    # get database size
    if DB_PATH.exists():
        db_size_bytes = os.path.getsize(DB_PATH)
        db_size_readable = f"{db_size_bytes / (1024 * 1024):.2f} MB" if db_size_bytes > 1024*1024 else f"{db_size_bytes / 1024:.1f} KB"
    else:
        db_size_readable = "[red]Not yet initialized[/red]"

    # 3. print important locations
    table.add_row("Database File:", f"[yellow]{DB_PATH.name}[/yellow] - {db_size_readable}")
    table.add_row("Database Path:", f"[i dim]{DB_DIR}[/i dim]")
    table.add_row("Log Directory:", f"[i dim]{LOG_DIR}[/i dim]")
    table.add_row("Raw HTML Directory:", f"[i dim]{RAW_DATA_DIR}[/i dim]")
    table.add_row("Processed CSV Directory:", f"[i dim]{PROCESSED_DATA_DIR}[/i dim]")
    table.add_row("Raw Fantasy Data:", f"[i dim]{FANTASY_RAW_DIR}[/i dim]")
    table.add_row("Processed Fantasy Data:", f"[i dim]{FANTASY_PROCESSED_DIR}[/i dim]")

    table.add_row("", "")  # Visual Spacer line

    # 4. Add current Session timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table.add_row("Session Started:", f"[magenta]{current_time}[/magenta]")

    # 5. Wrap the grid neatly inside a styled Rich Panel frame
    print(Panel(
        table, 
        #title="[bold white]Welcome[/bold white]", 
        #title_align="left",
        border_style="gray37",
        padding=(1, 2)
    ))
    print()  # Final trailing newline for padding

# just basic initialisation information
def _print_small_info():
    """Prints the session info to the console in the form of a table. Less verbose than print_big_info
    """
    # 1. Initialize table
    table = Table.grid()
    table.add_column(style="cyan", justify="left", width=20)   # Category Labels
    table.add_column(style="white", justify="left")            # Variable Data

    # 2. Basic info
    table.add_row("Version:", "v0.0.1")
    table.add_row("Author:", "Thomas Dawes")

    # get database size
    if DB_PATH.exists():
        db_size_bytes = os.path.getsize(DB_PATH)
        db_size_readable = f"{db_size_bytes / (1024 * 1024):.2f} MB" if db_size_bytes > 1024*1024 else f"{db_size_bytes / 1024:.1f} KB"
    else:
        db_size_readable = "[red]Not yet initialized[/red]"

    # 3. print important locations
    table.add_row("Database File:", f"[yellow]{DB_PATH.name}[/yellow] - {db_size_readable} [i dim]({DB_DIR})[/i dim]")

    # 5. Wrap the grid neatly inside a styled Rich Panel frame
    print(Panel(
        table, 
        border_style="gray37",
        padding=(1, 2)
    ))
    print()  # Final trailing newline for padding

def get_valid_years() -> tuple[int, int]:
    """
    Asks the user for start and end years with strict validation boundaries.
    """
    CURRENT_YEAR = int(datetime.now().strftime("%Y"))  # Setting current calendar context
    print("[b]Let's get scraping![/b]")
    
    while True:
        # IntPrompt automatically forces the user to input a valid integer
        start_year = IntPrompt.ask(f"  Enter Start Year (1950 -> {CURRENT_YEAR})")
        
        if start_year < 1950 or start_year > CURRENT_YEAR:
            print(f"  [red]❌ Error: Formula 1 started in 1950. Please choose between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        end_year = IntPrompt.ask(f"  Enter End Year ({start_year} -> {CURRENT_YEAR})")
        
        if end_year < 1950 or end_year > CURRENT_YEAR:
            print(f"  [red]❌ Error: End year must be between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        # Cross-validation: End year must be greater than or equal to start year
        if start_year > end_year:
            print(f"  [bold red]❌ Validation Error:[/bold red] Start year ({start_year}) cannot be after End year ({end_year})!")
            continue
            
        # If all checks pass, break the validation loop
        return start_year, end_year
    
def checker_summary(results: list, system_healthy: bool):
    """Prints a summary of the checks that have been completed

    Args:
        results (list): The checks
        system_healthy (bool): Whether the system is healthy or critical
    """
    print("\n  [b]The following checks have failed:[/b]")
    

    for result in results:
        if result.critical:
            colour = "red"
        else:
            colour = "yellow"
        if not result.passed:
            print(f"  - [{colour}][b]{result.description}:[/b] '{result.error}'[/{colour}]")

def network_status(network_results: dict):
    """Prints network status from network results

    Args:
        network_results (dict): Network results 
    """
    if network_results["error"] is None:
        print(f"   [green]Results:[/green]")
        print(f"    ├ [i yellow]{round(network_results["bytes_downloaded"]/ 1024 / 1024, 2)} MB [/i yellow]downloaded in [green]{round(network_results["duration_seconds"],2)}[/green] seconds.")
        print(f"    └─ Network speed: [bold cyan]{network_results["mbps"]}[/bold cyan] mbps / [cyan]{network_results["mb_per_sec"]}[/cyan] MB/s")
    else:
        print(f"[red]Speedtest failed: {network_results["error"]}[/red]")

def announce_offline_mode(error: Exception | None):
    """Announces offline mode

    Args:
        error (Exception | None): _description_
    """
    print(f"[b i]\nNetwork check has failed. Offline mode only.[/b i]")
    if error is not None:
        print(f"Network error: [dim]{error}[/dim]")
    else:
        print(f"Network error: [dim]unknown[/dim]")

def starting_switchboard(network_status: bool):
    """Displays the online or offline options
    Online: (1. Scrape data (Full, Recent (Most recent race / Most recent year)),
             2. Use current data (Check: Thorough/Quick),
             3. Quit)
    Offline: (1. Use current data (Check: Thorough/Quick),
              2. Quit)

    Args:
        network_status (bool): The current network status

    Returns:
        response: The user's response
    """
    online_options = ["Scrape data from F1 website",
                      "Continue with existing data",
                      "Quit"]
    offline_options = ["Continue with existing data",
                       "Quit"]

    if network_status:
        options = online_options
    else:
        options = offline_options
        
    for i, prompt in enumerate(options):
        print(f"{i+1}. {prompt}")

    user_choice = IntPrompt.ask("Enter option")
    while user_choice not in range(1, len(options)+1):
        user_choice = IntPrompt.ask(f"[i red]Invalid input![/i red]\nPlease enter value from {1} to {len(options)}.\nEnter option")
    else:
        print(f"You've picked: {options[int(user_choice)-1]}")
    
#starting_switchboard(True)
def scrape_anyway(message: str = ""):
    user_choice = input(f"Data already exists. {message}\nScrape anyway? (Y/N): ").lower()
    while user_choice not in ["y","n"]:
        user_choice = input(f"Invalid input.\nScrape anyway? (Y/N): ").lower()

    match user_choice:
        case "y":
            return True
        case "n": 
            return False