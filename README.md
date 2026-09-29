# MMGE: reproducing the figures and tables

This repository contains the code to reproduce every figure and table of

> Modiri, E., Samaniego, L., Schweppe, R., Shrestha, P. K., Rakovec, O., Kelbling, M., Kumar, R., Leal Rojas, J. J., Martínez-de la Torre, A., Chevuturi, A., Facer-Childs, K., Robinson, E., Sutanudjaja, E., Wanders, N., and Thober, S.: *Quantifying the Global Impact of Forcing Variability on Hydrological and Land Surface Model Performance: A Multi-Model Evaluation*, Journal of Hydrometeorology (submitted).

The study evaluates four large-scale hydrological and land-surface models (HTESSEL, JULES, mHM and PCR-GLOBWB), each driven by four meteorological forcing datasets (EM-Earth, ERA5-Land, MSWEP and W5E5) over 1981–2019 at 0.1° resolution.

The scripts start from processed datasets, for example long-term means, gauge-level skill scores, per-cell elasticities and anomaly correlations. These are archived separately on Zenodo ([doi:10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)). The full model simulations are available from the corresponding authors on request.

## Quick start

```bash
git clone https://github.com/EhsanGit/MMGE-reproducibility.git
cd MMGE-reproducibility
conda env create -f environment.yml
conda activate mmge
python download_data.py      # about 0.5 GB into data/
python run_all.py            # all figures and tables into output/
```

Each script can also be run on its own, for example `python scripts/40_cdf_kge_model_regional.py`. Figures are written to `output/figures/` (PNG at 300 dpi and PDF) under the same file names as in the manuscript. Tables are written to `output/tables/` as CSV files named after the table label.

The global maps take a few minutes each to draw. A full `run_all.py` takes roughly 30–60 minutes on a laptop.

## Contents

```
mmge/                shared helpers: paths, WMO regions, plotting style and colour scales
scripts/             one script per figure or table (list below)
download_data.py     fetches the input data from Zenodo into data/
run_all.py           runs every script in order
environment.yml      conda environment
```

### Figures and tables

