"""Verifies the negative-elasticity statistics quoted in Sect. 3.4's discussion
of fig:figure5-elasticity: the incidence of negative precipitation elasticity
of runoff by latitude band, by number of surviving screened forcing pairs,
and the sign-agreement among surviving pairs at negative cells. Not itself
a manuscript figure or table -- a numeric verification script for the
discussion prose (95.9%/4.1% pair retention; 0.9-16.2% negative incidence
by latitude band; sign agreement among surviving pairs).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import xarray as xr

from mmge.paths import data_file
from mmge.style import MODELS, MODEL_LABEL

MAX_ABS_DELTA = 5.0
MIN_SUM_DP2 = 1e-4
MIN_VALID_PAIRS = 2
FORCINGS = ['em_earth', 'mswep', 'w5e5']

LAT_BANDS = [(-60, -45), (-45, -30), (-30, -15), (-15, 0), (0, 15), (15, 30),
             (30, 45), (45, 60), (60, 75), (75, 84)]


def main():
    delta_p = xr.open_dataset(data_file('elasticity', 'delta_p_by_forcing.nc'))['delta_p_over_p']
    delta_q = xr.open_dataset(data_file('elasticity', 'delta_q_by_forcing_model.nc'))['delta_q_over_q']
    n_valid_ds = xr.open_dataset(data_file('elasticity', 'n_valid_pairs_by_model.nc'))['n_valid_pairs']
    elasticity = xr.open_dataset(data_file('elasticity', 'runoff_elasticity_by_model.nc'))['elasticity']

    lat = delta_p['lat'].values
    lat2d = np.broadcast_to(lat[:, None], (lat.size, delta_p['lon'].size))

    all_lat, all_nvalid, all_elasticity = [], [], []
    for model in MODELS:
        dp = delta_p.values
        dq = delta_q.sel(model=model).values
        n_valid = n_valid_ds.sel(model=model).values
        slope = elasticity.sel(model=model).values
        finite = np.isfinite(slope)

        all_lat.append(lat2d[finite])
        all_nvalid.append(n_valid[finite])
        all_elasticity.append(slope[finite])

        neg = finite & (slope <= 0)
        neg_count = int(neg.sum())
        if neg_count:
            dp_n = dp[:, neg]
            dq_n = dq[:, neg]
            valid_n = (np.isfinite(dp_n) & np.isfinite(dq_n)
                       & (np.abs(dp_n) <= MAX_ABS_DELTA) & (np.abs(dq_n) <= MAX_ABS_DELTA))
            with np.errstate(invalid='ignore', divide='ignore'):
                ratio_n = np.where(valid_n, dq_n / dp_n, np.nan)

            sign = np.sign(ratio_n)

            def all_same(col):
                v = col[np.isfinite(col)]
                return v.size > 0 and np.all(v == v[0])
            sign_agree_count = sum(all_same(sign[:, i]) for i in range(sign.shape[1]))
            print(f'{MODEL_LABEL[model]}: n_valid distribution: '
                  f'1pt={int((n_valid[finite] == 1).sum())}, 2pt={int((n_valid[finite] == 2).sum())}, '
                  f'3pt={int((n_valid[finite] == 3).sum())}; negative cells={neg_count}, '
                  f'surviving pairs agreeing in sign at negative cells='
                  f'{sign_agree_count}/{neg_count} ({100 * sign_agree_count / neg_count:.1f}%)')

    lat_all = np.concatenate(all_lat)
    nvalid_all = np.concatenate(all_nvalid)
    elasticity_all = np.concatenate(all_elasticity)

    print('\n=== Negative-elasticity incidence by latitude band (pooled over 4 models) ===')
    for lo, hi in LAT_BANDS:
        sel = (lat_all >= lo) & (lat_all < hi)
        n = int(sel.sum())
        if n == 0:
            continue
        neg_frac = float((elasticity_all[sel] <= 0).mean())
        print(f'{lo:+4d} to {hi:+4d} deg: n={n:>8d}, negative fraction = {100 * neg_frac:.1f}%')

    print('\n=== Negative-elasticity incidence by n_valid (pooled over 4 models) ===')
    for k in [1, 2, 3]:
        sel = nvalid_all == k
        n = int(sel.sum())
        if n == 0:
            print(f'n_valid={k}: no cells')
            continue
        neg_frac = float((elasticity_all[sel] <= 0).mean())
        print(f'n_valid={k}: n={n:>9d} ({100 * n / nvalid_all.size:.1f}% of all valid cells), '
              f'negative fraction = {100 * neg_frac:.1f}%')


if __name__ == '__main__':
    main()
