# data/forcing_hm_variance/

Input for `scripts/070_forcing_hm_variance_decomp.py` and
`scripts/071_attribution_workflow_schematic.py` (forcing- vs. hydrological-model
variance decomposition of simulated streamflow).

## q_climatology_cube.nc

One NetCDF file holding the long-term mean simulated river discharge for every
combination of hydrological model and meteorological forcing.

- Variable `q`: long-term (1981-2019) mean daily simulated river discharge,
  units m3 s-1, dimensions `(model, forcing, latitude, longitude)`, float32.
- `model`: `htessel`, `jules`, `mhm`, `pcrglobwb`.
- `forcing`: `em_earth`, `era5land`, `mswep`, `w5e5`.
- `latitude`, `longitude`: 0.1-degree global grid (3600 x 1400 cells), degrees
  north/east.

Each (model, forcing) field is the multi-year mean of the corresponding
routed-discharge simulation; the underlying annual values have already been
averaged out. Values are undefined (NaN) over ocean and other non-routed
cells.
