"""Reproduces figures/cdf_multimodel_ensemble_kge_era5land.png (fig:appendix-multimodel-ensemble):
regional CDF of streamflow KGE with ERA5-Land forcing, the four individual models against the
ensemble mean and median of their combined simulated discharge."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from mmge.paths import data_file
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL, PALETTE_MODELS, plot_cdf, sort_cdf, \
    style_region_grid, savefig

ENSEMBLE_GREY = '#4d4d4d'

df = pd.read_csv(data_file('kge', 'multimodel_ensemble_kge_gauges_era5land.csv'))
model_cols = [f'kge_{m}' for m in MODELS]
groups = {region: sub for region, sub in df.groupby('region')}

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(13, 8.5), sharey=True, sharex=True)
axes = axes.flatten()
for ax, region in zip(axes, REGION_ORDER):
    sub = groups[region]
    models = sub[model_cols].copy()
    models.columns = [MODEL_LABEL[m] for m in MODELS]
    plot_cdf(models, ax=ax, xlim=[-0.41, 1], palette=PALETTE_MODELS)

    for col, ls, lab in [('kge_ensemble_mean', '-', 'Ensemble mean'),
                          ('kge_ensemble_median', '--', 'Ensemble median')]:
        values = sub[col].dropna().values
        ax.plot(*sort_cdf(values), label=lab, linewidth=2.2, color=ENSEMBLE_GREY,
                 linestyle=ls, zorder=5)

    if ax is axes[-1]:
        ax.legend(fontsize=8, loc='lower right')
    ax.set_title(region, fontsize=11, fontweight='bold')
    n = sub['kge_ensemble_mean'].notna().sum()
    ax.text(0.03, 0.97, f'n={n}', transform=ax.transAxes, fontsize=9, va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
    ax.set_xticks(np.arange(-0.4, 1.2, 0.2))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(0.1))

style_region_grid(fig, axes)

savefig(fig, 'cdf_multimodel_ensemble_kge_era5land')
