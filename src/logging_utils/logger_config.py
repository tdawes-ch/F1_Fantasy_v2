from datetime import datetime
import logging
from pathlib import Path

# Assuming your config has a Path object for LOG_DIR
# If LOG_DIR is a string, wrap it in Path(LOG_DIR)
from config.config import LOG_DIR 

def setup_logging():
    # 1. Ensure the log directory actually exists on disk
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 2. Generate a unique timestamp string for this specific run
    # Format: runtime_17_06_2026_160530.log
    timestamp = datetime.now().strftime("%d_%m_%Y_%H%M%S")
    log_filename = f"runtime_{timestamp}.log"
    
    # 3. Combine the directory path with the dynamic file name
    full_log_path = LOG_DIR / log_filename

    # 4. Initialize the logging config with our dynamic path
    logging.basicConfig(
        level=logging.INFO,
        filename=full_log_path,
        filemode="w",  # "w" is perfect here since the filename is unique to this run
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )