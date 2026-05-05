import pandas as pd
import soccerdata as sd
import os
import requests
import io
import warnings

warnings.filterwarnings('ignore')

def download_football_data(data_dir):
    print("--- 1. Descargando Football-Data (2018-2026 para H2H e Historia) ---")
    seasons = ['1819', '1920', '2021', '2122', '2223', '2324', '2425', '2526']
    dfs = []
    for s in seasons:
        url = f"https://www.football-data.co.uk/mmz4281/{s}/E0.csv"
        try:
            df = pd.read_csv(url)
            df['Season_Str'] = s 
            dfs.append(df)
            print(f" * Descargada Temporada {s} ({len(df)} partidos)")
        except Exception as e:
            print(f"Error descargando {s}: {e}")
    
    df_raw = pd.concat(dfs, ignore_index=True)
    out_path = os.path.join(data_dir, 'football_data_18_24.csv')
    df_raw.to_csv(out_path, index=False)
    print(f"✅ Archivo Maestro guardado: {out_path} ({df_raw.shape[0]} partidos)\n")

def download_understat(data_dir):
    print("--- 2. Descargando Understat (Solo Temporada 25-26) ---")
    try:
        und = sd.Understat(leagues="ENG-Premier League", seasons="2526")
        df_und = und.read_team_match_stats()
        out_path = os.path.join(data_dir, 'understat_2526.csv')
        df_und.to_csv(out_path)
        print(f"✅ Archivo Avanzado guardado: {out_path} ({df_und.shape[0]} registros de nivel equipo/partido)\n")
    except Exception as e:
        print(f"Error descargando Understat: {e}")

def download_clubelo(data_dir):
    print("--- 3. Descargando Historial ELO (Equipos Premier 25/26) ---")
    # Nombres bajo el estándar de URL de la API api.clubelo.com
    teams_clubelo = ['Arsenal', 'AstonVilla', 'Bournemouth', 'Brentford', 'Brighton', 
                     'Burnley', 'Chelsea', 'CrystalPalace', 'Everton', 'Fulham', 
                     'Liverpool', 'ManCity', 'ManUnited', 'Newcastle', 
                     'Forest', 'Tottenham', 'WestHam', 'Wolves', 'Sunderland', 'Leeds']
    dfs = []
    for team in teams_clubelo:
        url = f"http://api.clubelo.com/{team}"
        try:
            req = requests.get(url)
            if req.status_code == 200:
                df = pd.read_csv(io.StringIO(req.text))
                # Filtraremos desde el 2023 para ahorrar peso innecesario, 
                # (Elo se mapea por dia, con 1.5 años es suficiente para el 25/26)
                df['From'] = pd.to_datetime(df['From'])
                df = df[df['From'] >= '2024-01-01']
                df['API_Name'] = team # Añadimos esta columna para facilitar la unión futura
                dfs.append(df)
            else:
                 print(f" * [Error HTTP {req.status_code}] no se encontró ELO de {team}")
        except Exception as e:
            print(f" * Error de Conexión en {team}: {e}")
            
    if dfs:
        df_elo = pd.concat(dfs, ignore_index=True)
        out_path = os.path.join(data_dir, 'clubelo_2526.csv')
        df_elo.to_csv(out_path, index=False)
        print(f"✅ Archivo ELO Ratings guardado: {out_path} ({df_elo.shape[0]} registros diarios)\n")

if __name__ == "__main__":
    print("🚀 INICIANDO INGESTA DE DATOS V4 (TEMPORADA 25/26) 🚀\n")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    download_football_data(data_dir)
    download_understat(data_dir)
    download_clubelo(data_dir)
    print("🎉 INGESTA DE DATOS V3 FINALIZADA EXITOSAMENTE 🎉")
