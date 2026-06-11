import time
import random
from rich.console import Console
from rich.text import Text
from rich.progress import (
    Progress,
    BarColumn,
    TaskProgressColumn,
    TextColumn,
    SpinnerColumn,
    ProgressColumn
)

class TaskTimerColumn(ProgressColumn):
    """A progress column that tracks and permanently freezes elapsed time per task."""
    def render(self, task):
        if "frozen_time" in task.fields:
            duration = task.fields["frozen_time"]
        else:
            duration = task.elapsed if task.elapsed is not None else 0.0
        return Text(f"{duration:0.2f}s", style="dim cyan")


def run_pipeline():
    console = Console()
    
    progress = Progress(
        SpinnerColumn(spinner_name="dots"),              
        TextColumn("[bold red]{task.fields[category]}"), 
        TextColumn("[bold blue]{task.description}"),     
        BarColumn(bar_width=40, complete_style="green", finished_style="bold bright_green"),
        TaskProgressColumn(text_format="[bold magenta]{task.percentage:>3.0f}%[/bold magenta]"),        
        TextColumn("•"),
        TaskTimerColumn(),  
        console=console
    )
    
    url_task = progress.add_task("Fetching Race URLs", total=5, category="[API] ")
    dl_task = progress.add_task("Downloading HTML Pages", total=25, category="[HTTP]")
    db_task = progress.add_task("Writing to Database", total=25, category="[SQL] ")

    with progress:
        while not progress.finished:
            # --- PHASE 1: Fetching URLs ---
            if not progress.tasks[url_task].finished:
                time.sleep(0.4)
                progress.advance(url_task, advance=1)
                
                if progress.tasks[url_task].finished:
                    progress.update(
                        url_task, 
                        description="[strike green]All URLs Fetched[/strike green]",
                        frozen_time=progress.tasks[url_task].elapsed
                    )
            
            # --- PHASE 2 & 3: Downloading & Writing ---
            else:
                # Handle Downloading
                if not progress.tasks[dl_task].finished:
                    time.sleep(random.uniform(0.05, 0.2))
                    progress.advance(dl_task, advance=1)
                    
                    # FIX: Cross off and freeze the downloader when done
                    if progress.tasks[dl_task].finished:
                        progress.update(
                            dl_task, 
                            description="[strike green]All HTML Pages Downloaded[/strike green]",
                            frozen_time=progress.tasks[dl_task].elapsed
                        )
                        
                    if progress.tasks[dl_task].completed > progress.tasks[db_task].completed + 2:
                        progress.advance(db_task, advance=1)
                        
                # Handle Database Writing (catching up at the end)
                elif not progress.tasks[db_task].finished:
                    time.sleep(0.1)
                    progress.advance(db_task, advance=1)
                    
                    # FIX: Cross off and freeze the database writer when done
                    if progress.tasks[db_task].finished:
                        progress.update(
                            db_task, 
                            description="[strike green]All Data Written to Database[/strike green]",
                            frozen_time=progress.tasks[db_task].elapsed
                        )

run_pipeline()