import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

def get_name_mapping():
    # Map from Football-Data names to Understat names
    return {
        'Man City': 'Manchester City',
        'Man United': 'Manchester United',
        'Newcastle': 'Newcastle United',
        'Nott\'m Forest': 'Nottingham Forest',
        'Sheffield Utd': 'Sheffield United',
        'Wolves': 'Wolverhampton Wanderers',
        'Leeds': 'Leeds',
        'Sunderland': 'Sunderland'
    }

def get_clubelo_name_mapping():
    # Understat to ClubElo Mapping
    return {
        'Manchester City': 'ManCity',
        'Manchester United': 'ManUnited',
        'Newcastle United': 'Newcastle',
        'Nottingham Forest': 'Forest',
        'Sheffield United': 'SheffieldUtd',
        'Wolverhampton Wanderers': 'Wolves',
        'Aston Villa': 'AstonVilla',
        'Crystal Palace': 'CrystalPalace',
        'West Ham': 'WestHam',
        'Leeds': 'Leeds',
        'Sunderland': 'Sunderland'
    }

def get_squad_value_dictionary():
    # Valores EXACTOS de Transfermarkt (Premier League 25/26) extraídos en vivo. (Millones de Euros)
    return {
        'Manchester City': 1310, 'Arsenal': 1230, 'Chelsea': 1160, 
        'Liverpool': 1020, 'Tottenham': 803, 'Manchester United': 747, 
        'Newcastle United': 708, 'Nottingham Forest': 568, 'Aston Villa': 548, 
        'Crystal Palace': 541, 'Bournemouth': 507, 'Brighton': 494, 
        'Brentford': 470, 'Everton': 450, 'Fulham': 387, 
        'Sunderland': 382, 'West Ham': 363, 'Leeds': 346, 
        'Wolverhampton Wanderers': 277, 'Burnley': 253
    }

