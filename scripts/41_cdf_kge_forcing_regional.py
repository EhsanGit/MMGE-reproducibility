"""Reproduces figures/cdf_forcings_kge_continents.png, panel (b) of fig:cdf-kge-regional:
regional CDF of streamflow KGE for mHM with each of the four precipitation forcings."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from mmge.paths import data_file
from mmge.regions import REGION_ORDER
from mmge.style import FORCINGS, FORCING_LABEL, plot_cdf, style_region_grid, savefig

# Forcings palette matching the manuscript source (gold/teal/rose/forest-green), a
# separate hue family from PALETTE_MODELS.
FORCING_PALETTE = ['#c99a2e', '#00a3a3', '#d6336c', '#2f6b2f']

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))
data = df[['region'] + [f'kge_mhm_{f}' for f in FORCINGS]].copy()
data.columns = ['region'] + [FORCING_LABEL[f] for f in FORCINGS]

groups = {region: sub for region, sub in data.groupby('region')}

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 8), sharey=True, sharex=True)
axes = axes.flatten()
for ax, region in zip(axes, REGION_ORDER):
    sub = groups[region].drop(columns='region')
    plot_cdf(sub, ax=ax, xlim=[-0.41, 1], palette=FORCING_PALETTE)
    if ax is axes[-1]:
        ax.legend(fontsize=9, loc='lower right')
    ax.set_title(region, fontsize=11, fontweight='bold')
    ax.set_xticks(np.arange(-0.4, 1.2, 0.2))
    n = sub.dropna(how='all').shape[0]
    ax.text(0.03, 0.97, f'n={n}', transform=ax.transAxes, fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))

style_region_grid(fig, axes)

top_left_pos = axes[0].get_position()
fig.text(top_left_pos.x0, top_left_pos.y1 + 0.012, 'b', fontsize=16, fontweight='bold',
          va='bottom', ha='left')

savefig(fig, 'cdf_forcings_kge_continents')
