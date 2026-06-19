import os
import sys
import time
import threading
import numpy as np
import pandas as pd
import fastf1

# =========================
# CONFIG
# =========================
YEAR = 2026
GP = 'Barcelona'
NUM_MICROSECTORS = 25

# =========================
# FASTF1 SETUP
# =========================
fastf1.set_log_level('WARNING')

CACHE_DIR = "./f1_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)


# =========================
# LOADING SPINNER
# =========================
class LoadingSpinner:
    def __init__(self, message="Loading..."):
        self.message = message
        self.spinner = ['|', '/', '-', '\\']
        self.running = False
        self.thread = None

    def spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r{self.message} {self.spinner[i % 4]}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def __enter__(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.thread.join()
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()


# =========================
# HELPERS
# =========================
def format_time(td):
    if pd.isna(td):
        return "N/A"
    try:
        total = td.total_seconds()
        m = int(total // 60)
        s = int(total % 60)
        ms = int((total - int(total)) * 1000)
        return f"{m:02d}:{s:02d}.{ms:03d}"
    except:
        return "N/A"


def microsector_time(lap, num_bins=25):
    try:
        tel = lap.get_telemetry()

        # Must have GPS data
        if tel is None or tel.empty or "X" not in tel or "Y" not in tel:
            return pd.NaT

        tel = tel.copy()

        # Build incremental track distance from GPS
        dx = tel["X"].diff()
        dy = tel["Y"].diff()

        tel["gps_dist"] = np.sqrt(dx**2 + dy**2)
        tel["gps_dist"].fillna(0, inplace=True)

        tel["track_pos"] = tel["gps_dist"].cumsum()

        if tel["track_pos"].max() == 0:
            return pd.NaT

        # Normalize 0–1
        tel["track_norm"] = tel["track_pos"] / tel["track_pos"].max()

        bins = np.linspace(0, 1, num_bins + 1)
        tel["bin"] = pd.cut(tel["track_norm"], bins=bins, labels=False)

        # Time delta per bin
        tel["time_diff"] = tel["Time"].diff()

        micro = tel.groupby("bin")["time_diff"].sum().sum()

        return micro

    except Exception:
        return pd.NaT


# =========================
# LOAD SESSIONS
# =========================
with LoadingSpinner("Loading FP sessions..."):
    fp1 = fastf1.get_session(YEAR, GP, "FP1")
    fp2 = fastf1.get_session(YEAR, GP, "FP2")
    fp3 = fastf1.get_session(YEAR, GP, "FP3")

    fp1.load()
    fp2.load()
    fp3.load()

with LoadingSpinner("Loading Qualifying..."):
    quali = fastf1.get_session(YEAR, GP, "Q")
    quali.load()


# =========================
# DRIVER LIST
# =========================
drivers = quali.results['Abbreviation'].dropna().unique()


# =========================
# PRACTICE COMBINED SESSION
# =========================
practice_sessions = [fp1, fp2, fp3]


# =========================
# GLOBAL MICRO BIN BASE (FASTEST PRACTICE LAP)
# =========================
all_practice_laps = pd.concat([s.laps for s in practice_sessions])

global_fast_practice = all_practice_laps.pick_accurate().pick_fastest()

if global_fast_practice is not None:
    try:
        tel = global_fast_practice.get_car_data().add_distance()
        max_dist = tel["Distance"].max()
        global_bins = np.linspace(0, max_dist, NUM_MICROSECTORS + 1)
    except:
        global_bins = None
else:
    global_bins = None


# =========================
# MAIN DATA COLLECTION
# =========================
data = {}

for drv in drivers:
    try:
        # -------------------------
        # PRACTICE FASTEST LAP
        # -------------------------
        driver_practice_laps = pd.concat([
            s.laps.pick_drivers(drv).pick_accurate()
            for s in practice_sessions
        ], ignore_index=True)

        fp_fastest = driver_practice_laps.pick_fastest()
        fp_fastest_time = fp_fastest["LapTime"] if fp_fastest is not None else pd.NaT


        # -------------------------
        # PRACTICE THEORETICAL SECTORS
        # -------------------------
        sector_laps = driver_practice_laps.dropna(
            subset=["Sector1Time", "Sector2Time", "Sector3Time"]
        )

        if not sector_laps.empty:
            best_s1 = sector_laps["Sector1Time"].min()
            best_s2 = sector_laps["Sector2Time"].min()
            best_s3 = sector_laps["Sector3Time"].min()
            practice_theoretical = best_s1 + best_s2 + best_s3
        else:
            practice_theoretical = pd.NaT


        # -------------------------
        # MICRO SECTORS (PRACTICE ONLY)
        # -------------------------
        if fp_fastest is not None and global_bins is not None:
            micro = microsector_time(fp_fastest, global_bins)
        else:
            micro = pd.NaT


        # -------------------------
        # QUALIFYING FASTEST LAP
        # -------------------------
        quali_laps = quali.laps.pick_drivers(drv).pick_accurate()
        quali_fastest = quali_laps.pick_fastest()
        quali_time = quali_fastest["LapTime"] if quali_fastest is not None else pd.NaT


        # -------------------------
        # STORE
        # -------------------------
        data[drv] = [
            fp_fastest_time,
            practice_theoretical,
            micro,
            quali_time
        ]

    except Exception:
        data[drv] = [pd.NaT, pd.NaT, pd.NaT, pd.NaT]


# =========================
# BUILD GRID
# =========================
index = [
    "fastest lap in practice",
    "fastest lap combining practice sectors",
    "fastest micro sectors",
    "fastest qualy lap"
]

df = pd.DataFrame(data, index=index)

formatted = df.applymap(format_time)


# =========================
# OUTPUT
# =========================
print("\n=== PRACTICE vs QUALI PREDICTION GRID ===\n")
print(formatted.to_string())

filename = f"{YEAR}_{GP}_grid_pace_comparison.csv"
formatted.to_csv(filename)

print(f"\nSaved: {filename}")