# Couche 6A — Rapport Power BI

## Contexte
Rapport stratégique 5 pages, destiné à une lecture managériale/audit — complémentaire au
dashboard opérationnel Dash (lecture temps réel terrain).

## Connexion technique
Power BI Desktop connecté à `apex.db` (SQLite) via driver ODBC (SQLite3 ODBC Driver), DSN
utilisateur `apex_db`. Thème custom appliqué (`apex_automotive_theme.json`, palette
Navy/Rouge/Amber cohérente avec le dashboard Dash).

## Pages réalisées (adaptées par rapport au plan initial)
1. Executive Dashboard — KPI cards (PPM, FTQ, DPMO, Sigma) + Pareto interactif
2. DMAIC Analysis — Cp/Cpk sur scores ML (adaptation : pas de mesure process continue en
   base), heatmap corrélation (image importée du notebook), répartition alertes par process
3. SPC & Control — carte de contrôle sur defect_score dans le temps (adaptation : suivi de
   score ML comme variable continue plutôt qu'une mesure process brute), violations 3-sigma,
   jauge niveau sigma
4. ML Prédictif — scatter scores de risque, table alertes qualité, feature importance
   (image), alertes équipement actives
5. Audit Trail & 8D — tableau d'audit dmaic_results, renvoi vers Business Case interactif
   (Dash) et rapports PDF (API), résumé FMEA (image)

## Limite assumée et documentée
Plusieurs éléments prévus dans la fiche projet initiale (Cp/Cpk sur features process brutes,
PPM par ligne L0-L3, business case interactif natif Power BI) nécessitaient des données non
conservées dans le schéma SQLite actuel (raw_inspections ne stocke que defect_type/conformite,
pas les 27 features). Adaptation choisie : utiliser les scores ML comme variables de
substitution méthodologiquement valides, et renvoyer vers Dash pour l'interactivité native
que Power BI ne permet pas nativement (calcul dynamique par API).

## Publication
Rapport publié sur Power BI Service (Mon espace de travail), lien public généré via
"Publier sur le web".
Lien : [À COMPLÉTER après publication]

## Lien avec le reste du projet
Complète le dashboard Dash : Power BI = vue stratégique/audit pour un manager,
Dash = supervision opérationnelle temps réel pour un opérateur ligne.
