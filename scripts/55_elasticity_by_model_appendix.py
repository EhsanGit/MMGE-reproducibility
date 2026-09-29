"""Reproduces fig:appendix-elasticity-by-model (figures/figure8_elasticity_precip_runoff_combined.png).

Per-model precipitation elasticity of simulated runoff (the same fields
averaged into fig:figure5-elasticity's ensemble mean), one panel per model.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file
from mmge.style import MODELS, MODEL_LABEL, savefig, two_slope_discrete_cmap_with_band, extended_discrete_cmap
from mmge.style import colorbar

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
VMIN, VMAX, VCENTER = -1, 5, 1.0
NEUTRAL_HALF_WIDTH = 0.25
BIN_WIDTH = 0.5


def main():
    ds = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity']

    base_cmap, _, boundaries = two_slope_discrete_cmap_with_band(
        VMIN, VMAX, vcenter=VCENTER, bin_width=BIN_WIDTH, neutral_half_width=NEUTRAL_HALF_WIDTH)
    cmap, norm = extended_discrete_cmap(base_cmap, boundaries, extend='neither')

    proj = ccrs.PlateCarree()
    n = len(MODELS)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3.0 * n), subplot_kw={'projection': proj})

    im = None
    for i, (ax, model) in enumerate(zip(axes, MODELS)):
        field = ds.sel(model=model)
        finite = np.isfinite(field.values)
        print(f'{MODEL_LABEL[model]}: {int(finite.sum())} valid cells, '
              f'5/50/95th pct = {np.percentile(field.values[finite], [5, 50, 95]).round(2)}')
        im = field.clip(min=VMIN, max=VMAX).plot(ax=ax, cmap=cmap, norm=norm, add_colorbar=False, transform=proj)
        ax.coastlines(linewidth=1.0)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        ax.text(0.02, 0.03, MODEL_LABEL[model], transform=ax.transAxes, fontsize=9, va='bottom', ha='left',
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

    fig.subplots_adjust(hspace=0.12)
    colorbar(fig, im, boundaries, ax=axes, fraction=0.025, pad=0.02, aspect=35, extend='both', ticks=np.arange(VMIN, VMAX + 1, 1),
                 label=r'Precipitation elasticity of runoff, $\varepsilon$ [-]')
    savefig(fig, 'figure8_elasticity_precip_runoff_combined')


if __name__ == '__main__':
    main()
