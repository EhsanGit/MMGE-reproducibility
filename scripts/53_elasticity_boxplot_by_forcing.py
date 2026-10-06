"""Reproduces fig:elasticity-boxplot-by-forcing (figures/figure_elasticity_boxplot_by_forcing.png).

Single-forcing-pair elasticity ratio Delta_Q/Delta_P (no pooling across
forcings, unlike fig:elasticity-boxplot), by WMO region, shown as a
distribution rather than a single median (that median is
tab:elasticity-by-forcing / fig:appendix-elasticity-by-forcing).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr

from mmge.paths import data_file
from mmge.style import MODELS, MODEL_LABEL, PALETTE_MODELS, savefig
from mmge.regions import REGION_MAP, REGION_ORDER

PERTURBED = ['em_earth', 'mswep', 'w5e5']
MAX_ABS_DELTA = 5.0
MIN_SUM_DP2 = 1e-4
MIN_ABS_DP = np.sqrt(MIN_SUM_DP2)
MAX_ABS_RATIO = 20.0

MODEL_COLORS = dict(zip(MODELS, PALETTE_MODELS))
ENSEMBLE_GREY = '#4d4d4d'
SUBGROUPS = MODELS + ['ensemble']
SUBGROUP_LABELS = [MODEL_LABEL[m] for m in MODELS] + ['Ensemble mean']
SUBGROUP_COLORS = [MODEL_COLORS[m] for m in MODELS] + [ENSEMBLE_GREY]

REGION_NAME_TO_CODE = {v: k for k, v in REGION_MAP.items()}
REGION_DISPLAY = {r: r for r in REGION_ORDER}
REGION_DISPLAY['North America, Central America, Caribbean'] = 'North/Central America and the Caribbean'
FORCING_LABELS = {'em_earth': 'EM-Earth', 'mswep': 'MSWEP', 'w5e5': 'W5E5'}


def single_pair_elasticity(delta_p, delta_q):
    dp, dq = delta_p.values, delta_q.values
    valid = (np.isfinite(dp) & np.isfinite(dq) & (np.abs(dp) <= MAX_ABS_DELTA)
             & (np.abs(dq) <= MAX_ABS_DELTA) & (np.abs(dp) >= MIN_ABS_DP))
    with np.errstate(invalid='ignore', divide='ignore'):
        slope = dq / dp
    slope = np.where(valid, slope, np.nan)
    return xr.DataArray(slope, coords=delta_p.coords, dims=delta_p.dims)


def main():
    delta_p = xr.open_dataset(data_file('elasticity', 'delta_p_by_forcing.nc'))['delta_p_over_p']
    delta_q = xr.open_dataset(data_file('elasticity', 'delta_q_by_forcing_model.nc'))['delta_q_over_q']
    region_code = xr.open_dataset(data_file('elasticity', 'wmo_region_mask.nc'))['region_code']
    region_sel = {r: (region_code == REGION_NAME_TO_CODE[r]).values for r in REGION_ORDER}

    model_fields, ensemble_fields = {}, {}
    for forcing in PERTURBED:
        per_model = []
        for model in MODELS:
            e = single_pair_elasticity(delta_p.sel(forcing=forcing), delta_q.sel(forcing=forcing, model=model))
            e = e.where(np.abs(e) <= MAX_ABS_RATIO)
            model_fields[(forcing, model)] = e
            per_model.append(e)
        ensemble_fields[forcing] = xr.concat(per_model, dim='model').mean(dim='model', skipna=True)

    data = {region: {forcing: {} for forcing in PERTURBED} for region in REGION_ORDER}
    for forcing in PERTURBED:
        for model in MODELS:
            field = model_fields[(forcing, model)].values
            for region in REGION_ORDER:
                vals = field[region_sel[region]]
                data[region][forcing][model] = vals[np.isfinite(vals)]
        field = ensemble_fields[forcing].values
        for region in REGION_ORDER:
            vals = field[region_sel[region]]
            data[region][forcing]['ensemble'] = vals[np.isfinite(vals)]
            if vals.size:
                print(f'{region} / {FORCING_LABELS[forcing]} ensemble: n={vals.size}, '
                      f'median={np.median(vals[np.isfinite(vals)]):.2f}')

    plot_boxplot(data)


def plot_boxplot(data):
    import matplotlib.pyplot as plt
    n_sub = len(SUBGROUPS)
    MODEL_W, MODEL_GAP = 0.10, 0.02
    model_step = MODEL_W + MODEL_GAP
    sub_offsets = (np.arange(n_sub) - (n_sub - 1) / 2) * model_step
    block_half_width = sub_offsets.max() + MODEL_W / 2

    FORCING_GAP = 0.20
    block_step = 2 * block_half_width + FORCING_GAP
    n_forcings = len(PERTURBED)
    forcing_offsets = (np.arange(n_forcings) - (n_forcings - 1) / 2) * block_step

    REGION_SPACING = 2 * (forcing_offsets.max() + block_half_width) + 0.6
    positions_base = np.arange(len(REGION_ORDER)) * REGION_SPACING

    fig, ax = plt.subplots(figsize=(26, 7))
    for r_i, region in enumerate(REGION_ORDER):
        for f_i, forcing in enumerate(PERTURBED):
            block_center = positions_base[r_i] + forcing_offsets[f_i]
            for s_i, subgroup in enumerate(SUBGROUPS):
                vals = data[region][forcing][subgroup]
                if vals.size == 0:
                    continue
                pos = block_center + sub_offsets[s_i]
                bp = ax.boxplot([vals], positions=[pos], widths=MODEL_W, patch_artist=True,
                                 showfliers=False, medianprops=dict(color='black', linewidth=0.9))
                for patch in bp['boxes']:
                    patch.set_facecolor(SUBGROUP_COLORS[s_i])
                    patch.set_alpha(0.85)
            ax.text(block_center, 1.005, FORCING_LABELS[forcing], transform=ax.get_xaxis_transform(),
                    fontsize=16, ha='center', va='bottom')

    ax.set_xticks(positions_base)
    ax.set_xticklabels([REGION_DISPLAY[r] for r in REGION_ORDER], fontsize=20)
    ax.tick_params(axis='y', labelsize=16)
    ax.axhline(0, color='0.6', linewidth=0.7, zorder=0)
    ax.axhline(1, color='0.6', linewidth=0.7, linestyle='--', zorder=0)
    ax.set_ylabel(r'$\varepsilon$, single-forcing pair, per model and ensemble mean [-]', fontsize=18)
    ax.set_xlim(positions_base[0] - REGION_SPACING / 2, positions_base[-1] + REGION_SPACING / 2)
    for r_i in range(1, len(REGION_ORDER)):
        ax.axvline((positions_base[r_i - 1] + positions_base[r_i]) / 2, color='0.5', linestyle=':', linewidth=1.2, zorder=0)
    ax.text(0.005, 0.98, '(b)', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top', ha='left')

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=SUBGROUP_COLORS[i], alpha=0.85) for i in range(n_sub)]
    ax.legend(handles, SUBGROUP_LABELS, loc='upper right', ncol=n_sub, fontsize=18)
    fig.tight_layout()
    savefig(fig, 'figure_elasticity_boxplot_by_forcing')


if __name__ == '__main__':
    main()
