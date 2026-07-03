import streamlit as st
import fastf1
import pandas as pd
import plotly.graph_objects as go
import os

# --- Page Setup ---
st.set_page_config(page_title="FastF1 Telemetry Replay", layout="wide", page_icon="🏎️")

# --- Sidebar Controls ---
st.sidebar.header("Session Selector")
st.sidebar.markdown("*(Note: Session must be fully completed to load)*")
year = st.sidebar.number_input("Year", min_value=2018, max_value=2026, value=2026)
event = st.sidebar.text_input("Event (e.g., 'Austria')", value="Austria")
session_type = st.sidebar.selectbox("Session", ["FP1", "FP2", "FP3", "Q", "SQ", "R"], index=4)

@st.cache_data
def fetch_fastf1_data(y, e, s):
    # FastF1 requires a local cache directory to store the downloaded data
    if not os.path.exists("f1cache"):
        os.makedirs("f1cache")
    fastf1.Cache.enable_cache("f1cache")
    
    session = fastf1.get_session(y, e, s)
    # Load timing, telemetry, and race control messages
    session.load(telemetry=True, weather=False, messages=True)
    return session

try:
    with st.spinner("Downloading and processing FastF1 data (this takes a minute on first run)..."):
        session = fetch_fastf1_data(year, event, session_type)
except Exception as e:
    st.error(f"Could not load session. Make sure the session has officially ended. Error: {e}")
    st.stop()

# --- Scrubbing Slider ---
# Calculate the start and end times of the session data
min_time = session.laps['Time'].min().total_seconds()
max_time = session.laps['Time'].max().total_seconds()

current_time_sec = st.slider(
    "⏱️ Scrub Session Time", 
    min_value=float(min_time), 
    max_value=float(max_time), 
    value=float(min_time + 600)
)
current_td = pd.Timedelta(seconds=current_time_sec)

# --- 1. Top Header ---
st.title(f"🏁 {session.event.EventName} | {session.name}")
st.markdown("---")

col_main, col_widget = st.columns([3, 1])

with col_main:
    # --- 2. Timing Table (Up to current time) ---
    st.subheader("⏱️ Best Sectors (At selected time)")
    
    # Filter for laps completed before the current slider time
    completed_laps = session.laps[session.laps['Time'] <= current_td]
    
    if not completed_laps.empty:
        # Get each driver's fastest lap up to this exact point in the session
        best_laps = completed_laps.loc[completed_laps.groupby('DriverNumber')['LapTime'].idxmin()]
        
        timing_df = best_laps[['Driver', 'Team', 'Compound', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'LapTime']].copy()
        
        # Format the timedelta columns for cleaner display
        for col in ['Sector1Time', 'Sector2Time', 'Sector3Time', 'LapTime']:
            timing_df[col] = timing_df[col].apply(
                lambda x: str(x).split()[-1][:8] if pd.notnull(x) else ""
            )
            
        timing_df.sort_values('LapTime', inplace=True)
        st.dataframe(timing_df, use_container_width=True, hide_index=True)
    else:
        st.info("No laps completed yet at this time stamp.")

 # --- 3. 3D Position Map ---
    st.subheader("📍 3D Track Positions")
    
    traces = []
    
    # 1. ADD THE TRACK OUTLINE
    try:
        # Get the telemetry of the fastest lap to use as the track map
        ref_lap = session.laps.pick_fastest()
        ref_tel = ref_lap.get_telemetry()
        
        traces.append(go.Scatter3d(
            x=ref_tel['X'], 
            y=ref_tel['Y'], 
            z=ref_tel['Z'],
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.4)', width=4), # Semi-transparent white line
            hoverinfo='skip',
            name="Track Outline"
        ))
    except Exception as e:
        pass # If fastest lap telemetry is missing, just skip drawing the track

    # 2. ADD THE CAR POSITIONS
    driver_positions = []
    for driver in session.drivers:
        try:
            pos_data = session.pos_data[driver]
            # Find the telemetry row closest to the current scrub time
            time_diffs = (pos_data['Time'] - current_td).abs()
            closest_idx = time_diffs.idxmin()
            closest_pos = pos_data.loc[closest_idx]
            
            # Only plot the car if the telemetry ping is within 3 seconds of the slider
            if time_diffs[closest_idx].total_seconds() < 3:
                driver_info = session.get_driver(driver)
                team_color = driver_info['TeamColor']
                
                driver_positions.append({
                    'Driver': driver_info['Abbreviation'],
                    'TeamColor': f"#{team_color}" if pd.notna(team_color) and team_color else "#FFFFFF",
                    'X': closest_pos['X'],
                    'Y': closest_pos['Y'],
                    'Z': closest_pos['Z']
                })
        except (KeyError, ValueError):
            continue
            
    if driver_positions:
        pos_df = pd.DataFrame(driver_positions)
        traces.append(go.Scatter3d(
            x=pos_df['X'], y=pos_df['Y'], z=pos_df['Z'],
            mode='markers+text',
            text=pos_df['Driver'],
            textposition="top center",
            textfont=dict(color='white', size=10),
            marker=dict(
                size=8, 
                color=pos_df['TeamColor'],
                line=dict(color='black', width=1)
            ),
            name="Cars"
        ))
        
    if traces:
        fig = go.Figure(data=traces)
        
        # 3. FIX THE SCALING
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            showlegend=False,
            scene=dict(
                xaxis=dict(title='X', showgrid=False, zeroline=False, showticklabels=False), 
                yaxis=dict(title='Y', showgrid=False, zeroline=False, showticklabels=False), 
                zaxis=dict(title='Elevation (Z)', showgrid=True),
                aspectmode='data' # THIS FIXES THE SCALING - Forces 1:1 physical ratio
            ),
            height=600,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No telemetry data available for this exact timestamp.")

with col_widget:
    # --- 4. F1 Comms Widget ---
    st.subheader("📻 Race Control")
    
    # Filter messages up to the current time
    messages = session.race_control_messages
    
    # Fix: Convert the slider's timedelta into an absolute datetime for comparison
    current_absolute_time = session.t0_date + current_td
    
    # Now compare datetime to datetime
    past_messages = messages[messages['Time'] <= current_absolute_time]
    
    if not past_messages.empty:
        # Display the 8 most recent messages relative to the slider position
        for _, row in past_messages.tail(8).iloc[::-1].iterrows():
            # Extract just the HH:MM:SS from the absolute timestamp
            time_str = str(row['Time']).split()[-1][:8]
            msg = row['Message']
            
            if "FLAG" in msg.upper():
                st.error(f"**{time_str}** - {msg}")
            else:
                st.warning(f"**{time_str}** - {msg}")
    else:
        st.info("No race control messages yet.")