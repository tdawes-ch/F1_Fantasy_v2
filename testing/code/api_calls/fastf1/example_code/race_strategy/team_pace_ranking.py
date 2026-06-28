import seaborn as sns
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1')

# Load the race session and pick quick laps
race = fastf1.get_session(2024, 1, 'R')
race.load()
laps = race.laps.pick_quicklaps()

# Convert lap time to seconds
transformed_laps = laps.copy()
transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

# Order teams from fastest to slowest (by median lap time)
team_order = (
    transformed_laps[["Team", "LapTime (s)"]]
    .groupby("Team")
    .median()["LapTime (s)"]
    .sort_values()
    .index
)
print(team_order)

# Create color palette for teams
team_palette = {team: fastf1.plotting.get_team_color(team, session=race)
                for team in team_order}

# Create box plot
fig, ax = plt.subplots(figsize=(15, 10))
sns.boxplot(
    data=transformed_laps,
    x="Team",
    y="LapTime (s)",
    hue="Team",
    order=team_order,
    palette=team_palette,
    whiskerprops=dict(color="white"),
    boxprops=dict(edgecolor="white"),
    medianprops=dict(color="grey"),
    capprops=dict(color="white"),
)

plt.title("2024 Bahrain Grand Prix - Team Pace Comparison")
plt.grid(visible=False)
ax.set(xlabel=None)
plt.tight_layout()
plt.show()