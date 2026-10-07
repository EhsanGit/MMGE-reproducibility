"""Reproduces tab:elasticity-regional.

Per-model, per-WMO-region median precipitation elasticity of runoff, with a
cross-model agreement/disagreement classification. The per-cell elasticity
fields are coarsened to a 1 degree grid (nearest-neighbour) before taking
the regional median, matching the manuscript's own method.
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

REGION_DISPLAY = {
    'Africa': 'Africa', 'Asia': 'Asia', 'Europe': 'Europe',
    'North America, Central America, Caribbean': 'North America, Central America, Caribbean',
    'South America': 'South America', 'South-West Pacific': 'South-West Pacific',
}


def coarsen_grid(lat, lon, step=1.0):
    lat_start, lat_stop = (lat.min(), lat.max()) if lat[0] < lat[-1] else (lat.max(), lat.min())
    lon_start, lon_stop = (lon.min(), lon.max()) if lon[0] < lon[-1] else (lon.max(), lon.min())
    new_lat = np.arange(lat_start, lat_stop, step if lat[0] < lat[-1] else -step)
    new_lon = np.arange(lon_start, lon_stop, step if lon[0] < lon[-1] else -step)
    return new_lat, new_lon


def main():
    elasticity = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity']
    region_code = xr.open_dataset(data_file('elasticity', 'wmo_region_mask.nc'))['region_code']

    full_lat, full_lon = elasticity['lat'].values, elasticity['lon'].values
    target_lat, target_lon = coarsen_grid(full_lat, full_lon, step=1.0)

    coarse = elasticity.interp(lat=target_lat, lon=target_lon, method='nearest').compute()
    region_coarse = region_code.interp(lat=target_lat, lon=target_lon, method='nearest').values

    rows = []
    for region in REGION_ORDER:
        code = {v: k for k, v in REGION_MAP.items()}[region]
        region_sel = region_coarse == code
        medians = {}
        for model in MODELS:
            vals = coarse.sel(model=model).values[region_sel]
            vals = vals[np.isfinite(vals)]
            medians[model] = float(np.median(vals)) if vals.size else np.nan
        row = {'Region': REGION_DISPLAY[region]}
        for model in MODELS:
            row[MODEL_LABEL[model]] = round(medians[model], 2)
        vals_list = [medians[m] for m in MODELS if np.isfinite(medians[m])]
        spread = round(max(round(v, 2) for v in vals_list) - min(round(v, 2) for v in vals_list), 2)
        if spread < 0.5:
            behaviour = 'Models agree'
        elif spread < 1.5:
            behaviour = 'Moderate disagreement'
        else:
            behaviour = 'Models disagree'
        row['Behaviour'] = behaviour
        row['Range'] = round(spread, 2)
        rows.append(row)

    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

    for model in MODELS:
        col = MODEL_LABEL[model]
        top = df[df[col] == df[col].max()]
        names = '/'.join(top['Region'])
        print(f'Highest-elasticity region for {col}: {names} ({df[col].max()})')

    out_path = TABLE_DIR / 'elasticity-regional.csv'
    df.to_csv(out_path, index=False)
    print(f'Saved {out_path}')


if __name__ == '__main__':
    main()
