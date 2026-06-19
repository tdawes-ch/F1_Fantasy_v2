import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import fastf1
import fastf1.plotting

# 1. Setup caching and styling
cache_dir = 'f1_cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

# Set FastF1's signature dark aesthetic
fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1')

# 2. Load the Qualifying session
session = fastf1.get_session(2026, 'Barcelona', 'Q')
session.load()

# 3. Target Lewis Hamilton's fastest lap
ham_lap = session.laps.pick_driver('HAM').pick_fastest()

# Get full telemetry (including X, Y coordinates and throttle/brake inputs)
telemetry = ham_lap.get_telemetry()

# 4. Extract the variables needed for mapping
x = telemetry['X'].to_numpy()
y = telemetry['Y'].to_numpy()
throttle = telemetry['Throttle'].to_numpy()

# 5. Prepare the data for segmenting the line
# LineCollection expects a shape of (num_segments, 2, 2)
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# 6. Build the Plot
fig, ax = plt.subplots(figsize=(12, 10), facecolor='black')

# Using the 'RdYlGn' (Red-Yellow-Green) colormap.
# Green = 100% Throttle, Red = 0% Throttle (Braking zones/Coasting)
cmap = plt.colormaps.get_cmap('RdYlGn')
lc = LineCollection(segments, cmap=cmap, linewidth=4)

# Assign telemetry values (Throttle) to determine the segment colors
lc.set_array(throttle)

# Add the colored trajectory line to our map
ax.add_collection(lc)

# 7. Formatting and Polishing
ax.axis('equal')  # Critical to prevent the track layout from distorting
ax.set_xticks([]) # Turn off background grid/axis markers for a clean track view
ax.set_yticks([])

# Create a clean color bar legend
cbar = fig.colorbar(lc, ax=ax, orientation='horizontal', pad=0.05, shrink=0.6)
cbar.set_label('Throttle Position (%)', color='white', fontsize=12)
cbar.ax.xaxis.set_tick_params(color='white', labelcolor='white')

# Set text headers
plt.title(f"Lewis Hamilton - Racing Line & Throttle Map\n"
          f"{session.event['EventName']} {session.event['OfficialEventName'].split()[-1]} | Lap Time: {ham_lap['LapTime']}",
          color='white', fontsize=14, fontweight='bold', pad=20)

plt.show()