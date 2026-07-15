# Couches 5 & 6B — API FastAPI & Dashboard Plotly Dash (Floor Monitoring)

## Contexte métier

Ces deux couches transforment les résultats bruts stockés dans `apex.db` (couche 4) en un
véritable outil de pilotage utilisable par un opérateur ou un responsable qualité sur le
terrain. L'API sert de pont technique : elle interroge la base et applique les modèles ML en
temps réel, pendant que le dashboard Dash affiche ces informations dans une interface visuelle
inspirée d'un poste de contrôle industriel ("cockpit" thème sombre).

Dans une vraie usine automobile, ce type d'outil serait affiché sur un écran au poste de
supervision de ligne, permettant à l'opérateur de voir en continu si la production dérive vers
la non-qualité, sans avoir à interroger manuellement une base de données ou un rapport.

## Architecture mise en place
apex.db (SQLite)  →  FastAPI (port 8000)  →  Plotly Dash (port 8050)  →  Navigateur
[couche 4]           [couche 5]              [couche 6B]
L'API et le dashboard sont deux processus Python indépendants, lancés dans deux terminaux
séparés en parallèle. Le dashboard interroge l'API via des requêtes HTTP (`requests`), jamais
directement la base — ce découplage permet à Power BI (couche 6A) de consommer les mêmes
données via la même base, sans dépendre du dashboard.

## Couche 5 — FastAPI, endpoints réalisés

- **KPIs** : `/ppm`, `/ftq`, `/oee`, `/dpmo` — calculés à partir des tables `dmaic_results` et
  `raw_inspections`
- **Analyse qualité** : `/pareto-defects` (avec cumul 80/20), `/spc-chart/{feature}` (cartes de
  contrôle avec détection de violation aux limites 3-sigma), `/fmea` (tableau FMEA structuré)
- **Machine Learning en temps réel** : `/predict-defect` (POST, Module A rechargé), `/go-nogo`
  (POST, Module B rechargé), `/ml-scores` et `/equipment-alerts` (lecture des scores déjà en
  base)
- **Rapports PDF générés à la demande** : `/quality-report` (8D complet), `/control-plan`
- **Simulation business** : `/business-case` (économie estimée selon la station de détection du
  défaut)

## Couche 6B — Dashboard Dash, 5 onglets

Thème sombre "cockpit" (palette Navy/Rouge définie dans `apex_style.css`), rafraîchissement
automatique toutes les 10 secondes (`dcc.Interval`) pour simuler un flux de production en
temps réel :
1. **Line Overview** : KPI cards (PPM, FTQ, OEE, Niveau Sigma) + Pareto interactif
2. **Qualité / SPC** : carte de contrôle avec sélecteur de feature
3. **ML Prédictif** : tables des dernières alertes qualité et équipement
4. **FMEA Live** : tableau avec mise en forme conditionnelle par niveau de RPN
5. **Rapports** : génération PDF à la volée + calculateur de business case interactif (slider)

## Résultat obtenu (premier rendu validé)

Capture d'écran de l'onglet "Line Overview" :
- PPM Emboutissage : 1 000 000 (rappel : artefact du dataset Steel Plates, déjà documenté en
  couche 4 — à expliciter à l'oral/rapport, pas un vrai taux de rebut usine)
- FTQ : 0.0% et OEE : 0.0% — cohérents avec le PPM ci-dessus (base 100% de pièces "non
  conformes" dans ce dataset précis)
- Niveau Sigma : 4.02σ — calculé à partir du DPMO réel du dataset Bosch (donnée qualité
  représentative du projet)
- Pareto des défauts : rendu correctement, hiérarchie confirmée (Other_Faults > Bumps >
  K_Scratch > Z_Scratch...), courbe de cumul 80/20 fonctionnelle

## Problèmes rencontrés et résolus

1. **Import inter-fichiers cassé sous Windows avec `uvicorn --reload`** : le rechargeur
   automatique ne résolvait pas les imports entre `main.py`, `schemas.py` et `pdf_reports.py`
   → solution : fusion de tout le code API dans un seul fichier `main.py`
2. **Incohérence des noms de colonnes lors de la prédiction ML** (`/predict-defect`) : l'ordre
   des champs Pydantic ne correspondait pas à l'ordre appris par le `StandardScaler` → solution :
   réordonnancement explicite via `scaler_a.feature_names_in_` avant transformation
3. **Librairies installées dans le mauvais environnement** (Python global au lieu du venv) à
   deux reprises (`ucimlrepo`, puis `dash`) → cause récurrente : installation lancée avant
   activation du venv — point de vigilance à garder pour la suite du projet
4. **Dashboard inaccessible aux données** : nécessité de garder l'API et le dashboard actifs
   simultanément dans deux terminaux séparés — organisation de travail à maintenir jusqu'à la
   fin du projet

## Lien avec le reste du projet APEX

- Cette double couche (API + Dash) constitue le livrable "dashboard opérationnel" mentionné
  dans l'argumentaire CV/entretien
- Réutilise directement les 3 modèles ML (couche 3) et la base unifiée (couche 4), validant
  que l'architecture en couches fonctionne de bout en bout
- Reste à faire : Power BI (couche 6A, rapport stratégique) et enrichissement DMAIC avancé
  (SPC Western Electric complet, Ishikawa, MSA/Gauge R&R) si le temps le permet
  