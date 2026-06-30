import requests
import pandas as pd

BASE_URL = "https://api.openf1.org/v1"

def get_all_possible_driver_data(year=2024):
    print(f"🔄 Contacting OpenF1 to find an active race session for {year}...")
    
    # 1. Fetch a valid session to get a live grid context
    session_res = requests.get(f"{BASE_URL}/sessions?year={year}&session_name=Race")
    
    if session_res.status_code != 200 or not session_res.json():
        print("❌ Could not find a valid race session context.")
        return None
        
    session_key = session_res.json()[0]['session_key']
    country = session_res.json()[0]['country_name']
    print(f"✅ Found key {session_key} for the {country} GP. Scraping all raw driver records...")
    
    # 2. Fetch all raw rows from the /drivers endpoint
    driver_res = requests.get(f"{BASE_URL}/drivers?session_key={session_key}")
    
    if driver_res.status_code == 200:
        raw_data = driver_res.json()
        df = pd.DataFrame(raw_data)
        
        # Deduplicate rows by driver number so we get exactly one comprehensive row per driver
        df = df.drop_duplicates(subset=['driver_number'])
        
        # Clean up session keys that aren't specific to the driver's biography
        keys_to_remove = ['session_key', 'meeting_key']
        df = df.drop(columns=[col for col in keys_to_remove if col in df.columns])
        
        # Sort sequentially by their official racing number
        df = df.sort_values(by='driver_number').reset_index(drop=True)
        
        return df
    else:
        print(f"❌ Failed to reach endpoint. HTTP Status: {driver_res.status_code}")
        return None

# Run the pipeline
all_drivers_df = get_all_possible_driver_data(2024)

if all_drivers_df is not None:
    # Configure pandas to output the massive grid cleanly in your terminal
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print("\n🏎️ COMPLETE DRIVER DATA PROFILE SET AVAILABLE FROM OPENF1:")
    print("=" * 90)
    print(all_drivers_df)
    
    # Optional: Save it out directly to a CSV file to inspect it manually
    all_drivers_df.to_csv("openf1_driver_profiles.csv", index=False)