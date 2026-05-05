import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost no está instalado. Ejecutando sin él de momento...")

def train_and_evaluate():
    print("Iniciando Entrenamiento Refinado (con Tiros y Corners)...")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    processed_path = os.path.join(project_root, 'data', 'processed', 'premier_league_features.csv')
    
    df = pd.read_csv(processed_path)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date'] >= '2023-08-01') & (df['Date'] <= '2024-07-31')].copy()
    
    df = df.sort_values(by='Date')
    
    # 🆕 Nuevas variables poderosas (Shots Target + Corners)
    features = [
        'HomePoints_L3', 'AwayPoints_L3', 
        'HomeGoals_L3', 'AwayGoals_L3',
        'HomeShots_L3', 'AwayShots_L3',
        'HomeCorners_L3', 'AwayCorners_L3'
    ]
    if 'B365H' in df.columns:
        features += ['B365H', 'B365D', 'B365A']
        
    df = df.dropna(subset=features + ['Target'])
    
    X = df[features]
    y = df['Target']
    
    n = len(df)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)
    
    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]
    X_val = X.iloc[train_end:val_end]
    y_val = y.iloc[train_end:val_end]
    X_test = X.iloc[val_end:]
    y_test = y.iloc[val_end:]
    
    models = {
        "Regresión Logística": LogisticRegression(max_iter=5000), # Subimos iter para escalar convergencia
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    }
    if HAS_XGB:
        models["XGBoost"] = XGBClassifier(
            n_estimators=100, 
            random_state=42, 
            use_label_encoder=False, 
            eval_metric='mlogloss'
        )
        
    best_acc = 0
    best_name = ""
    best_model = None
    
    print("--- Resultados en Fase de Validación (Val 15%) ---")
    for name, m in models.items():
        m.fit(X_train, y_train)
        y_val_pred = m.predict(X_val)
        acc = accuracy_score(y_val, y_val_pred)
        print(f" {name:20s} Accuracy: {acc:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_name = name
            best_model = m
            
    print(f"\n🥇 Mejor algoritmo ajustado en Validación: {best_name}")
    
    y_test_pred = best_model.predict(X_test)
    test_acc = accuracy_score(y_test, y_test_pred)
    print(f"\n🎯 Accuracy en Test del modelo {best_name}: {test_acc:.4f}")
    
    print("\n--- Reporte Detallado de Clasificación ---")
    print(classification_report(y_test, y_test_pred, target_names=['Visita (0)', 'Empate (1)', 'Local (2)']))
    
    models_dir = os.path.join(project_root, 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, 'premier_league_predictor.joblib')
    joblib.dump(best_model, model_path)
    print(f"✅ Modelo V2 (con Tiros y Corners) guardado en: {model_path}")

if __name__ == "__main__":
    train_and_evaluate()
