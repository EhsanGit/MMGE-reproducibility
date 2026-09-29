"""Reproduces fig:figure5-elasticity (figures/figure8_elasticity_ensemble_mean.png).

Ensemble-mean (across the four models) precipitation elasticity of
simulated runoff: the through-origin regression slope of relative runoff
change on relative precipitation change, fitted per grid cell from
ERA5-Land vs. EM-Earth/MSWEP/W5E5 (Sect. 3.4). Also prints the global and
per-model medians quoted in the text.
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
from mmge.style import colorbar
from mmge.style import (MODELS, MODEL_LABEL, savefig, two_slope_discrete_cmap_with_band,
                         extended_discrete_cmap)

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)

# Diverging colour scale centred on elasticity = 1 (unity response), with a
# near-white neutral band for [0.75, 1.25] -- same convention as the
# manuscript figure.
VMIN, VMAX, VCENTER = -1, 5, 1.0
NEUTRAL_HALF_WIDTH = 0.25
BIN_WIDTH = 0.5


def main():
    ds = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))
    per_model = ds['elasticity'].sel(model=MODELS)
    ensemble_mean = per_model.mean(dim='model', skipna=True).load()

    finite = np.isfinite(ensemble_mean.values)
    print(f'Ensemble-mean elasticity: {int(finite.sum())} valid cells, '
          f'median = {np.median(ensemble_mean.values[finite]):.2f} (manuscript: 1.95)')
    for model in MODELS:
        vals = per_model.sel(model=model).values
        vals = vals[np.isfinite(vals)]
        print(f'  {MODEL_LABEL[model]} global median = {np.median(vals):.2f}')

    base_cmap, _, boundaries = two_slope_discrete_cmap_with_band(
        VMIN, VMAX, vcenter=VCENTER, bin_width=BIN_WIDTH, neutral_half_width=NEUTRAL_HALF_WIDTH)
    # The field is clipped to [VMIN, VMAX] before plotting, so no values fall outside the bins.
    cmap, norm = extended_discrete_cmap(base_cmap, boundaries, extend='neither')

    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(14, 4.2), subplot_kw={'projection': proj})
    im = ensemble_mean.clip(min=VMIN, max=VMAX).plot(
        ax=ax, cmap=cmap, norm=norm, add_colorbar=False, transform=proj)
    ax.coastlines(linewidth=1.0)
    ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
    ax.set_title('')
    gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
    gl.xlocator = plt.FixedLocator(LON_TICKS)
    gl.ylocator = plt.FixedLocator(LAT_TICKS)
    ax.set_xticks(LON_TICKS, crs=proj)
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.set_yticks(LAT_TICKS, crs=proj)
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis='both', labelsize=9)
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha('right')
    ax.set_xlabel('')
    ax.set_ylabel('')

    colorbar(fig, im, boundaries, ax=ax, fraction=0.03, pad=0.02, aspect=30, extend='both', ticks=np.arange(VMIN, VMAX + 1, 1),
                 label=r'Precipitation elasticity of runoff, $\varepsilon$ [-]')

    savefig(fig, 'figure8_elasticity_ensemble_mean')


if __name__ == '__main__':
    main()
