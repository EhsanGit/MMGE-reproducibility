"""Reproduces Figure 3 (\\label{fig:acc-main-body}): standardised anomaly
correlation coefficient (ACC) between simulated TWSa and GravIS (top),
simulated ET and FLUXCOM (middle), and simulated runoff and GRUN (bottom),
as the ensemble mean across all four models and all four forcings.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file
from mmge.style import two_slope_discrete_cmap, discrete_map_colours, savefig
from mmge.style import colorbar

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
VMIN, VMAX, VCENTER = -0.4, 1.0, 0.6

METRICS = [('twsa', 'TWSa'), ('et', 'ET'), ('runoff', 'Run-off')]


def main():
    ds = xr.open_dataset(data_file('acc', 'acc_ensemble_mean.nc'))
    proj = ccrs.PlateCarree()
    fig, axes = plt.subplots(len(METRICS), 1, figsize=(14, 3.0 * len(METRICS)),
                              subplot_kw={'projection': proj})
    cmap, norm, boundaries = two_slope_discrete_cmap(VMIN, VMAX, vcenter=VCENTER)

    im = None
    for i, (ax, (metric, label)) in enumerate(zip(axes, METRICS)):
        field = ds['acc'].sel(metric=metric)
        im = field.plot(ax=ax, **discrete_map_colours(field, cmap, boundaries), add_colorbar=False, transform=proj)
        ax.coastlines(linewidth=1.0)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        ax.text(0.02, 0.03, label, transform=ax.transAxes, fontsize=9, va='bottom', ha='left',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
        gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
        gl.xlocator = plt.FixedLocator(LON_TICKS)
        gl.ylocator = plt.FixedLocator(LAT_TICKS)
        ax.set_yticks(LAT_TICKS, crs=proj)
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(axis='y', labelsize=9)
        ax.set_ylabel('')
        if i == len(METRICS) - 1:
            ax.set_xticks(LON_TICKS, crs=proj)
            ax.xaxis.set_major_formatter(LongitudeFormatter())
            ax.tick_params(axis='x', labelsize=8)
            for lab in ax.get_xticklabels():
                lab.set_rotation(45)
                lab.set_ha('right')
        else:
            ax.set_xticks([])
        ax.set_xlabel('')

    fig.subplots_adjust(hspace=0.12)
    tick_boundaries = np.arange(VMIN, VMAX + 0.01, 0.2)
    cbar = colorbar(fig, im, boundaries, ax=axes, fraction=0.025, pad=0.02, aspect=35, ticks=tick_boundaries, extend='min',
                         label='ACC (ensemble mean across models and forcings) [-]')
    cbar.ax.set_yticklabels([f'{t:.1f}' for t in cbar.get_ticks()])

    savefig(fig, 'figure_acc_main_body')


if __name__ == '__main__':
    main()
