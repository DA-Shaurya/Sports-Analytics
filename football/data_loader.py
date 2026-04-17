import os
import pandas as pd
import requests
import time
from functools import lru_cache

API_KEY = '1fce9b07c9eaba9b9dd83010d9353358'
API_HOST = 'v3.football.api-sports.io'
CACHE_FILE = os.path.join(os.path.dirname(__file__), 'cached_api_data.csv')
STATIC_FILE = os.path.join(os.path.dirname(__file__), 'players_data-2025_2026.csv')
CACHE_EXPIRY_HOURS = 24

LEAGUES = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61
}
SEASON = '2023'

def fetch_hybrid_data():
    # 1. Load the huge static database of 2,600+ players
    if not os.path.exists(STATIC_FILE):
        return pd.DataFrame()
        
    df = pd.read_csv(STATIC_FILE)
    
    # 2. Standardize column names for the dashboard
    rename_map = {
        'Player': 'player', 'Age': 'age', 'Squad': 'squad', 
        'Comp': 'comp', 'Pos': 'pos', 'MP': 'mp', 
        'Min': 'min', 'Gls': 'gls', 'Ast': 'ast'
    }
    df = df.rename(columns=rename_map)
    df = df[list(rename_map.values())].copy()
    
    # Clean string names to match
    df['player'] = df['player'].astype(str).str.strip()
    
    # 3. Fetch Live Data for Top Players (Using endpoints that don't block free tiers)
    headers = {'x-apisports-key': API_KEY}
    endpoints = ['players/topscorers', 'players/topassists']
    
    print("Fetching live stats to update top performers...")
    live_updates = {}
    
    for league_name, league_id in LEAGUES.items():
        for endpoint in endpoints:
            url = f"https://{API_HOST}/{endpoint}"
            params = {'league': str(league_id), 'season': SEASON}
            try:
                res = requests.get(url, headers=headers, params=params, timeout=10)
                
                # Free tier allows these endpoints to return 20 players without pagination blocks
                if res.status_code == 200:
                    data = res.json()
                    if 'response' in data:
                        for item in data['response']:
                            p_name = item['player']['name']
                            s_data = item['statistics'][0]
                            
                            live_updates[p_name] = {
                                'mp': s_data['games'].get('appearences', 0),
                                'min': s_data['games'].get('minutes', 0),
                                'gls': s_data['goals'].get('total', 0) or 0,
                                'ast': s_data['goals'].get('assists', 0) or 0,
                                'squad': s_data['team']['name'],
                                'comp': s_data['league']['name'],
                            }
                time.sleep(6) # Stay under 10 req/min
            except Exception as e:
                print(f"Failed to fetch {endpoint} for {league_name}: {e}")
                
    # 4. Apply Live Updates to the massive dataframe
    for player_name, stats in live_updates.items():
        # Fuzzy/exact match update. For simplicity, we use exact name match
        mask = df['player'] == player_name
        if mask.any():
            for key, val in stats.items():
                df.loc[mask, key] = val
        else:
            # If player doesn't exist in CSV, append them
            stats['player'] = player_name
            stats['age'] = 0 # Default fallback
            stats['pos'] = 'Unknown'
            new_row = pd.DataFrame([stats])
            df = pd.concat([df, new_row], ignore_index=True)
            
    print(f"Hybrid DB built: {len(df)} total players ({len(live_updates)} live-updated).")
    return df

@lru_cache(maxsize=1)
def load_data():
    if os.path.exists(CACHE_FILE):
        file_mod_time = os.path.getmtime(CACHE_FILE)
        current_time = time.time()
        hours_since_modified = (current_time - file_mod_time) / 3600
        
        if hours_since_modified < CACHE_EXPIRY_HOURS:
            print("Loading live database from local cache...")
            df = pd.read_csv(CACHE_FILE)
            return df
            
    print("Building Hybrid Worldwide Database...")
    df = fetch_hybrid_data()
    
    if not df.empty:
        df.to_csv(CACHE_FILE, index=False)
        print("Hybrid Database cached successfully.")
        return df
        
    return pd.DataFrame()