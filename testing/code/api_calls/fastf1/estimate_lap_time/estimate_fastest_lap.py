import os
import pandas as pd
import fastf1

# 1. Setup Caching
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

YEAR = 2025
LOCATION = 'Silverstone'
DRIVER = 'HAM'

# Storage for the absolute minimum times achieved in practice
best_s1 = pd.Timedelta.max
best_s2 = pd.Timedelta.max
best_s3 = pd.Timedelta.max

# 2. Extract peak data across all Practice Sessions
for practice in ['FP1', 'FP2', 'FP3']:
    try:
        session = fastf1.get_session(YEAR, LOCATION, practice)
        session.load(laps=True, telemetry=False, weather=False, messages=False)
        
        # Isolate clean, fast laps on Soft tyres to simulate Qualy compound conditions
        p_laps = session.laps.pick_drivers(DRIVER).pick_quicklaps()
        soft_laps = p_laps[p_laps['Compound'] == 'SOFT']
        
        if not soft_laps.empty:
            # Continually update our micro-bests if a faster sector is found
            best_s1 = min(best_s1, soft_laps['Sector1Time'].min())
            best_s2 = min(best_s2, soft_laps['Sector2Time'].min())
            best_s3 = min(best_s3, soft_laps['Sector3Time'].min())
            
    except Exception as e:
        print(f"Skipping {practice}: {e}")

# Calculate the compiled ideal combination lap
theoretical_practice_best = best_s1 + best_s2 + best_s3

# 3. Load actual Qualifying session to compare
quali = fastf1.get_session(YEAR, LOCATION, 'Q')
quali.load(laps=True, telemetry=False, weather=False, messages=False)
actual_quali_best = quali.laps.pick_drivers(DRIVER).pick_fastest()['LapTime']

# 4. Helper function to make Timedeltas human-readable
def format_time(td):
    total_secs = td.total_seconds()
    return f"{int(total_secs // 60)}:{total_secs % 60:06.3f}"

# 5. Output Comparison Matrix
print(f"\n===== QUALIFYING PREDICTION ANALYSIS: {DRIVER} =====")
print(f"Theoretical Practice Best: {format_time(theoretical_practice_best)}")
print(f"Actual Qualifying Time:    {format_time(actual_quali_best)}")

delta = actual_quali_best - theoretical_practice_best
if delta.total_seconds() < 0:
    print(f"Result: Driver found track evolution! Went {abs(delta.total_seconds()):.3f}s faster than practice potential.")
else:
    print(f"Result: Driver left {delta.total_seconds():.3f}s on the table relative to peak practice sectors.")
print("==================================================")