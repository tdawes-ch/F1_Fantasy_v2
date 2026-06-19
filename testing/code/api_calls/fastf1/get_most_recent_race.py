import pandas as pd
from datetime import datetime, timezone
import fastf1

# Mute FastF1's background log spam
fastf1.set_log_level('WARNING')

def main():
    # Capture the exact current moment in UTC to match FastF1's dates
    now = datetime.now(timezone.utc)
    
    print("Scanning the F1 calendar schedule...")
    
    # Load the current season schedule
    schedule = fastf1.get_event_schedule(2026, include_testing=False)
    
    all_past_sessions = []

    # Flatten out the schedule matrix to check every individual session slot (1 through 5)
    for _, event in schedule.iterrows():
        for i in range(1, 6):
            session_name = event[f'Session{i}']
            session_date = event[f'Session{i}Date']
            
            # If the session date exists and is in the past, store it
            if pd.notna(session_date) and session_date < now:
                all_past_sessions.append({
                    'RoundNumber': event['RoundNumber'],
                    'EventName': event['EventName'],
                    'SessionName': session_name,
                    'SessionDate': session_date,
                    'OfficialName': event['OfficialEventName']
                })

    # Convert our list into a dataframe to slice easily
    if all_past_sessions:
        past_sessions_df = pd.DataFrame(all_past_sessions)
        
        # Sort chronologically and extract the absolute latest session entry
        most_recent = past_sessions_df.sort_values(by='SessionDate').iloc[-1]
        
        # Print the data cleanly to the console
        print("\n" + "="*55)
        print("         🏁 MOST RECENT COMPLETED SESSION 🏁         ")
        print("="*55)
        print(f"Grand Prix:   {most_recent['EventName']} (Round {most_recent['RoundNumber']})")
        print(f"Session:      {most_recent['SessionName']}")
        print(f"Date/Time:    {most_recent['SessionDate'].strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Official Name: {most_recent['OfficialName']}")
        print("="*55)
        
        print("\n💡 You can now load this session using:")
        print(f"session = fastf1.get_session(2026, {int(most_recent['RoundNumber'])}, '{most_recent['SessionName']}')")
        
    else:
        print("\n❌ No sessions found in the past for this calendar year yet.")

if __name__ == "__main__":
    main()