# Data Dictionary: Premier League Predictor V3 (fusion_dataset.csv)

Este glosario define las **41 variables predictivas** creadas por la fusión de *Football-Data*, *Understat* y *ClubElo* para alimentar al algoritmo Lasso/Random Forest.

## 1. Identificadores y Contexto de Apuestas (7 Variables)
Estas columnas brindan la base de dónde y cuándo se juega, además del "saberes del mercado" de las casas de apuestas (muy útiles para inferir lesiones o cambios de última hora).

*   `Date`: Fecha del enfrentamiento.
*   `HomeTeam`: Nombre del equipo local.
*   `AwayTeam`: Nombre del equipo visitante.
*   `B365H`: Cuota de Victoria Local pagada por la Casa Apuestas Bet365.
*   `B365D`: Cuota de Empate pagada por Bet365.
*   `B365A`: Cuota de Victoria Visitante pagada por Bet365.
*   `Target_FTR`: (Nuestra Variable Objetivo) Resultado Real (H=Gana Local, D=Empata, A=Gana Visita).

## 2. Jerarquía Pura y Plantilla (3 Variables)
Variables matemáticas absolutas relativas al poder "espiritual" o económico.

*   `Elo_Diff`: *[Home_Elo - Away_Elo]* Métrica ajedrecística. Si es altamenete positiva indica gran favoritismo del Local. Si es negativa, el equipo Visita es muy superior.
*   `Home_SquadValue`: Valor de mercado en Millones de Euros de la plantilla Local al inicio de la Liga.
*   `Away_SquadValue`: Valor de mercado en Millones de Euros de la plantilla Visitante.

## 3. Head-To-Head (H2H) (2 Variables)
La historia pura y directa de rivalidad obtenida desde el 2018.

*   `H2H_Overall_L5`: (Pts ganados por equipo A vs B en los últimos 5 encuentros, restados). Valores positivos puros = "El HomeTeam es papá históricamente del AwayTeam en cualquier estadio".
*   `H2H_Venue_L5`: Exactamente lo mismo pero evaluando exclusivamente partidos donde el *HomeTeam* fue local, y el *AwayTeam* visitante. (Ej. El dominio de Anfield).

## 4. Totalidad Táctica de Temporada (Home=10, Away=9 Variables)
Estas son métricas acumuladas desde la Jornada 1 hasta este partido en específico, expresadas como **Promedios Puros (Averages)** para evitar sesgos de fechas pospuestas. Todas traen de forma idéntica su versión local (`H_`) o visitante (`A_`).

*   `[H/A]_Points_Avg_Tot`: Promedio de puntos de liga recogidos por encuentro.
*   `[H/A]_Goals_Scored_Avg_Tot`: Promedio de Goles que de hecho SÍ entraron a la red por encuentro.
*   `[H/A]_Goals_Against_Avg_Tot`: Promedio de Goles en contra permiditos por encuentro.
*   `[H/A]_GD_Avg_Tot`: (*Goal Difference*) Diferencia matemática de goles puros por partido.
*   `[H/A]_xG_Avg_Tot`: Promedio de los "Goles Esperados" generados táctiamente, entren o no entren a la red.
*   `[H/A]_npxG_Avg_Tot`: Promedio de xG **Sin Penales** (Rendimiento 100% natural del equipo en jugada viva).
*   `[H/A]_xPts_Avg_Tot`: Promedio de "Puntos Merecidos" según la suerte ofensiva. Un `xPts` gigante junto a un `Points` bajísimo demuestra muy mala suerte.
*   `[H/A]_PPDA_Avg_Tot`: Promedio de Asfixia o Intensidad Defensiva (Pases Permitidos por Acción Defensiva. Más bajo = Equipo más agresivo que presiona brutalmente).
*   `[H/A]_DeepComp_Avg_Tot`: Promedio de pases clavados peligrosamente adentro del área chica rival por partido (Indicador TOP de dominio Guardiola/Klopp).
*   `H_xG_GD_Avg_Tot`: *(Solo aplicable como resta absoluta Home-Away)*. Mismatch de Expected Goals. Distancia real de poder letal entre ambos en el torneo general.

## 5. Momentum y Forma Reciente (L5) (Home=3, Away=3 Variables)
La famosa "racha". A diferencia de Totales, estas no evalúan a los equipos en todo el torneo, sino estrictamente cómo vienen rindiendo de ánimo y suerte en sus recientes **5 encuentros**.

*   `[H/A]_Points_L5`: Suma de los puntos ganados (Racha Positiva, Racha de Derrotas) en 5 juegos.
*   `[H/A]_Goals_Scored_L5`: Goles anotados recientes. (Indica si los delanteros vienen encendidos o secos).
*   `[H/A]_Goals_Against_L5`: Goles recibidos recientes. (Indica si se acaban de quedar sin sus defensas titulares por lesiones recientes o expulsiones y la defensa colapsó).

## 6. Posición Histórica (Absolutos) (Home=2, Away=2 Variables)
Métricas brutas para reconstruir la clásica "Posición en la Tabla de la Premier". Sumas acumuladas directas.

*   `[H/A]_Points_Abs_Tot`: Puntos reales brutos que tiene el equipo acumulados antes del silbatazo.
*   `[H/A]_GD_Abs_Tot`: Diferencia general real que les da su posición en la tabla de clasificación.
