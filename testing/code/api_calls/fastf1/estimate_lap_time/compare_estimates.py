import os
import sys
import time
import threading
import pandas as pd
import numpy as np
import fastf1

# 1. Silence log spam completely
fastf1.set_log_level('WARNING')

class LoadingSpinner:
    """A clean, console-friendly background loading animator."""
    def __init__(self, message="Loading F1 Data..."):
        self.message = message
        self.spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.stop_running = False
        self.thread = None

    def _animate(self):
        idx = 0
        while not self.stop_running:
            sys.stdout.write(f"\r{self.spinner[idx]} {self.message}")
            sys.stdout.flush()
            idx = (idx + 1) % len(self.spinner)
            time.sleep(0.08)
        sys.stdout.write("\r" + " " * (len(self.message) + 4) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self.stop_running = False
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_running = True
        if self.thread:
            self.thread.join()

def format_laptime(seconds):
    """Formats a float time in seconds into MM:SS.fff"""
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"

def format_delta(delta_seconds):
    """Formats time differences cleanly with +/- signs"""
    sign = "+" if delta_seconds >= 0 else "-"
    return f"({sign}{abs(delta_seconds):.3f}s)"

def main():
    # Setup cache directory
    cache_dir = './f1_cache'
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    fastf1.Cache.enable_cache(cache_dir)

    # Change these config parameters to target any driver/track
    YEAR = 2026
    GP = 'Barcelona'
    DRIVER = 'LEC'

    best_practice_time = float('inf')
    best_practice_lap = None

    # 2. Extract practice records inside spinner visual
    with LoadingSpinner(f"Processing FP1, FP2, and FP3 telemetry for {DRIVER}..."):
        for p_sess in ['FP1', 'FP2', 'FP3']:
            try:
                session = fastf1.get_session(YEAR, GP, p_sess)
                session.load(telemetry=True, weather=False)
                
                # Filter out slow out-laps and isolate driver
                laps = session.laps.pick_quicklaps().pick_drivers(DRIVER)
                if len(laps) == 0:
                    continue
                
                fastest_lap = laps.pick_fastest()
                if fastest_lap is not None and not pd.isna(fastest_lap['LapTime']):
                    lap_time_secs = fastest_lap['LapTime'].total_seconds()
                    if lap_time_secs < best_practice_time:
                        best_practice_time = lap_time_secs
                        best_practice_lap = fastest_lap
            except Exception:
                continue

    if best_practice_lap is None:
        print("Error: Could not retrieve any practice lap data.")
        return

    # 3. Process Qualifying Session inside spinner visual
    with LoadingSpinner(f"Retrieving Qualifying data for {DRIVER}..."):
        try:
            q_session = fastf1.get_session(YEAR, GP, 'Q')
            q_session.load(telemetry=False, weather=False)
            q_lap = q_session.laps.pick_quicklaps().pick_drivers(DRIVER).pick_fastest()
            qualy_lap_time = q_lap['LapTime'].total_seconds() if q_lap is not None else None
        except Exception:
            qualy_lap_time = None

    # 4. Math: Theoretical Sector Combinations (Standard S1 + S2 + S3)
    s1 = best_practice_lap['Sector1Time'].total_seconds()
    s2 = best_practice_lap['Sector2Time'].total_seconds()
    s3 = best_practice_lap['Sector3Time'].total_seconds()
    sector_lap_time = s1 + s2 + s3 

    # 5. Math: Theoretical Micro-Sectors (Split telemetry into 20 distance chunks)
    telemetry = best_practice_lap.get_telemetry()
    num_micro_sectors = 10
    total_distance = telemetry['Distance'].max()
    micro_sector_edges = np.linspace(0, total_distance, num_micro_sectors + 1)
    
    micro_sector_times = []
    for i in range(num_micro_sectors):
        start_dist = micro_sector_edges[i]
        end_dist = micro_sector_edges[i+1]
        
        chunk = telemetry[(telemetry['Distance'] >= start_dist) & (telemetry['Distance'] < end_dist)]
        if not chunk.empty:
            chunk_time = chunk['Time'].dt.total_seconds().max() - chunk['Time'].dt.total_seconds().min()
            micro_sector_times.append(chunk_time)
            
    micro_sector_lap_time = sum(micro_sector_times)

    # 6. Sequential Deltas Calculations
    diff_sectors_to_practice = sector_lap_time - best_practice_time 
    diff_micro_to_sectors = micro_sector_lap_time - sector_lap_time
    diff_qualy_to_micro = (qualy_lap_time - micro_sector_lap_time) if qualy_lap_time else 0.0

    # 7. Print the final strict block layout requested
    print(f"Fastest lap across practice: {format_laptime(best_practice_time)}")
    print(f"fastest lap comparing sectors: {format_laptime(sector_lap_time)} {format_delta(diff_sectors_to_practice)}")
    print(f"fastest lap comparing micro sectors: {format_laptime(micro_sector_lap_time)} {format_delta(diff_micro_to_sectors)}")
    if qualy_lap_time:
        print(f"fastest lap in qualy: {format_laptime(qualy_lap_time)} {format_delta(diff_qualy_to_micro)}")
    else:
        print("fastest lap in qualy: Data Unavailable")

if __name__ == "__main__":
    main()