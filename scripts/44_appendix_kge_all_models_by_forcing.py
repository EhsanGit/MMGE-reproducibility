"""Reproduces figures/appendix_cdf_kge_all_models_by_forcing.png
(fig:appendix-kge-all-models-by-forcing): regional CDF of streamflow KGE for all four
models (rows: forcing, columns: region), complete gauge coverage."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from mmge.paths import data_file
from mmge.regions import REGION_ORDER
from mmge.style import MODELS, MODEL_LABEL, FORCINGS, FORCING_LABEL, PALETTE_MODELS, \
    plot_cdf, GRIDLINE_COLOR, savefig

df = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))

fig, axes = plt.subplots(nrows=4, ncols=6, figsize=(20, 13), sharey=True, sharex=True)

for row_i, forcing in enumerate(FORCINGS):
    cols = [f'kge_{m}_{forcing}' for m in MODELS]
    data = df[['region'] + cols].copy()
    data.columns = ['region'] + [MODEL_LABEL[m] for m in MODELS]
    groups = {region: sub for region, sub in data.groupby('region')}
    for col_i, region in enumerate(REGION_ORDER):
        ax = axes[row_i, col_i]
        sub = groups[region].drop(columns='region')
        plot_cdf(sub, ax=ax, xlim=[-0.41, 1], palette=PALETTE_MODELS)
        ax.set_xticks(np.arange(-0.4, 1.2, 0.2))
        ax.grid(True, color=GRIDLINE_COLOR, linewidth=0.7, alpha=0.8, zorder=0)
        ax.set_axisbelow(True)
        n = sub.dropna(how='all').shape[0]
        ax.text(0.03, 0.97, f'n={n}', transform=ax.transAxes, fontsize=8, va='top', ha='left',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.85, edgecolor='0.6'))
        if row_i == 0:
            ax.set_title(region, fontsize=10, fontweight='bold')
        if col_i == 0:
            ax.set_ylabel(FORCING_LABEL[forcing], fontsize=11, fontweight='bold')
        else:
            ax.set_ylabel('')
        if row_i != 3:
            ax.set_xlabel('')
            ax.tick_params(axis='x', labelbottom=False)
        else:
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()
            if col_i == 5:
                ax.legend(fontsize=8, loc='lower right')

fig.subplots_adjust(hspace=0.12, wspace=0.10)
fig.suptitle('Regional CDF of KGE, all four models x all four forcings (complete gauge coverage)',
             fontsize=13, fontweight='bold', y=1.0)

savefig(fig, 'appendix_cdf_kge_all_models_by_forcing')
