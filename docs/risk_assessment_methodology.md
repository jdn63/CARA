# Risk Assessment Methodology

## Version 2.5
Last Updated: April 2026

## Overview

CARA uses a Public Health Risk Assessment Tool (PHRAT) quadratic mean formula to combine seven primary risk domains into a single composite score. Two supplementary domains (cybersecurity and utilities) are modeled from proxy indicators and displayed separately for planning context but are not included in the PHRAT score.

The formula uses p=2 (quadratic mean) to appropriately emphasize higher-risk domains rather than averaging them away:

```
Total Risk Score = sqrt(w1 * Risk1^2 + w2 * Risk2^2 + ... + w7 * Risk7^2)
```

## Primary PHRAT Domain Weights (Public Health Discipline)

| Domain | Weight | Rationale |
|--------|--------|-----------|
| Natural Hazards | 28% | Largest annualized expected losses in WI per FEMA NRI data. Covers 4 sub-types (flood, tornado, winter storm, thunderstorm). |
| Active Shooter | 18% | CDC/ASPR identifies active shooter as high-consequence threat requiring dedicated PHEP planning. |
| Health Metrics | 17% | Infectious disease is a core PHEP capability. |
| Air Quality | 12% | EPA data shows increasing wildfire smoke episodes affecting WI. |
| Extreme Heat | 11% | NOAA data: heat is leading weather-related cause of death nationally; WI's northern latitude tempers exposure. |
| Dam Failure | 7% | Standalone EVR domain using NID/WI DNR dam inventory and FEMA flood data. |
| Vector-Borne Disease | 7% | Lyme disease (WI top-5 nationally) and West Nile Virus using WI DHS surveillance data. |

Weights are defined in `config/risk_weights.yaml` and hard-coded in `utils/data_processor.py`. They sum to 1.0.

## Supplementary Domains (Not in PHRAT Score)

| Domain | Status | Description |
|--------|--------|-------------|
| Cybersecurity | Modeled from proxy indicators | County characteristics + SVI socioeconomic percentile. No direct empirical data source. |
| Utilities | Modeled from proxy indicators | Electrical outage, utilities disruption, supply chain, and fuel shortage sub-models. |

## Data Sources

### Active Data Sources (Scheduler-Cached)

| Data Type | Source | Refresh Frequency | Data Scale |
|-----------|--------|-------------------|------------|
| Storm Events | NOAA NCEI Storm Events Database | Quarterly bulk CSV download | County level |
| Disaster Declarations | OpenFEMA Disaster Declarations Summaries v2 | Weekly | County level |
| NFIP Claims | OpenFEMA NFIP Redacted Claims v2 | Weekly | County level |
| Hazard Mitigation | OpenFEMA HMA Projects v4 | Weekly | County level |
| Dam Inventory | WI DNR Dam Safety ArcGIS FeatureServer (primary) / USACE NID (fallback) | Weekly | County level |
| Social Vulnerability | CDC/ATSDR SVI 2022 ArcGIS REST API | Annual | County level (all 72 WI counties) |
| Air Quality | EPA AirNow API | Daily | Monitoring stations |
| Heat Forecasts | NOAA/NWS API | Daily | County level |
| Respiratory Disease Surveillance | CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm, keyless Socrata API) | Weekly (Friday) | Statewide (Wisconsin) |
| Vector-Borne Disease | WI DHS EPHT CSV downloads (Lyme, WNV county-level incidence) | Weekly | County level (all 72 counties) |
| Flu Vaccination Rate | County Health Rankings 2025 CSV (BRFSS survey, all-ages seasonal) | Annual | County level (all 72 WI counties) |
| Primary Care Access | County Health Rankings 2025 CSV (physicians per 100k) | Annual | County level (all 72 WI counties) |
| COPD Prevalence | CDC PLACES Socrata API (model-based BRFSS estimates, no key required) | Annual | County level (all 72 WI counties) |
| MMR Vaccination Rate | WI DHS WIR county immunization CSV (county-immunization-data.csv) | Annual | County level (all 72 WI counties) |

### Static/Local Data Sources

