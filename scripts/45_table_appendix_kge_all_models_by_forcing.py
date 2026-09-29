"""Reproduces tab:appendix-kge-all-models-by-forcing: median streamflow KGE by region,
model and forcing (full breakdown of fig:appendix-kge-all-models-by-forcing)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pandas as pd

from mmge.paths import data_file, TABLE_DIR
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL, FORCINGS, FORCING_LABEL
from mmge.style import round_frame

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))

rows = []
for region in REGION_ORDER:
    for m in MODELS:
        row = {'Region': region, 'Model': MODEL_LABEL[m]}
        for f in FORCINGS:
            row[FORCING_LABEL[f]] = df.loc[df['region'] == region, f'kge_{m}_{f}'].median()
        rows.append(row)
table = pd.DataFrame(rows)
forcing_cols = [FORCING_LABEL[f] for f in FORCINGS]
table[forcing_cols] = round_frame(table[forcing_cols], 2)

# Best forcing per model-region (bolded on the value in the manuscript table) and
# best-performing model per region (bolded on the model name).
table['best_forcing'] = table[forcing_cols].idxmax(axis=1)
best_model = (table.set_index(['Region', 'Model'])[forcing_cols].mean(axis=1)
              .groupby('Region').idxmax().apply(lambda t: t[1]))
table['region_best_model'] = table['Region'].map(best_model)

table.to_csv(TABLE_DIR / 'appendix-kge-all-models-by-forcing.csv', index=False)
print(table.to_string(index=False))

print('\nHighest-KGE region per forcing column (max cell over all region-model rows):')
for f in FORCINGS:
    col = FORCING_LABEL[f]
    print(f'  {col}: {table.loc[table[col].idxmax(), "Region"]} ({table[col].max():.2f})')

print('\nSaved output/tables/appendix-kge-all-models-by-forcing.csv')
