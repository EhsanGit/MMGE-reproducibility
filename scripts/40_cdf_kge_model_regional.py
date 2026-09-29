"""Reproduces figures/cdf_model_kge_continents.png, panel (a) of fig:cdf-kge-regional:
regional CDF of streamflow KGE for each hydrological model with ERA5-Land forcing."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from mmge.paths import data_file
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL, PALETTE_MODELS, plot_cdf, style_region_grid, savefig

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))
data = df[['region'] + [f'kge_{m}_era5land' for m in MODELS]].copy()
data.columns = ['region'] + [MODEL_LABEL[m] for m in MODELS]

groups = {region: sub for region, sub in data.groupby('region')}

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(12, 8), sharey=True, sharex=True)
axes = axes.flatten()
for ax, region in zip(axes, REGION_ORDER):
    sub = groups[region].drop(columns='region')
    plot_cdf(sub, ax=ax, xlim=[-0.41, 1], palette=PALETTE_MODELS)
    if ax is axes[-1]:
        ax.legend(fontsize=9, loc='lower right')
    ax.set_title(region, fontsize=11, fontweight='bold')
    n = len(sub)
    ax.text(0.03, 0.97, f'n={n}', transform=ax.transAxes, fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
    ax.set_xticks(np.arange(-0.4, 1.2, 0.2))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))

style_region_grid(fig, axes)

top_left_pos = axes[0].get_position()
fig.text(top_left_pos.x0, top_left_pos.y1 + 0.012, 'a', fontsize=16, fontweight='bold',
          va='bottom', ha='left')

savefig(fig, 'cdf_model_kge_continents')
