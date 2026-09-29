# Elasticity data

Precipitation elasticity of simulated runoff and evapotranspiration (Sect. 3.4,
Fig. 5, Appendix C), and its supporting geography layers. All fields are on the
0.1 degree study grid (1400 lat x 3600 lon, -55.95 to 83.95 N, -179.95 to
179.95 E), float32, zlib-compressed, NaN over ocean/non-land cells unless
noted otherwise. `model` uses the keys `htessel`, `jules`, `mhm`, `pcrglobwb`;
`forcing` uses `em_earth`, `mswep`, `w5e5` (the three forcings perturbed
relative to the ERA5-Land reference).

Elasticity here always means the through-origin regression slope of relative
change in the named flux (runoff or evapotranspiration) on relative change in
precipitation (Eq. in Sect. 3.4), fitted per grid cell from ERA5-Land vs.
EM-Earth/MSWEP/W5E5, after screening out any single perturbation pair whose
relative precipitation or flux change exceeds +/-500%, and masking cells with
fewer than 2 surviving pairs or too little surviving precipitation-change
spread.

- `runoff_elasticity_by_model.nc`: `elasticity(model, lat, lon)`, the
  published per-model precipitation elasticity of runoff.
- `runoff_elasticity_avg_method_by_model.nc`: `elasticity(model, lat, lon)`,
  the same quantity under the alternative method (arithmetic mean of the
  three screened ratios instead of a regression), for the method-comparison
  check.
- `runoff_elasticity_by_forcing.nc`: `elasticity(forcing, lat, lon)`, the
  single-forcing-pair elasticity ratio (no pooling across forcings),
  ensemble mean across the four models.
- `runoff_elasticity_by_forcing_model.nc`: `elasticity(forcing, model, lat,
  lon)`, the same single-forcing-pair ratio kept per model.
- `et_elasticity_by_model.nc`: `elasticity(model, lat, lon)`, precipitation
  elasticity of simulated evapotranspiration, computed identically with
  evapotranspiration in place of runoff.
- `delta_p_perturbation.nc`: `delta_p_mean(lat, lon)` and `delta_p_std(lat,
  lon)`, the relative precipitation perturbation Delta_P/P (screened at
  +/-500%), averaged and its cross-forcing standard deviation across the
  three perturbed forcings.
- `delta_p_by_forcing.nc`: `delta_p_over_p(forcing, lat, lon)`, the
  unscreened relative precipitation perturbation per forcing (screening is
  applied in the analysis scripts, not baked into this file).
- `delta_q_by_forcing_model.nc`: `delta_q_over_q(forcing, model, lat, lon)`,
  the unscreened relative simulated-runoff perturbation per forcing and
  model.
- `n_valid_pairs_by_model.nc`: `n_valid_pairs(model, lat, lon)`, int8 count
  (0-3) of forcing pairs surviving the +/-500% screen at each cell.
- `precip_reference.nc`: `precip_mm_per_year(lat, lon)`, ERA5-Land
  long-term-mean annual precipitation (1981-2019), the reference series.
- `mrro_reference_by_model.nc`: `mrro_mm_per_day(model, lat, lon)`,
  ERA5-Land-forced long-term-mean simulated runoff (1981-2019) per model,
  the reference series.
- `wmo_region_mask.nc`: `region_code(lat, lon)`, int8 WMO Regional
  Association (RA I-VI) region assignment, built from the official wmo-ra
  boundary polygons (https://github.com/OGCMetOceanDWG/wmo-ra). Codes:
  1=Africa, 2=Asia, 3=South America, 4=North America/Central America/
  Caribbean, 5=South-West Pacific, 6=Europe, 0=none (matches
  `mmge.regions.REGION_MAP`). Covers ocean as well as land, since the WMO-RA
  boundary is a governance region, not a land mask.
- `koppen_elevation.nc`: `koppen_group(lat, lon)` (int8; 1=A tropical,
  2=B arid, 3=C temperate, 4=D continental, 5=E polar, 0=none) and
  `elevation(lat, lon)` (metres). The Koeppen-Geiger group is the
  present-day classification of Beck et al. (2018, Scientific Data),
  majority-vote regridded from its native 1 km resolution; elevation is
  ERA5 surface geopotential converted to metres, bilinearly interpolated.
  Both on the same grid as the elasticity fields.
