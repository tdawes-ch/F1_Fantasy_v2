from rich.console import Console
from rich.prompt import IntPrompt
import datetime

console = Console()

def print_welcome_message():
    console.print("======= F1 DATA SCRAPER =======\n", style="blink yellow")

def get_valid_years() -> tuple[int, int]:
    """
    Asks the user for start and end years with strict validation boundaries.
    """
    CURRENT_YEAR = int(datetime.datetime.now().strftime("%Y"))  # Setting current calendar context
    
    while True:
        # IntPrompt automatically forces the user to input a valid integer
        start_year = IntPrompt.ask(f"Enter Start Year (1950 - {CURRENT_YEAR})")
        
        if start_year < 1950 or start_year > CURRENT_YEAR:
            console.print(f"[red]❌ Error: Formula 1 started in 1950. Please choose between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        end_year = IntPrompt.ask(f"Enter End Year ({start_year} - {CURRENT_YEAR})")
        
        if end_year < 1950 or end_year > CURRENT_YEAR:
            console.print(f"[red]❌ Error: End year must be between 1950 and {CURRENT_YEAR}.[/red]")
            continue
            
        # Cross-validation: End year must be greater than or equal to start year
        if start_year > end_year:
            console.print(f"[bold red]❌ Validation Error:[/bold red] Start year ({start_year}) cannot be after End year ({end_year})!")
            continue
            
        # If all checks pass, break the validation loop
        return start_year, end_year