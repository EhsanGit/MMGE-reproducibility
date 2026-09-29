# data/water_balance/

Derived precipitation and water-balance fields for EM-Earth, ERA5-Land,
MSWEP and W5E5. All grids share the native 0.1 degree lat/lon grid
(lat 83.95 to -55.95, lon -179.95 to 179.95, 1400 x 3600 cells), stored as
float32, zlib-compressed NetCDF. Ocean and other no-data cells are NaN.

## Files

- `precipitation_relative_difference.nc`: long-term (1981-2019) mean annual
  precipitation and its relative difference to ERA5-Land.
  - `era5land_annual_precipitation(lat, lon)`: ERA5-Land mean annual
    precipitation, mm/yr.
  - `relative_difference_em_earth`, `relative_difference_mswep`,
    `relative_difference_w5e5` (lat, lon): relative difference in mean
    annual precipitation to ERA5-Land, %.

- `water_balance_closure.nc`: long-term water balance closure error and its
  two component ratios, common period 2002-05 to 2015-12, evaluated against
  FLUXCOM (latent heat) and G-RUN (runoff), and masked to land.
  For each forcing `f` in `em_earth`, `era5land`, `mswep`, `w5e5`:
  - `closure_error_f(lat, lon)`: chi = 1 - Qbar/Pbar - Ebar/Pbar, unitless.
  - `runoff_ratio_f(lat, lon)`: Qbar/Pbar, unitless.
  - `et_ratio_f(lat, lon)`: Ebar/Pbar, unitless.

- `wmo_ra_regions.geojson`: WMO Regional Association (RA I-VI) boundary
  polygons, used to assign each grid cell to one of the six regions
  (Africa, Asia, Europe, North America/Central America/Caribbean, South
  America, South-West Pacific) for the regional tables.
