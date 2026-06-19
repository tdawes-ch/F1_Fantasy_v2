import os
import pandas as pd
import numpy as np
import fastf1
import joblib  # This is the library used to save and load AI models to your hard drive

# 1. Setup Caching so your computer saves the downloaded F1 data locally
os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

def extract_race_features(year, gp_name):
    """
    Our Data Factory. You give it a year and a race, and it builds a clean 
    table of clues (Features) and actual outcomes (Targets).
    """
    try:
        print(f"-> Processing: {year} {gp_name}...")
        fp3 = fastf1.get_session(year, gp_name, 'FP3')
        qualy = fastf1.get_session(year, gp_name, 'Q')
        race = fastf1.get_session(year, gp_name, 'R')
        
        # Load data. Using weather=True for track temperatures
        fp3.load(telemetry=False, weather=True)
        qualy.load(telemetry=False, weather=False)
        race.load(telemetry=False, weather=False)
        
        # CLUE 1 & 2: Best Lap Delta and Tire Compound Score
        quick_laps = fp3.laps.pick_quicklaps()
        best_laps = quick_laps.groupby('Driver').agg({'LapTime': 'min', 'Compound': 'first'}).reset_index()
        best_laps['LapTime_Secs'] = best_laps['LapTime'].dt.total_seconds()
        best_laps['FP3_Delta'] = best_laps['LapTime_Secs'] - best_laps['LapTime_Secs'].min()
        
        compound_map = {'SOFT': 3, 'MEDIUM': 2, 'HARD': 1}
        best_laps['Tyre_Compound_Score'] = best_laps['Compound'].map(compound_map).fillna(2)
        
        # CLUE 3: Tire Degradation Rate (from long practice stints)
        deg_results = []
        for driver, driver_laps in fp3.laps.groupby('Driver'):
            long_stints = driver_laps.groupby('Stint').filter(lambda x: len(x) > 5)
            if not long_stints.empty:
                first_lap = long_stints['LapTime'].dt.total_seconds().iloc[0]
                last_lap = long_stints['LapTime'].dt.total_seconds().iloc[-1]
                stint_length = len(long_stints)
                deg_rate = (last_lap - first_lap) / stint_length
            else:
                deg_rate = 0.1  # Default penalty if they didn't do a long run
            deg_results.append({'Driver': driver, 'Tyre_Degradation': deg_rate})
        deg_df = pd.DataFrame(deg_results)
        
        # CLUE 4: Track Temperature
        avg_track_temp = fp3.weather_data['TrackTemp'].mean()
        
        # Assemble all clues
        features_df = pd.merge(best_laps, deg_df, on='Driver')
        features_df['Track_Temp'] = avg_track_temp
        
        # Gather actual answers
        q_res = qualy.results[['Abbreviation', 'Position']].rename(columns={'Abbreviation': 'Driver', 'Position': 'Qualy_Pos'})
        r_res = race.results[['Abbreviation', 'Position']].rename(columns={'Abbreviation': 'Driver', 'Position': 'Race_Pos'})
        
        # Merge clues and answers together
        final_df = pd.merge(features_df, q_res, on='Driver')
        final_df = pd.merge(final_df, r_res, on='Driver')
        
        return final_df[['Driver', 'FP3_Delta', 'Tyre_Compound_Score', 'Tyre_Degradation', 'Track_Temp', 'Qualy_Pos', 'Race_Pos']]
    
    except Exception as e:
        print(f"Skipping {gp_name} due to an error (e.g., session cancelled or data gap): {e}")
        return None

# =========================================================================
# STEP 1: DEFINE THE SEASON AND THE UNSEEN "TEST" RACE
# =========================================================================
# We will use a subset of the 2023 season to train our model.
# We will deliberately keep 'Silverstone' out of the training loop to be our blind test.
training_races = ['Bahrain', 'Monaco', 'Austria', 'Spa', 'Monza', 'Singapore', 'Japan', 'Silverstone']
unseen_race = 'Abu Dhabi'
season_year = 2023

