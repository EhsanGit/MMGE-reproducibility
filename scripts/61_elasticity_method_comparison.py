"""Reproduces tab:elasticity-method-comparison.

Compares the published through-origin regression method for the
precipitation elasticity of runoff against a simpler alternative
(arithmetic mean of the three screened Delta_Q/Delta_P ratios instead of a
fitted slope), both regionally and at the individual grid-cell scale.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xarray as xr

from mmge.paths import data_file, TABLE_DIR
from mmge.style import MODELS, MODEL_LABEL
from mmge.regions import REGION_MAP, REGION_ORDER

REGION_NAME_TO_CODE = {v: k for k, v in REGION_MAP.items()}
REGION_DISPLAY = {r: r for r in REGION_ORDER}
REGION_DISPLAY['North America, Central America, Caribbean'] = 'North/Central America and the Caribbean'


def main():
    reg = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity'].sel(model=MODELS)
    avg = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_avg_method_by_model.nc'))['elasticity'] \
        .sel(model=MODELS)
    region_code = xr.open_dataset(data_file('elasticity', 'wmo_region_mask.nc'))['region_code']

    reg_mean = reg.mean(dim='model', skipna=True).load()
    avg_mean = avg.mean(dim='model', skipna=True).load()

    rows = []
    for region in REGION_ORDER:
        sel = (region_code == REGION_NAME_TO_CODE[region]).values
        reg_vals = reg_mean.values[sel]
        avg_vals = avg_mean.values[sel]
        reg_med = float(np.median(reg_vals[np.isfinite(reg_vals)]))
        avg_med = float(np.median(avg_vals[np.isfinite(avg_vals)]))
        rows.append({'Region': REGION_DISPLAY[region], 'Regression': round(reg_med, 2),
                     'Averaging': round(avg_med, 2), 'Difference': round(avg_med - reg_med, 2)})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    df.to_csv(TABLE_DIR / 'elasticity-method-comparison.csv', index=False)
    print(f'Saved {TABLE_DIR / "elasticity-method-comparison.csv"}')

    # Grid-cell-scale comparison (quoted in the Appendix text).
    a = reg_mean.values
    b = avg_mean.assign_coords(lat=reg_mean.lat, lon=reg_mean.lon).values
    both_valid = np.isfinite(a) & np.isfinite(b)
    n_both = int(both_valid.sum())
    n_land = n_both

    sign_a, sign_b = np.sign(a[both_valid]), np.sign(b[both_valid])
    n_flip = int((sign_a != sign_b).sum())
    print(f'\nGrid-cell sign disagreement: {n_flip}/{n_both} = {100 * n_flip / n_both:.2f}% '
          f'(manuscript: 9.24%, 135205 of 1462945)')

    reg_negative = both_valid & (a < 0)
    n_reg_negative = int(reg_negative.sum())
    n_also_negative = int((b[reg_negative] < 0).sum())
    print(f'Regression-negative cells: {n_reg_negative} ({100 * n_reg_negative / n_land:.2f}% of land) '
          f'(manuscript: 4.29%, 62800 cells)')
    print(f'  -> also negative under averaging: {n_also_negative}/{n_reg_negative} = '
          f'{100 * n_also_negative / n_reg_negative:.2f}% (manuscript: 77.61%)')

    avg_negative = both_valid & (b < 0)
    n_avg_negative = int(avg_negative.sum())
    n_reg_also_negative = int((a[avg_negative] < 0).sum())
    print(f'Averaging-negative cells: {n_avg_negative} ({100 * n_avg_negative / n_land:.2f}% of land) '
          f'(manuscript: 11.61%, 169881 cells)')
    print(f'  -> also negative under regression: {n_reg_also_negative}/{n_avg_negative} = '
          f'{100 * n_reg_also_negative / n_avg_negative:.2f}% (manuscript: 28.69%)')


if __name__ == '__main__':
    main()
