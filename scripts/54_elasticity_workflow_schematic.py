"""Reproduces fig:appendix-elasticity-workflow (figures/figure8_elasticity_workflow_schematic.png).

Step-by-step illustration of the precipitation-elasticity-of-runoff
computation (Sect. 3.4) at one concrete, ordinary grid cell near 48.5N,
11.0E (Danube basin, Bavaria, Germany): relative change vs. the ERA5-Land
reference, the +/-500% screen, the through-origin OLS fit per model, and
the cross-model average.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from mmge.paths import data_file
from mmge.style import MODELS, MODEL_LABEL, PALETTE_MODELS, savefig

REFERENCE = 'era5land'
PERTURBED = ['em_earth', 'mswep', 'w5e5']
FORCINGS_ALL = [REFERENCE] + PERTURBED
FORCING_LABEL = {'era5land': 'ERA5-Land', 'em_earth': 'EM-Earth', 'mswep': 'MSWEP', 'w5e5': 'W5E5'}

PALETTE_MODELS_DICT = dict(zip(MODELS, PALETTE_MODELS))
# Same forcing palette as the original workflow-schematic script (kept local:
# this schematic's forcing/model colour split is specific to this one figure).
PALETTE_FORCINGS_DICT = {'em_earth': '#c99a2e', 'era5land': '#00a3a3', 'mswep': '#d6336c', 'w5e5': '#2f6b2f'}

MAX_ABS_DELTA = 5.0
CANDIDATE_CELLS = [(51.0, 12.0), (50.5, 11.0), (49.5, 11.5), (51.5, 9.5), (48.5, 11.0)]
TARGET_MEDIAN = 1.95


def gather_example_cell_data():
    htessel_field = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity'] \
        .sel(model='htessel')
    precip_ref = xr.open_dataset(data_file('elasticity', 'precip_reference.nc'))['precip_mm_per_year']
    mrro_ref = xr.open_dataset(data_file('elasticity', 'mrro_reference_by_model.nc'))['mrro_mm_per_day']
    delta_p = xr.open_dataset(data_file('elasticity', 'delta_p_by_forcing.nc'))['delta_p_over_p']
    delta_q = xr.open_dataset(data_file('elasticity', 'delta_q_by_forcing_model.nc'))['delta_q_over_q']

    best = None
    for lat0, lon0 in CANDIDATE_CELLS:
        val = float(htessel_field.sel(lat=lat0, lon=lon0, method='nearest').values)
        score = abs(val - TARGET_MEDIAN) if np.isfinite(val) else np.inf
        if best is None or score < best[0]:
            best = (score, lat0, lon0)
    _, lat0, lon0 = best

    p_ref_val = float(precip_ref.sel(lat=lat0, lon=lon0, method='nearest').values)
    p_vals = {REFERENCE: p_ref_val}
    delta_p_here = {}
    for f in PERTURBED:
        dp = float(delta_p.sel(forcing=f).sel(lat=lat0, lon=lon0, method='nearest').values)
        delta_p_here[f] = dp
        p_vals[f] = p_ref_val * (1 + dp)

    q_vals, delta_q_here, slope = {}, {}, {}
    for model in MODELS:
        q_ref_val = float(mrro_ref.sel(model=model).sel(lat=lat0, lon=lon0, method='nearest').values)
        q_vals[model] = {REFERENCE: q_ref_val}
        delta_q_here[model] = {}
        dp_list, dq_list = [], []
        for f in PERTURBED:
            dq = float(delta_q.sel(forcing=f, model=model).sel(lat=lat0, lon=lon0, method='nearest').values)
            delta_q_here[model][f] = dq
            q_vals[model][f] = q_ref_val * (1 + dq)
            dp_list.append(delta_p_here[f])
            dq_list.append(dq)
        dp_arr, dq_arr = np.array(dp_list), np.array(dq_list)
        valid = np.abs(dp_arr) <= MAX_ABS_DELTA
        slope[model] = float(np.sum(dp_arr[valid] * dq_arr[valid]) / np.sum(dp_arr[valid] ** 2))

    ensemble_mean = float(np.mean(list(slope.values())))
    return {'lat': lat0, 'lon': lon0, 'p_vals': p_vals, 'q_vals': q_vals,
            'delta_p': delta_p_here, 'delta_q': delta_q_here, 'slope': slope, 'ensemble_mean': ensemble_mean}


def box(ax, x, y, w, h, text, facecolor='white', edgecolor='0.3', lw=1.3,
        fontsize=11.5, fontweight='normal', textcolor='0.1', ha='center', va='center',
        boxstyle='round,pad=0.02,rounding_size=0.15', zorder=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=boxstyle, linewidth=lw,
                                 edgecolor=edgecolor, facecolor=facecolor, zorder=zorder))
    ax.text(x + w / 2, y + h / 2, text, ha=ha, va=va, fontsize=fontsize,
            fontweight=fontweight, color=textcolor, zorder=zorder + 1, linespacing=1.5, clip_on=False)


def arrow(ax, xy_from, xy_to, color='0.25', lw=1.4, style='-|>', connectionstyle='arc3,rad=0.0'):
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle=style, mutation_scale=13,
                                  color=color, lw=lw, connectionstyle=connectionstyle, zorder=3))


def section_label(ax, x, y, text, color='0.15'):
    ax.text(x, y, text, ha='left', va='center', fontsize=15.5, fontweight='bold', color=color, zorder=4)


def add_inset_axes(fig, ax, data_x0, data_y0, data_x1, data_y1, label):
    pos_display = ax.transData.transform([(data_x0, data_y0), (data_x1, data_y1)])
    pos_fig = fig.transFigure.inverted().transform(pos_display)
    rect = [pos_fig[0, 0], pos_fig[0, 1], pos_fig[1, 0] - pos_fig[0, 0], pos_fig[1, 1] - pos_fig[0, 1]]
    return fig.add_axes(rect, label=label)


def main():
    data = gather_example_cell_data()
    print(f"Example cell: {data['lat']:.2f}, {data['lon']:.2f}")
    print('Per-model elasticity:', {MODEL_LABEL[m]: round(v, 4) for m, v in data['slope'].items()})
    print('Ensemble-mean elasticity:', round(data['ensemble_mean'], 4))

    fig = plt.figure(figsize=(15, 16))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 150)
    ax.axis('off')

    col_w, col_gap = 17.5, 1.0
    n_models = len(MODELS)
    grid_span = n_models * col_w + (n_models - 1) * col_gap
    row_label_w = 9.6

    LABEL_X = 2.0
    col_x0 = LABEL_X + row_label_w + 3.6
    grid_center = col_x0 + grid_span / 2

    cursor = 148.0

    section_label(ax, LABEL_X, cursor, 'INPUT')
    ax.text(LABEL_X, cursor - 2.6, '4 models x 4 forcings, each a 1981-2019 climatological\n'
                                    'long-term-mean Q and P field, at this one grid cell',
            fontsize=11.7, color='0.3', va='top')
    cursor -= 7.4

    arrow(ax, (col_x0, cursor), (col_x0 + grid_span, cursor), color='0.15', lw=1.6)
    ax.text(grid_center, cursor + 1.6, 'MODEL axis', ha='center', fontsize=14, fontweight='bold', color='0.15')
    cursor -= 3.4
    header_y = cursor - 4.2
    for j, model in enumerate(MODELS):
        cx = col_x0 + j * (col_w + col_gap)
        box(ax, cx, header_y, col_w, 4.2, MODEL_LABEL[model], facecolor=PALETTE_MODELS_DICT[model],
            edgecolor=PALETTE_MODELS_DICT[model], textcolor='white', fontweight='bold', fontsize=13)
    cursor = header_y - 1.0

    row_h, row_gap = 6.6, 1.0
    grid_top = cursor
    grid_bottom = cursor - (4 * row_h + 3 * row_gap)
    arrow(ax, (col_x0 - row_label_w - 1.8, grid_top), (col_x0 - row_label_w - 1.8, grid_bottom), color='0.15', lw=1.6)
    ax.text(col_x0 - row_label_w - 3.6, (grid_top + grid_bottom) / 2, 'FORCING axis',
            ha='center', va='center', fontsize=14, fontweight='bold', color='0.15', rotation=90)

    for i, forcing in enumerate(FORCINGS_ALL):
        ry = grid_top - i * (row_h + row_gap) - row_h
        is_ref = forcing == REFERENCE
        label_lines = [FORCING_LABEL[forcing]]
        if is_ref:
            label_lines.append('(REFERENCE)')
        label_lines.append(f"P = {data['p_vals'][forcing]:.1f} mm/yr")
        box(ax, col_x0 - row_label_w - 1.0, ry, row_label_w, row_h, '\n'.join(label_lines),
            facecolor=PALETTE_FORCINGS_DICT[forcing], edgecolor=PALETTE_FORCINGS_DICT[forcing],
            textcolor='white', fontweight='bold', fontsize=10.2)
        for j, model in enumerate(MODELS):
            cx = col_x0 + j * (col_w + col_gap)
            q = data['q_vals'][model][forcing]
            box(ax, cx, ry, col_w, row_h, f"Q = {q:.3f} mm/day",
                facecolor='white', edgecolor=PALETTE_MODELS_DICT[model], lw=1.6, fontsize=11.3)

    cursor = grid_bottom - 3.0

    arrow(ax, (grid_center, cursor + 2.0), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 1')
    ax.text(15, cursor,
            r'per model, per perturbed forcing: $\Delta P/P = (P_f - P_{ref})/P_{ref}$ ,  '
            r'$\Delta Q/Q = (Q_f - Q_{model,ref})/Q_{model,ref}$',
            fontsize=12, color='0.3', va='center')
    cursor -= 3.0

    step1_h = 16.5
    tbl_w = col_w
    step1_y0 = cursor - step1_h
    for j, model in enumerate(MODELS):
        cx = col_x0 + j * (col_w + col_gap)
        box(ax, cx, step1_y0, tbl_w, step1_h, '', facecolor='0.98', edgecolor=PALETTE_MODELS_DICT[model], lw=1.8)
        ax.text(cx + tbl_w / 2, step1_y0 + step1_h - 1.8, MODEL_LABEL[model],
                ha='center', fontsize=12.3, fontweight='bold', color=PALETTE_MODELS_DICT[model])
        for k, f in enumerate(PERTURBED):
            ty = step1_y0 + step1_h - 4.6 - k * 4.55
            dp = data['delta_p'][f]
            dq = data['delta_q'][model][f]
            ax.text(cx + 0.9, ty, FORCING_LABEL[f], fontsize=10.4, fontweight='bold',
                    color=PALETTE_FORCINGS_DICT[f], ha='left', va='center')
            ax.text(cx + 0.9, ty - 1.85, f"ΔP/P={dp:+.3f}  ΔQ/Q={dq:+.3f}",
                    fontsize=9.7, color='0.15', ha='left', va='center')

    cursor = step1_y0 - 3.0

    arrow(ax, (grid_center, cursor + 2.0), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 2')
    box_h = 7.6
    box(ax, col_x0, cursor - box_h - 1.2, grid_span, box_h,
        r'screen out any single pair with $|\Delta P/P| > 500\%$ or $|\Delta Q/Q| > 500\%$ '
        '(near-zero-reference artefact, not signal).\n'
        'All 3 forcing pairs pass at this cell, for every model (✓) -- elsewhere, a cell left with '
        'fewer than 2 surviving pairs is masked out entirely.',
        facecolor='#eef7f0', edgecolor='#2f6b2f', lw=1.3, fontsize=11.7)
    cursor = cursor - box_h - 1.2 - 3.0

    arrow(ax, (grid_center, cursor + 2.0), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 3')
    ax.text(15, cursor,
            'through-origin OLS fit of ' r'$\Delta Q/Q$' ' on ' r'$\Delta P/P$' ' across the surviving '
            'points -> one elasticity ' r'$\varepsilon$' ' per model, per grid cell',
            fontsize=12, color='0.3', va='center')
    cursor -= 3.0

    inset_h, inset_w = 21.0, tbl_w
    inset_y0 = cursor - inset_h
    slope_boxes = []
    for j, model in enumerate(MODELS):
        cx = col_x0 + j * (col_w + col_gap) - (tbl_w - col_w) / 2
        box(ax, cx, inset_y0, inset_w, inset_h, '', facecolor='white', edgecolor=PALETTE_MODELS_DICT[model], lw=1.8)
        ax.text(cx + inset_w / 2, inset_y0 + inset_h - 1.9, MODEL_LABEL[model],
                ha='center', fontsize=12.3, fontweight='bold', color=PALETTE_MODELS_DICT[model])

        inset_ax = add_inset_axes(fig, ax, cx + 1.6, inset_y0 + 4.6, cx + inset_w - 1.6,
                                   inset_y0 + inset_h - 4.0, label=f'inset_{model}')
        dp_arr = np.array([data['delta_p'][f] for f in PERTURBED])
        dq_arr = np.array([data['delta_q'][model][f] for f in PERTURBED])
        for f, dpv, dqv in zip(PERTURBED, dp_arr, dq_arr):
            inset_ax.scatter([dpv], [dqv], color=PALETTE_FORCINGS_DICT[f], s=55, zorder=3,
                              edgecolor='white', linewidth=0.7)
        span = max(abs(dp_arr).max(), 1e-6) * 1.25
        xline = np.array([-span, span])
        inset_ax.plot(xline, xline * data['slope'][model], color=PALETTE_MODELS_DICT[model], lw=2.0, zorder=2)
        inset_ax.axhline(0, color='0.82', lw=0.6, zorder=0)
        inset_ax.axvline(0, color='0.82', lw=0.6, zorder=0)
        inset_ax.set_xlim(-span, span)
        inset_ax.set_xticks([])
        inset_ax.set_yticks([])
        for spine in inset_ax.spines.values():
            spine.set_visible(False)
        inset_ax.set_facecolor('none')

        ax.text(cx + inset_w / 2, inset_y0 + 1.7, fr"$\varepsilon$ = {data['slope'][model]:.3f}",
                ha='center', fontsize=14.5, fontweight='bold', color='0.1', zorder=5)
        slope_boxes.append((cx + inset_w / 2, inset_y0))

    cursor = inset_y0 - 3.0

    section_label(ax, LABEL_X, cursor, 'STEP 4')
    ax.text(15, cursor, "average the 4 models' elasticities at this same grid cell",
            fontsize=12, color='0.3', va='center', zorder=4, bbox=dict(facecolor='white', edgecolor='none', pad=2.0))
    cursor -= 3.0

    final_box_w, final_box_h = 36, 8.6
    final_x0 = grid_center - final_box_w / 2
    final_y0 = cursor - final_box_h
    for (sx, sy), model in zip(slope_boxes, MODELS):
        arrow(ax, (sx, sy - 0.2), (grid_center, final_y0 + final_box_h + 0.4), color=PALETTE_MODELS_DICT[model], lw=1.3)

    box(ax, final_x0, final_y0, final_box_w, final_box_h, fr"ensemble-mean $\varepsilon$ = {data['ensemble_mean']:.3f}",
        facecolor='#fff6e6', edgecolor='#c99a2e', lw=2.0, fontsize=16, fontweight='bold')
    cursor = final_y0 - 2.6
    ax.text(grid_center, cursor,
            "→ one grid cell of Fig. 5's ensemble-mean elasticity map (main body).\n"
            "The per-model maps behind Step 3, before this averaging step, are Appendix C's own "
            "per-model breakdown (Fig. C1).",
            ha='center', va='top', fontsize=11.3, color='0.3', style='italic', linespacing=1.6)

    from mmge.paths import FIG_DIR
    savefig(fig, 'figure8_elasticity_workflow_schematic')


if __name__ == '__main__':
    main()
