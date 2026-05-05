# Premier League Predictor — Contexto del proyecto

## Qué es este proyecto

Modelo de clasificación multiclase para predecir el resultado de partidos de la Premier League:
- **Victoria local (H)**, **Empate (D)**, **Victoria visitante (A)**
- Orientado a portafolio de Data Science
- El dataset contiene features **pre-partido** (no hay marcador final)

---

## Sesión 2026-04-27 — EDA completo

### Qué hicimos

1. **Exploramos el dataset** `data/processed/fusion_dataset.csv`:
   - 319 partidos, 41 features, temporada 2025/26 (ago 2025 – abr 2026)
   - 20 equipos de la Premier League
   - Target: H 41.7% · A 31.3% · D 27.0% (desbalance moderado)
   - 10 nulos por columna (jornada 1, sin historial — estructural, no errores)

2. **Creamos `notebooks/EDA_premier_league.ipynb`** con dos iteraciones:
   - Primera versión: EDA básico con 12 variables seleccionadas
   - Segunda versión (final): EDA completo con narrativa y todas las variables agrupadas

3. **Estructura final del notebook** (11 secciones):
   - Sección 0: configuración y helper `plot_group()`
   - Sección 1: carga y vista previa
   - Sección 2: shape, tipos, nulos
   - Sección 3: estadísticas descriptivas con CV%
   - Sección 4: distribuciones de **todas las variables** en 6 grupos temáticos
   - Sección 5: tabla de posiciones y V/E/D por equipo
   - Sección 6: goles promedio por equipo y jornada
   - Sección 7: heatmap de correlaciones + top 15 pares
   - Sección 8: evolución temporal (resultados, xG, PPDA por jornada)
   - Sección 9: top 10 partidos por potencial ofensivo (proxy xG)
   - Sección 10: análisis complementario (cuotas, valor de plantilla, Elo, H2H, ventaja local)
   - Sección 11: conclusiones

### Decisiones tomadas

| Decisión | Razón |
|---|---|
| Distribuciones coloreadas por clase (H/D/A) | Más informativo que histogramas planos — muestra directamente qué tan bien separa cada variable |
| 6 grupos de variables por categoría | Cubre las 37 variables numéricas sin hacer una figura de 37 paneles ilegible |
| Narrativa en cada sección | El notebook es para portafolio: quien lo lea no tiene contexto previo |
| Sin feature engineering ni ajuste de modelos | El alcance definido es solo EDA |
| Jornada aproximada: `index // 10 + 1` | El dataset no tiene campo de jornada; 10 partidos/jornada en la PL |
| Colores oficiales Premier League | `#38003c` (morado), `#00ff85` (verde), `#e90052` (rosa) |
| Baseline de cuotas B365 | ~49–55% de precisión eligiendo al favorito — referencia para el futuro modelo |

### Hallazgos clave del EDA

1. `Elo_Diff` es la variable más discriminante: medianas claramente separadas entre H, D y A
2. Métricas `_L5` (últimas 5 jornadas) separan mejor las clases que las acumuladas de temporada
3. Los empates (D) tienen la menor separación en todas las variables — son el resultado más impredecible
4. Existe multicolinealidad entre `xG` / `npxG` y entre `Points_Avg` / `GD_Avg` (esperado)
5. La ventaja de local varía mucho por equipo (de ~25% a ~65%) — el equipo específico importa
6. Valor de plantilla correlaciona con rendimiento pero no de forma determinista

---

## Estado actual del proyecto

| Componente | Estado |
|---|---|
| Dataset (`fusion_dataset.csv`) | Listo — 319 partidos, 41 features |
| EDA (`EDA_premier_league.ipynb`) | Completo |
| Feature engineering | Pendiente |
| Modelo ML | Pendiente |
| Evaluación / comparativa con baseline | Pendiente |

---

## Estructura de archivos relevante

```
premier_league_predictor/
├── data/
│   ├── processed/
│   │   └── fusion_dataset.csv       ← dataset principal
│   └── raw/
├── notebooks/
│   └── EDA_premier_league.ipynb     ← EDA completo (sesión 2026-04-27)
├── models/
├── src/
└── CLAUDE.md
```

---

## Convenciones y preferencias del usuario

- El notebook es para **portafolio**: cada sección debe tener narrativa breve que dé contexto a alguien externo
- **Solo EDA en el notebook de EDA** — sin feature engineering ni recomendaciones de modelo dentro de ese archivo
- Librerías: pandas, matplotlib, seaborn, plotly (todas disponibles en el entorno)
- Las visualizaciones usan los colores de la Premier League definidos arriba
