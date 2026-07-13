# Module C — Maintenance prédictive équipements (AI4I 2020)

## Contexte métier
Prédire la panne d'un équipement de ligne (presse d'emboutissage, robot de soudure) à partir de
ses paramètres de fonctionnement, avant qu'elle ne survienne.

## Données
- 10 000 cycles machine, 5 features numériques (température air/process, vitesse rotation,
  couple, usure outil) + type de machine (L/M/H)
- Label : Machine failure (0/1), 3.39% de pannes (339/10000)
- 5 sous-types de panne (TWF, HDF, PWF, OSF, RNF) disponibles mais non utilisés comme cible
  directe : 9 pannes n'ont aucun sous-type actif (pannes aléatoires RNF sans cause assignable,
  comportement volontaire du dataset) — on prédit donc le label global Machine failure,
  plus robuste et plus proche d'un cas d'usage industriel réel

## Démarche
Split stratifié 80/20 → standardisation → SMOTE (déséquilibre modéré 3.39%) → comparaison
Random Forest vs XGBoost

## Résultats
| Modèle | F1-macro | AUC |
|---|---|---|
| **XGBoost** | **0.872** | 0.964 |
| Random Forest | 0.809 | 0.977 |

XGBoost retenu : meilleur équilibre précision/rappel sur la classe panne (précision 71%,
rappel 81%).

## Lien avec le reste du projet APEX
- Alimente l'endpoint API `POST /predict-defect` équivalent équipement (RUL/alerte)
- Modèle sauvegardé : `models/module_c_equipment_classifier.pkl`
## Feature importance — enseignement métier

| Feature | Importance |
|---|---|
| Rotational speed [rpm] | 0.343 |
| Torque [Nm] | 0.264 |
| Tool wear [min] | 0.199 |
| Type_encoded | 0.083 |
| Air temperature [K] | 0.066 |
| Process temperature [K] | 0.045 |

La vitesse de rotation et le couple dominent (~61% de l'importance cumulée) — cohérent
mécaniquement : une combinaison anormale vitesse/couple est le signal le plus direct d'une
contrainte mécanique excessive sur la presse. Les températures ont un poids marginal.
Point réutilisable dans le FMEA/Ishikawa : cause dominante rattachée à la branche "Machine"
plutôt qu'à "Milieu".