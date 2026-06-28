import seaborn as sns
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

# Enable Matplotlib patches for plotting timedelta values and load
# FastF1's dark color scheme
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')

# Load the race session
race = fastf1.get_session(2023, "Azerbaijan", 'R')
race.load()

# Get all the laps for a single driver
# Filter out slow laps as they distort the graph axis
driver_laps = race.laps.pick_drivers("ALO").pick_quicklaps().reset_index()

# Make the scatterplot using lap number as x-axis and lap time as y-axis
# Marker colors correspond to the compounds used
fig, ax = plt.subplots(figsize=(8, 8))

sns.scatterplot(data=driver_laps,
                x="LapNumber",
                y="LapTime",
                ax=ax,
                hue="Compound",
                palette=fastf1.plotting.get_compound_mapping(session=race),
                s=80,
                linewidth=0,
                legend='auto')

# Make the plot more aesthetic
ax.set_xlabel("Lap Number")
ax.set_ylabel("Lap Time")

# The y-axis increases from bottom to top by default
# Since we are plotting time, it makes sense to invert the axis
ax.invert_yaxis()
plt.suptitle("Alonso Laptimes in the 2023 Azerbaijan Grand Prix")

# Turn on major grid lines
plt.grid(color='w', which='major', axis='both')
sns.despine(left=True, bottom=True)

plt.tight_layout()
plt.show()