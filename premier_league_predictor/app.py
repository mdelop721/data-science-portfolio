import streamlit as st
import pandas as pd
import joblib
import os

st.set_page_config(page_title="Premier League Predictor V2", page_icon="⚽", layout="wide")

st.title("⚽ Predictor de la Premier League (V2)")
st.markdown("Ahora con esteroides: Predice el resultado basado no solo en puntos y goles, sino en presiones ofensivas (Tiros al Arco y Corners).")

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'premier_league_predictor.joblib')
    return joblib.load(model_path)

try:
    model = load_model()
except Exception as e:
    st.error(f"Error cargando el modelo: {e}")
    st.stop()

st.sidebar.header("Configure el Partido")
st.sidebar.info("Ajusta los parámetros ofensivos y defensivos para predecir si ganará el Local, habrá Empate, o ganará la Visita.")

col_h, col_a = st.columns(2)

with col_h:
    st.subheader("🏟️ Equipo Local (Stats Últs 3 juegos)")
    home_points = st.slider("Puntos Recientes", 0, 9, 4, key="hp")
    home_goals  = st.slider("Goles Anotados", 0, 15, 4, key="hg")
    home_shots  = st.slider("Tiros a Puerta (Destreza)", 0, 45, 12, key="hs")
    home_corns  = st.slider("Corners (Presión Ofensiva)", 0, 30, 15, key="hc")

with col_a:
    st.subheader("✈️ Equipo Visita (Stats Últs 3 juegos)")
    away_points = st.slider("Puntos Recientes", 0, 9, 3, key="ap")
    away_goals  = st.slider("Goles Anotados", 0, 15, 3, key="ag")
    away_shots  = st.slider("Tiros a Puerta (Destreza)", 0, 45, 8, key="as")
    away_corns  = st.slider("Corners (Presión Ofensiva)", 0, 30, 10, key="ac")

st.divider()
st.subheader("Predicciones Externas (Cuotas de Apuesta)")
col3, col4, col5 = st.columns(3)
with col3: odds_h = st.number_input("Cuota Local", min_value=1.0, value=2.10, step=0.1)
with col4: odds_d = st.number_input("Cuota Empate", min_value=1.0, value=3.20, step=0.1)
with col5: odds_a = st.number_input("Cuota Visita", min_value=1.0, value=3.60, step=0.1)

st.divider()
if st.button("🔮 Predecir Resultado", use_container_width=True, type="primary"):
    
    # Feature Order: ['HomePoints_L3', 'AwayPoints_L3', 'HomeGoals_L3', 'AwayGoals_L3', 
    #                 'HomeShots_L3', 'AwayShots_L3', 'HomeCorners_L3', 'AwayCorners_L3', 
    #                 'B365H', 'B365D', 'B365A']
    input_data = pd.DataFrame({
        'HomePoints_L3': [home_points],
        'AwayPoints_L3': [away_points],
        'HomeGoals_L3': [home_goals],
        'AwayGoals_L3': [away_goals],
        'HomeShots_L3': [home_shots],
        'AwayShots_L3': [away_shots],
        'HomeCorners_L3': [home_corns],
        'AwayCorners_L3': [away_corns],
        'B365H': [odds_h],
        'B365D': [odds_d],
        'B365A': [odds_a]
    })
    
    prediction = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]
    options = {0: "GANA LA VISITA ✈️", 1: "EMPATE 🤝", 2: "GANA EL LOCAL 🏟️"}
    
    st.subheader(f"💥 Predicción Final: {options[prediction]}")
    
    st.progress(probabilities[2], text=f"Local ({probabilities[2]*100:.1f}%)")
    st.progress(probabilities[1], text=f"Empate ({probabilities[1]*100:.1f}%)")
    st.progress(probabilities[0], text=f"Visita ({probabilities[0]*100:.1f}%)")
