from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

# Load the race session
session = fastf1.get_session(2021, "Hungary", 'R')
session.load()
laps = session.laps

# Get the list of drivers and convert to abbreviations
drivers = session.drivers
drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
print(drivers)

# Find the stint length and compound used for every stint by every driver
# Group by driver, stint number, and compound, then count laps
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Driver", "Stint", "Compound"])
stints = stints.count().reset_index()

# Rename LapNumber column to StintLength
stints = stints.rename(columns={"LapNumber": "StintLength"})
print(stints)

# Plot the strategies for each driver
fig, ax = plt.subplots(figsize=(5, 10))

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    
    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        # Each row contains the compound name and stint length
        # Use these to draw horizontal bars
        compound_color = fastf1.plotting.get_compound_color(row["Compound"],
                                                            session=session)
        plt.barh(
            y=driver,
            width=row["StintLength"],
            left=previous_stint_end,
            color=compound_color,
            edgecolor="black",
            fill=True
        )
        
        previous_stint_end += row["StintLength"]

# Make the plot more readable
plt.title("2022 Hungarian Grand Prix Strategies")
plt.xlabel("Lap Number")
plt.grid(False)
# Invert y-axis so drivers that finish higher are closer to the top
ax.invert_yaxis()

# Plot aesthetics
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.show()