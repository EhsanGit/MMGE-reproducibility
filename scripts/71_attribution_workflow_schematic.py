"""
Reproduces:
    fig:appendix-attribution-workflow
        figures/figure9_attribution_workflow_schematic.png

Illustrates the forcing-vs-model variance decomposition of script 70
step by step, at one concrete grid cell (51.85N, 6.10E, on the Rhine,
Netherlands/Germany border), using the same climatology cube and the
same magnitude threshold (computed over the whole grid, not just this cell).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import xarray as xr

from mmge.paths import data_file
from mmge.style import savefig, MODEL_LABEL, FORCING_LABEL

CELL_NAME, CELL_LAT, CELL_LON = 'Rhine, Netherlands/Germany border', 51.85, 6.10
FORCING_ORDER = ['em_earth', 'era5land', 'mswep', 'w5e5']
MODEL_ORDER = ['htessel', 'jules', 'mhm', 'pcrglobwb']
MIN_VARIANCE_PERCENTILE = 25

# Figure-specific colours (kept local rather than mmge.style's general model/forcing
# palette, so this one schematic keeps the colour-per-axis-value convention its
# boxes rely on).
PALETTE_MODELS = {'htessel': '#2a78d6', 'jules': '#eb6834', 'mhm': '#1baf7a', 'pcrglobwb': '#4a3aa7'}
PALETTE_FORCINGS = {'em_earth': '#c99a2e', 'era5land': '#00a3a3', 'mswep': '#d6336c', 'w5e5': '#2f6b2f'}


def magnitude_threshold(*components, percentile=MIN_VARIANCE_PERCENTILE):
    pooled = np.concatenate([c.where(c > 0).values.ravel() for c in components])
    pooled = pooled[np.isfinite(pooled)]
    return float(np.nanpercentile(pooled, percentile))


def log2_ratio(forcing_component, model_component, threshold):
    safe_model = model_component.where(model_component > 0)
    ratio = (forcing_component / safe_model).where(lambda r: r > 0)
    above = (forcing_component >= threshold) | (model_component >= threshold)
    return np.log2(ratio.where(above))


def gather_cell_data():
    """Re-derive every number in the workflow at one concrete grid cell, using
    the pooled magnitude threshold from the full grid (not meaningful from a
    single cell alone)."""
    cube = xr.open_dataset(data_file('forcing_hm_variance', 'q_climatology_cube.nc'))['q']

    forcing_contribution = cube.var(dim='forcing').mean(dim='model')
    model_contribution = cube.var(dim='model').mean(dim='forcing')
    model_contribution_by_forcing = cube.var(dim='model')
    threshold = magnitude_threshold(forcing_contribution, model_contribution)
    ratio_combined = log2_ratio(forcing_contribution, model_contribution, threshold)

    sel = dict(latitude=CELL_LAT, longitude=CELL_LON, method='nearest')
    q_vals = {m: {f: float(cube.sel(model=m, forcing=f).sel(**sel).values) for f in FORCING_ORDER}
              for m in MODEL_ORDER}
    forcing_var_per_model = {m: float(np.var([q_vals[m][f] for f in FORCING_ORDER])) for m in MODEL_ORDER}
    model_var_per_forcing = {f: float(np.var([q_vals[m][f] for m in MODEL_ORDER])) for f in FORCING_ORDER}

    fc = float(forcing_contribution.sel(**sel).values)
    mc = float(model_contribution.sel(**sel).values)
    lr = float(ratio_combined.sel(**sel).values)
    mc_by_forcing = {f: float(model_contribution_by_forcing.sel(forcing=f).sel(**sel).values) for f in FORCING_ORDER}
    lr_by_forcing = {}
    for f in FORCING_ORDER:
        v = log2_ratio(forcing_contribution, model_contribution_by_forcing.sel(forcing=f), threshold).sel(**sel).values
        lr_by_forcing[f] = float(v) if np.isfinite(v) else np.nan

    return dict(q_vals=q_vals, forcing_var_per_model=forcing_var_per_model,
                model_var_per_forcing=model_var_per_forcing, forcing_contribution=fc,
                model_contribution=mc, threshold=threshold, log2_ratio=lr,
                model_contrib_by_forcing=mc_by_forcing, log2_by_forcing=lr_by_forcing)


# --------------------------- drawing helpers --------------------------- #

def box(ax, x, y, w, h, text, facecolor='white', edgecolor='0.3', lw=1.3,
        fontsize=11.5, fontweight='normal', textcolor='0.1'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.15',
                                 linewidth=lw, edgecolor=edgecolor, facecolor=facecolor, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fontsize,
            fontweight=fontweight, color=textcolor, zorder=3, linespacing=1.5)


def arrow(ax, xy_from, xy_to, color='0.25', lw=1.4):
    ax.add_patch(FancyArrowPatch(xy_from, xy_to, arrowstyle='-|>', mutation_scale=13,
                                  color=color, lw=lw, zorder=3))


def section_label(ax, x, y, text):
    ax.text(x, y, text, ha='left', va='center', fontsize=15.5, fontweight='bold', color='0.15')


def bar_inset(fig, ax, x0, y0, x1, y1, label, values, colors):
    pos_display = ax.transData.transform([(x0, y0), (x1, y1)])
    pos_fig = fig.transFigure.inverted().transform(pos_display)
    rect = [pos_fig[0, 0], pos_fig[0, 1], pos_fig[1, 0] - pos_fig[0, 0], pos_fig[1, 1] - pos_fig[0, 1]]
    inset_ax = fig.add_axes(rect, label=label)
    inset_ax.bar(np.arange(len(values)), values, color=colors, width=0.68, edgecolor='white', linewidth=0.5)
    inset_ax.set_xticks([])
    inset_ax.set_yticks([])
    for spine in inset_ax.spines.values():
        spine.set_visible(False)
    inset_ax.set_facecolor('none')
    inset_ax.set_ylim(0, max(values) * 1.25 if max(values) > 0 else 1)


def main():
    data = gather_cell_data()

    fig = plt.figure(figsize=(15, 18.5))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 175)
    ax.axis('off')

    col_w, col_gap = 17.5, 1.0
    n = 4
    grid_span = n * col_w + (n - 1) * col_gap
    row_label_w = 7.6
    LABEL_X = 2.0
    col_x0 = LABEL_X + row_label_w + 3.6
    grid_center = col_x0 + grid_span / 2

    cursor = 172.0

    # ZONE 1: INPUT
    section_label(ax, LABEL_X, cursor, 'INPUT')
    ax.text(LABEL_X, cursor - 2.6,
            f'4 hydrological models x 4 forcings, each a climatological mean simulated\n'
            f'river discharge q (m3/s) field, at one grid cell: {CELL_NAME}\n'
            f'({CELL_LAT}N, {CELL_LON}E)',
            fontsize=11.7, color='0.3', va='top')
    cursor -= 10.0

    arrow(ax, (col_x0, cursor), (col_x0 + grid_span, cursor), color='0.15', lw=1.6)
    ax.text(grid_center, cursor + 1.6, 'MODEL axis', ha='center', fontsize=14, fontweight='bold', color='0.15')
    cursor -= 3.4
    header_y = cursor - 4.2
    for j, m in enumerate(MODEL_ORDER):
        cx = col_x0 + j * (col_w + col_gap)
        box(ax, cx, header_y, col_w, 4.2, MODEL_LABEL[m], facecolor=PALETTE_MODELS[m],
            edgecolor=PALETTE_MODELS[m], textcolor='white', fontweight='bold', fontsize=13)
    cursor = header_y - 1.0

    row_h, row_gap = 6.0, 1.0
    grid_top = cursor
    grid_bottom = cursor - (4 * row_h + 3 * row_gap)
    arrow(ax, (col_x0 - row_label_w - 1.8, grid_top), (col_x0 - row_label_w - 1.8, grid_bottom), color='0.15', lw=1.6)
    ax.text(col_x0 - row_label_w - 3.6, (grid_top + grid_bottom) / 2, 'FORCING axis',
            ha='center', va='center', fontsize=14, fontweight='bold', color='0.15', rotation=90)

    for i, f in enumerate(FORCING_ORDER):
        ry = grid_top - i * (row_h + row_gap) - row_h
        box(ax, col_x0 - row_label_w - 1.0, ry, row_label_w, row_h, FORCING_LABEL[f],
            facecolor=PALETTE_FORCINGS[f], edgecolor=PALETTE_FORCINGS[f], textcolor='white',
            fontweight='bold', fontsize=10.9)
        for j, m in enumerate(MODEL_ORDER):
            cx = col_x0 + j * (col_w + col_gap)
            q = data['q_vals'][m][f]
            box(ax, cx, ry, col_w, row_h, f'q = {q:,.1f} m3/s', facecolor='white',
                edgecolor=PALETTE_MODELS[m], lw=1.6, fontsize=11.3)
    cursor = grid_bottom - 3.0

    # ZONE 2: STEP 1 -- variance along each axis
    arrow(ax, (grid_center, cursor + 2.0), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 1')
    ax.text(15, cursor, 'per model: variance of q across the 4 forcings  -  per forcing: variance of q across the 4 models',
            fontsize=12, color='0.3', va='center')
    cursor -= 2.6
    ax.text(grid_center, cursor, '(units: m6 s-2, i.e. the variance of an m3 s-1 quantity)',
            ha='center', fontsize=10.5, color='0.4', style='italic')
    cursor -= 3.4

    block_gap = 4.0
    block_w = (grid_span - block_gap) / 2
    left_x0 = col_x0
    right_x0 = col_x0 + block_w + block_gap
    sub_gap = 0.8
    sub_w = (block_w - 3 * sub_gap) / 4
    step1_h = 15.5
    step1_y0 = cursor - step1_h

    ax.text(left_x0 + block_w / 2, step1_y0 + step1_h + 1.7, 'variance across forcings, per model',
            ha='center', fontsize=11.8, fontweight='bold', color='0.2')
    for j, m in enumerate(MODEL_ORDER):
        cx = left_x0 + j * (sub_w + sub_gap)
        box(ax, cx, step1_y0, sub_w, step1_h, '', facecolor='0.98', edgecolor=PALETTE_MODELS[m], lw=1.7)
        ax.text(cx + sub_w / 2, step1_y0 + step1_h - 1.7, MODEL_LABEL[m], ha='center', fontsize=10.1,
                fontweight='bold', color=PALETTE_MODELS[m])
        vals = [data['q_vals'][m][f] for f in FORCING_ORDER]
        bar_inset(fig, ax, cx + 0.9, step1_y0 + 3.6, cx + sub_w - 0.9, step1_y0 + step1_h - 3.4,
                  f'fvar_{m}', vals, [PALETTE_FORCINGS[f] for f in FORCING_ORDER])
        ax.text(cx + sub_w / 2, step1_y0 + 1.5, f"var=\n{data['forcing_var_per_model'][m]:,.0f}",
                ha='center', fontsize=9.8, color='0.15', linespacing=1.1)

    ax.text(right_x0 + block_w / 2, step1_y0 + step1_h + 1.7, 'variance across models, per forcing',
            ha='center', fontsize=11.8, fontweight='bold', color='0.2')
    for i, f in enumerate(FORCING_ORDER):
        cx = right_x0 + i * (sub_w + sub_gap)
        box(ax, cx, step1_y0, sub_w, step1_h, '', facecolor='0.98', edgecolor=PALETTE_FORCINGS[f], lw=1.7)
        ax.text(cx + sub_w / 2, step1_y0 + step1_h - 1.7, FORCING_LABEL[f], ha='center', fontsize=10.1,
                fontweight='bold', color=PALETTE_FORCINGS[f])
        vals = [data['q_vals'][m][f] for m in MODEL_ORDER]
        bar_inset(fig, ax, cx + 0.9, step1_y0 + 3.6, cx + sub_w - 0.9, step1_y0 + step1_h - 3.4,
                  f'mvar_{f}', vals, [PALETTE_MODELS[m] for m in MODEL_ORDER])
        ax.text(cx + sub_w / 2, step1_y0 + 1.5, f"var=\n{data['model_var_per_forcing'][f]:,.0f}",
                ha='center', fontsize=9.8, color='0.15', linespacing=1.1)
    cursor = step1_y0 - 3.0

    # ZONE 3: STEP 2 -- average across the other axis
    section_label(ax, LABEL_X, cursor, 'STEP 2')
    ax.text(15, cursor, 'average each set of 4 numbers over the other axis -> one number per component, per grid cell',
            fontsize=12, color='0.3', va='center', bbox=dict(facecolor='white', edgecolor='none', pad=2.0))
    cursor -= 3.4

    step2_h = 8.6
    step2_w = block_w * 0.62
    fc_x0 = left_x0 + block_w / 2 - step2_w / 2
    hc_x0 = right_x0 + block_w / 2 - step2_w / 2
    step2_y0 = cursor - step2_h
    box(ax, fc_x0, step2_y0, step2_w, step2_h, f"forcing_contribution\n= {data['forcing_contribution']:,.0f}",
        facecolor='#fdf3e2', edgecolor='#c99a2e', lw=1.8, fontsize=12.5, fontweight='bold')
    box(ax, hc_x0, step2_y0, step2_w, step2_h, f"model_contribution\n= {data['model_contribution']:,.0f}",
        facecolor='#e9f2fb', edgecolor='#2a78d6', lw=1.8, fontsize=12.5, fontweight='bold')
    for j, m in enumerate(MODEL_ORDER):
        cx = left_x0 + j * (sub_w + sub_gap) + sub_w / 2
        arrow(ax, (cx, step1_y0), (fc_x0 + step2_w / 2, step2_y0 + step2_h), color=PALETTE_MODELS[m], lw=1.0)
    for i, f in enumerate(FORCING_ORDER):
        cx = right_x0 + i * (sub_w + sub_gap) + sub_w / 2
        arrow(ax, (cx, step1_y0), (hc_x0 + step2_w / 2, step2_y0 + step2_h), color=PALETTE_FORCINGS[f], lw=1.0)
    cursor = step2_y0 - 2.4
    ax.text(grid_center, cursor,
            'model_contribution is also kept unaveraged, per forcing, for the main-body per-forcing panels.',
            ha='center', fontsize=10.9, color='0.35', style='italic')
    cursor -= 4.0

    # ZONE 4: STEP 3 -- magnitude threshold
    arrow(ax, (grid_center, cursor + 1.6), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 3')
    box_h = 10.5
    both_below = (data['forcing_contribution'] < data['threshold']) and (data['model_contribution'] < data['threshold'])
    verdict = 'both below threshold -> cell masked out' if both_below else 'at least one clears the threshold -> cell kept'
    box(ax, col_x0, cursor - box_h - 1.2, grid_span, box_h,
        'mask this cell unless max(forcing_contribution, model_contribution) >= magnitude threshold\n'
        f"({data['threshold']:,.4g}, the bottom 25th percentile of pooled positive variance, computed once "
        "over the whole grid).\n"
        f"At this cell: forcing_contribution = {data['forcing_contribution']:,.0f}, "
        f"model_contribution = {data['model_contribution']:,.0f}\n- {verdict}",
        facecolor='#eef7f0', edgecolor='#2f6b2f', lw=1.3, fontsize=11.5)
    cursor = cursor - box_h - 1.2 - 3.0

    # ZONE 5: STEP 4 -- log2 ratio
    arrow(ax, (grid_center, cursor + 1.6), (grid_center, cursor - 1.4))
    cursor -= 3.6
    section_label(ax, LABEL_X, cursor, 'STEP 4')
    ax.text(15, cursor, 'log2(forcing_contribution / model_contribution)  ->  one ratio value per grid cell',
            fontsize=12, color='0.3', va='center')
    cursor -= 3.0

    final_box_w, final_box_h = 40, 9.0
    final_x0 = grid_center - final_box_w / 2
    final_y0 = cursor - final_box_h
    dominant = 'forcing' if data['log2_ratio'] > 0 else 'model'
    box(ax, final_x0, final_y0, final_box_w, final_box_h,
        f"log2 ratio = {data['log2_ratio']:+.2f}  ({dominant}-dominated)",
        facecolor='#fff6e6', edgecolor='#c99a2e', lw=2.0, fontsize=16, fontweight='bold')
    cursor = final_y0 - 2.6

    ax.text(grid_center, cursor,
            "-> one grid cell of the main-body per-forcing log2 ratio map (per-forcing value shown below) "
            "and of the appendix combined map (this page's value, averaged over forcing).",
            ha='center', va='top', fontsize=11.1, color='0.3', style='italic', linespacing=1.5)
    cursor -= 5.0

    per_forcing_str = '   '.join(
        f"{FORCING_LABEL[f]}: {data['log2_by_forcing'][f]:+.2f}" if np.isfinite(data['log2_by_forcing'][f]) else
        f"{FORCING_LABEL[f]}: masked" for f in FORCING_ORDER)
    ax.text(grid_center, cursor, per_forcing_str, ha='center', fontsize=11.1, color='0.2')

    savefig(fig, 'figure9_attribution_workflow_schematic')
    print(f'Example cell: {CELL_NAME} ({CELL_LAT}, {CELL_LON})')
    print('forcing_contribution:', round(data['forcing_contribution'], 4))
    print('model_contribution:', round(data['model_contribution'], 4))
    print('threshold:', round(data['threshold'], 6))
    print('log2_ratio (combined):', round(data['log2_ratio'], 4))
    print('log2_ratio by forcing:', {FORCING_LABEL[f]: round(v, 4) if np.isfinite(v) else None
                                      for f, v in data['log2_by_forcing'].items()})


if __name__ == '__main__':
    main()
