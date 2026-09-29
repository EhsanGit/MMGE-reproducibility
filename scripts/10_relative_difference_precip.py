"""Reproduces Figure 1 (\\label{fig:figure2-relative difference}): relative
difference in the long-term mean annual precipitation (1981-2019) between
EM-Earth, MSWEP, W5E5 and ERA5-Land (the reference), with ERA5-Land's own
long-term mean annual precipitation shown above for scale.
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
from matplotlib.colors import BoundaryNorm, ListedColormap

from mmge.paths import data_file
from mmge.style import savefig, FORCING_LABEL
from mmge.style import colorbar
from mmge.style import discrete_map_colours

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
FORCINGS = ['em_earth', 'mswep', 'w5e5']
VMIN, VMAX, NUM_COLORS = -50, 50, 20  # 5% per colour step

# ECMWF's own "era5_explorer_yearly_precipitation" style (Magics style library):
# discrete, unequal-width bins for the reference panel's absolute field.
ABS_LEVELS = [0, 100, 200, 500, 1000, 2000, 3000, 4000]  # mm/yr
ABS_COLORS = ['#ffffe0', '#c5eddf', '#a5d5d8', '#8abccf', '#73a2c6',
              '#5d8abd', '#4771b2', '#2e59a8', '#00429d']


def style_axis(ax, i, n_rows):
    ax.coastlines(linewidth=1.0)
    ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
    ax.set_title('')
    proj = ccrs.PlateCarree()
    gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
    gl.xlocator = plt.FixedLocator(LON_TICKS)
    gl.ylocator = plt.FixedLocator(LAT_TICKS)
    ax.set_yticks(LAT_TICKS, crs=proj)
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis='y', labelsize=9)
    ax.set_ylabel('')
    if i == n_rows - 1:
        ax.set_xticks(LON_TICKS, crs=proj)
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
    ds = xr.open_dataset(data_file('water_balance', 'precipitation_relative_difference.nc'))
    proj = ccrs.PlateCarree()
    n_rows = 1 + len(FORCINGS)
    fig, axes = plt.subplots(n_rows, 1, figsize=(14, 3.2 * n_rows), subplot_kw={'projection': proj})

    era5land_abs = ds['era5land_annual_precipitation']
    abs_cmap = ListedColormap(ABS_COLORS)
    abs_norm = BoundaryNorm(ABS_LEVELS, ncolors=abs_cmap.N, extend='both')
    im_abs = era5land_abs.clip(min=ABS_LEVELS[0], max=ABS_LEVELS[-1]).plot(
        ax=axes[0], **discrete_map_colours(era5land_abs.clip(min=ABS_LEVELS[0], max=ABS_LEVELS[-1]), abs_cmap, ABS_LEVELS), add_colorbar=False, transform=proj)
    style_axis(axes[0], 0, n_rows)
    axes[0].text(0.02, 0.03, 'ERA5-Land (reference)', transform=axes[0].transAxes, fontsize=9,
                 va='bottom', ha='left',
                 bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
    abs_cbar = colorbar(fig, im_abs, ABS_LEVELS, ax=axes[0], fraction=0.025, pad=0.02, aspect=12, ticks=ABS_LEVELS, extend='both',
                             label='Precipitation [mm/yr]')
    abs_cbar.ax.set_yticklabels([f'{int(round(t))}' for t in abs_cbar.get_ticks()])

    diff_cmap = plt.get_cmap('RdBu', NUM_COLORS)
    diff_boundaries = np.linspace(VMIN, VMAX, NUM_COLORS + 1)
    diff_norm = BoundaryNorm(diff_boundaries, diff_cmap.N)

    im_diff = None
    for j, forcing in enumerate(FORCINGS):
        ax = axes[j + 1]
        im_diff = ds[f'relative_difference_{forcing}'].plot(
            ax=ax, **discrete_map_colours(ds[f'relative_difference_{forcing}'], diff_cmap, diff_boundaries), add_colorbar=False, transform=proj)
        style_axis(ax, j + 1, n_rows)
        ax.text(0.02, 0.03, f'{FORCING_LABEL[forcing]} - reference', transform=ax.transAxes, fontsize=9,
                va='bottom', ha='left',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))

    fig.subplots_adjust(hspace=0.1)
    tick_boundaries = np.arange(VMIN, VMAX + 1, 10)  # labels every 10%, colour steps every 5%
    cbar = colorbar(fig, im_diff, diff_boundaries, ax=list(axes[1:]), fraction=0.025, pad=0.02, aspect=35, ticks=tick_boundaries,
                         label='Precipitation difference [%]')
    cbar.ax.set_yticklabels([f'{int(round(t))}' for t in cbar.get_ticks()])

    savefig(fig, 'figure1_relative_difference_combined')


if __name__ == '__main__':
    main()
