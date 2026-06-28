import fastf1
from fastf1.ergast import Ergast

SEASON = 2026
ROUND = 8

# Get current driver standings
def get_drivers_standings():
    ergast = Ergast()
    standings = ergast.get_driver_standings(season=SEASON, round=ROUND)
    return standings.content[0]

# Calculate maximum points for remaining season
def calculate_max_points_for_remaining_season():
    POINTS_FOR_SPRINT = 8 + 25  # Winning sprint and race
    POINTS_FOR_CONVENTIONAL = 25  # Winning race
    
    events = fastf1.events.get_event_schedule(SEASON, backend='ergast')
    events = events[events['RoundNumber'] > ROUND]
    
    # Count sprint and conventional races
    sprint_events = len(events.loc[events["EventFormat"] == "sprint_shootout"])
    conventional_events = len(events.loc[events["EventFormat"] == "conventional"])
    
    # Calculate points for each
    sprint_points = sprint_events * POINTS_FOR_SPRINT
    conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL
    
    return sprint_points + conventional_points

# Determine who can win
def calculate_who_can_win(driver_standings, max_points):
    LEADER_POINTS = int(driver_standings.loc[0]['points'])
    
    for i, _ in enumerate(driver_standings.iterrows()):
        driver = driver_standings.loc[i]
        driver_max_points = int(driver["points"]) + max_points
        can_win = 'No' if driver_max_points < LEADER_POINTS else 'Yes'
        
        print(f"{driver['position']}: {driver['givenName'] + ' ' + driver['familyName']}, "
              f"Current points: {driver['points']}, "
              f"Theoretical max points: {driver_max_points}, "
              f"Can win: {can_win}")

# Execute calculation
driver_standings = get_drivers_standings()
points = calculate_max_points_for_remaining_season()
calculate_who_can_win(driver_standings, points)