import requests
import pandas as pd
import plotly.graph_objects as go

BASE_URL = "https://api.openf1.org/v1"

def discover_session_keys(year=2024):
    # Query all race sessions for that year
    url = f"{BASE_URL}/sessions?year={year}&session_name=Race"
    res = requests.get(url)
    
    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        
        # Select key identifying columns to display
        summary = df[['session_key', 'circuit_short_name', 'country_name', 'location']]
        print(f"\n🏁 VERIFIED OPENF1 RACE KEYS FOR {year}:")
        print("=" * 65)
        print(summary.to_string(index=False))
    else:
        print(f"Failed to fetch sessions. Status code: {res.status_code}")

# Run the lookup tool
discover_session_keys(2024)

def plot_fastest_lap_3d(session_key, driver_number):
    print(f"🔄 Step 1: Finding fastest lap for Driver #{driver_number}...")
    
    # Query all laps for this driver in the specific session
    laps_url = f"{BASE_URL}/laps?session_key={session_key}&driver_number={driver_number}"
    laps_res = requests.get(laps_url)
    
    if laps_res.status_code != 200 or not laps_res.json():
        print("❌ Could not retrieve lap records.")
        return
        
    laps_df = pd.DataFrame(laps_res.json())
    
    # Filter out out-laps / in-laps or rows missing duration data
    valid_laps = laps_df[laps_df['lap_duration'].notna()]
    
    if valid_laps.empty:
        print("❌ No valid timed laps found.")
        return
        
    # Find the row with the minimum lap duration (fastest lap)
    fastest_lap_row = valid_laps.loc[valid_laps['lap_duration'].idxmin()]
    lap_num = fastest_lap_row['lap_number']
    lap_time = fastest_lap_row['lap_duration']
    
    # Calculate the end time dynamically since 'date_end' doesn't exist
    start_time_raw = fastest_lap_row['date_start']
    start_time_dt = pd.to_datetime(start_time_raw)
    end_time_dt = start_time_dt + pd.to_timedelta(lap_time, unit='s')
    
    # Format them back into string timestamps for the API query string
    start_time = start_time_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    end_time = end_time_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    
    print(f"⏱️ Fastest Lap Found: Lap {lap_num} (Time: {lap_time}s)")
    print(f"⏳ Mapping GPS window: {start_time} ➡️ {end_time}")
    
    print("🔄 Step 2: Extracting X, Y, Z telemetry data from OpenF1...")
    # Request coordinate location records mapped tightly inside the lap timestamp window
    loc_url = (f"{BASE_URL}/location?session_key={session_key}"
               f"&driver_number={driver_number}"
               f"&date>={start_time}&date<={end_time}")
    
    loc_res = requests.get(loc_url)
    
    if loc_res.status_code != 200 or not loc_res.json():
        print("❌ No GPS location coordinates found inside this lap window.")
        return
        
    loc_df = pd.DataFrame(loc_res.json())
    
    # Sort chronologically by date
    loc_df = loc_df.sort_values(by='date').reset_index(drop=True)
    
    print(f"📈 Step 3: Generating interactive 3D track map from {len(loc_df)} GPS nodes...")
    
    # Render the 3D Scatter Plot
    fig = go.Figure(data=[go.Scatter3d(
        x=loc_df['x'],
        y=loc_df['y'],
        z=loc_df['z'],
        mode='lines+markers',
        marker=dict(
            size=3,
            color=loc_df.index, # Color path sequentially over time
            colorscale='Viridis',
            opacity=0.8
        ),
        line=dict(
            color='rgb(100, 100, 255)',
            width=5
        ),
        name=f"Lap {lap_num}"
    )])
    
    # Customize layout constraints to preserve realistic aspect ratios
    fig.update_layout(
        title=f"Driver #{driver_number} - Fastest Lap 3D Profile (Lap {lap_num})",
        scene=dict(
            xaxis_title='X (East/West)',
            yaxis_title='Y (North/South)',
            zaxis_title='Z (Elevation/Altitude)',
            aspectmode='data' # Keeps the circuit dimensions realistic instead of stretching
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )
    
    # Launches an interactive view locally in your web browser
    fig.show()

# Run the plotting trace
session_key = int(input("ENTER SESSION KEY: "))
plot_fastest_lap_3d(session_key=session_key, driver_number=16)