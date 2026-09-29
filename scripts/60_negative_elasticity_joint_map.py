"""Reproduces fig:appendix-negative-elasticity-joint (figures/figure8_negative_elasticity_joint_map.png).

Joins two candidate explanations directly at every grid cell where the
ensemble-mean runoff elasticity (fig:figure5-elasticity) is negative: (a)
the evapotranspiration elasticity there (the mass-balance explanation) and
(b) the cross-forcing precipitation disagreement there (the
forcing-disagreement explanation), both against the global land baseline.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from mmge.paths import data_file, FIG_DIR
from mmge.style import MODELS, two_slope_discrete_cmap_with_band, extended_discrete_cmap
from mmge.style import colorbar
from mmge.style import savefig

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)
NOT_NEGATIVE_CMAP = ListedColormap(['#cfe0ea'])


def summarize(name, vals, label=''):
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        print(f'  {name}{label}: no valid cells')
        return None
    pct = np.percentile(vals, [5, 25, 50, 75, 95])
    print(f'  {name}{label}: n={vals.size}, mean={vals.mean():.3f}, median={pct[2]:.3f}, '
          f'5/25/75/95th pct = {pct[[0, 1, 3, 4]].round(3)}')
    return {'n': int(vals.size), 'mean': float(vals.mean()), 'median': float(pct[2]),
            'p75': float(pct[3])}


def main():
    runoff = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity']
    reg_ensemble_mean = runoff.sel(model=MODELS).mean(dim='model', skipna=True).load()

    et = xr.open_dataset(data_file('elasticity', 'et_elasticity_by_model.nc'))['elasticity']
    et_ensemble_mean = et.sel(model=MODELS).mean(dim='model', skipna=True).load()

    dp_std = (xr.open_dataset(data_file('elasticity', 'delta_p_perturbation.nc'))['delta_p_std'] * 100).load()

    avg = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_avg_method_by_model.nc'))['elasticity']
    avg_ensemble_mean = avg.sel(model=MODELS).mean(dim='model', skipna=True).load()

    reg_vals = reg_ensemble_mean.values
    negative_mask = np.isfinite(reg_vals) & (reg_vals < 0)
    n_negative = int(negative_mask.sum())
    n_land = int(np.isfinite(reg_vals).sum())
    print(f'Negative run-off elasticity (regression ensemble mean): {n_negative}/{n_land} land cells '
          f'({100 * n_negative / n_land:.2f}%)')

    et_vals_all = et_ensemble_mean.values
    dp_std_vals_all = dp_std.values
    avg_vals_all = avg_ensemble_mean.values

    print('\n--- ET elasticity: global land vs. negative-run-off-elasticity cells ---')
    et_global = summarize('ET elasticity', et_vals_all, ' (global land)')
    et_negative = summarize('ET elasticity', et_vals_all[negative_mask], ' (negative-Q-elasticity cells)')

    print('\n--- Cross-forcing Delta_P disagreement (std, %): global vs. negative cells ---')
    dp_global = summarize('Delta_P disagreement', dp_std_vals_all, ' (global land)')
    dp_negative = summarize('Delta_P disagreement', dp_std_vals_all[negative_mask], ' (negative-Q-elasticity cells)')

    if et_global and et_negative:
        frac = float(np.mean(et_vals_all[negative_mask & np.isfinite(et_vals_all)] > et_global['p75']))
        print(f'\n  Fraction of negative cells with ET elasticity above the global 75th percentile '
              f'({et_global["p75"]:.2f}): {100 * frac:.2f}% (baseline 25%)')
    if dp_global and dp_negative:
        frac = float(np.mean(dp_std_vals_all[negative_mask & np.isfinite(dp_std_vals_all)] > dp_global['p75']))
        print(f'  Fraction of negative cells with Delta_P disagreement above the global 75th percentile '
              f'({dp_global["p75"]:.2f}%): {100 * frac:.2f}% (baseline 25%)')

    valid_both = negative_mask & np.isfinite(avg_vals_all)
    n_valid_both = int(valid_both.sum())
    n_also_negative = int((avg_vals_all[valid_both] < 0).sum())
    print(f'\n--- Averaging-method elasticity at the same negative cells ---')
    print(f'  n cells with both methods valid: {n_valid_both}/{n_negative}')
    if n_valid_both:
        print(f'  Also negative under the averaging method: {n_also_negative}/{n_valid_both} = '
              f'{100 * n_also_negative / n_valid_both:.2f}%')

    plot_negative_cells(reg_ensemble_mean, et_ensemble_mean, dp_std)


def plot_negative_cells(reg_ensemble_mean, et_field, dp_std_field_pct):
    negative_mask = np.isfinite(reg_ensemble_mean.values) & (reg_ensemble_mean.values < 0)
    not_negative_mask = np.isfinite(reg_ensemble_mean.values) & (reg_ensemble_mean.values >= 0)
    et_masked = et_field.where(negative_mask)
    dp_masked = dp_std_field_pct.where(negative_mask)
    not_negative_layer = xr.DataArray(np.where(not_negative_mask, 1.0, np.nan),
                                       coords=reg_ensemble_mean.coords, dims=reg_ensemble_mean.dims)

    proj = ccrs.PlateCarree()
    fig, axes = plt.subplots(2, 1, figsize=(14, 6.4), subplot_kw={'projection': proj})

    et_base, _, et_boundaries = two_slope_discrete_cmap_with_band(
        -1, 2, vcenter=0.0, bin_width=0.25, neutral_half_width=0.125)
    et_cmap, et_norm = extended_discrete_cmap(et_base, et_boundaries, extend='neither')
    not_negative_layer.plot(ax=axes[0], cmap=NOT_NEGATIVE_CMAP, vmin=0, vmax=1,
                             add_colorbar=False, transform=proj, zorder=0.5)
    im_a = et_masked.clip(min=-1, max=2).plot(ax=axes[0], cmap=et_cmap, norm=et_norm,
                                               add_colorbar=False, transform=proj)
    axes[0].text(0.02, 0.03, 'a', transform=axes[0].transAxes, fontsize=11, fontweight='bold',
                 va='bottom', ha='left', bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                                                    alpha=0.85, edgecolor='0.6'))
    colorbar(fig, im_a, et_boundaries, ax=axes[0], fraction=0.025, pad=0.02, aspect=20, extend='both', ticks=np.arange(-1, 3, 1), label=r'$\varepsilon_{ET}$ [-]')

    dp_base = plt.get_cmap('YlOrRd', 16)
    dp_boundaries = np.linspace(0, 40, 17)
    dp_cmap, dp_norm = extended_discrete_cmap(dp_base, dp_boundaries, extend='neither')
    not_negative_layer.plot(ax=axes[1], cmap=NOT_NEGATIVE_CMAP, vmin=0, vmax=1,
                             add_colorbar=False, transform=proj, zorder=0.5)
    im_b = dp_masked.clip(min=0, max=40).plot(ax=axes[1], cmap=dp_cmap, norm=dp_norm,
                                               add_colorbar=False, transform=proj)
    axes[1].text(0.02, 0.03, 'b', transform=axes[1].transAxes, fontsize=11, fontweight='bold',
                 va='bottom', ha='left', bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                                                    alpha=0.85, edgecolor='0.6'))
    colorbar(fig, im_b, dp_boundaries, ax=axes[1], fraction=0.025, pad=0.02, aspect=20, extend='max', ticks=np.arange(0, 41, 10),
                 label=r'Std. dev. of $\Delta P/P$ across forcings [%]')

    for i, ax in enumerate(axes):
        ax.coastlines(linewidth=1.0)
        ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
        ax.add_feature(cfeature.LAND, color='lightgray', zorder=0, linewidth=0.5, edgecolor='black')
        ax.set_title('')
        gl = ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
        gl.xlocator = plt.FixedLocator(LON_TICKS)
        gl.ylocator = plt.FixedLocator(LAT_TICKS)
        ax.set_yticks(LAT_TICKS, crs=proj)
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.tick_params(axis='y', labelsize=9)
        ax.set_ylabel('')
        if i == 1:
            ax.set_xticks(LON_TICKS, crs=proj)
            ax.xaxis.set_major_formatter(LongitudeFormatter())
            ax.tick_params(axis='x', labelsize=8)
            for label in ax.get_xticklabels():
                label.set_rotation(45)
                label.set_ha('right')
        else:
            ax.set_xticks([])
        ax.set_xlabel('')

    fig.subplots_adjust(hspace=0.15)
    savefig(fig, 'figure8_negative_elasticity_joint_map')


if __name__ == '__main__':
    main()