| Data Type | Source | File |
|-----------|--------|------|
| Natural Hazard Baselines | FEMA NRI Census Tract data | `attached_assets/NRI_Table_CensusTracts_Wisconsin_FloodTornadoWinterOnly.csv` |
| Gun Violence Incidents | Gun Violence Archive 2023 | `attached_assets/GunViolenceArchive 2023 mass shootings data.csv` |
| School Safety | NCES SSOCS 2019-2020 | `attached_assets/SSOCS 2019_2020 data.zip` |
| Demographics/Housing | US Census Bureau ACS | `data/census/wisconsin_housing_data.csv`, `data/census/wisconsin_demographics.csv` |
| Climate Normals | NOAA 1991-2020 | Static baselines for heat risk |

## Natural Hazards Risk Methodology

Uses an Exposure-Vulnerability-Resilience (EVR) framework with a health impact factor for each sub-type (flood, tornado, winter storm, thunderstorm).

The residual risk formula:
```
Residual Risk = (Exposure * Vulnerability) * (1.5 - Resilience) * Health_Impact_Factor
```

Where:
- Exposure incorporates NOAA Storm Events historical counts, OpenFEMA disaster declarations/NFIP claims, and FEMA NRI baseline scores. Each exposure component is held on its native 0-1 scale and combined with a single layer of documented weights (no hidden pre-scaling). Raw NOAA event counts and NFIP claim counts are first normalized to events-per-year and then percentile-ranked across all 72 Wisconsin counties so that larger urban counties do not dominate every hazard purely by virtue of size. For flood: NRI 30%, NOAA storm-events percentile 20%, NFIP claims percentile 10%, proximity to major water bodies 15%, flat terrain 5%, precipitation patterns 5%, climate trend 5%, plus an additive +0.10 urban-stormwater boost (capped at 1.0) for high-impervious-surface counties (Milwaukee, Racine, Kenosha, Waukesha, Ozaukee, Washington) to reflect combined sewer overflow and runoff flooding that FEMA NRI does not capture. When the NFIP cross-county cache is empty, the NFIP weight is dropped and the remaining weights renormalize, so missing data does not silently depress every county's flood score. Tornado, winter storm, and thunderstorm exposures use the same single-weight-layer pattern, each including a NOAA storm-events percentile term (tornado 25%, winter storm 15%, thunderstorm 20%).
- Vulnerability uses SVI theme percentiles with hazard-specific sub-weights from `config/risk_weights.yaml`
- Resilience is sourced from the FEMA National Risk Index Community Resilience score (HVRI BRIC index), aggregated to the county mean and mapped onto [0.1, 0.9], with no hard-coded county adjustments. The (1.5 - Resilience) modifier is centered at neutral: low resilience (0.1) produces a 1.4x multiplier, average resilience (0.5) produces exactly 1.0x (no adjustment), and high resilience (0.9) produces a 0.6x multiplier that genuinely attenuates risk below the exposure-times-vulnerability baseline. The term was recentered from (2.0 - Resilience) after a 2026-07 external methodology review. Earlier versions of CARA applied flat bonuses to short lists of "well-resourced" or "EOC-capable" counties (typically Milwaukee, Dane, Brown, Waukesha and a few others); those lists were removed because they created abrupt cliffs between adjacent counties and were not backed by a cited capacity dataset. If a continuous capacity index (e.g. emergency-management staffing FTE per capita, hospital beds per capita, training-program participation) becomes available, it can be reintroduced as a smooth term rather than a list lookup.
- Health Impact Factor (0.80–1.50) is derived from the FEMA NRI Expected Annual Loss Score (EALS) for each hazard type, mapping county EALS percentile linearly to the adjustment range
- The four EVR scores (flood, tornado, winter storm, thunderstorm) are combined into the natural hazards domain score using an equal-weighted quadratic mean (RMS, p=2), consistent with the outer PHRAT formula. A county with one high-severity sub-hazard scores higher than one with uniformly moderate sub-domain scores.

### Mobile Home Impact on Tornado Risk
```
mobile_home_percentage = census_mobile_homes / total_housing_units
mobile_home_factor = min(1.0, mobile_home_percentage * 5)
adjusted_tornado_risk = min(1.0, base_tornado_risk * (1 + mobile_home_factor))
```

## Dam Failure Risk Methodology

Standalone EVR domain using:
- WI DNR Dam Safety Database (primary, ArcGIS FeatureServer) or USACE NID (fallback)
- Downstream population exposure based on dam height, hazard classification, and proximity
- OpenFEMA NFIP flood claims as flood exposure proxy
- SVI housing/transportation theme as vulnerability adjustment

