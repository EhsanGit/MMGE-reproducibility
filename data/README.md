# Processed datasets for the MMGE figures and tables

Processed data underlying the figures and tables of *Quantifying the Global Impact of Forcing Variability on Hydrological and Land Surface Model Performance: A Multi-Model Evaluation* (Modiri et al., submitted to Journal of Geophysical Research: Atmospheres). The code that reads these files is available at https://github.com/EhsanGit/MMGE-reproducibility and archived on Zenodo (doi:10.5281/zenodo.23211061).

The data cover four models (HTESSEL, JULES, mHM, PCR-GLOBWB) and four meteorological forcings (EM-Earth, ERA5-Land, MSWEP, W5E5), over 1981–2019 unless stated otherwise. Gridded fields are on a regular 0.1° grid (3600 × 1400 cells, 55.95°S–83.95°N). They are stored as compressed NetCDF-4, with land cells only (ocean = NaN). Gauge-level data are CSV files, one row per GRDC station, keyed by the GRDC station number.

| Folder | Content | Details |
|---|---|---|
| `water_balance/` | Precipitation differences relative to ERA5-Land; water-balance closure error; runoff and evapotranspiration ratios | `README_water_balance.md` |
| `acc/` | Standardised anomaly correlation of simulated TWSa, ET and runoff against GravIS, FLUXCOM and GRUN | `README_acc.md` |
| `kge/` | Streamflow Kling–Gupta efficiency at 1,445 GRDC stations for all 16 model–forcing combinations and for the multi-model ensemble | `README_kge.md` |
| `elasticity/` | Precipitation elasticity of runoff and evapotranspiration; precipitation and runoff perturbations; Köppen–Geiger classes and elevation | `README_elasticity.md` |
| `forcing_hm_variance/` | Long-term mean discharge for all 16 model–forcing combinations, input to the forcing-versus-model variance decomposition | `README_forcing_hm_variance.md` |

Licence: CC BY 4.0.
