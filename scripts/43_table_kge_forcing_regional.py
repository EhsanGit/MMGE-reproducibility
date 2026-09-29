"""Reproduces tab:cdf-kge-forcing-regional: median streamflow KGE by region for each
precipitation forcing with the mHM model (summary of fig:cdf-kge-regional, panel b)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pandas as pd

from mmge.paths import data_file, TABLE_DIR
from mmge.regions import REGION_ORDER
from mmge.style import FORCINGS, FORCING_LABEL
from mmge.style import round_frame

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))
cols = [f'kge_mhm_{f}' for f in FORCINGS]
labels = [FORCING_LABEL[f] for f in FORCINGS]
medians = df.groupby('region')[cols].median()
medians.columns = labels
medians = medians.reindex(REGION_ORDER)


def classify_behaviour(row, min_spread=0.10):
    """Names the forcing that clearly leads or lags the other three, or 'Comparable'
    when the row's spread is small. Spread is the row's max minus its min."""
    spread = row.max() - row.min()
    if spread < min_spread:
        return 'Comparable', spread
    winner, loser = row.idxmax(), row.idxmin()
    winner_gap = row[winner] - row.drop(winner).max()
    loser_gap = row.drop(loser).min() - row[loser]
    behaviour = f'{winner} leads' if winner_gap >= loser_gap else f'{loser} lags'
    return behaviour, spread


behaviours, spreads = zip(*(classify_behaviour(row) for _, row in medians.iterrows()))
medians['Behaviour'] = behaviours
medians['Spread'] = spreads

out = round_frame(medians, 2)
out.index.name = 'Region'
out.loc['Highest-KGE region'] = [medians[f].idxmax() for f in labels] + ['', '']
out.to_csv(TABLE_DIR / 'cdf-kge-forcing-regional.csv')
print(out)
print('Saved output/tables/cdf-kge-forcing-regional.csv')
