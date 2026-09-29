"""Reproduces Appendix Figure B2 (\\label{fig:appendix-acc-by-model}):
standardised ACC for each model (rows), for simulated TWSa vs GravIS,
ET vs FLUXCOM and runoff vs GRUN (columns), each panel the ensemble mean
across the four forcings.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from string import ascii_lowercase

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file
from mmge.style import two_slope_discrete_cmap, discrete_map_colours, savefig, MODELS, MODEL_LABEL
from mmge.style import colorbar

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
VMIN, VMAX, VCENTER = -0.4, 1.0, 0.6

METRICS = [('twsa', 'Simulated TWSa vs GravIS'), ('et', 'Simulated ET vs FLUXCOM'),
           ('runoff', 'Simulated run-off vs GRUN')]


def main():
    ds = xr.open_dataset(data_file('acc', 'acc_by_model.nc'))
    proj = ccrs.PlateCarree()
    nrows, ncols = len(MODELS), len(METRICS)
    panel_width = 4.6
    panel_height = panel_width * (140 / 360)
    fig, axes = plt.subplots(nrows, ncols, figsize=(panel_width * ncols, panel_height * nrows),
                              subplot_kw={'projection': proj})
    cmap, norm, boundaries = two_slope_discrete_cmap(VMIN, VMAX, vcenter=VCENTER)

    im = None
    panel_letters = iter(ascii_lowercase)
    for row, model in enumerate(MODELS):
        for col, (metric, col_label) in enumerate(METRICS):
            ax = axes[row, col]
            field = ds['acc'].sel(metric=metric, model=model)
            im = field.plot(ax=ax, **discrete_map_colours(field, cmap, boundaries), add_colorbar=False, transform=proj)
            ax.coastlines(linewidth=0.8)
            ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
            ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.3, edgecolor='black')
            ax.set_title('')
            ax.text(0.98, 0.95, f'{next(panel_letters)})', transform=ax.transAxes,
                    fontsize=10, fontweight='bold', va='top', ha='right', zorder=5)
            if row == 0:
                ax.set_title(col_label, fontsize=11, fontweight='bold', pad=6)
            if col == 0:
                ax.text(0.02, 0.05, MODEL_LABEL[model], transform=ax.transAxes,
                        fontsize=9, va='bottom', ha='left',
                        bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
            gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.4)
            gl.xlocator = plt.FixedLocator(LON_TICKS)
            gl.ylocator = plt.FixedLocator(LAT_TICKS)
            if col == 0:
                ax.set_yticks(LAT_TICKS, crs=proj)
                ax.yaxis.set_major_formatter(LatitudeFormatter())
                ax.tick_params(axis='y', labelsize=7)
            else:
                ax.set_yticks([])
            ax.set_ylabel('')
            if row == nrows - 1:
                ax.set_xticks(LON_TICKS, crs=proj)
                ax.xaxis.set_major_formatter(LongitudeFormatter())
                ax.tick_params(axis='x', labelsize=7)
                for lab in ax.get_xticklabels():
                    lab.set_rotation(45)
                    lab.set_ha('right')
            else:
                ax.set_xticks([])
            ax.set_xlabel('')

    fig.subplots_adjust(hspace=0.04, wspace=0.04)
    tick_boundaries = np.arange(VMIN, VMAX + 0.01, 0.2)
    cbar = colorbar(fig, im, boundaries, ax=axes, fraction=0.02, pad=0.015, aspect=45, ticks=tick_boundaries, extend='min',
                         label='ACC (ensemble mean across forcings) [-]')
    cbar.ax.set_yticklabels([f'{t:.1f}' for t in cbar.get_ticks()])

    savefig(fig, 'figure_acc_combined_by_model')


if __name__ == '__main__':
    main()
