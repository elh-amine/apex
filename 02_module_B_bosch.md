# Module B — Prédiction Go/No-Go (Bosch Production Line)

## Contexte métier

Ce module simule un système d'alerte précoce sur une ligne d'assemblage automobile : prédire
qu'une pièce va échouer au contrôle qualité final, dès son entrée en ligne, avant qu'elle
n'accumule de la valeur ajoutée à travers tous les postes. Dans une vraie usine, ça permettrait
d'arrêter ou de dérouter une pièce à risque avant qu'elle n'atteigne le contrôle final, évitant
ainsi une retouche coûteuse ou une mise au rebut.

## Données utilisées

- **Source** : Bosch Production Line Performance (Kaggle), fichier `train_numeric.csv` uniquement
- **Volume original** : ~1.18M pièces, 970 features numériques (fichiers dates et catégoriels
  écartés pour ce projet, volume/complexité trop élevés pour un portfolio)
- **Sous-échantillon utilisé** : 118 375 pièces (chargement par chunks de 50k, échantillon
  aléatoire 10% par chunk pour ne pas saturer la RAM)
- **Structure des colonnes** : format `L{ligne}_S{station}_F{numéro}` — la ligne et la station
  sont directement encodées dans le nom de la colonne
- **Label** : `Response` (0 = conforme, 1 = défectueuse)

## Constats clés de l'EDA

- Déséquilibre extrême : seulement 0.58% de pièces défectueuses (690 sur 118 375) — bien plus
  sévère que Steel Plates (2.8%)
- 80.9% de valeurs manquantes en moyenne — normal et attendu : chaque pièce ne passe que par
  certaines stations selon son parcours dans la ligne, ce n'est pas une donnée corrompue
- 4 lignes de production identifiées : L0, L1, L2, L3

## Démarche

1. Filtrage des colonnes à >90% de valeurs manquantes → 970 → 332 colonnes
2. Imputation des valeurs manquantes restantes par 0 (absence de mesure = pièce non passée par
   ce capteur)
3. Split train/test stratifié (80/20) — critique vu le déséquilibre extrême
4. Sélection des 80 features les plus importantes via un XGBoost rapide (plutôt que SMOTE,
   `scale_pos_weight` utilisé pour gérer le déséquilibre sans données synthétiques)
5. Entraînement XGBoost et LightGBM sur les 80 features retenues
6. Optimisation du seuil de décision (recherche du seuil maximisant le MCC, plutôt que le
   seuil par défaut de 0.5)

## Résultats

| Étape | MCC |
|---|---|
| XGBoost, seuil 0.5 | 0.037 |
| LightGBM, seuil 0.5 | 0.045 |
| **XGBoost, seuil optimal (0.84)** | **0.131** |

Avec le seuil optimisé : précision de 31% sur la classe défectueuse (contre 2% au seuil par
défaut), au prix d'un rappel plus faible (6%) — le modèle devient plus prudent et fiable dans
ses alertes, mais détecte une fraction plus restreinte des vraies pièces défectueuses.

## Limites et discussion honnête

Le MCC obtenu (0.131) reste en dessous du repère du leaderboard Kaggle (0.35-0.50). Écart
expliqué principalement par :
- Sous-échantillon de 118k lignes contre 1.18M pour les équipes du concours (10x moins de
  données, donc 10x moins d'exemples positifs pour apprendre le signal rare)
- Fichiers dates et catégoriels écartés (auraient permis un feature engineering temporel plus
  riche, mais complexité jugée disproportionnée pour un projet portfolio)
- Choix assumé : privilégier un pipeline complet et compréhensible plutôt qu'une optimisation
  poussée sur un seul module

## Feature importance — enseignement métier

- La station **S30 de la ligne L3** revient très fréquemment dans le top des features
  importantes → point de procédé à surveiller en priorité, piste concrète pour une action
  qualité ciblée (analyse de cause racine sur cette station)
- D'autres stations notables : L0_S9, L0_S12, L2_S26, L1_S24

## Lien avec le reste du projet APEX

- Alimentera l'endpoint API `POST /go-nogo`
- L'observation sur la station L3_S30 est réutilisable dans le FMEA et l'Ishikawa (branche
  Machine/Méthode)
- Sert de base au calcul du PPM par ligne de production (endpoint `/ppm`)
- Modèle, features sélectionnées et seuil optimal sauvegardés dans `models/module_b_*.pkl`