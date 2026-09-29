"""Reproduces fig:appendix-koppen-elasticity (figures/figure_appendix_koppen_elasticity.png)
and tab:elasticity-by-koppen.

Checks the ensemble-mean precipitation elasticity of runoff map against the
Koeppen-Geiger climate classification (Beck et al. 2018, first-letter
groups) and ERA5 elevation: group medians/IQR, a Kruskal-Wallis test with a
rank-based effect size and a plain ANOVA R^2, and a Spearman correlation
against elevation.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from scipy import stats

from mmge.paths import data_file, TABLE_DIR, FIG_DIR
from mmge.style import MODELS, extended_discrete_cmap
from mmge.style import discrete_map_colours
from mmge.style import colorbar
from mmge.style import savefig

GROUP_CODES = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
GROUP_LABELS = {'A': 'A: Tropical', 'B': 'B: Arid', 'C': 'C: Temperate', 'D': 'D: Continental', 'E': 'E: Polar'}
GROUP_ORDER = ['A', 'B', 'C', 'D', 'E']
GROUP_COLORS = {'A': '#4477AA', 'B': '#EE6677', 'C': '#228833', 'D': '#AA3377', 'E': '#BBBBBB'}

LON_TICKS = np.arange(-180, 181, 20)
LAT_TICKS = np.arange(-60, 81, 20)


def eta_squared_kruskal(groups_values):
    all_vals = np.concatenate(groups_values)
    ranks = stats.rankdata(all_vals)
    idx = 0
    group_rank_means, group_ns = [], []
    for g in groups_values:
        r = ranks[idx:idx + g.size]
        group_rank_means.append(r.mean())
        group_ns.append(g.size)
        idx += g.size
    grand_mean = ranks.mean()
    ss_between = sum(n_g * (m_g - grand_mean) ** 2 for n_g, m_g in zip(group_ns, group_rank_means))
    ss_total = np.sum((ranks - grand_mean) ** 2)
    return ss_between / ss_total


def anova_r2(groups_values):
    all_vals = np.concatenate(groups_values)
    grand_mean = all_vals.mean()
    ss_total = np.sum((all_vals - grand_mean) ** 2)
    ss_between = sum(g.size * (g.mean() - grand_mean) ** 2 for g in groups_values)
    return ss_between / ss_total


def main():
    elasticity = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity']
    ens_mean = elasticity.sel(model=MODELS).mean(dim='model', skipna=True).load()

    koppen_ds = xr.open_dataset(data_file('elasticity', 'koppen_elevation.nc'))
    kg_code = koppen_ds['koppen_group'].values
    kg_group = np.vectorize(lambda c: GROUP_CODES.get(int(c), ''))(kg_code)
    elev = koppen_ds['elevation'].values

    e_vals = ens_mean.values
    finite_e = np.isfinite(e_vals)
    print(f'Ensemble-mean elasticity valid cells: {int(finite_e.sum())}')

    group_values = {}
    for g in GROUP_ORDER:
        sel = finite_e & (kg_group == g)
        group_values[g] = e_vals[sel]
        print(f'Group {g}: n={group_values[g].size}')

    rows = []
    for g in GROUP_ORDER:
        vals = group_values[g]
        if vals.size == 0:
            continue
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        rows.append({'Group': GROUP_LABELS[g], 'n cells': int(vals.size), 'Median': round(float(med), 2),
                     'Q1': round(float(q1), 2), 'Q3': round(float(q3), 2), 'IQR': round(float(q3 - q1), 2)})
    table = pd.DataFrame(rows)
    print(table.to_string(index=False))
    table.to_csv(TABLE_DIR / 'elasticity-by-koppen.csv', index=False)
    print(f'Saved {TABLE_DIR / "elasticity-by-koppen.csv"}')

    nonempty = [group_values[g] for g in GROUP_ORDER if group_values[g].size > 0]
    h_stat, p_val = stats.kruskal(*nonempty)
    eps2 = eta_squared_kruskal(nonempty)
    r2 = anova_r2(nonempty)
    print(f'Kruskal-Wallis H={h_stat:.1f}, p={p_val:.3g}, rank eta^2={eps2:.4f}, ANOVA R^2={r2:.4f}')
    print('(manuscript: H=94209.09, rank eta^2=0.0644, ANOVA R^2=0.0154)')

    sel_elev = finite_e & np.isfinite(elev)
    rho, p_elev = stats.spearmanr(elev[sel_elev], e_vals[sel_elev])
    print(f'Spearman elasticity-vs-elevation: rho={rho:.4f}, p={p_elev:.3g}, n={int(sel_elev.sum())}')
    print('(manuscript: rho=-0.0695, n=1462901)')

    plot_figure(ens_mean, kg_code, kg_group, group_values, h_stat, eps2, r2)


def plot_figure(ens_mean, kg_code, kg_group, group_values, h_stat, eps2, r2):
    lat, lon = ens_mean['lat'].values, ens_mean['lon'].values
    proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(13, 14))
    gs = fig.add_gridspec(3, 2, width_ratios=[30, 1], height_ratios=[1, 1, 0.85], hspace=0.38, wspace=0.04)

    def _force_box(ax):
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1.1)

    # Panel (a): ensemble-mean elasticity, plain sequential viridis (as in
    # the manuscript), not the diverging scale used elsewhere in this family.
    ax_a = fig.add_subplot(gs[0, 0], projection=proj)
    ax_a.set_aspect('auto')
    vmin, vmax, num_colors = -1, 5, 12
    boundaries = np.linspace(vmin, vmax, num_colors + 1)
    base_cmap = plt.get_cmap('viridis', num_colors)
    im_a = ens_mean.plot(ax=ax_a, **discrete_map_colours(ens_mean, base_cmap, boundaries), add_colorbar=False, transform=proj)
    ax_a.coastlines(linewidth=0.8)
    ax_a.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax_a.set_title('(a) Ensemble-mean precipitation elasticity of run-off', loc='left', fontsize=11)
    ax_a.set_xlabel('')
    ax_a.set_ylabel('')
    gl_a = ax_a.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
    gl_a.xlocator = plt.FixedLocator(LON_TICKS)
    gl_a.ylocator = plt.FixedLocator(LAT_TICKS)
    ax_a.set_xticks(LON_TICKS, crs=proj)
    ax_a.xaxis.set_major_formatter(LongitudeFormatter())
    ax_a.set_yticks(LAT_TICKS, crs=proj)
    ax_a.yaxis.set_major_formatter(LatitudeFormatter())
    ax_a.tick_params(axis='both', labelsize=8)
    ax_a.set_aspect('auto')
    _force_box(ax_a)
    cax_a = fig.add_subplot(gs[0, 1])
    cbar_a = colorbar(fig, im_a, boundaries, cax=cax_a, extend='both', ticks=np.arange(vmin, vmax + 1, 1))
    cbar_a.set_label(r'$\Delta Q/Q \, / \, \Delta P/P$ [-]', fontsize=9)
    cbar_a.ax.tick_params(labelsize=8)

    # Panel (b): Koeppen-Geiger group map.
    ax_b = fig.add_subplot(gs[1, 0], projection=proj)
    ax_b.set_aspect('auto')
    code_to_color_idx = np.zeros(6, dtype=np.uint8)
    for i, g in enumerate(GROUP_ORDER):
        code_to_color_idx[[k for k, v in GROUP_CODES.items() if v == g][0]] = i
    color_idx_grid = code_to_color_idx[kg_code]
    display_grid = np.where(kg_code == 0, np.nan, color_idx_grid.astype(float))
    from matplotlib.colors import ListedColormap
    kg_cmap = ListedColormap([GROUP_COLORS[g] for g in GROUP_ORDER])
    ax_b.pcolormesh(lon, lat, display_grid, cmap=kg_cmap, vmin=-0.5, vmax=len(GROUP_ORDER) - 0.5,
                     transform=proj, shading='nearest')
    ax_b.coastlines(linewidth=0.8)
    ax_b.add_feature(cfeature.OCEAN, color='white', zorder=0)
    ax_b.set_title('(b) Köppen-Geiger climate classification (Beck et al. 2018), first-letter groups',
                    loc='left', fontsize=11)
    gl_b = ax_b.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)
    gl_b.xlocator = plt.FixedLocator(LON_TICKS)
    gl_b.ylocator = plt.FixedLocator(LAT_TICKS)
    ax_b.set_xticks(LON_TICKS, crs=proj)
    ax_b.xaxis.set_major_formatter(LongitudeFormatter())
    ax_b.set_yticks(LAT_TICKS, crs=proj)
    ax_b.yaxis.set_major_formatter(LatitudeFormatter())
    ax_b.tick_params(axis='both', labelsize=8)
    ax_b.set_aspect('auto')
    _force_box(ax_b)
    handles = [mpatches.Patch(color=GROUP_COLORS[g], label=GROUP_LABELS[g]) for g in GROUP_ORDER]
    ax_b.legend(handles=handles, loc='upper center', fontsize=8, ncol=5, framealpha=0.9, bbox_to_anchor=(0.5, -0.12))

    # Panel (c): boxplot by group.
    ax_c = fig.add_subplot(gs[2, 0])
    box_data = [group_values[g] for g in GROUP_ORDER if group_values[g].size > 0]
    box_labels = [g for g in GROUP_ORDER if group_values[g].size > 0]
    bp = ax_c.boxplot(box_data, tick_labels=box_labels, showfliers=False, patch_artist=True, widths=0.55)
    for patch, g in zip(bp['boxes'], box_labels):
        patch.set_facecolor(GROUP_COLORS[g])
        patch.set_alpha(0.75)
    for median_line in bp['medians']:
        median_line.set_color('black')
        median_line.set_linewidth(1.5)
    ax_c.set_ylabel(r'Ensemble-mean elasticity $\Delta Q/Q \, / \, \Delta P/P$ [-]', fontsize=9)
    ax_c.set_xlabel('Köppen-Geiger group', fontsize=9)
    ax_c.set_title(f'(c) Elasticity by climate group (Kruskal-Wallis H={h_stat:.0f}, '
                   f'rank $\\eta^2$={eps2:.2f}, ANOVA $R^2$={r2:.2f})', loc='left', fontsize=11)
    for i, g in enumerate(box_labels):
        vals = group_values[g]
        med = np.median(vals)
        ax_c.annotate(f'n={vals.size:,}\nmed={med:.2f}', xy=(i + 1, med), ha='center', va='center',
                      fontsize=7, linespacing=1.3, color='black')
    ax_c.grid(axis='y', alpha=0.3, linewidth=0.5)
    ax_c.set_ylim(-2, 8)
    _force_box(ax_c)

    savefig(fig, 'figure_appendix_koppen_elasticity')


if __name__ == '__main__':
    main()
