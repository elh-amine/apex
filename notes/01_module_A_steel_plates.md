# Module A — Classification des défauts de carrosserie (Steel Plates Faults)

## Contexte métier

Sur une ligne d'assemblage automobile, chaque panneau de carrosserie (portière, capot, aile...)
sortant de la presse d'emboutissage passe devant un système de vision industrielle qui inspecte
sa surface. L'objectif de ce module est de simuler ce système : à partir des mesures géométriques
et optiques capturées par la caméra, prédire automatiquement le type de défaut détecté, sans
intervention humaine.

Dans une vraie usine (Stellantis, Renault, équipementier Tier-1), ce module remplacerait ou
compléterait l'inspection visuelle manuelle, et permettrait de tracer automatiquement chaque
défaut dans la GPAO (Gestion de Production Assistée par Ordinateur).

## Données utilisées

- **Source** : Steel Plates Faults (UCI ML Repository, id=198), licence CC BY 4.0
- **Volume** : 1941 pièces inspectées
- **Features** : 27 mesures géométriques et optiques par pièce (position du défaut, surface en
  pixels, périmètre, luminosité min/max/moyenne, indices dérivés comme l'orientation ou la
  log-transformée de la surface)
- **Labels** : 7 types de défauts (one-hot), reframés en contexte automobile :
  - Z_Scratch / K_Scratch → rayures de carrosserie
  - Stains / Dirtiness → taches / salissures
  - Bumps → bosses / déformations
  - Pastry → mauvaise découpe
  - Other_Faults → défauts divers non catégorisés

## Constat clé de l'EDA

- Dataset fortement déséquilibré : Other_Faults (34.7%) et Bumps (20.7%) dominent, alors que
  Dirtiness ne représente que 2.8% des pièces
- Aucune feature seule ne sépare parfaitement les 7 types (confirmé via boxplots) : Pixels_Areas
  isole bien K_Scratch (grand) et Stains (petit), mais les 5 autres types se chevauchent → 
  justifie le recours au ML plutôt qu'à des règles de seuils simples

## Démarche

1. Fusion features (X) + labels (y) en un seul DataFrame exploitable
2. Split train/test stratifié (80/20) pour préserver les proportions de classes
3. Standardisation des features (StandardScaler) — écarts d'échelle énormes détectés en EDA
   (certaines colonnes en millions, d'autres entre -1 et 1)
4. Rééquilibrage des classes via SMOTE (uniquement sur le train, jamais sur le test)
5. Entraînement et comparaison de 3 modèles : Decision Tree (baseline), Random Forest, XGBoost
6. Évaluation via F1-macro (adapté aux classes déséquilibrées, contrairement à l'accuracy brute)

## Résultats

| Modèle | F1-macro |
|---|---|
| **Random Forest** | **0.841** ← modèle retenu |
| XGBoost | 0.814 |
| Decision Tree | 0.733 |

Note : la littérature sur ce dataset donne généralement XGBoost comme meilleur modèle, mais le
benchmark empirique sur ce projet montre l'inverse — probablement lié à la taille limitée du
dataset (XGBoost nécessite plus de données ou un tuning plus poussé pour exprimer son potentiel).

## Feature importance — enseignement métier

- `LogOfAreas` (taille du défaut, log-transformée) est de très loin la feature la plus
  discriminante (importance ~0.35, plus du double de la 2e feature)
- `TypeOfSteel_A300` (type de tôle) arrive en 2e position (~0.12) → le type de matière première
  utilisée en emboutissage a un impact direct sur la nature des défauts observés

## Lien avec le reste du projet APEX

- Ce modèle alimentera l'endpoint API `POST /predict-defect`
- Le constat sur `TypeOfSteel_A300` est réutilisable dans le FMEA (cause matière) et le diagramme
  Ishikawa (branche "Matière")
- Le F1-macro et la matrice de confusion seront affichés dans la page 4 du rapport Power BI
  ("ML Prédictif")
- Modèle et scaler sauvegardés dans `models/module_a_defect_classifier.pkl` et
  `models/module_a_scaler.pkl`, réutilisables tels quels par l'API FastAPI (couche 5)