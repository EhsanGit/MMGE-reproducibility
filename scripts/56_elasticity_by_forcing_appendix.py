"""Reproduces fig:appendix-elasticity-by-forcing (figures/figure8_elasticity_by_forcing.png)
and tab:elasticity-by-forcing.

Single-forcing-pair precipitation elasticity of runoff (no pooling across
forcings, unlike fig:figure5-elasticity), ensemble mean across the four
models, one panel per perturbed forcing, plus the regional median table.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file, TABLE_DIR
from mmge.style import FORCINGS, FORCING_LABEL, savefig, two_slope_discrete_cmap_with_band, extended_discrete_cmap
from mmge.style import colorbar
from mmge.regions import REGION_MAP, REGION_ORDER

PERTURBED = ['em_earth', 'mswep', 'w5e5']
LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
VMIN, VMAX, VCENTER = -1, 5, 1.0
NEUTRAL_HALF_WIDTH = 0.25
BIN_WIDTH = 0.5

REGION_NAME_TO_CODE = {v: k for k, v in REGION_MAP.items()}
REGION_DISPLAY = {r: r for r in REGION_ORDER}
REGION_DISPLAY['North America, Central America, Caribbean'] = 'North/Central America and the Caribbean'


def main():
    ds = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_forcing.nc'))['elasticity']
    region_code = xr.open_dataset(data_file('elasticity', 'wmo_region_mask.nc'))['region_code']

    for forcing in PERTURBED:
        field = ds.sel(forcing=forcing)
        finite = np.isfinite(field.values)
        print(f'{FORCING_LABEL[forcing]}: {int(finite.sum())} valid cells '
              f'({100 * finite.mean():.1f}% of grid)')

    plot_by_forcing(ds)
    build_table(ds, region_code)


def build_table(ds, region_code):
    rows = []
    for region in REGION_ORDER:
        sel = (region_code == REGION_NAME_TO_CODE[region]).values
        row = {'Region': REGION_DISPLAY[region]}
        medians = {}
        for forcing in PERTURBED:
            vals = ds.sel(forcing=forcing).values[sel]
            vals = vals[np.isfinite(vals)]
            med = float(np.median(vals)) if vals.size else np.nan
            medians[forcing] = med
            row[FORCING_LABEL[forcing]] = round(med, 2)
        spread = max(medians.values()) - min(medians.values())
        row['Behaviour'] = 'Forcings agree' if spread < 0.5 else 'Moderate disagreement'
        row['Range'] = round(spread, 2)
        rows.append(row)
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    for forcing in PERTURBED:
        col = FORCING_LABEL[forcing]
        top = df[df[col] == df[col].max()]
        names = '/'.join(top['Region'])
        print(f'Highest-elasticity region for {col}: {names} ({df[col].max()})')
    out_path = TABLE_DIR / 'elasticity-by-forcing.csv'
    df.to_csv(out_path, index=False)
    print(f'Saved {out_path}')


def plot_by_forcing(ds):
    base_cmap, _, boundaries = two_slope_discrete_cmap_with_band(
        VMIN, VMAX, vcenter=VCENTER, bin_width=BIN_WIDTH, neutral_half_width=NEUTRAL_HALF_WIDTH)
    cmap, norm = extended_discrete_cmap(base_cmap, boundaries, extend='neither')

    proj = ccrs.PlateCarree()
    n = len(PERTURBED)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3.0 * n), subplot_kw={'projection': proj})

    im = None
    for i, (ax, forcing) in enumerate(zip(axes, PERTURBED)):
        field = ds.sel(forcing=forcing)
        im = field.clip(min=VMIN, max=VMAX).plot(ax=ax, cmap=cmap, norm=norm, add_colorbar=False, transform=proj)
        ax.coastlines(linewidth=1.0)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        ax.text(0.02, 0.03, FORCING_LABEL[forcing], transform=ax.transAxes, fontsize=9, va='bottom', ha='left',
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
    savefig(fig, 'figure8_elasticity_by_forcing')


if __name__ == '__main__':
    main()
