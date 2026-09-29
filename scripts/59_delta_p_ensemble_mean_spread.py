"""Reproduces fig:appendix-delta-p (figures/figure8_delta_p_ensemble_mean_and_spread.png).

(a) Ensemble-mean relative precipitation perturbation Delta_P/P (screened
at +/-500%) behind fig:figure5-elasticity, averaged across the three
perturbed forcings, and (b) its cross-forcing standard deviation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file, FIG_DIR
from mmge.style import extended_discrete_cmap
from mmge.style import colorbar
from mmge.style import savefig

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
MEAN_VMIN, MEAN_VMAX, MEAN_NUM_COLORS = -50, 50, 20
SPREAD_VMIN, SPREAD_VMAX = 0, 40


def _style_map_axis(ax, is_bottom_row):
    ax.coastlines(linewidth=1.0)
    ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
    ax.set_title('')
    gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
    gl.xlocator = plt.FixedLocator(LON_TICKS)
    gl.ylocator = plt.FixedLocator(LAT_TICKS)
    ax.set_yticks(LAT_TICKS, crs=ccrs.PlateCarree())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis='y', labelsize=9)
    ax.set_ylabel('')
    if is_bottom_row:
        ax.set_xticks(LON_TICKS, crs=ccrs.PlateCarree())
        ax.xaxis.set_major_formatter(LongitudeFormatter())
        ax.tick_params(axis='x', labelsize=8)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha('right')
        ax.set_xlabel('')
    else:
        ax.set_xticks([])
        ax.set_xlabel('')


def main():
    ds = xr.open_dataset(data_file('elasticity', 'delta_p_perturbation.nc'))
    mean_pct = (ds['delta_p_mean'] * 100).load()
    std_pct = (ds['delta_p_std'] * 100).load()

    for name, field in [('mean', mean_pct), ('std', std_pct)]:
        vals = field.values
        finite = np.isfinite(vals)
        pct = np.percentile(vals[finite], [5, 25, 50, 75, 95])
        print(f'Ensemble Delta_P/P {name}: {int(finite.sum())} valid cells, '
              f'5/25/50/75/95th pct [%] = {pct.round(2)}')

    proj = ccrs.PlateCarree()
    fig, axes = plt.subplots(2, 1, figsize=(14, 6.4), subplot_kw={'projection': proj})

    mean_base = plt.get_cmap('RdBu', MEAN_NUM_COLORS)
    mean_boundaries = np.linspace(MEAN_VMIN, MEAN_VMAX, MEAN_NUM_COLORS + 1)
    mean_cmap, mean_norm = extended_discrete_cmap(mean_base, mean_boundaries, extend='neither')
    im_mean = mean_pct.clip(min=MEAN_VMIN, max=MEAN_VMAX).plot(
        ax=axes[0], cmap=mean_cmap, norm=mean_norm, add_colorbar=False, transform=proj)
    _style_map_axis(axes[0], is_bottom_row=False)
    axes[0].text(0.02, 0.03, 'a', transform=axes[0].transAxes, fontsize=11, fontweight='bold',
                 va='bottom', ha='left', bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                                                    alpha=0.85, edgecolor='0.6'))
    colorbar(fig, im_mean, mean_boundaries, ax=axes[0], fraction=0.025, pad=0.02, aspect=20, extend='both', ticks=np.arange(MEAN_VMIN, MEAN_VMAX + 1, 10),
                 label=r'Mean $\Delta P/P$ [%]')

    spread_base = plt.get_cmap('YlOrRd', 16)
    spread_boundaries = np.linspace(SPREAD_VMIN, SPREAD_VMAX, 17)
    spread_cmap, spread_norm = extended_discrete_cmap(spread_base, spread_boundaries, extend='neither')
    im_spread = std_pct.clip(min=SPREAD_VMIN, max=SPREAD_VMAX).plot(
        ax=axes[1], cmap=spread_cmap, norm=spread_norm, add_colorbar=False, transform=proj)
    _style_map_axis(axes[1], is_bottom_row=True)
    axes[1].text(0.02, 0.03, 'b', transform=axes[1].transAxes, fontsize=11, fontweight='bold',
                 va='bottom', ha='left', bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                                                    alpha=0.85, edgecolor='0.6'))
    colorbar(fig, im_spread, spread_boundaries, ax=axes[1], fraction=0.025, pad=0.02, aspect=20, extend='max', ticks=np.arange(SPREAD_VMIN, SPREAD_VMAX + 1, 10),
                 label=r'Std. dev. of $\Delta P/P$ across forcings [%]')

    fig.subplots_adjust(hspace=0.15)
    savefig(fig, 'figure8_delta_p_ensemble_mean_and_spread')


if __name__ == '__main__':
    main()
