# data/acc/

Gridded standardised anomaly correlation coefficient (ACC) between the
reference-run ensemble and independent observations, aggregated from the
full 4-model x 4-forcing x 3-variable set of native-resolution correlation
maps. All grids share the native 0.1 degree lat/lon grid (lat 83.95 to
-55.95, lon -179.95 to 179.95, 1400 x 3600 cells), stored as float32,
zlib-compressed NetCDF.

Three variables (`metric` coordinate) are covered throughout:
- `twsa`: simulated terrestrial water storage anomaly vs GravIS
- `et`: simulated evapotranspiration vs FLUXCOM
- `runoff`: simulated runoff vs GRUN

Models: `htessel`, `jules`, `mhm`, `pcrglobwb`.
Forcings: `em_earth`, `era5land`, `mswep`, `w5e5`.

## Files

- `acc_ensemble_mean.nc`: variable `acc(metric, lat, lon)`, the mean ACC
  across all 16 model x forcing combinations. Feeds the main-body ACC
  figure and the merged regional table.
- `acc_by_forcing.nc`: variable `acc(metric, forcing, lat, lon)`, the mean
  ACC across the four models, kept separate by forcing. Feeds the
  per-forcing Appendix figure.
- `acc_by_model.nc`: variable `acc(metric, model, lat, lon)`, the mean ACC
  across the four forcings, kept separate by model. Feeds the per-model
  Appendix figure.
- `wmo_ra_regions.geojson`: WMO Regional Association (RA I-VI) boundary
  polygons, used to assign each grid cell to one of the six regions
  (Africa, Asia, Europe, North America/Central America/Caribbean, South
  America, South-West Pacific) for the regional table.

ACC is unitless, dimensionless in [-1, 1].
