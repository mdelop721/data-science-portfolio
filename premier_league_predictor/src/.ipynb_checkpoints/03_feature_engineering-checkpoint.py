import pandas as pd
import numpy as np
import os

def assign_points(result, is_home):
    """
    Retorna 3 puntos por victoria, 1 por empate, 0 por derrota.
    """
    if result == 'H':
        return 3 if is_home else 0
    elif result == 'A':
        return 0 if is_home else 3
    else:
        return 1

def build_features(df):
    print("Iniciando Feature Engineering...")
    
    # 1. Parsear Fechas correctamente
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.sort_values(by='Date')
    
    # 2. Extraer columnas útiles y filtrar NaNs en Resultados
    cols_to_keep = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR']
    odds_cols = [c for c in ['B365H', 'B365D', 'B365A'] if c in df.columns]
    
    df = df[cols_to_keep + odds_cols].copy()
    df = df.dropna(subset=['FTR', 'HomeTeam', 'AwayTeam'])
    
    # 3. Iterar y construir historias de desempeño
    team_stats = {}
    
    home_points_l3 = []
    away_points_l3 = []
    home_goals_l3 = []
    away_goals_l3 = []
    
    for _, row in df.iterrows():
        ht = row['HomeTeam']
        at = row['AwayTeam']
        
        # Inicializar diccionario para equipos nuevos
        if ht not in team_stats:
            team_stats[ht] = {'points': [], 'goals': []}
        if at not in team_stats:
            team_stats[at] = {'points': [], 'goals': []}
            
        # Calcular estadísticas de los últimos 3 partidos que han jugado antes de HOY (este partido)
        hp = sum(team_stats[ht]['points'][-3:]) if len(team_stats[ht]['points']) > 0 else 0
        ap = sum(team_stats[at]['points'][-3:]) if len(team_stats[at]['points']) > 0 else 0
        hg = sum(team_stats[ht]['goals'][-3:]) if len(team_stats[ht]['goals']) > 0 else 0
        ag = sum(team_stats[at]['goals'][-3:]) if len(team_stats[at]['goals']) > 0 else 0
        
        home_points_l3.append(hp)
        away_points_l3.append(ap)
        home_goals_l3.append(hg)
        away_goals_l3.append(ag)
        
        # Actualizar diccionario con los resultados de ESTE partido para que existan mañana
        team_stats[ht]['points'].append(assign_points(row['FTR'], is_home=True))
        team_stats[at]['points'].append(assign_points(row['FTR'], is_home=False))
        team_stats[ht]['goals'].append(row['FTHG'])
        team_stats[at]['goals'].append(row['FTAG'])
        
    # Agregarlas al dataframe
    df['HomePoints_L3'] = home_points_l3
    df['AwayPoints_L3'] = away_points_l3
    df['HomeGoals_L3'] = home_goals_l3
    df['AwayGoals_L3'] = away_goals_l3
    
    # Target Encoding Numérico -> 'Away': 0, 'Draw': 1, 'Home': 2
    # Esto es crucial para modelos como XGBoost o Random Forest
    mapping = {'A': 0, 'D': 1, 'H': 2}
    df['Target'] = df['FTR'].map(mapping)
    
    # Remover los primeros partidos de los equipos donde no tienen "pasado" (ej. Puntos_L3 = 0)
    # No lo filtramos por completo, pero es importante tenerlo en cuenta.
    
    print("Nuevas variables creadas exitosamente.")
    return df

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    raw_path = os.path.join(project_root, 'data', 'raw', 'premier_league_raw.csv')
    processed_dir = os.path.join(project_root, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Cargando dataset crudo desde: {raw_path}")
    df_raw = pd.read_csv(raw_path)
    
    df_features = build_features(df_raw)
    
    output_path = os.path.join(processed_dir, 'premier_league_features.csv')
    df_features.to_csv(output_path, index=False)
    print(f"Dataset procesado (+features) exportado a {output_path} con dimensiones {df_features.shape}")