| Script | Manuscript item | Output |
|---|---|---|
| `10_relative_difference_precip.py` | Fig. 1: precipitation relative to ERA5-Land | `figure1_relative_difference_combined` |
| `11_relative_difference_regional_table.py` | Table 2: regional precipitation differences | `figure1-regional.csv` |
| `12_water_balance_closure.py` | Fig. 2: water-balance closure error | `figure2_water_balance_error_combined` |
| `13_water_balance_regional_table.py` | Table 3: regional closure error | `figure2-regional.csv` |
| `14_runoff_ratio_map.py` | Appendix: runoff ratio Q/P | `figure_sp1_mrro_ratio_combined` |
| `15_et_ratio_map.py` | Appendix: evapotranspiration ratio E/P | `figure_sp2_et_ratio_combined` |
| `20_acc_main_body.py` | Fig. 3: anomaly correlation, ensemble mean | `figure_acc_main_body` |
| `21_acc_by_forcing.py` | Appendix: anomaly correlation by forcing | `figure_acc_combined` |
| `22_acc_by_model.py` | Appendix: anomaly correlation by model | `figure_acc_combined_by_model` |
| `23_acc_merged_regional_table.py` | Table 4: regional anomaly correlation | `acc-merged-regional.csv` |
| `40_cdf_kge_model_regional.py` | Fig. 4a: regional KGE CDFs by model (ERA5-Land) | `cdf_model_kge_continents` |
| `41_cdf_kge_forcing_regional.py` | Fig. 4b: regional KGE CDFs by forcing (mHM) | `cdf_forcings_kge_continents` |
| `42_table_kge_model_regional.py` | Table 5: regional median KGE by model | `cdf-kge-model-regional.csv` |
| `43_table_kge_forcing_regional.py` | Table 6: regional median KGE by forcing | `cdf-kge-forcing-regional.csv` |
| `44_appendix_kge_all_models_by_forcing.py` | Appendix: KGE CDFs, all 16 combinations | `appendix_cdf_kge_all_models_by_forcing` |
| `45_table_appendix_kge_all_models_by_forcing.py` | Appendix table: median KGE, all combinations | `appendix-kge-all-models-by-forcing.csv` |
| `46_appendix_multimodel_ensemble.py` | Appendix: multi-model ensemble KGE | `cdf_multimodel_ensemble_kge_era5land` |
| `47_table_appendix_multimodel_ensemble.py` | Appendix table: multi-model ensemble | `appendix-multimodel-ensemble-regional.csv` |
| `50_elasticity_ensemble_mean.py` | Fig. 5: precipitation elasticity of runoff | `figure8_elasticity_ensemble_mean` |
| `51_elasticity_regional_table.py` | Table 7: regional elasticity | `elasticity-regional.csv` |
| `52_elasticity_boxplot_by_region.py` | Fig. 6: elasticity by region | `figure8_boxplot_by_region` |
| `53_elasticity_boxplot_by_forcing.py` | Fig. 7: elasticity by region and forcing | `figure_elasticity_boxplot_by_forcing` |
| `54_elasticity_workflow_schematic.py` | Appendix: elasticity workflow | `figure8_elasticity_workflow_schematic` |
| `55_elasticity_by_model_appendix.py` | Appendix: elasticity by model | `figure8_elasticity_precip_runoff_combined` |
| `56_elasticity_by_forcing_appendix.py` | Appendix: elasticity by forcing, and table | `figure8_elasticity_by_forcing`, `elasticity-by-forcing.csv` |
| `57_elasticity_by_koppen.py` | Appendix: elasticity by Köppen–Geiger class and elevation, and table | `figure_appendix_koppen_elasticity`, `elasticity-by-koppen.csv` |
| `58_et_elasticity_ensemble_mean.py` | Appendix: precipitation elasticity of evapotranspiration | `figure_elasticity_ensemble_mean_et` |
| `59_delta_p_ensemble_mean_spread.py` | Appendix: precipitation perturbation across forcings | `figure8_delta_p_ensemble_mean_and_spread` |
| `60_negative_elasticity_joint_map.py` | Appendix: drivers of negative elasticity | `figure8_negative_elasticity_joint_map` |
| `61_elasticity_method_comparison.py` | Appendix table: regression vs. averaging | `elasticity-method-comparison.csv` |
| `62_negative_elasticity_crosstab.py` | Statistics quoted in the elasticity discussion (printed) | — |
| `70_forcing_hm_variance_decomp.py` | Fig. 8 and appendix: forcing vs. model variance | `figure9_log2_ratio_by_forcing_combined`, `figure9_log2_ratio_combined`, `figure9_forcing_contribution`, `figure9_hm_contribution` |
| `71_attribution_workflow_schematic.py` | Appendix: variance attribution workflow | `figure9_attribution_workflow_schematic` |

## Input data

`download_data.py` places the Zenodo files under `data/`, with one subfolder per analysis. Each subfolder has a `README_<analysis>.md` describing its variables, units and dimensions.

| Folder | Content |
|---|---|
| `water_balance/` | long-term mean precipitation differences, water-balance closure error, runoff and ET ratios (0.1°) |
| `acc/` | standardised anomaly correlation of TWSa, ET and runoff against GravIS, FLUXCOM and GRUN (0.1°) |
| `kge/` | gauge-level streamflow KGE for all 16 model–forcing combinations and for the multi-model ensemble (1,445 GRDC stations) |
| `elasticity/` | per-cell precipitation elasticity of runoff and ET, precipitation and runoff perturbations, Köppen–Geiger classes and elevation (0.1°) |
| `forcing_hm_variance/` | long-term mean discharge for all 16 model–forcing combinations (0.1°) |

Streamflow KGE follows Gupta et al. (2009) and is computed from monthly discharge against GRDC observations over 1981–2019. The KGE values for PCR-GLOBWB were provided by the PCR-GLOBWB team (Department of Physical Geography, Utrecht University).

## Citation

If you use this code, please cite the article and this repository ([doi:10.5281/zenodo.YYYYYYY](https://doi.org/10.5281/zenodo.YYYYYYY)); see `CITATION.cff`.

## Licence

Code: MIT (see `LICENSE`). Data on Zenodo: CC BY 4.0.
