"""
Reproduces:
    fig:forcing-hm-variance-decomp
        figures/figure9_log2_ratio_by_forcing_combined.png
    fig:appendix-forcing-hm-variance-components
        figures/figure9_forcing_contribution.png
        figures/figure9_hm_contribution.png
        figures/figure9_log2_ratio_combined.png

Decomposes the spread of the long-term mean simulated streamflow across the
4 models x 4 forcings ensemble into a forcing-driven component and a
model-driven component (Eq. eq:variance_decomp), and takes their log2 ratio
(Eq. eq:variance_ratio): positive values mean forcing choice dominates the
local spread, negative values mean model choice dominates.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.colors import BoundaryNorm
import xarray as xr

from mmge.paths import data_file
from mmge.style import savefig, FORCING_LABEL
from mmge.style import colorbar
from mmge.style import discrete_map_colours

MIN_VARIANCE_PERCENTILE = 25  # mask the bottom quartile of pooled variance magnitude
LOG2_VMIN, LOG2_VMAX, LOG2_NUM_COLORS = -5, 5, 10
LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
# Panel order of Fig. 7 (main body): em_earth, era5land, mswep, w5e5 -- kept separate from
# mmge.style.FORCINGS, whose ordering serves the model-comparison CDF figures instead.
FORCING_PANEL_ORDER = ['em_earth', 'era5land', 'mswep', 'w5e5']


def significance_floor(*components, percentile=MIN_VARIANCE_PERCENTILE):
    """Bottom percentile of the pooled positive values of the given variance maps."""
    pooled = np.concatenate([c.where(c > 0).values.ravel() for c in components])
    pooled = pooled[np.isfinite(pooled)]
    return float(np.nanpercentile(pooled, percentile))


def log2_ratio(forcing_component, model_component, floor):
    """log2(forcing / model), masked where neither component clears the significance floor."""
    safe_model = model_component.where(model_component > 0)
    ratio = (forcing_component / safe_model).where(lambda r: r > 0)
    significant = (forcing_component >= floor) | (model_component >= floor)
    return np.log2(ratio.where(significant))


def single_panel_map(field, cmap, vmin, vmax, extend, colorbar_label, corner_label, name, num_colors=None):
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(12, 6), subplot_kw={'projection': proj})
    if num_colors:
        cmap = plt.get_cmap(cmap, num_colors)
    im = field.plot(ax=ax, cmap=cmap, vmin=vmin, vmax=vmax, add_colorbar=False, transform=proj)
    ax.coastlines(linewidth=0.5)
    ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
    ax.set_title('')
    gl = ax.gridlines(draw_labels=True, alpha=0.3)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlocator = plt.FixedLocator(LON_TICKS)
    gl.ylocator = plt.FixedLocator(LAT_TICKS)
    ax.text(0.02, 0.03, corner_label, transform=ax.transAxes, fontsize=9, va='bottom', ha='left',
            zorder=5, bbox=dict(boxstyle='round,pad=0.25', facecolor='white', alpha=0.85, edgecolor='0.6'))
    fig.colorbar(im, ax=ax, extend=extend, fraction=0.044, pad=0.02, label=colorbar_label)
    savefig(fig, name)


def by_forcing_grid(log2_ratio_by_forcing, name):
    """Per-forcing log2 ratio, stacked in one column with a single shared colorbar."""
    proj = ccrs.PlateCarree()
    n = len(FORCING_PANEL_ORDER)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3.0 * n), subplot_kw={'projection': proj})

    base_cmap = plt.get_cmap('RdBu_r', LOG2_NUM_COLORS)
    boundaries = np.linspace(LOG2_VMIN, LOG2_VMAX, LOG2_NUM_COLORS + 1)
    norm = BoundaryNorm(boundaries, base_cmap.N)

    im = None
    for i, (ax, forcing) in enumerate(zip(axes, FORCING_PANEL_ORDER)):
        field = log2_ratio_by_forcing.sel(forcing=forcing)
        im = field.plot(ax=ax, **discrete_map_colours(field, base_cmap, boundaries), add_colorbar=False, transform=proj)
        ax.coastlines(linewidth=0.5)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        ax.text(0.02, 0.03, FORCING_LABEL[forcing], transform=ax.transAxes, fontsize=9,
                va='bottom', ha='left', zorder=5,
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
        else:
            ax.set_xticks([])
        ax.set_xlabel('')

    fig.subplots_adjust(hspace=0.12)
    colorbar(fig, im, boundaries, ax=axes, fraction=0.025, pad=0.02, aspect=35,
                 extend='both', label='log$_2$(Forcing variance / HM variance)')
    savefig(fig, name)


def main():
    cube = xr.open_dataset(data_file('forcing_hm_variance', 'q_climatology_cube.nc'))['q']

    forcing_contribution = cube.var(dim='forcing').mean(dim='model')
    model_contribution = cube.var(dim='model').mean(dim='forcing')
    model_contribution_by_forcing = cube.var(dim='model')  # kept per forcing, dims (forcing, lat, lon)

    floor = significance_floor(forcing_contribution, model_contribution)
    print(f'Significance floor (bottom {MIN_VARIANCE_PERCENTILE}th percentile of variance magnitude): {floor:.6g}')

    ratio_combined = log2_ratio(forcing_contribution, model_contribution, floor)
    ratio_by_forcing = xr.concat(
        [log2_ratio(forcing_contribution, model_contribution_by_forcing.sel(forcing=f), floor)
         for f in FORCING_PANEL_ORDER],
        dim=xr.DataArray(FORCING_PANEL_ORDER, dims='forcing', name='forcing'))

    # Main-body figure: one panel per forcing, shared colorbar.
    by_forcing_grid(ratio_by_forcing, 'figure9_log2_ratio_by_forcing_combined')

    # Appendix: the two unmasked variance components, and the ratio collapsed
    # to a single map (averaged over forcing).
    single_panel_map(forcing_contribution, 'viridis', 0, 5, 'max',
                      'Forcing-driven variance of Q (m$^6$ s$^{-2}$)',
                      'Forcing-driven variance', 'figure9_forcing_contribution', num_colors=7)
    single_panel_map(model_contribution, 'viridis', 0, 5, 'max',
                      'HM-driven variance of Q (m$^6$ s$^{-2}$)',
                      'HM-driven variance', 'figure9_hm_contribution', num_colors=7)
    single_panel_map(ratio_combined, 'RdBu_r', LOG2_VMIN, LOG2_VMAX, 'both',
                      'log$_2$(Forcing variance / HM variance)',
                      'Combined ratio, averaged over forcing', 'figure9_log2_ratio_combined',
                      num_colors=LOG2_NUM_COLORS)


if __name__ == '__main__':
    main()
