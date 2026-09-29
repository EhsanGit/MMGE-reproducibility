"""Reproduces Table 4 (\\label{tab:acc-merged-regional}): ensemble-mean
standardised ACC (TWSa vs GravIS, ET vs FLUXCOM, runoff vs GRUN), area
averaged over each WMO Regional Association region, together with a
region's overall Behaviour classified from the mean of the three metrics
as Weak (below 0.35), Moderate (0.35-0.45) or Strong (above 0.45).
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import xarray as xr
from shapely import contains_xy
from shapely.geometry import shape as shapely_shape

from mmge.paths import data_file, TABLE_DIR
from mmge.style import round_frame
from mmge.regions import REGION_ORDER

METRICS = [('twsa', 'TWSa ACC'), ('et', 'ET ACC'), ('runoff', 'GRUN ACC')]


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
        inside = contains_xy(geom, lon2d, lat2d)
        region_grid[inside] = region
    return xr.DataArray(region_grid, coords={'lat': lat, 'lon': lon}, dims=['lat', 'lon'])


def main():
    ds = xr.open_dataset(data_file('acc', 'acc_ensemble_mean.nc'))
    lat, lon = ds['lat'].values, ds['lon'].values
    target_lat, target_lon = coarsen_grid(lat, lon, step=1.0)

    region_mask = build_region_mask(target_lat, target_lon, data_file('acc', 'wmo_ra_regions.geojson'))

    coarse = {}
    for metric, label in METRICS:
        coarse[label] = ds['acc'].sel(metric=metric).interp(
            lat=target_lat, lon=target_lon, method='nearest').compute()

    labels = [label for _m, label in METRICS]
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
        vals_list = [means[l] for l in labels if np.isfinite(means[l])]
        if len(vals_list) == len(labels):
            row_mean = np.mean(vals_list)
            row['Behaviour'] = 'Strong' if row_mean > 0.45 else ('Moderate' if row_mean > 0.35 else 'Weak')
        else:
            row['Behaviour'] = 'Incomplete'
        rows.append(row)

    df = pd.DataFrame(rows).set_index('Region')
    df = round_frame(df, 2)
    out_path = TABLE_DIR / 'acc-merged-regional.csv'
    df.to_csv(out_path)
    print(df)
    print(f'Saved {out_path}')


if __name__ == '__main__':
    main()
