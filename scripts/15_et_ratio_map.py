"""Reproduces the Appendix figure \\label{fig:sp2-et_ratio}: the long-term
evapotranspiration ratio Ebar/Pbar for EM-Earth, ERA5-Land, MSWEP and W5E5,
the second of the two ratios that make up the water balance closure error
of Eq. eq:water_balance_error (see also Fig. fig:figure3-water balance error).
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
from matplotlib.colors import BoundaryNorm

from mmge.paths import data_file
from mmge.style import savefig, FORCING_LABEL
from mmge.style import colorbar
from mmge.style import discrete_map_colours

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
FORCINGS = ['em_earth', 'era5land', 'mswep', 'w5e5']
VMIN, VMAX, NUM_COLORS = 0.0, 2.0, 10


def main():
    ds = xr.open_dataset(data_file('water_balance', 'water_balance_closure.nc'))
    proj = ccrs.PlateCarree()
    n = len(FORCINGS)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3.0 * n), subplot_kw={'projection': proj})

    base_cmap = plt.get_cmap('RdBu', NUM_COLORS)
    boundaries = np.linspace(VMIN, VMAX, NUM_COLORS + 1)
    norm = BoundaryNorm(boundaries, base_cmap.N)

    im = None
    for i, (ax, forcing) in enumerate(zip(axes, FORCINGS)):
        # Clipped to [vmin, vmax] before plotting: near-zero-denominator desert
        # cells reach values far outside this range (see manuscript Appendix D).
        field = ds[f'et_ratio_{forcing}'].clip(min=VMIN, max=VMAX)
        im = field.plot(ax=ax, **discrete_map_colours(field, base_cmap, boundaries), add_colorbar=False, transform=proj)
        ax.coastlines(linewidth=1.0)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        ax.text(0.02, 0.03, FORCING_LABEL[forcing], transform=ax.transAxes, fontsize=9,
                va='bottom', ha='left',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
        gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
        gl.xlocator = plt.FixedLocator(LON_TICKS)
        gl.ylocator = plt.FixedLocator(LAT_TICKS)
        ax.set_yticks(LAT_TICKS, crs=proj)
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(axis='y', labelsize=9)
        ax.set_ylabel('')
        if i == n - 1:
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

    fig.subplots_adjust(hspace=0.04)
    cbar = colorbar(fig, im, boundaries, ax=axes, fraction=0.025, pad=0.02, aspect=35, extend='max',
                         label=r'Evapotranspiration ratio $\bar{E}/\bar{P}$')

    savefig(fig, 'figure_sp2_et_ratio_combined')


if __name__ == '__main__':
    main()
