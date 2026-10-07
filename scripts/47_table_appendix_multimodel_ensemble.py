"""Reproduces tab:appendix-multimodel-ensemble-regional: median streamflow KGE by region
with ERA5-Land forcing for the four individual models against the ensemble mean and median
of their combined simulated discharge (fig:appendix-multimodel-ensemble). Behaviour and
Spread are computed across the four individual models only."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pandas as pd

from mmge.paths import data_file, TABLE_DIR
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL
from mmge.style import round_half_away
from mmge.style import round_frame

df = pd.read_csv(data_file('kge', 'multimodel_ensemble_kge_gauges_era5land.csv'))

model_cols = [f'kge_{m}' for m in MODELS]
labels = [MODEL_LABEL[m] for m in MODELS]
medians = df.groupby('region')[model_cols + ['kge_ensemble_mean', 'kge_ensemble_median']].median()
medians.columns = labels + ['Ens. mean', 'Ens. median']
medians = medians.reindex(REGION_ORDER)


def classify_spread(row, low=0.15, high=0.35):
    """Classifies model agreement from the row's spread (max minus min); same
    convention and thresholds used throughout this analysis for the individual
    models' own agreement/disagreement."""
    row = row.map(lambda v: round_half_away(v, 2))
    spread = round_half_away(row.max() - row.min(), 2)
    if spread < low:
        return 'Agree', spread
    elif spread < high:
        return 'Moderate disagreement', spread
    return 'Disagree', spread


behaviours, spreads = zip(*(classify_spread(row[labels]) for _, row in medians.iterrows()))
medians['Behaviour'] = behaviours
medians['Range'] = spreads

out = round_frame(medians, 2)
out.index.name = 'Region'
out.to_csv(TABLE_DIR / 'appendix-multimodel-ensemble-regional.csv')
print(out)
print('Saved output/tables/appendix-multimodel-ensemble-regional.csv')
