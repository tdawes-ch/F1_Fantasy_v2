# src/interface/progress_mngr.py
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

def create_shared_progress():
    """Configures and returns a basic Rich progress bar."""
    return Progress(
        TextColumn("[bold blue]{task.description}"), # Shows the text we give it
        BarColumn(),                                 # Shows the visual bar
        TaskProgressColumn(),                        # Shows the percentage %
    )