## Vector-Borne Disease Risk Methodology

Standalone domain covering Lyme disease and West Nile Virus:
- County-level incidence rates per 100k from WI DHS EPHT CSV downloads (confirmed + probable cases)
- Environmental factors: forest cover (USDA NLCD 2021), deer density (WI DNR)
- Climate-adjusted range expansion projections
- Composite: Lyme (65% weight) + WNV (35% weight) based on relative WI burden

## SVI Integration

CDC/ATSDR Social Vulnerability Index 2022 data for all 72 Wisconsin counties. Four SVI theme percentile rankings (socioeconomic, household composition/disability, minority status/language, housing type/transportation) are used as vulnerability and resilience proxies across all risk domains. Adjustment factors are configurable in `config/risk_weights.yaml`.

## Risk Level Categories

| Level | Score Range |
|-------|------------|
| Low | Below 0.3 |
| Moderate | 0.3 to 0.5 |
| High | 0.5 to 0.7 |
| Very High | Above 0.7 |

## PHRAT Domain Dropout and Confidence Intervals

When data for a domain is unavailable or below quality thresholds for a given county, the PHRAT composite (`utils/data_processor.py`) excludes that domain, renormalizes the remaining weights to sum to 1.0, and reports a confidence interval that widens as coverage decreases. The result object exposes `original_weights`, `renormalized_weights`, `included_domains`, `excluded_domains`, `coverage_fraction`, `composite_confidence`, `confidence_interval` (lower/upper), and a human-readable `banner` summarizing any dropped domains. The dashboard surfaces this information as a data-quality banner and a confidence gauge so users can see when a composite score is built on partial coverage.

## Temporal Baseline Fallback

The Baseline-Seasonal-Trend-Acute (BSTA) temporal framework in `utils/temporal_risk.py` requires at least 12 historical data points per jurisdiction/hazard pair to compute a locally-derived baseline (trimmed mean of the middle 60 percent of historical values). When fewer than 12 points are available, the baseline component substitutes a generic 0.5 moderate-risk default; the seasonal, trend, and acute components remain locally-derived. This substitution is now exposed through the `data_quality` block returned by `analyze_temporal_risk()` (`baseline_used_fallback`, `baseline_sample_size`, `classification` of `partial` vs `full`) so the dashboard can disclose when a temporal score is built on partial coverage. This matters most for smaller counties and for tribal/regional entries that have shorter or sparser historical records.

## Predictive Analysis Limitations

The predictive analysis module (`utils/predictive_analysis.py`) uses a deterministic linear projection (±0.01 per year, converging toward 0.5) and fixed ±0.10 confidence intervals. These are illustrative planning projections, not statistically modeled forecasts. The "historical" values displayed are anchored to current risk minus a small offset. These projections should not be cited as empirical data-driven forecasts.

## References

1. FEMA National Risk Index (NRI) - Wisconsin Census Tract Data
2. NOAA NCEI Storm Events Database (bulk CSV)
3. OpenFEMA APIs: Disaster Declarations v2, NFIP Claims v2, HMA Projects v4
4. US Census Bureau American Community Survey (ACS 5-Year Estimates)
5. CDC/ATSDR Social Vulnerability Index 2022
6. WI DNR Dam Safety Database (ArcGIS FeatureServer)
7. USACE National Inventory of Dams (NID, ArcGIS FeatureServer)
8. EPA AirNow API
9. NOAA/NWS Heat Forecast API
10. CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm) - Wisconsin-specific Influenza, COVID-19, and RSV percent of ED visits; same NSSP/ESSENCE feed that underlies the WI DHS Tableau respiratory dashboards
11. WI DHS Environmental Public Health Tracking (EPHT) - Lyme/WNV county CSVs
12. Gun Violence Archive
13. NCES School Safety and Climate Survey (SSOCS) 2019-2020
14. County Health Rankings 2025 (University of Wisconsin Population Health Institute) - flu vaccination rate, primary care physician access
15. CDC PLACES 2024 (Socrata API) - COPD crude prevalence by county
16. Wisconsin Immunization Registry (WI DHS WIR) - county-level MMR vaccination rates for 24-month-olds
