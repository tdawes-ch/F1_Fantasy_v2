import pandas as pd
import plotly.graph_objects as go
from plotly.io import show
from plotly.subplots import make_subplots
import fastf1 as ff1

season = 2024
schedule = ff1.get_event_schedule(season, include_testing=False)

# Get each driver's finishing positions and points for each round
standings = []
short_event_names = []

for _, event in schedule.iterrows():
    event_name, round_number = event["EventName"], event["RoundNumber"]
    short_event_names.append(event_name.replace("Grand Prix", "").strip())
    
    # Load race results
    race = ff1.get_session(season, event_name, "R")
    race.load(laps=False, telemetry=False, weather=False, messages=False)
    
    # Check for sprint race
    sprint = None
    if event["EventFormat"] == "sprint_qualifying":
        sprint = ff1.get_session(season, event_name, "S")
        sprint.load(laps=False, telemetry=False, weather=False, messages=False)
    
    for _, driver_row in race.results.iterrows():
        abbreviation, race_points, race_position = (
            driver_row["Abbreviation"],
            driver_row["Points"],
            driver_row["Position"],
        )
        
        sprint_points = 0
        if sprint is not None:
            driver_row = sprint.results[
                sprint.results["Abbreviation"] == abbreviation
            ]
            if not driver_row.empty:
                sprint_points = driver_row["Points"].values[0]
        
        standings.append(
            {
                "EventName": event_name,
                "RoundNumber": round_number,
                "Driver": abbreviation,
                "Points": race_points + sprint_points,
                "Position": race_position,
            }
        )

# Create dataframe
df = pd.DataFrame(standings)

# Reshape to heatmap format
heatmap_data = df.pivot(
    index="Driver", columns="RoundNumber", values="Points"
).fillna(0)

# Sort by total points
heatmap_data["total_points"] = heatmap_data.sum(axis=1)
heatmap_data = heatmap_data.sort_values(by="total_points", ascending=True)
total_points = heatmap_data["total_points"].values
heatmap_data = heatmap_data.drop(columns=["total_points"])

# Do the same for position
position_data = df.pivot(
    index="Driver", columns="RoundNumber", values="Position"
).fillna("N/A")

# Prepare hover info
hover_info = [
    [
        {
            "position": position_data.at[driver, race],
        }
        for race in schedule["RoundNumber"]
    ]
    for driver in heatmap_data.index
]

# Create subplots for two heatmaps
fig = make_subplots(
    rows=1,
    cols=2,
    column_widths=[0.85, 0.15],
    subplot_titles=("F1 2024 Season Summary", "Total Points"),
)
fig.update_layout(width=900, height=800)

# Per round summary heatmap
fig.add_trace(
    go.Heatmap(
        x=short_event_names,
        y=heatmap_data.index,
        z=heatmap_data.values,
        text=heatmap_data.values,
        texttemplate="%{text}",
        textfont={"size": 12},
        customdata=hover_info,
        hovertemplate=(
            "Driver: %{y}<br>"
            "Race Name: %{x}<br>"
            "Points: %{z}<br>"
            "Position: %{customdata.position}<extra></extra>"
        ),
        colorscale="YlGnBu",
        showscale=False,
        zmin=0,
        zmax=heatmap_data.values.max(),
    ),
    row=1,
    col=1,
)

# Heatmap for total points
fig.add_trace(
    go.Heatmap(
        x=["Total Points"] * len(total_points),
        y=heatmap_data.index,
        z=total_points,
        text=total_points,
        texttemplate="%{text}",
        textfont={"size": 12},
        colorscale="YlGnBu",
        showscale=False,
        zmin=0,
        zmax=total_points.max(),
    ),
    row=1,
    col=2,
)

show(fig)