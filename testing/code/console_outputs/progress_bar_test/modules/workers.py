# src/modules/workers.py
import time

def backup_database(progress, main_task):
    """Simulates backing up a database."""
    # 1. Create a temporary sub-bar just for this function
    sub_task = progress.add_task(" -> Copying tables...", total=4)
    
    for i in range(4):
        time.sleep(0.3) # Simulate backing up a table
        progress.advance(sub_task, 1) # Advance the sub-bar by 1
        
    # 2. When this helper function is completely done, advance the MAIN bar by 1
    progress.advance(main_task, 1)


def upload_logs(progress, main_task):
    """Simulates uploading log files."""
    # 1. Create a temporary sub-bar just for this function
    sub_task = progress.add_task(" -> Uploading log chunks...", total=3)
    
    for i in range(3):
        time.sleep(0.4) # Simulate uploading a log file
        progress.advance(sub_task, 1) # Advance the sub-bar by 1
        
    # 2. When this helper function is completely done, advance the MAIN bar by 1
    progress.advance(main_task, 1)