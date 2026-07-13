# Couche 4 — Base de données SQLite & KPIs DMAIC

## Structure
4 tables créées : raw_inspections, dmaic_results, ml_quality_scores, equipment_alerts.
Peuplées à partir des 3 modules ML déjà entraînés (modèles rechargés via joblib, pas
ré-entraînés).

## KPIs calculés

| KPI | Valeur | Cible | Statut |
|---|---|---|---|
| PPM emboutissage | 1 000 000 | 500 | Hors cible |
| DPMO assemblage | 5828.93 | 500 | Hors cible |
| Taux panne équipement | 3.39% | 2.0% | Hors cible |

## Point de vigilance — PPM emboutissage

Ce chiffre (1 000 000 PPM, soit 100%) est un artefact du dataset Steel Plates Faults, qui ne
contient QUE des pièces défectueuses par construction (créé à l'origine pour la classification
de type de défaut, pas pour mesurer un taux de rebut réel). Ce n'est donc pas un KPI qualité
représentatif à présenter tel quel — il doit être expliqué avec ce contexte dans le rapport
final et le dashboard, pour ne pas induire en erreur.

Le KPI qualité réellement exploitable et représentatif du projet est le DPMO_assemblage
(5828.93), calculé sur le dataset Bosch qui contient à la fois pièces conformes et défectueuses.