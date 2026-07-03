import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(page_title="F1 Quali Command Center", layout="wide", page_icon="🏎️")
BASE_URL = "https://api.openf1.org/v1"

# --- Data Fetching Layer ---
@st.cache_data(ttl=5) # Polls every 5 seconds for live updates
def fetch_openf1(endpoint, params=None):
    if params is None:
        params = {}
    params['session_key'] = 'latest'
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

# --- 1. Top Header: Session & Status ---
sessions = fetch_openf1("sessions")
race_control = fetch_openf1("race_control")

session_name = sessions['session_name'].iloc[0] if not sessions.empty else "Loading Session..."
print(session_name)
status = "LIVE"
if not race_control.empty and 'flag' in race_control.columns:
    # Get the most recent flag status
    status = race_control['flag'].iloc[-1].upper() 

st.title(f"🏁 {session_name} | Track Status: {status}")
st.markdown("---")

# --- Layout: Main Content & Sidebar Widget ---
col_main, col_widget = st.columns([3, 1])

with col_main:
    # --- 2. Live Timing Table ---
    st.subheader("⏱️ Live Timing & Sector Times")
    drivers = fetch_openf1("drivers")
    laps = fetch_openf1("laps")
    stints = fetch_openf1("stints")
    
    if not drivers.empty and not laps.empty:
        # Get the latest lap for each driver
        latest_laps = laps.sort_values("date_start").drop_duplicates("driver_number", keep="last")
        
        # Merge driver info with lap info
        timing_df = drivers[['driver_number', 'name_acronym', 'team_name']].merge(
            latest_laps[['driver_number', 'duration_sector_1', 'duration_sector_2', 'duration_sector_3', 'is_pit_out_lap']], 
            on="driver_number", 
            how="left"
        )
        
        # Merge tyre compound from stints
        if not stints.empty:
            latest_stints = stints.sort_values("stint_number").drop_duplicates("driver_number", keep="last")
            timing_df = timing_df.merge(latest_stints[['driver_number', 'compound']], on="driver_number", how="left")
        else:
            timing_df['compound'] = "Unknown"

        # Format track status
        timing_df['Status'] = timing_df['is_pit_out_lap'].apply(lambda x: "Out Lap/In Pit" if x else "Fast Lap")
        
        # Clean up column names for display
        timing_df = timing_df.rename(columns={
            'name_acronym': 'Driver', 
            'team_name': 'Team',
            'compound': 'Tyre',
            'duration_sector_1': 'S1',
            'duration_sector_2': 'S2',
            'duration_sector_3': 'S3'
        }).drop(columns=['driver_number', 'is_pit_out_lap'])

        st.dataframe(timing_df, use_container_width=True, hide_index=True)
    else:
        st.info("Waiting for timing data...")

    # --- 3. 3D Live Position Map ---
    st.subheader("📍 3D Track Positions")
    # Fetch recent location telemetry
    locations = fetch_openf1("location") 
    
    if not locations.empty and 'x' in locations.columns:
        # Filter down to just the latest coordinate ping per driver
        latest_locations = locations.drop_duplicates("driver_number", keep="last")
        
        fig = go.Figure(data=[go.Scatter3d(
            x=latest_locations['x'], 
            y=latest_locations['y'], 
            z=latest_locations['z'],
            mode='markers+text',
            marker=dict(size=8, color=latest_locations['driver_number'], colorscale='Turbo'),
            text=latest_locations['driver_number'],
            textposition="top center"
        )])
        
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0), 
            scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Elevation'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Location telemetry not currently broadcasting.")

with col_widget:
    # --- 4. F1 Comms Widget ---
    st.subheader("📻 Control & Radio")
    
    st.markdown("**Race Control Updates**")
    if not race_control.empty:
        # Display the last 5 messages in reverse chronological order
        for _, row in race_control.tail(5).iloc[::-1].iterrows():
            time_str = str(row.get('date', ''))[11:19]
            msg = row.get('message', '')
            st.warning(f"**{time_str}** - {msg}")
    
    st.markdown("---")
    st.markdown("**Team Radio Log**")
    radios = fetch_openf1("team_radio")
    if not radios.empty:
        for _, row in radios.tail(10).iloc[::-1].iterrows():
            time_str = str(row.get('date', ''))[11:19]
            driver = row.get('driver_number', '??')
            st.info(f"**{time_str}** | Car {driver} Broadcast")