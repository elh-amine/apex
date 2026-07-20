# ▲ APEX — Automotive Process EXcellence Platform

**Plateforme de contrôle qualité prédictif & Zéro Défaut pour ligne d'assemblage automobile**

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi)
![Dash](https://img.shields.io/badge/Plotly-Dash-3F4F75?logo=plotly)
![Power BI](https://img.shields.io/badge/Power%20BI-Report-F2C811?logo=powerbi)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-EB5E28)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Contexte

APEX simule un système de contrôle qualité intelligent sur une ligne d'assemblage automobile
fictive (carrosserie, assemblage, équipements de production), en appliquant la méthodologie
**DMAIC** et les référentiels **IATF 16949 / APQP** propres à l'industrie automobile.

Le projet répond à un enjeu industriel réel : le coût de la non-qualité représente
typiquement 5 à 15% du chiffre d'affaires d'un site automobile, et une pièce détectée en fin
de ligne coûte jusqu'à 10x plus cher à corriger qu'un défaut détecté à la source.

Ce projet a été réalisé en autonomie complète, données publiques réelles à l'appui, comme
projet portfolio orienté vers un poste d'ingénieur qualité/amélioration continue dans
l'industrie automobile (Stellantis, Renault, équipementiers Tier-1).

---

## 🏗️ Architecture — 6 couches

```
Données (Steel Plates · Bosch · AI4I 2020)
        ↓
DMAIC / Lean (PPM · DPMO · SPC · Pareto · FMEA · 8D)
        ↓
Machine Learning (Classification défauts · Go/No-go · Maintenance prédictive)
        ↓
SQLite — base unique (raw_inspections · dmaic_results · ml_quality_scores · equipment_alerts)
        ↓                                    ↓
FastAPI (REST + PDF)              Power BI (rapport stratégique 5 pages)
        ↓
Plotly Dash (dashboard opérationnel temps réel, 5 onglets)
```

---

## 📊 Les 3 modules Machine Learning

| Module | Dataset | Objectif | Résultat |
|---|---|---|---|
| **A — Classification défauts** | Steel Plates Faults (UCI) | Identifier automatiquement 7 types de défauts carrosserie | Random Forest, **F1-macro = 0.841** |
| **B — Go/No-go qualité** | Bosch Production Line (Kaggle) | Prédire la non-conformité avant contrôle final | XGBoost, **MCC = 0.131** (seuil optimisé) |
| **C — Maintenance prédictive** | AI4I 2020 (UCI) | Prédire les pannes d'équipement de ligne | XGBoost, **F1-macro = 0.872**, AUC = 0.964 |

Détails complets, démarche et limites de chaque module : voir [`notes/`](notes/).

---

## 🖥️ Aperçu

### Dashboard Plotly Dash — Floor Monitoring
*(Insère ici une capture d'écran de l'onglet Line Overview)*

### Rapport Power BI — Quality Management
*(Insère ici une capture d'écran d'une page du rapport)*
**Démo en ligne :** [lien Power BI Service à compléter]

---

## 🛠️ Stack technique

- **Langage** : Python 3.13
- **Machine Learning** : scikit-learn, XGBoost, LightGBM, imbalanced-learn (SMOTE)
- **API** : FastAPI, Uvicorn, Pydantic
- **Visualisation** : Plotly Dash, Power BI Desktop/Service
- **Base de données** : SQLite
- **Génération PDF** : ReportLab
- **Données** : UCI ML Repository (`ucimlrepo`), Kaggle

---

## 📁 Structure du projet

```
apex/
├── data/                    # Datasets (non versionnés, voir data/README.md)
├── notebooks/               # EDA et entraînement ML (Jupyter)
├── notes/                   # Documentation détaillée par module
├── src/api/                 # API FastAPI (main.py)
├── dashboard/               # Plotly Dash (app.py + assets)
├── powerbi/                 # Rapport Power BI (.pbix) + thème JSON
├── reports/                 # PDF générés (8D, Control Plan) + visuels
├── models/                  # Modèles ML sauvegardés (joblib)
└── requirements.txt
```

---

## 🚀 Installation et lancement

### 1. Cloner le repo
```bash
git clone https://github.com/elh-amine/apex.git
cd apex
```

### 2. Environnement virtuel
```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

### 3. Récupérer les données
Voir [`data/README.md`](data/README.md) pour les instructions de téléchargement
(Steel Plates Faults, Bosch Production Line, AI4I 2020).

### 4. Lancer l'API (terminal 1)
```bash
cd src/api
uvicorn main:app --reload
```
→ Documentation interactive : http://127.0.0.1:8000/docs

### 5. Lancer le dashboard (terminal 2)
```bash
cd dashboard
python app.py
```
→ http://127.0.0.1:8050

---

## 📈 Méthodologie DMAIC appliquée

- **Définir** : Charte de projet, SIPOC, Voice of Customer, KPIs (PPM, DPMO, FTQ, OEE)
- **Mesurer** : Cp/Cpk, PPM/DPMO par type de défaut, niveau Sigma
- **Analyser** : Pareto des défauts, corrélations, cartes SPC (règles Western Electric)
- **Innover** : Seuils d'alerte ML, recommandations d'action, business case par station
- **Contrôler** : Control Plan auto-généré, rapport 8D auto-généré (PDF), FMEA

---

## 🎓 Auteur

**El-Houssni Mohamed Amine** — ENSMR, Génie Productique
Projet réalisé dans le cadre d'un portfolio orienté PFE automobile.

📧 [ton email] · 🔗 [LinkedIn] · 💻 [GitHub](https://github.com/elh-amine)

---

## 📄 Licence

Ce projet est distribué sous licence MIT — voir [LICENSE](LICENSE) pour plus de détails.
Les datasets utilisés (UCI, Kaggle) restent soumis à leurs licences respectives.