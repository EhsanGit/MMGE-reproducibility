"""Reproduces Table 2 (\\label{tab:figure1-regional}): mean relative
precipitation difference to ERA5-Land, area-averaged by WMO Regional
Association region, for EM-Earth, MSWEP and W5E5. A region's Behaviour is
"Wetter" if all three forcings are higher than ERA5-Land there, "Drier" if
all three are lower, and "Mixed" otherwise.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xarray as xr
import shapely.vectorized
from shapely.geometry import shape as shapely_shape

from mmge.paths import data_file, TABLE_DIR
from mmge.regions import REGION_ORDER
from mmge.style import FORCING_LABEL
from mmge.style import round_frame

FORCINGS = ['em_earth', 'mswep', 'w5e5']


def coarsen_grid(lat, lon, step=1.0):
    """Nearest-neighbour target grid at `step` degree resolution, spanning
    the same extent as the native grid."""
    lat_start, lat_stop = (lat.min(), lat.max()) if lat[0] < lat[-1] else (lat.max(), lat.min())
    lon_start, lon_stop = (lon.min(), lon.max()) if lon[0] < lon[-1] else (lon.max(), lon.min())
    new_lat = np.arange(lat_start, lat_stop, step if lat[0] < lat[-1] else -step)
    new_lon = np.arange(lon_start, lon_stop, step if lon[0] < lon[-1] else -step)
    return new_lat, new_lon


def build_region_mask(lat, lon, geojson_path):
    """One WMO Regional Association region-name string per (lat, lon) cell."""
    lon2d, lat2d = np.meshgrid(lon, lat)
    region_grid = np.full(lon2d.shape, '', dtype=object)
    with open(geojson_path) as f:
        collection = json.load(f)
    for feature in collection['features']:
        region = feature['properties']['Region']
        geom = shapely_shape(feature['geometry'])
        inside = shapely.vectorized.contains(geom, lon2d, lat2d)
        region_grid[inside] = region
    return xr.DataArray(region_grid, coords={'lat': lat, 'lon': lon}, dims=['lat', 'lon'])


def main():
    ds = xr.open_dataset(data_file('water_balance', 'precipitation_relative_difference.nc'))
    lat, lon = ds['lat'].values, ds['lon'].values
    target_lat, target_lon = coarsen_grid(lat, lon, step=1.0)
    region_mask = build_region_mask(target_lat, target_lon, data_file('water_balance', 'wmo_ra_regions.geojson'))

    labels = [FORCING_LABEL[f] for f in FORCINGS]
    coarse = {label: ds[f'relative_difference_{f}'].interp(lat=target_lat, lon=target_lon, method='nearest').compute()
              for f, label in zip(FORCINGS, labels)}

    rows = []
    for region in REGION_ORDER:
        region_sel = (region_mask == region).values
        means = {}
        for label in labels:
            vals = coarse[label].values[region_sel]
            vals = vals[np.isfinite(vals)]
            means[label] = float(np.mean(vals)) if len(vals) else np.nan
        row = {'Region': region}
        row.update(means)
        signs = [np.sign(means[label]) for label in labels]
        if all(s > 0 for s in signs):
            row['Behaviour'] = 'Wetter'
        elif all(s < 0 for s in signs):
            row['Behaviour'] = 'Drier'
        else:
            row['Behaviour'] = 'Mixed'
        rows.append(row)

    df = pd.DataFrame(rows).set_index('Region')
    df[labels] = round_frame(df[labels], 1)

    summary = {}
    for label in labels:
        abs_vals = df[label].abs()
        tied = df.index[abs_vals == abs_vals.max()]
        summary[label] = ' / '.join(tied)
    summary_row = pd.DataFrame([summary], index=['Largest-difference region'])
    out_df = pd.concat([df, summary_row])

    out_path = TABLE_DIR / 'figure1-regional.csv'
    out_df.to_csv(out_path)
    print(out_df)
    print(f'Saved {out_path}')


if __name__ == '__main__':
    main()
