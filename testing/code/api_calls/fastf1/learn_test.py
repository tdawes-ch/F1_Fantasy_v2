import os
import pandas as pd
import numpy as np
import fastf1
from sklearn.ensemble import RandomForestRegressor

os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

def get_advanced_session_features(year, gp_name):
    print(f"Loading advanced data for {year} {gp_name}...")
    
    fp3 = fastf1.get_session(year, gp_name, 'FP3')
    qualy = fastf1.get_session(year, gp_name, 'Q')
    race = fastf1.get_session(year, gp_name, 'R')
    
    # We turn weather=True ON because we need track temperatures now
    fp3.load(telemetry=False, weather=True)
    qualy.load(telemetry=False, weather=False)
    race.load(telemetry=False, weather=False)
    
    # All laps driven in FP3
    all_laps = fp3.laps
    
    # -------------------------------------------------------------------------
    # CLUE 1: Best Lap Delta & Tire Compound Used
    # -------------------------------------------------------------------------
    quick_laps = all_laps.pick_quicklaps()
    # Find the single best lap time for each driver
    best_laps = quick_laps.groupby('Driver').agg({
        'LapTime': 'min',
        'Compound': 'first' # Look at what compound they were wearing
    }).reset_index()
    
    # Convert best lap times to raw seconds and calculate the Delta (like before)
    best_laps['LapTime_Secs'] = best_laps['LapTime'].dt.total_seconds()
    best_laps['FP3_Delta'] = best_laps['LapTime_Secs'] - best_laps['LapTime_Secs'].min()
    
    # Map the Compound words to numbers so the AI can read them
    compound_map = {'SOFT': 3, 'MEDIUM': 2, 'HARD': 1}
    best_laps['Tyre_Compound_Score'] = best_laps['Compound'].map(compound_map).fillna(2) 
    # (.fillna(2) means if they used a weird tire like 'WET', just treat it as a Medium for now)
    
    # -------------------------------------------------------------------------
    # CLUE 2: Calculating Tire Degradation (Long Runs)
    # -------------------------------------------------------------------------
    deg_results = []
    for driver, driver_laps in all_laps.groupby('Driver'):
        # An F1 'Stint' is a continuous run on one set of tires. 
        # We only care about long runs, let's say stints with more than 5 laps.
        long_stints = driver_laps.groupby('Stint').filter(lambda x: len(x) > 5)
        
        if not long_stints.empty:
            # How much did their lap time increase from the start of the stint to the end?
            first_lap_time = long_stints['LapTime'].dt.total_seconds().iloc[0]
            last_lap_time = long_stints['LapTime'].dt.total_seconds().iloc[-1]
            total_laps_in_stint = len(long_stints)
            
            # Calculate average seconds lost per lap
            deg_rate = (last_lap_time - first_lap_time) / total_laps_in_stint
        else:
            # If a driver didn't do a long run, we assume an average degradation of 0.1 seconds per lap
            deg_rate = 0.1
            
        deg_results.append({'Driver': driver, 'Tyre_Degradation': deg_rate})
    
    deg_df = pd.DataFrame(deg_results)
    
    # -------------------------------------------------------------------------
    # CLUE 3: Track Temperature
    # -------------------------------------------------------------------------
    # Get the average track temperature across the entire FP3 session
    avg_track_temp = fp3.weather_data['TrackTemp'].mean()
    
    # -------------------------------------------------------------------------
    # STITCHING IT ALL TOGETHER
    # -------------------------------------------------------------------------
    # Merge Clue 1 (Deltas & Compounds) with Clue 2 (Degradation)
    features_df = pd.merge(best_laps, deg_df, on='Driver')
    
    # Add Clue 3 (Track Temp) as a flat value for everyone in this specific race
    features_df['Track_Temp'] = avg_track_temp
    
    # Grab the actual results (Our targets/answers)
    q_res = qualy.results[['Abbreviation', 'Position']].rename(columns={'Abbreviation': 'Driver', 'Position': 'Qualy_Pos'})
    r_res = race.results[['Abbreviation', 'Position']].rename(columns={'Abbreviation': 'Driver', 'Position': 'Race_Pos'})
    
    # Merge features with answers
    final_df = pd.merge(features_df, q_res, on='Driver')
    final_df = pd.merge(final_df, r_res, on='Driver')
    
    # Return our neat table containing the Driver name, our 4 Clues, and our 2 Answers
    return final_df[['Driver', 'FP3_Delta', 'Tyre_Compound_Score', 'Tyre_Degradation', 'Track_Temp', 'Qualy_Pos', 'Race_Pos']]

# --- TRAINING THE UPGRADED MODEL ---

# 1. Gather data from our history book races
train_gp1 = get_advanced_session_features(2023, 'Silverstone')
train_gp2 = get_advanced_session_features(2023, 'Monza')
train_df = pd.concat([train_gp1, train_gp2], ignore_index=True).dropna()

# 2. Define multiple input features (X now has 4 columns instead of 1!)
feature_columns = ['FP3_Delta', 'Tyre_Compound_Score', 'Tyre_Degradation', 'Track_Temp']
X_train = train_df[feature_columns]

y_qualy_train = train_df['Qualy_Pos']
y_race_train = train_df['Race_Pos']

# 3. Train the AI Brains (They will now look at all 4 clues simultaneously)
model_qualy = RandomForestRegressor(n_estimators=100, random_state=42)
model_race = RandomForestRegressor(n_estimators=100, random_state=42)

model_qualy.fit(X_train, y_qualy_train)
model_race.fit(X_train, y_race_train)

print("\nModel training complete! The AI now evaluates lap times, tire choices, degradation, and weather.")

# 4. Predict an unseen race
print("\n--- Predicting Future Race (Singapore 2023) ---")
test_df = get_advanced_session_features(2023, 'Singapore').dropna()
X_test = test_df[['FP3_Delta']]

# Generate continuous predictions
test_df['Pred_Qualy_Raw'] = model_qualy.predict(X_test)
test_df['Pred_Race_Raw'] = model_race.predict(X_test)

# Convert raw scores into discrete finishing ranks (1st to 20th)
test_df['Pred_Qualy_Pos'] = test_df['Pred_Qualy_Raw'].rank(method='min').astype(int)
test_df['Pred_Race_Pos'] = test_df['Pred_Race_Raw'].rank(method='min').astype(int)

# Display Results sorted by predicted race finish
output = test_df[['Driver', 'Qualy_Pos', 'Pred_Qualy_Pos', 'Race_Pos', 'Pred_Race_Pos']]
print(output.sort_values(by='Pred_Race_Pos').to_string(index=False))