def main():
    print("--- FASE 1: LECTURA Y ALINEACIÓN (NAME MAPPING) ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(os.path.dirname(script_dir), 'data', 'raw')
    
    # 1. Cargar bases 
    fd_full = pd.read_csv(os.path.join(raw_dir, 'football_data_18_24.csv'))
    und = pd.read_csv(os.path.join(raw_dir, 'understat_2526.csv'))
    elo = pd.read_csv(os.path.join(raw_dir, 'clubelo_2526.csv'))
    
    # Mapeo de Nombres en Football Data hacia Understat
    name_map = get_name_mapping()
    fd_full['HomeTeam'] = fd_full['HomeTeam'].replace(name_map)
    fd_full['AwayTeam'] = fd_full['AwayTeam'].replace(name_map)
    
    # Filtro solo temporada actual
    fd_2526 = fd_full[fd_full['Season_Str'] == 2526].copy()
    
    # Merging is safest on HomeTeam and AwayTeam since they play only once at Home.
    # We will pick the odds and the target outcome from FD.
    merge_cols = ['HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A', 'FTR']
    fd_sub = fd_2526[merge_cols].rename(columns={'HomeTeam': 'home_team', 'AwayTeam': 'away_team'})
    
    df = pd.merge(und, fd_sub, on=['home_team', 'away_team'], how='inner')
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df.sort_values(by='date').reset_index(drop=True)
    
    print(f"Merge Completado: {df.shape[0]} Partidos alineados.")

    # --- FASE 2: H2H DEL ARCHIVO GIGANTE (2018-2024) ---
    print("--- FASE 2: CALCULANDO HEAD TO HEAD HISTÓRICO ---")
    fd_full['Date'] = pd.to_datetime(fd_full['Date'], dayfirst=True, errors='coerce').dt.date
    
    def get_points(ftr, is_home):
        if ftr == 'H': return 3 if is_home else 0
        if ftr == 'A': return 0 if is_home else 3
        return 1

    h2h_overall = []
    h2h_venue = []
    
    for _, row in df.iterrows():
        match_date = row['date']
        ht = row['home_team']
        at = row['away_team']
        
        # Filtramos historia hasta antes del partido de hoy
        mh = fd_full[(fd_full['Date'] < match_date)].copy()
        
        # 1. Overall (Cualquiera de local/visita) Ultimos 5
        ov = mh[((mh['HomeTeam']==ht) & (mh['AwayTeam']==at)) | ((mh['HomeTeam']==at) & (mh['AwayTeam']==ht))]
        ov = ov.sort_values(by='Date').tail(5)
        
        ht_pts_ov, at_pts_ov = 0, 0
        for _, r in ov.iterrows():
            if r['HomeTeam'] == ht:
                ht_pts_ov += get_points(r['FTR'], True)
                at_pts_ov += get_points(r['FTR'], False)
            else:
                ht_pts_ov += get_points(r['FTR'], False)
                at_pts_ov += get_points(r['FTR'], True)
                
        h2h_overall.append(ht_pts_ov - at_pts_ov)
        
        # 2. Especifico de Estadio (Solo cuando HT fue local y AT fue visita)
        ve = mh[(mh['HomeTeam']==ht) & (mh['AwayTeam']==at)]
        ve = ve.sort_values(by='Date').tail(5)
        ht_pts_ve, at_pts_ve = 0, 0
        for _, r in ve.iterrows():
            ht_pts_ve += get_points(r['FTR'], True)
            at_pts_ve += get_points(r['FTR'], False)
            
        h2h_venue.append(ht_pts_ve - at_pts_ve)
        
    df['H2H_Overall_L5'] = h2h_overall
    df['H2H_Venue_L5'] = h2h_venue
    
    # --- FASE 3: INGENIERÍA DE EXTRACCIÓN (TOTALIDADES Y FORMA L5) ---
    print("--- FASE 3: CALCULANDO FORM (L5) Y TOTALIDADES ACUMULADAS ---")
    
    teams = df['home_team'].unique()
    team_history = {t: pd.DataFrame() for t in teams}
    
    def calculate_match_stats_for_team(row, t):
        if row['home_team'] == t:
            return pd.Series({
                'date': row['date'],
                'pts': get_points(row['FTR'], True),
                'goals': row['home_goals'],
                'goals_against': row['away_goals'],
                'xG': row['home_xg'],
                'npxG': row['home_np_xg'],
                'xPts': row['home_expected_points'],
                'PPDA': row['home_ppda'],
                'DeepComp': row['home_deep_completions'],
            })
        else:
            return pd.Series({
                'date': row['date'],
                'pts': get_points(row['FTR'], False),
                'goals': row['away_goals'],
                'goals_against': row['home_goals'],
                'xG': row['away_xg'],
                'npxG': row['away_np_xg'],
                'xPts': row['away_expected_points'],
                'PPDA': row['away_ppda'],
                'DeepComp': row['away_deep_completions'],
            })

    # Construir historial temporal de cada equipo
    for t in teams:
        team_matches = df[(df['home_team'] == t) | (df['away_team'] == t)].copy()
        team_logs = team_matches.apply(lambda r: calculate_match_stats_for_team(r, t), axis=1)
        
        # Desfasar estadisticas usando SHIFT (Data Leakage Protection!!)
        shifted = team_logs.drop(columns='date').shift(1)
        
        # Expanding MEANS (Averages per game)
        exp = shifted.expanding().mean()
        exp.columns = [f"{c}_Avg_Tot" for c in exp.columns]
        
        # Rolling SUMS (Forma de ultimos 5 partidos con salvataje min_periods=1)
        rol = shifted[['pts', 'goals', 'goals_against']].rolling(5, min_periods=1).sum()
        rol.columns = [f"{c}_L5" for c in rol.columns]
        
        # Cumsum (Totales para posición en la tabla)
        cum = shifted[['pts', 'goals', 'goals_against']].cumsum()
        cum['GD_Tot'] = cum['goals'] - cum['goals_against']
        
        combined = pd.concat([team_logs[['date']], exp, rol, cum[['pts', 'GD_Tot']]], axis=1)
        team_history[t] = combined.set_index('date')

    # Reinyectar en el DataFrame principal
    final_features = []
    
    elo['From'] = pd.to_datetime(elo['From']).dt.date
    elo['To'] = pd.to_datetime(elo['To']).dt.date
    elo_map = get_clubelo_name_mapping()
    
    def get_elo(team, date):
        t_api = elo_map.get(team, team)
        match = elo[(elo['API_Name'] == t_api) & (elo['From'] <= date) & (elo['To'] >= date)]
        if not match.empty:
            return match.iloc[-1]['Elo']
        else:
            # Si hay un fallback (no debería)
            fallback = elo[(elo['API_Name'] == t_api) & (elo['To'] < date)]
            return fallback.iloc[-1]['Elo'] if not fallback.empty else 1500

    squad_vals = get_squad_value_dictionary()

    for idx, row in df.iterrows():
        ht = row['home_team']
        at = row['away_team']
        d = row['date']
        
        # Historial de Locales y Visitas (Solo mirando al pasado de cada uno)
        h_hist = team_history[ht].loc[d]
        a_hist = team_history[at].loc[d]
        
        # Elos y Diferencia
        h_elo = get_elo(ht, d)
        a_elo = get_elo(at, d)
        
        f = {
            'Date': d,
            'HomeTeam': ht,
            'AwayTeam': at,
            'Target_FTR': row['FTR'],
            
            # Contexto
            'Elo_Diff': h_elo - a_elo,
            'Home_SquadValue': squad_vals.get(ht, 300),
            'Away_SquadValue': squad_vals.get(at, 300),
            'B365H': row['B365H'],
            'B365D': row['B365D'],
            'B365A': row['B365A'],
            
            # H2H
            'H2H_Overall_L5': row['H2H_Overall_L5'],
            'H2H_Venue_L5': row['H2H_Venue_L5'],
            
            # Totales (Averages) HOME
            'H_Points_Avg_Tot': h_hist['pts_Avg_Tot'],
            'H_xG_Avg_Tot': h_hist['xG_Avg_Tot'],
            'H_npxG_Avg_Tot': h_hist['npxG_Avg_Tot'],
            'H_Goals_Scored_Avg_Tot': h_hist['goals_Avg_Tot'],
            'H_Goals_Against_Avg_Tot': h_hist['goals_against_Avg_Tot'],
            'H_xPts_Avg_Tot': h_hist['xPts_Avg_Tot'],
            'H_PPDA_Avg_Tot': h_hist['PPDA_Avg_Tot'],
            'H_DeepComp_Avg_Tot': h_hist['DeepComp_Avg_Tot'],
            'H_GD_Avg_Tot': h_hist['goals_Avg_Tot'] - h_hist['goals_against_Avg_Tot'],
            
            # L5 HOME
            'H_Points_L5': h_hist['pts_L5'],
            'H_Goals_Scored_L5': h_hist['goals_L5'],
            'H_Goals_Against_L5': h_hist['goals_against_L5'],
            
            # Tablas HOME (Posición relativa por pts y gd)
            'H_Points_Abs_Tot': h_hist['pts'],
            'H_GD_Abs_Tot': h_hist['GD_Tot'],

            # Totales (Averages) AWAY
            'A_Points_Avg_Tot': a_hist['pts_Avg_Tot'],
            'A_xG_Avg_Tot': a_hist['xG_Avg_Tot'],
            'A_npxG_Avg_Tot': a_hist['npxG_Avg_Tot'],
            'A_Goals_Scored_Avg_Tot': a_hist['goals_Avg_Tot'],
            'A_Goals_Against_Avg_Tot': a_hist['goals_against_Avg_Tot'],
            'A_xPts_Avg_Tot': a_hist['xPts_Avg_Tot'],
            'A_PPDA_Avg_Tot': a_hist['PPDA_Avg_Tot'],
            'A_DeepComp_Avg_Tot': a_hist['DeepComp_Avg_Tot'],
            'A_GD_Avg_Tot': a_hist['goals_Avg_Tot'] - a_hist['goals_against_Avg_Tot'],
            
            # L5 AWAY
            'A_Points_L5': a_hist['pts_L5'],
            'A_Goals_Scored_L5': a_hist['goals_L5'],
            'A_Goals_Against_L5': a_hist['goals_against_L5'],

            # Tablas AWAY
            'A_Points_Abs_Tot': a_hist['pts'],
            'A_GD_Abs_Tot': a_hist['GD_Tot']
        }
        
        final_features.append(f)
        
    df_fusion = pd.DataFrame(final_features)
    
    # Derivados Críticos Finales
    df_fusion['H_xG_GD_Avg_Tot'] = df_fusion['H_xG_Avg_Tot'] - df_fusion['A_xG_Avg_Tot'] # Mismatch ofensivo total
    
    out_dir = os.path.join(os.path.dirname(script_dir), 'data', 'processed')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'fusion_dataset.csv')
    df_fusion.to_csv(out_path, index=False)
    
    print("--- FASE 4: EXPORTACIÓN Y TÉRMINO ---")
    print(f"✅ Súper Matriz Exportada Exitosamente a {out_path} con dimensiones {df_fusion.shape}")
    print("Todas las variables crudas inútiles fueron dropeadas. Listo para Machine Learning.")

if __name__ == "__main__":
    main()
