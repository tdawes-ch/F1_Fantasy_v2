import os
import pandas as pd
import fastf1

# 1. Safe Cache Setup
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# 2. Define our target data parameters
YEAR = 2025
LOCATION = 'Silverstone'
DRIVER = 'HAM'
# Suffix identifiers for all standard weekend sessions
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'R']

# List to store processed rows before compilation
table_rows = []

print(f"Fetching 2026 {LOCATION} data for {DRIVER}...")

# 3. Iterate through each track session
for session_id in SESSIONS:
    try:
        # Load the individual weekend session
        session = fastf1.get_session(YEAR, LOCATION, session_id)
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        
        # Filter down specifically to Hamilton's representative timed laps
        driver_laps = session.laps.pick_drivers(DRIVER).pick_quicklaps()
        
        if driver_laps.empty:
            continue
            
        # Group by the tire compound and compute average lap time
        grouped = driver_laps.groupby('Compound')
        for compound, group in grouped:
            # Calculate mean lap time (FastF1 stores lap times as Timedeltas)
            mean_timedelta = group['LapTime'].mean()
            
            # Format the timedeltas nicely into 'MM:SS.ms'
            total_seconds = mean_timedelta.total_seconds()
            minutes = int(total_seconds // 60)
            seconds = total_seconds % 60
            formatted_pace = f"{minutes}:{seconds:06.3f}"
            
            # Record our metrics
            table_rows.append({
                "Session": session_id,
                "Compound": compound,
                "Average Pace": formatted_pace,
                "Laps Measured": len(group)
            })
            
    except Exception as e:
        # Fallback handle if a session isn't available or fails to initialize
        print(f"Could not load session {session_id}: {e}")

# 4. Convert gathered records into a cleanly presented table
df = pd.DataFrame(table_rows)

# Create a clear hierarchy structure by grouping headings visually
df.set_index(['Session', 'Compound'], inplace=True)

print("\n================ HAMILTON PACE ANALYSIS ================")
print(df)
print("========================================================")