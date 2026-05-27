import logging
from pathlib import Path
from datetime import datetime
from config.config import LOG_DIR

"""
Is used to create the log files used for debugging. It creates one log file every time the program is run.
"""

def get_log_file():
    # Creates log file path
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return Path(LOG_DIR) / f"runtime_{timestamp}.log"

print(get_log_file())

def setup_logger():
    ...