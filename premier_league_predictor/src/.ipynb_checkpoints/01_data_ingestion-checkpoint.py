import pandas as pd
import os

def download_data(seasons, output_dir):
    """
    Downloads Premier League match data from football-data.co.uk.
    """
    base_url = "https://www.football-data.co.uk/mmz4281/{season}/E0.csv"
    
    os.makedirs(output_dir, exist_ok=True)
    all_data = []
    
    for season in seasons:
        url = base_url.format(season=season)
        print(f"Downloading data for season {season}...")
        try:
            df = pd.read_csv(url)
            df['Season'] = season  # Add origin sequence ID
            all_data.append(df)
            print(f"Season {season} downloaded successfully ({len(df)} matches).")
        except Exception as e:
            print(f"Failed to download {season}: {e}")
            
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        # Clean column names spaces just in case
        full_df.columns = [c.strip() if isinstance(c, str) else c for c in full_df.columns]
        
        output_file = os.path.join(output_dir, 'premier_league_raw.csv')
        full_df.to_csv(output_file, index=False)
        print(f"\nAll data successfully saved to {output_file} ({len(full_df)} total matches).")

if __name__ == "__main__":
    # Target last 5 completed seasons
    # "1819" represents the 2018-2019 season
    target_seasons = ['1819', '1920', '2021', '2122', '2223', '2324']
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    target_path = os.path.join(project_root, 'data', 'raw')
    
    print(f"Initializing download to path: {target_path}")
    download_data(target_seasons, target_path)
