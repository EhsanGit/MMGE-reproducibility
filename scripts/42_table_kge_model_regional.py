"""Reproduces tab:cdf-kge-model-regional: median streamflow KGE by region for each
hydrological model with ERA5-Land forcing (summary of fig:cdf-kge-regional, panel a)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pandas as pd

from mmge.paths import data_file, TABLE_DIR
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL
from mmge.style import round_frame, round_half_away

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))
cols = [f'kge_{m}_era5land' for m in MODELS]
labels = [MODEL_LABEL[m] for m in MODELS]
medians = df.groupby('region')[cols].median()
medians.columns = labels
medians = medians.reindex(REGION_ORDER)


def classify_behaviour(row, min_range=0.15, disagree_range=1.0, lag_gap=0.3):
    """Behaviour label from the rounded medians of one region: 'Models disagree' when the
    range across the models exceeds disagree_range, 'Comparable' when it is below min_range,
    otherwise the model that lags by more than lag_gap or, failing that, the leading model."""
    row = row.map(lambda v: round_half_away(v, 2))
    spread = round_half_away(row.max() - row.min(), 2)
    if spread > disagree_range:
        return 'Models disagree', spread
    if spread < min_range:
        return 'Comparable', spread
    winner, loser = row.idxmax(), row.idxmin()
    if row.drop(loser).min() - row[loser] > lag_gap:
        return f'{loser} lags', spread
    return f'{winner} leads', spread


behaviours, spreads = zip(*(classify_behaviour(row) for _, row in medians.iterrows()))
medians['Behaviour'] = behaviours
medians['Range'] = spreads

out = round_frame(medians, 2)
out.index.name = 'Region'
out.loc['Highest-KGE region'] = [medians[m].idxmax() for m in labels] + ['', '']
out.to_csv(TABLE_DIR / 'cdf-kge-model-regional.csv')
print(out)
print('Saved output/tables/cdf-kge-model-regional.csv')
