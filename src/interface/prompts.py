from datetime import datetime
from rich import print
import os
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt
from config.config import DB_PATH, LOG_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, DB_DIR  # Assuming these import paths

def print_welcome_message():
    print("[b i yellow]======= F1 DATA SCRAPER =======[/b i yellow]\n")
    _print_small_info()

# more info on paths and stuff
def _print_big_info():
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
    
    while True:
        # IntPrompt automatically forces the user to input a valid integer
        start_year = IntPrompt.ask(f"Enter Start Year (1950 -> {CURRENT_YEAR})")
        
        if start_year < 1950 or start_year > CURRENT_YEAR:
            print(f"[red]❌ Error: Formula 1 started in 1950. Please choose between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        end_year = IntPrompt.ask(f"Enter End Year ({start_year} -> {CURRENT_YEAR})")
        
        if end_year < 1950 or end_year > CURRENT_YEAR:
            print(f"[red]❌ Error: End year must be between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        # Cross-validation: End year must be greater than or equal to start year
        if start_year > end_year:
            print(f"[bold red]❌ Validation Error:[/bold red] Start year ({start_year}) cannot be after End year ({end_year})!")
            continue
            
        # If all checks pass, break the validation loop
        return start_year, end_year
    
def checker_summary(results: list, system_healthy: bool):
    print("\n[i b] ollowing checks have failed:[/i b]")
    if system_healthy:
        colour = "yellow"
        print("[green][/green]")
    else:
        colour = "red"
        print("BAD")
        print(results)
        print(system_healthy)