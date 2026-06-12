# main.py
import time
from interface.progress_mngr import create_shared_progress
from modules.workers import backup_database, upload_logs

def run_application():
    # Step 1: Get our progress bar configuration
    progress = create_shared_progress()
    
    # Step 2: Start the progress animation using 'with'
    with progress:
        
        # Step 3: Define our overarching main task. 
        # It has a total of 2 steps (1. Backup, 2. Upload)
        main_task = progress.add_task("[green]Total Project Progress", total=2)
        
        # --- Run Helper Function 1 ---
        # We pass 'progress' and 'main_task' so the function can talk back to main.py
        backup_database(progress, main_task)
        
        # --- Run Helper Function 2 ---
        upload_logs(progress, main_task)

if __name__ == "__main__":
    run_application()