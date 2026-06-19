import os
import fastf1

# 1. Name your cache folder
cache_dir = 'f1_cache'

# 2. Automatically create the folder if it doesn't exist yet
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

# 3. Now enable the cache safely
fastf1.Cache.enable_cache(cache_dir)

# Your session code will work perfectly now!
session = fastf1.get_session(2026, 'Monaco', 'Q')
session.load()

# FastF1 automatically finds the fastest lap and extracts the telemetry DataFrame
fastest_lap = session.laps.pick_fastest()
telemetry = fastest_lap.get_telemetry()

print(telemetry[['X', 'Y', 'Speed', 'Throttle']])