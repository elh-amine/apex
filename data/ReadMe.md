# Données du projet APEX

Les datasets ne sont pas inclus dans ce repo (trop volumineux). Pour les régénérer :

## Steel Plates Faults (UCI)
```python
from ucimlrepo import fetch_ucirepo
steel = fetch_ucirepo(id=198)
```

## Bosch Production Line Performance (Kaggle)
Télécharger `train_numeric.csv` depuis :
https://www.kaggle.com/c/bosch-production-line-performance/data
Placer dans `data/bosch_subset/train_numeric.csv`

## AI4I 2020 (UCI)
https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset