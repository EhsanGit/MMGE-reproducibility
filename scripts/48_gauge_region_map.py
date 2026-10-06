"""Reproduces the appendix figure fig:appendix-gauge-regions (figures/gauge_region_map.png):
the six WMO Regional Associations used for all regional summaries, and the 1445 GRDC
gauges used for the streamflow evaluation, with the number of gauges per region."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from matplotlib.patches import Patch
from shapely.geometry import shape

from mmge.paths import data_file
from mmge.regions import REGION_ORDER
from mmge.style import savefig

REGION_DISPLAY = {'North America, Central America, Caribbean': 'North/Central America and the Caribbean'}
FILL = {'Africa': '#f4d8a8', 'Asia': '#d9e7c4', 'Europe': '#c9dcef', 'North America, Central America, Caribbean': '#f1c9c4',
        'South America': '#d7cdea', 'South-West Pacific': '#c7e6e1'}
DOT = {'Africa': '#b5651d', 'Asia': '#5b8a2b', 'Europe': '#2f6aa3', 'North America, Central America, Caribbean': '#b23a2e',
       'South America': '#6a4c9c', 'South-West Pacific': '#1f8a7a'}
LON_TICKS = np.arange(-180, 181, 30)
LAT_TICKS = np.arange(-60, 81, 20)


def main():
    regions = json.load(open(data_file('water_balance', 'wmo_ra_regions.geojson')))
    gauges = pd.read_csv(data_file('kge', 'streamflow_kge_gauges.csv'))
    counts = gauges['region'].value_counts()

    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(14, 6.4), subplot_kw={'projection': proj})
    ax.set_extent([-180, 180, -60, 84], crs=proj)
    ax.add_feature(cfeature.OCEAN, color='white', zorder=0)
    for feat in regions['features']:
        name = feat['properties']['Region']
        ax.add_geometries([shape(feat['geometry'])], crs=proj, facecolor=FILL[name],
                          edgecolor='0.35', linewidth=0.6, zorder=1)
    ax.coastlines(linewidth=0.5, zorder=2)
    for name in REGION_ORDER:
        sel = gauges[gauges['region'] == name]
        ax.scatter(sel['lon'], sel['lat'], s=7, color=DOT[name], edgecolor='none', transform=proj, zorder=3)

    ax.set_xticks(LON_TICKS, crs=proj)
    ax.set_yticks(LAT_TICKS, crs=proj)
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.tick_params(axis='both', labelsize=9)
    ax.gridlines(draw_labels=False, alpha=0.3, linewidth=0.5)

    handles = [Patch(facecolor=FILL[n], edgecolor=DOT[n], linewidth=1.5,
                     label=f'{REGION_DISPLAY.get(n, n)} (n = {int(counts.get(n, 0))})') for n in REGION_ORDER]
    ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.08), ncol=3, fontsize=9,
              frameon=False, title=f'WMO region (number of gauges; total n = {len(gauges)})', title_fontsize=9.5)
    savefig(fig, 'gauge_region_map')


if __name__ == '__main__':
    main()
