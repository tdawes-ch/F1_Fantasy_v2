from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    MofNCompleteColumn
)
from config.config import SHOW_PROGRESS_BARS  # Import our toggle from config

# spinner types: https://pypi.org/project/rich/ https://pypi-camo.freetls.fastly.net/bb28a7def0f690e774f903c8176d331377826fd6/68747470733a2f2f6769746875622e636f6d2f7465787475616c697a652f726963682f7261772f6d61737465722f696d67732f7370696e6e6572732e676966

def get_progress_bar():
    """
    Factory function to configure and return a custom Rich Progress instance.
    """
    # Define custom columns
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),                 
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        MofNCompleteColumn(), # Shows "1/3" instead of just percentages
        TaskProgressColumn(), # Shows percentage (e.g., 50%)
        TimeElapsedColumn(), # Shows estimated time left
        disable=not SHOW_PROGRESS_BARS  # True turns off the bars completely
    )