print("--- PHASE 1: Building the Full Season Training Dataset ---")
season_data_list = []

for race in training_races:
    race_df = extract_race_features(season_year, race)
    if race_df is not None:
        season_data_list.append(race_df)

# Combine all the individual race tables into one massive history book
full_season_training_df = pd.concat(season_data_list, ignore_index=True).dropna()

# Separating our inputs (X) from our outputs/answers (y)
feature_cols = ['FP3_Delta', 'Tyre_Compound_Score', 'Tyre_Degradation', 'Track_Temp']
X_train = full_season_training_df[feature_cols]
y_race_train = full_season_training_df['Race_Pos']

# =========================================================================
# STEP 2: TRAINING THE MODEL
# =========================================================================
print("\n--- PHASE 2: Training the AI Model on the Season Data ---")
from sklearn.ensemble import RandomForestRegressor

# Creating the AI brain structure
f1_race_model = RandomForestRegressor(n_estimators=100, random_state=42)

# Forcing the model to study the season history book
f1_race_model.fit(X_train, y_race_train)
print("Training complete! The model has mapped out the patterns.")

# =========================================================================
# STEP 3: SAVING THE MODEL TO A FILE
# =========================================================================
print("\n--- PHASE 3: Freezing and Saving the Model to Disk ---")
model_filename = 'trained_f1_race_predictor.joblib'

# This takes the live computer memory structure and writes it to a binary file
joblib.dump(f1_race_model, model_filename)
print(f"Success! The model is now saved on your hard drive as: '{model_filename}'")

# =========================================================================
# STEP 4: LOADING THE SAVED MODEL (Simulating a fresh race weekend script)
# =========================================================================
print("\n--- PHASE 4: Loading the Saved Model for a New Race Weekend ---")
# Imagine this is a completely different Python file running a week later. 
# We don't have the training data loaded anymore. We just read the file.
loaded_f1_model = joblib.load(model_filename)
print("Model loaded back into memory successfully.")

# Get data for the race the model has never seen before (Silverstone)
print(f"\nGathering fresh weekend data for the unseen race: {unseen_race}...")
unseen_race_df = extract_race_features(season_year, unseen_race).dropna()

# Extract only the clues for the unseen race
X_unseen = unseen_race_df[feature_cols]

# Command the loaded model to predict the results based on its frozen math rules
unseen_race_df['Raw_Predicted_Finish'] = loaded_f1_model.predict(X_unseen)

# Rank the continuous decimal guesses into clean grid positions (1 to 20)
unseen_race_df['Predicted_Race_Pos'] = unseen_race_df['Raw_Predicted_Finish'].rank(method='min').astype(int)

print(f"\n=== PREDICTION RESULTS FOR {unseen_race.upper()} ===")
print(unseen_race_df[['Driver', 'Race_Pos', 'Predicted_Race_Pos']].sort_values(by='Predicted_Race_Pos').to_string(index=False))

# =========================================================================
# STEP 5: UPDATING THE MODEL WITH THE COMPLETED RACE DATA
# =========================================================================
print("\n--- PHASE 5: Updating the Model for Next Week ---")
print(f"The {unseen_race} GP is now finished. We add its data to our historical record.")

# 1. Take the Silverstone data table (which contains both the clues and the actual final race positions)
# 2. Add it to our original season dataset to make it bigger and more complete
updated_season_df = pd.concat([full_season_training_df, unseen_race_df[full_season_training_df.columns]], ignore_index=True)

# 3. Separate features and targets of this expanded data
X_updated = updated_season_df[feature_cols]
y_updated_race = updated_season_df['Race_Pos']

# 4. Retrain a fresh model instance on the expanded data
updated_model = RandomForestRegressor(n_estimators=100, random_state=42)
updated_model.fit(X_updated, y_updated_race)

# 5. Overwrite the old file on your hard drive with the newly updated model
joblib.dump(updated_model, model_filename)
print(f"Success! '{model_filename}' has been updated and overwritten. It now includes Silverstone knowledge.")