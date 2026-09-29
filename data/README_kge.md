# data/kge/

Input for `scripts/40_cdf_kge_model_regional.py` through
`scripts/47_table_appendix_multimodel_ensemble.py` (streamflow KGE by hydrological
model, forcing and region).

## streamflow_kge_gauges.csv

Gauge-level Kling-Gupta efficiency (KGE, Gupta et al., 2009 formula) of simulated
against observed monthly mean discharge, one row per GRDC gauge (n = 1445).

- `grdc_id`: GRDC station number.
- `region`: WMO/GRDC region name (see `mmge/regions.py`).
- `lat`, `lon`: gauge latitude/longitude, degrees north/east.
- `kge_<model>_<forcing>`: KGE for one of the 16 model-forcing combinations
  (`model` in `htessel`, `jules`, `mhm`, `pcrglobwb`; `forcing` in `era5land`,
  `em_earth`, `mswep`, `w5e5`), unitless, float32. Missing values (a small
  number of gauges per combination) are blank.

## multimodel_ensemble_kge_gauges_era5land.csv

Gauge-level KGE, ERA5-Land forcing only, for the four individual models and for
a genuine multi-model ensemble built by averaging/medianing the four models'
simulated discharge before scoring it against observed discharge (rather than
averaging the four already-computed KGE scores).

- `grdc_id`, `region`: as above.
- `kge_htessel`, `kge_jules`, `kge_mhm`, `kge_pcrglobwb`: each model's own KGE.
- `kge_ensemble_mean`, `kge_ensemble_median`: KGE of the mean, respectively
  median, of the four models' simulated discharge.
