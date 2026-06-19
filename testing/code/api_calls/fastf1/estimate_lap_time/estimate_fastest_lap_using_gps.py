import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import fastf1

# 1. Cache Setup
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

YEAR = 2025
LOCATION = 'Silverstone'
DRIVER = 'HAM'
NUM_MINISECTORS = 25

# Dictionary to hold the uniform telemetry records from different practice sessions
practice_telemetry = {}

# 2. Extract and uniformize data from FP1, FP2, and FP3
for practice in ['FP1', 'FP2', 'FP3']:
    try:
        session = fastf1.get_session(YEAR, LOCATION, practice)
        session.load(laps=True, telemetry=True, weather=False, messages=False)
        
        # Get the fastest clean lap on Softs
        p_laps = session.laps.pick_drivers(DRIVER).pick_quicklaps()
        soft_laps = p_laps[p_laps['Compound'] == 'SOFT']
        if soft_laps.empty:
            continue
        fastest_lap = soft_laps.pick_fastest()
        
        # Pull telemetry and standardize it with Distance
        tel = fastest_lap.get_telemetry().add_distance()
        practice_telemetry[practice] = tel
    except Exception as e:
        print(f"Skipping {practice}: {e}")

# 3. Standardize the distance mapping array
# We find the baseline max track length across the loaded runs
total_distance = max([tel['Distance'].max() for tel in practice_telemetry.values()])
ref_distance = np.linspace(0, total_distance, 2000) # 2000 clean coordinate steps
minisector_length = total_distance / NUM_MINISECTORS

# 4. Map speeds onto our uniform track layout
aligned_data = []
for session_name, tel in practice_telemetry.items():
    # Use 1D interpolation to match raw speeds and coordinates to our standard 2000 steps
    speed_interp = np.interp(ref_distance, tel['Distance'], tel['Speed'])
    x_interp = np.interp(ref_distance, tel['Distance'], tel['X'])
    y_interp = np.interp(ref_distance, tel['Distance'], tel['Y'])
    
    # Identify which mini-sector each of the 2000 steps belongs to
    minisectors = ((ref_distance // minisector_length) + 1).astype(int)
    
    df = pd.DataFrame({
        'Session': session_name, 'Distance': ref_distance, 'Minisector': minisectors,
        'Speed': speed_interp, 'X': x_interp, 'Y': y_interp
    })
    aligned_data.append(df)

master_df = pd.concat(aligned_data)

# 5. Determine the fastest session per individual mini-sector
# Find average speed per mini-sector group
grouped = master_df.groupby(['Minisector', 'Session'])['Speed'].mean().reset_index()
# Isolate the session name that clocked the highest average velocity value
fastest_sessions = grouped.loc[grouped.groupby('Minisector')['Speed'].idxmax()]
fastest_sessions = fastest_sessions[['Minisector', 'Session']].rename(columns={'Session': 'Best_Session'})

# Merge results back into the geographical telemetry mapping system
final_map = master_df.merge(fastest_sessions, on='Minisector')
# Filter down to a singular reference shape loop
final_map = final_map[final_map['Session'] == 'FP3'].sort_values('Distance')

# 6. Build the Visual Map
# Convert categorical session names (FP1, FP2, FP3) into numbers for color plotting
session_mapping = {'FP1': 1, 'FP2': 2, 'FP3': 3}
color_values = final_map['Best_Session'].map(session_mapping).to_numpy()

x = final_map['X'].to_numpy()
y = final_map['Y'].to_numpy()
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

fig, ax = plt.subplots(figsize=(12, 10), facecolor='black')
# Distinct color segments to show track ownership
cmap = plt.get_cmap('Set1', 3) 
lc = LineCollection(segments, cmap=cmap, linewidth=5)
lc.set_array(color_values)
ax.add_collection(lc)

ax.axis('equal')
ax.set_xticks([])
ax.set_yticks([])

# Create legend keys
cbar = fig.colorbar(lc, ax=ax, ticks=[1.33, 2.0, 2.66], shrink=0.5)
cbar.ax.set_yticklabels(['FP1 Peak', 'FP2 Peak', 'FP3 Peak'], color='white', fontsize=12)
cbar.ax.tick_params(color='white')

plt.title(f"Lewis Hamilton's Micro-Telemetry Peak Map\n"
          f"Which practice run dominated each corner?", color='white', fontsize=14, fontweight='bold')
plt.show()

# 1. Sort the optimal track map sequentially by distance to calculate time step-by-step
final_map = final_map.sort_values('Distance').reset_index(drop=True)

# 2. Calculate the distance delta delta (dx) between each data sample point
# This tells us exactly how long each mini track piece is in meters
final_map['dx'] = final_map['Distance'].diff().fillna(0)

# 3. Convert Speed from km/h to meters per second (divide by 3.6)
final_map['Speed_mps'] = final_map['Speed'] / 3.6

# 4. Calculate Time delta (dt = dx / speed) spent in each segment
# Avoid division by zero on the absolute starting line if speed is 0
final_map['dt'] = np.where(
    final_map['Speed_mps'] > 0, 
    final_map['dx'] / final_map['Speed_mps'], 
    0
)

# 5. Sum all the tiny chunks of time together to find the Total Synthesized Lap Time!
theoretical_telemetry_time_seconds = final_map['dt'].sum()

# 6. Fetch his actual fastest Qualifying Lap time for comparison
quali_session = fastf1.get_session(YEAR, LOCATION, 'Q')
quali_session.load(laps=True, telemetry=False, weather=False, messages=False)
actual_quali_laptime = quali_session.laps.pick_driver(DRIVER).pick_fastest()['LapTime']
actual_quali_seconds = actual_quali_laptime.total_seconds()

# 7. Formatting function for beautiful terminal output
def format_seconds(seconds):
    minutes = int(seconds // 60)
    remaining_secs = seconds % 60
    return f"{minutes}:{remaining_secs:06.3f}"

# 8. Print the Final Report
print("\n" + "="*50)
print(f"       {DRIVER} TELEMETRY SYNTHESIS VS QUALIFYING")
print("="*50)
print(f"Predicted Lap Time (Best of Practice):  {format_seconds(theoretical_telemetry_time_seconds)}")
print(f"Actual Lap Time (Qualifying Run):      {format_seconds(actual_quali_seconds)}")

time_delta = actual_quali_seconds - theoretical_telemetry_time_seconds

print("-"*50)
if time_delta < 0:
    print(f"Result: Qualy was {abs(time_delta):.3f}s FASTER than the model.")
    print("Interpretation: Track evolution (rubber laid down) or lower fuel loads")
    print("allowed him to exceed his theoretical practice limits!")
else:
    print(f"Result: Qualy was {time_delta:.3f}s SLOWER than the model.")
    print("Interpretation: The driver failed to hook up the perfect lap when it")
    print("mattered, leaving time on the table relative to practice sector speed.")
print("="*50)