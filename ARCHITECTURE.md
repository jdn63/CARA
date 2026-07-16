# CARA Architecture and Decision Log

This document holds the deep architectural detail and dated decision notes for
CARA. The top-level `replit.md` is intentionally short and points here for any
agent or contributor who needs the full picture.

Sections:
- System Architecture (backend, frontend, core features)
- External Data Sources and Integrations
- Strategic Preparedness Baseline (Option 1)
- Disease Expansion v1 (Shape A outbreak flags)
- Operational Notes and Architectural Decisions

## System Architecture

### Backend

- Framework: Flask (Python) with a modular utility structure under `utils/`.
- Database: PostgreSQL with PostGIS extension. Schema migrations are managed
  by Alembic in `migrations/`. Run `alembic upgrade head` after any model
  change.
- Scheduling: APScheduler runs all live data fetches. See
  `utils/data_source_refresher.py` and `data/config/scheduler_config.json`.
- Configuration: YAML in `config/risk_weights.yaml` for risk-domain weights,
  temporal weights, disease severity profiles, alert thresholds, and
  jurisdiction-specific overrides.
- Data processing: Pandas, NumPy, GeoPandas. The runtime composite path uses
  (a) PHRAT quadratic-mean weight renormalization over the surviving set of
  available domains in `utils.data_processor.process_risk_data()` and
  (b) min-max percentile normalization in
  `utils.data_processor.process_jurisdictions_percentile_data()`.
  The Z-score helpers in `utils.config_manager` exist but are not currently
  called from the runtime pipeline (review finding M7, 2026-05-20); the prior
  claim of active Z-score normalization and outlier handling was inaccurate
  and has been removed pending a decision to either wire them in or delete
  the helpers.

### Frontend

- Templates: Jinja2 with Bootstrap 5. The dashboard view is split into 17
  partials under `templates/dashboard/` (one per section, category, and tile);
  `templates/dashboard.html` is a thin 29-line orchestrator that includes
  them. Edit individual sections in their partial, not the orchestrator.
- Styling: custom CSS with accessibility support and a dark theme.
- Visualization: Folium for interactive geospatial maps; CSS progress bars
  and inline SVG sparklines for BSTA temporal components (no JS chart
  library).
- JavaScript: modern ES6+ for dynamic interactions.

### Core System Features

- Risk Assessment Engine: multi-domain scoring (natural hazards, infectious
  disease, active shooter, climate-adjusted risks, dam failure, vector-borne
  disease) with weighted calculations and geographic scaling. Includes
  historical analysis, predictive modeling, and detailed logging of variable
  contributions.
- Multi-Discipline Support: Public Health and Emergency Management
  perspectives use the same data sources but different vulnerability and
  resilience weights (population health outcomes for PH; critical
  infrastructure impacts for EM). See "Discipline toggle and WEM Regions
  (Phase 1, 2026-05-20)" below for the active surface, cache-key shape,
  and Phase 2/3 roadmap.
- Data Integration Layer: scheduler-driven, with all external data
  pre-fetched and stored in the Postgres cache. User requests never make
  external HTTP calls (see Cache-only request path below).
- User Interface: interactive dashboard, automated action plans, PDF report
  generation, user feedback intake.
- Administrative Features: scheduler management, feedback analytics, system
  status monitoring.
- Data Export: Kaiser Permanente HVA-compatible Excel reports for HERC
  regions and individual jurisdictions; PH-versus-EM comparison Excel export.

### Risk Methodologies

- Natural Hazard EVR: CARA-specific Exposure-Vulnerability-Resilience
  transform `Risk = E * V * (2.0 - R) * HIF` with a health impact factor,
  using real NOAA Storm Events counts and OpenFEMA claims/declarations.
  Review finding H5 (2026-05-20): this is NOT the FEMA NRI
  `(1+SVI)/(1+R)` denominator residual-risk formula and will produce
  different numbers. See `templates/methodology.html` EVR Framework card
  for the side-by-side comparison. FEMA NRI EALS data feeds the Health
  Impact Factor input only.
- Dam Failure: standalone EVR domain using NID Wisconsin dam inventory data,
  with downstream population exposure computed from inundation zones.
- Vector-Borne Disease: standalone domain covering Lyme disease and West
  Nile Virus, using county-level incidence rates per 100k from official
  WI DHS EPHT CSV downloads (weekly), environmental factors, and
  climate-adjusted range expansion projections.

## External Data Sources and Integrations

All integrations below are keyless unless noted. The 23 canonical source IDs
accepted by the admin refresh endpoint live in
`data/config/scheduler_config.json -> data_sources`.

- Local Census Data Files: county demographic and housing data, CSV.
- Wisconsin DHS API: health metrics and surveillance.
- CDC NSSP Emergency Department Visits (weekly): WI percent of ED visits
  for Influenza, COVID-19, RSV. Endpoint `data.cdc.gov/resource/vutn-jzwm.json`,
  Friday refresh. Activity level + week-over-week trend. Used in
  `utils/nssp_respiratory.py`. Replaces former WI DHS Tableau PDF scraper.
- WI DHS EPHT Lyme and WNV Surveillance: county-level vector-borne incidence
  from official EPHT CSVs (lyme-county.csv, west-nile-data-county.csv). All
  72 counties, confirmed and probable case counts and crude rates per 100k.
  Weekly automated CSV download. Source WEDSS via dhs.wisconsin.gov/epht.
- USDA Forest Service FIA (Forest Inventory and Analysis) forest cover:
  per-county forest-cover percent for all 72 counties, used by the
  vector-borne disease land-cover exposure term. Design-based area
  estimate from FIADB EVALID 552501 (WISCONSIN 2025 current-area
  evaluation): forest_cover_pct = accessible forest land
  (COND_STATUS_CD=1) divided by total land (COND_STATUS_CD in 1,2), each
  condition expanded by CONDPROP_UNADJ * ADJ_FACTOR (SUBP or MACR by
  PROP_BASIS) * EXPNS from POP_STRATUM. Replaces the v1 curated seed
  estimates. Static seed written into
  `data/disease/wisconsin_vector_borne_baseline.json`
  (`forest_cover_source` = FIA_EVALID_552501 on every county) with an
  audit snapshot in `data/forest/wisconsin_county_forest_cover.json`.
  Source `apps.fs.usda.gov/fia/datamart/CSV/`.
- PHMSA Pipeline Safety Flagged Incident Files: per-county Wisconsin
  pipeline incident counts (gas distribution, gas transmission/gathering,
  hazardous liquid), trailing 20 years (incident year 2006 onward), used
  as an additive term in hazmat_industrial exposure. All 72 counties;
  zero counts are real measurements (full WI extract), not gaps. The
  PHMSA host blocks automated access (Akamai 403), so the file is
  retrieved from the Internet Archive Wayback snapshot; the dataset is
  also cataloged at datahub.transportation.gov (qdme-9bbm). Seed in
  `data/hazmat_scoping/wi_county_pipeline_incidents.json`.
- USDA NASS Census of Agriculture 2022 (QuickStats API): real per-county
  chemical expense, fertilizer expense, harvested cropland acres, and
  milk-cow inventory for all 72 counties, combined into a 0-1
  ag_chemical_intensity score (weights 0.5 chemical+fertilizer expense,
  0.25 cropland, 0.25 milk cows; each normalized to the statewide 95th
  percentile; weights renormalize when a field is census
  disclosure-suppressed). Drives hazmat_agricultural exposure, replacing
  the v0 tier proxy. Rebuilt with
  `python3 scripts/build_ag_chemical_seed.py` using the
  NASS_QUICKSTATS_API_KEY secret (development only; the runtime app
  never calls the API, so the key is NOT needed on Render). Rerun when
  a new Census of Agriculture is released (every 5 years). Static seed
  in `data/hazmat_scoping/wi_county_ag_chemical.json`. Suppressed
  values are stored as null, never fabricated; Menominee has no census
  farm records and scores an honest floor.
- CDC/ATSDR SVI 2022 ArcGIS REST API: county SVI percentile rankings for
  all 72 WI counties. Bulk fetch. Stored in
  `data/svi/wisconsin_svi_data.json`. Scheduler refreshes annually via
  `fetch_bulk_svi_data()`.
- WI DHS Heat Vulnerability Index (quarterly): public ArcGIS MapServer at
  `https://dhsgis.wi.gov/server/rest/services/DHS_HVI/Heat_Vulnerability_Index/MapServer/0`.
  4,472 census block groups; composite HVI z-score plus environmental,
  health, population, and socioeconomic sub-indices. Paginated fetch (3
  pages), aggregated to a 72-county table via unweighted mean of
  block-group z-scores, min-max normalized to a 0-to-1 vulnerability_score
  and bucketed to DHS quintile categories (Low / Moderate Low / Moderate
  / Moderate High / High). Snapshot in
  `data/wi_dhs_hvi/wisconsin_county_hvi.json`; persistent cache 90-day TTL.
  Scheduler refreshes quarterly via `refresh_all_wi_dhs_hvi()`. Replaces
  former 404-prone HTTP fetcher in `utils/heat_vulnerability.py`. Used as
  the preferred baseline-vulnerability source in
  `utils/strategic_extreme_heat.py` (SVI is fallback) and as the data
  behind `calculate_heat_acute_risk()` consumed by
  `utils/temporal_risk.py` acute heat path.
- FEMA APIs: natural hazard risk indices.
- OpenFEMA APIs: Disaster Declarations Summaries v2, NFIP Redacted Claims
  v2, Hazard Mitigation Assistance Projects v4.
- NOAA NCEI Storm Events Database: bulk CSV downloads of WI storm events.
- WI DNR Dam Safety Database (primary): Wisconsin Repository of Dams
  ArcGIS FeatureServer.
- USACE NID ArcGIS FeatureServer (fallback): National Inventory of Dams.
- EPA AirNow API: air quality monitoring.
- NOAA/NWS: heat forecasting data.
- Wisconsin Hospital Association (WHA) API: REMOVED 2026-05. Previously
  used for hospital capacity. Replaced by CDC NHSN Hospital Respiratory
  Data (`utils/nhsn_hospital.py`, Socrata endpoint
  `data.cdc.gov/resource/ua7e-t2fy`), which provides equivalent statewide
  ICU bed and respiratory-disease occupancy without a HERC partner
  agreement. No code path still calls a WHA endpoint.
- County Health Rankings Annual CSV: flu vaccination rate (BRFSS,
  all-ages seasonal, county-specific) and primary care physician density
  (per 100k) for all 72 WI counties. Annual March release. Used in
  `utils/health_metrics_data.py`.
- CDC PLACES Socrata API: COPD crude prevalence by county for all 72 WI
  counties. Endpoint `data.cdc.gov/resource/swc5-untb.json`. Model-based
  BRFSS estimates, annual update. Used in `utils/health_metrics_data.py`.
- WI DHS WIR County Immunization CSV: MMR (1) vaccination rate for
  24-month olds by county (most recent year). Direct download from
  `dhs.wisconsin.gov/immunization/county-immunization-data.csv`. Annual
  update. Used in `utils/dhs_data.py`.
- USDA APHIS HPAI H5N1 Detections (weekly): WI-filtered livestock and
  commercial poultry detections from public CSV exports. Drives the H5N1
  outbreak flag (`utils/h5n1_surveillance.py`). Scheduler job
  `refresh_all_h5n1`. Registry ID `h5n1` (168h, max_age 14d). Tiers:
  none / national_only / state / local (configurable boosts in
  `config/risk_weights.yaml -> disease_alert_thresholds.h5n1`).
- CDC Mpox State Surveillance Socrata (weekly): endpoint
  `data.cdc.gov/resource/usqr-pmk5.json`. WI 4-week rolling case count
  thresholded to baseline / elevated / cluster tiers. Used in
  `utils/mpox_surveillance.py`. Scheduler job `refresh_all_mpox`.
- CDC NNDSS Enteric and Legionellosis Subset (weekly): same Socrata
  endpoint as `nndss_communicable` (`data.cdc.gov/resource/x9gk-5huc.json`)
  filtered to Salmonellosis, STEC, Shigellosis, Campylobacteriosis,
  Cryptosporidiosis, Giardiasis, plus Legionellosis. Drives two flags:
  an enteric composite (norovirus folded in) and a separate legionellosis
  building-water flag. Used in `utils/nndss_enteric.py`. Scheduler job
  `refresh_all_nndss_enteric`.

Third-Party Services: Bootstrap 5 (frontend framework), Font Awesome (icons).

## Strategic Preparedness Baseline (Option 1, 2026-05-20)

P-times-C floor on the infectious-disease risk score so the displayed value
never drops below a meaningful preparedness level on quiet surveillance
weeks. Acute case-driven paths are unchanged; the floor only ever raises the
displayed score.

- Module: `utils/strategic_baseline.py`
  (`compute_disease_baselines(county_name)`).
- Formula: per-disease baseline = severity_index * county_vulnerability *
  (1 - 0.5 * response_capacity), clamped to [0.10, 0.60]; aggregate =
  severity-weighted mean across the disease portfolio.
- Severity inputs: `config/risk_weights.yaml -> disease_severity_profiles`,
  14 diseases (measles, meningococcal, seasonal influenza, COVID-19,
  RSV, H5N1, mpox, legionellosis, salmonellosis, STEC, shigellosis,
  campylobacteriosis, cryptosporidiosis, giardiasis). Pertussis was
  removed in v28.7 along with the CARA-specific pertussis_elevated
  heuristic. Each
  entry carries CFR, hospitalization rate, R0, vulnerable-population
  multiplier, plus an explicit literature citation and source URL (CDC
  Pink Book, Yellow Book, MMWR, FoodNet, WHO).
- County inputs: SVI, MMR coverage, COPD prevalence, primary-care density,
  all pulled from existing CARA caches; missing values resolve to neutral
  0.5.
- Integration: `utils/disease_surveillance.get_disease_metrics()` computes
  `acute_risk_score` (unchanged formula), then
  `risk_score = max(acute_risk_score, aggregate_baseline)`. Both numbers
  plus the per-disease table are attached to the returned dict for
  dashboard transparency.
- Mode: applied unconditionally. CARA is effectively always in
  strategic_planning mode for the request path (emergency_response mode
  retired 2026-05). No mode flag plumbing required.
- Dashboard: `templates/dashboard/_strategic_baseline_panel.html` renders
  aggregate, current acute, and displayed scores side by side, plus the
  full per-disease table with citations. Included by
  `_category_biological.html`.
- Upgrade path to Option 2: per-disease scores are returned explicitly, so
  a future two-component side-by-side display (Current Activity vs
  Strategic Preparedness) can be added without rewriting
  `utils/strategic_baseline.py`.

## Disease Expansion v1 (Shape A outbreak flags, 2026-05-20)

Lightweight statewide outbreak flags that nudge the infectious_disease
Acute multiplier. Dispatched from `utils/disease_surveillance.py`
immediately after the measles `outbreak_boost` calculation. Surfaced in
`templates/dashboard/_active_surveillance_flags.html` (included by
`_category_biological.html`).

- Modules: `utils/h5n1_surveillance.py`, `utils/mpox_surveillance.py`,
  `utils/nndss_enteric.py` (provides both `get_enteric_outbreak_flags()`
  and `get_legionella_outbreak_flags()`).
- Stacking rule: `stacked_boost = min(0.40, max_individual_boost + 0.05 *
  other_active_flag_count)`. Replaces the measles-only boost when any flag
  is active. Stored on `outbreak_conditions['stacked_outbreak_boost']`.
- Isolation: flags are written only to `outbreak_conditions` inside
  `disease_surveillance.py`. They do NOT cross-contaminate active_shooter,
  natural_hazards, or any other domain (design decision #5).
- Granularity: all v1 flags are statewide Wisconsin (design decision #2).
  Each dashboard row shows a "WI statewide" badge. County-level escalation
  tiers are reserved for v2.
- Norovirus: folded into the enteric composite per design decision #3
  (NNDSS does not list norovirus as individually notifiable; the composite
  cluster signal reflects the same PHEP response posture).
- Cache-only invariant: every fetcher calls `is_cache_only_mode()` after
  its persistent-cache lookup and short-circuits to a `_fallback()` payload
  on cache miss in request context. Live HTTP is performed exclusively by
  the scheduler jobs (`refresh_all_h5n1`, `refresh_all_mpox`,
  `refresh_all_nndss_enteric` in `utils/data_source_refresher.py`).
- Thresholds: all tunable in
  `config/risk_weights.yaml -> disease_alert_thresholds` (h5n1, mpox,
  enteric, legionella blocks). Marked as CARA operational heuristics, not
  CSTE/CDC published thresholds.

## Discipline toggle and WEM Regions (Phase 1, 2026-05-20)

Phase 1 surfaces the previously backend-only Emergency Management
discipline weights in the user interface and adds a WEM (Wisconsin
Emergency Management) regional rollup mirroring the existing HERC
surface. The toggle does NOT alter any data source, scheduler, or
cache-only invariant; it only changes which weight set
`process_risk_data()` applies and which template-context strings render.

Discipline resolution. `utils/discipline.py` is the single source of
truth. Resolution order on every request: `?discipline=<v>` URL param
(persisted to session if valid), then `session['discipline']`, then
`'public_health'` default. `VALID = {'public_health', 'em'}`; anything
else is ignored. `discipline_label(d)` returns "Public Health" or
"Emergency Management". The context processor in `core.py` injects
`active_discipline` and `discipline_label` into every template so the
header toggle in `templates/components/navigation.html` and the EM
banner in `templates/components/em_banner.html` (included from
`templates/base.html`) work site-wide.

Route threading. Three routes in `routes/dashboard.py` pass the active
discipline into `process_risk_data(jurisdiction_id, discipline=...)`:
`dashboard`, `print_summary`, `action_plan`. The dashboard persistent
cache key is bumped to `dashboard_full_v6_{discipline}_{jurisdiction_id}`
because the cached payload is discipline-specific; v5 caches were
discipline-blind and are invalidated by the version suffix. Action plan
CONTENT remains Public-Health-tailored (rationale strings, recommended
actions) until Phase 2; only the prioritization order shifts under EM
weights. The EM banner in `templates/components/em_banner.html` makes
this caveat explicit and is per-session dismissable via
`sessionStorage`.

WEM regional surface. `data/wem/wem_regions.json` defines 6 WEM regions
covering all 72 Wisconsin counties exactly once (no overlap, no gaps).
`data/geojson/wisconsin_wem_regions.geojson` is built by
`scripts/build_wem_geojson.py` from the existing county GeoJSON
(`data/tribal/wisconsin_counties.geojson`); each WEM region is a
MultiPolygon grouping its member counties without dissolving internal
boundaries (informative for EM planners). `utils/wem_risk_aggregator.py`
mirrors the two-stage county-mean rollup in
`utils/herc_risk_aggregator.py` but always calls
`process_risk_data(jid, discipline='em')` and uses
`em_overall_risk_weights` from `config/risk_weights.yaml`. The output
dict aliases `herc_id = wem_id` so the shared regional dashboard
template can consume it without forking.

Multi-county health departments (2026-07-16). Two Wisconsin LHDs serve
two counties each: Shawano-Menominee Counties Health Department
(jurisdiction id 45) and Washington Ozaukee Public Health Department
(id 61). `utils/jurisdiction_mapping_code.py` remains one-to-one
(id -> primary county) for single-county lookups, but regional
aggregation must use `get_counties_for_jurisdiction()` (same module),
which returns every served county via the `multi_county_jurisdictions`
override. Both `utils/herc_risk_aggregator.py` and
`utils/wem_risk_aggregator.py` use it for region membership and bucket
the jurisdiction's scores into EVERY served county that belongs to the
region. Before this fix, Shawano and Washington silently vanished from
the county-balanced rollup (Northeast WEM showed 12 of 13 counties,
Southeast 7 of 8), so the tool disagreed with the official WEM region
composition at wem.wi.gov/regional-offices. Regression coverage:
`tests/test_regional_aggregation_integrity.py`
(TestMultiCountyJurisdictionCoverage) asserts every county in
`data/wem/wem_regions.json` has at least one covering jurisdiction.

Shared regional dashboard. `templates/herc_dashboard.html` is shared
between HERC (PH, default) and WEM (EM) via Jinja `set` defaults at the
top of the template:
- `region_kind` ("HERC" or "WEM"; controls h2 title, overview header,
  badge text, badge color via `region_badge_class`)
- `discipline_label` ("Public Health" or "Emergency Management")
- `print_url_prefix` ("/herc-print-summary" or "/wem-print-summary")
- `export_url` (optional; KP HVA export shown only when set; HERC sets
  it, WEM passes `None`)
- `show_hpp_section` (Hospital Preparedness Program block; True for
  HERC, False for WEM)

Routes are `/wem-dashboard/<wem_id>` and `/wem-print-summary/<wem_id>`
in `routes/wem.py`, registered as `wem_bp` in `core.py` alongside
`herc_bp`. The home page (`templates/index.html`) gains a "WEM Regions
(EM)" tab next to "HERC Regions (PH)"; `routes/public.py` fetches
`get_all_wem_regions()` and passes `wem_regions` to the template.

Phase 2 (planned). EM-tailored action plan rationale and recommended
actions in `templates/action_plan.html` (today the template renders the
same PH copy regardless of discipline). The EM banner explicitly flags
this as upcoming.

Phase 3 (planned). EM-specific outbreak / incident triggers, EM-only
domains (e.g., critical infrastructure status from utilities feeds),
and a dedicated EM print summary layout that omits population-health
narrative.

Invariants preserved end-to-end:
- Cache-only request path: no new external fetchers; WEM aggregator
  consumes the same cached domain scores HERC does.
- Tribal-hide v22: WEM rollups operate at the county level and do not
  expose Tribal jurisdictions.
- PH/EM comparison Excel (`/em-comparison-export/<jid>`) is untouched
  and still produces the same numbers as v26.

## Operational Notes and Architectural Decisions

### BSTA Acute retirement (2026-05)

The Acute temporal component is formally retired from every non-infectious
domain. `utils/temporal_risk.TemporalRiskComponent.calculate_components()`
only calls `_check_for_active_events()` when
`risk_type == 'infectious_disease'`; the dead helpers
`_check_weather_alerts`, `_check_extreme_heat_conditions`, and
`_check_basic_heat_conditions` were deleted. `config/risk_weights.yaml` no
longer declares an `acute` key on the `strategic_planning` mode and the
former `emergency_response` mode block was removed so acute cannot be
flipped on by accident. Infectious disease keeps its 15% Acute weight from
CDC NSSP respiratory surveillance via the `domain_overrides.infectious_disease`
block. Canonical 12-month seasonal patterns were hoisted to
`utils.temporal_risk.SEASONAL_PATTERNS` as the single source of truth shared
by the calculator, `get_hazard_calendar`, and the new
`utils.bsta_visualization` module. `templates/dashboard/_bsta_temporal.html`
was redesigned to a sparkline-plus-current-month-dot view with a
plain-language posture toggle (inline SVG, no JS chart library). The HERC
regional rollup table marks Acute as "retired" for non-infectious rows. See
`methodology.html` Temporal Framework card for the public-facing description.

### Cache persistence across deploys (2026-05-20)

The persistent cache lives in the Postgres `data_source_cache` table, not on
the application filesystem. Normal Render code redeploys do not touch the
database, so cached data survives every routine deploy and the APScheduler
keeps weekly, monthly, and quarterly feeds rolling on their normal cadence.
The cache only goes empty after an explicit DB-resetting event: recreating
the Postgres add-on, a destructive migration, a manual TRUNCATE, or a
"Clear cache & deploy" that coincided with a fresh DB. After any such
event, trigger the per-source admin refresh endpoint
`GET /api/refresh-data/<source>` with header
`X-API-Key: $CARA_ADMIN_API_KEY` for each of the 23 source IDs in
`data/config/scheduler_config.json -> data_sources`.

Do not add an auto-seed-on-startup hook. A version-keyed trigger
under-fires because `VERSION.txt` rarely bumps relative to deploy
frequency; a commit-SHA trigger over-fires on every push; an unconditional
startup trigger re-runs every time Render wakes the instance from sleep.
The manual loop is the right tool for this rare event.

### Cache-only request path (architectural guarantee, enforced 2026-05-19)

User dashboard requests never make external HTTP calls.
`utils.data_processor.process_risk_data()` enters
`utils.request_context.cache_only_context()`, which sets a thread-local
flag. Every fetcher reachable from the request path (`nssp_respiratory`,
`nndss_communicable`, `nhsn_hospital`, `dhs_data` MMR, `health_metrics_data`
CHR/PLACES, `svi_data`, `wi_dhs_hvi`, `vbd_data_fetcher`, `air_quality_data`,
`correctional_facilities`, `extreme_heat_metrics`) checks
`is_cache_only_mode()` after its persistent-cache lookup and, on a cache
miss in request context, returns its existing fallback payload while
recording the blocked source on
`result['data_quality']['blocked_fetches']`. Live HTTP is performed
exclusively by scheduler jobs in `utils/data_source_refresher.py` (those
jobs do not enter the context). To add a new request-path fetcher: import
`is_cache_only_mode, record_blocked_fetch` from `utils.request_context` and
short-circuit after the cache check.

## Discipline-tailored landing surfaces (v28)

v27 added the PH vs EM toggle and routed every dashboard render through
`process_risk_data(..., discipline=...)`. v28 extends that work by giving each
discipline its own landing experience instead of just re-weighting the same
LHD picker.

Home page tab visibility (`templates/index.html`). The HERC Regions tab and
pane render only when `active_discipline == 'public_health'`. The WEM Regions
tab and pane render only when `active_discipline == 'em'`. Tab labels are
"HERC Regions" and "WEM Regions" with no discipline suffix because the
discipline is implied by which tab is present. The Jurisdiction tab itself
swaps content by discipline: PH shows the 84-LHD dropdown that posts to
`/dashboard/<jurisdiction_id>`; EM shows the 72-county dropdown that posts to
`/em-dashboard/<county_slug>`. Help text and dropdown labels follow the same
split (84 LHDs vs 72 counties). The Tribal-hide stopgap (replit.md "Completed
Stopgaps") still filters tribal LHDs out of the PH dropdown.

EM county dashboard route (`routes/em.py`). `/em-dashboard/<county_slug>`
forces EM for the current request only via `g.forced_discipline = 'em'`
(not via `session`, so visiting an EM county view does not silently flip
the user's next `/dashboard/<jid>` hit into EM mode), resolves the slug
to a county name via
`utils.em_counties.get_county_for_slug()`, maps that name to the canonical
county-level LHD jurisdiction id via
`utils.data_processor.get_county_id()`, and delegates inline to
`routes.dashboard.dashboard`. This means the EM county view reuses the
existing dashboard view, the existing v6 discipline-aware dashboard cache key
(`dashboard_full_v6_em_<jid>`), the existing temporal risk and predictive
analysis paths, and the existing dashboard template; the only practical
differences are EM weights applied by `process_risk_data()` and the
streamlined biological panel rendered when `active_discipline == 'em'`. The
companion `/em-print-summary/<county_slug>` does the same for the printable
summary. Unknown slugs produce a neutral flash and redirect to the home
page; `/em-dashboard` and `/em-dashboard/` (no slug) redirect to the home
page so the user picks again. The Back-to-Dashboard link on the print
summary template is built by `routes.dashboard.print_summary` via
`utils.em_counties.get_slug_for_jurisdiction_id()`: in EM mode, if the
jurisdiction id resolves to a Wisconsin county it links to
`/em-dashboard/<slug>`; otherwise it falls back to `/dashboard/<jid>`.

EM county catalog (`utils/em_counties.py`). Single source of truth for the
EM county list. `get_wi_counties_for_em()` returns the 72 Wisconsin counties
sorted alphabetically; each entry has `id` (URL slug), `name` (human label),
and `jurisdiction_id` (canonical county LHD id). Slugs are deterministic:
lowercase, periods stripped, spaces converted to hyphens
(`Eau Claire -> eau-claire`, `Fond du Lac -> fond-du-lac`,
`St. Croix -> st-croix`). The slug is the user-facing identifier on EM
URLs; the jurisdiction id is the internal identifier used by
`process_risk_data()`. The reverse maps `_SLUG_TO_COUNTY` and
`_JURISDICTION_ID_TO_SLUG` are built once at import time. Note: the session
plan referred to `<county_fips>`; the implementation uses slugs instead
because the user-facing URL is more meaningful (`/em-dashboard/milwaukee`)
and slugs sidestep needing to thread a FIPS column through
`WISCONSIN_COUNTIES`.

EM weight redistribution. `config/risk_weights.yaml`
`em_overall_risk_weights` previously had no key for `infectious_disease`
(0% weight). v28 adds it at 0.05, taken proportionally from the four
largest EM domains: natural_hazards 0.32 -> 0.30, health_metrics 0.10 ->
0.09, active_shooter 0.13 -> 0.12, extreme_heat 0.13 -> 0.12. All other
EM weights are unchanged. The total still sums to 1.00. PH weights are
unchanged. The PH vs EM comparison Excel export now reflects the new EM
weight for infectious_disease; PH columns are unchanged.
`utils.wem_risk_aggregator.DOMAINS` adds `infectious_disease`, and the
EM weighted linear sum sources its per-jurisdiction value from
`risk_data['health_risk']` (the acute infectious-disease composite signal
already produced at the LHD level), so WEM regional scores also reflect
the 5% contribution.

County-level infectious_disease wiring fix (v28.10, 2026-07-07). The v28
redistribution above wired infectious_disease into the WEM regional
aggregator, but the county-level EM composite in
`utils/data_processor.py` never received a corresponding entry in its EM
`raw_values` map. The domain was therefore treated as missing on every
EM county dashboard: silently excluded from the weighted quadratic mean,
weights renormalized over the other ten domains, and a permanent "data
coverage 95%; excluded: infectious_disease" notice shown. The EM
`raw_values` map now feeds `infectious_disease` from
`health_metrics_score` (the same acute infectious-disease composite
signal as `health_risk`), exactly as the WEM aggregator does. This
restores the documented 5% contribution, 100% EM data coverage, and
county-vs-regional consistency. EM county composites shift slightly
(counties whose disease signal sits above their renormalized composite
tick up, those below tick down); PH scores are unchanged. An
"Infectious Disease (EM Disease Awareness)" row is appended to
`score_provenance.domains` in EM mode only, and the dashboard context
cache key was bumped (`dashboard_full_v6` to `dashboard_full_v7`) so
cached pre-fix EM dashboards are invalidated at deploy. The compact-grid
EM disease tile label shows the combined 14% (9% health_metrics + 5%
disease awareness) applied to that single signal.

Streamlined EM biological panel
(`templates/dashboard/_category_biological.html`). When the composite is
rendered with `active_discipline == 'em'`, the Strategic Preparedness
Baseline panel include (per-disease P x C with severity citations) and
the detailed per-disease activity breakdown table are both wrapped in
`{% if active_discipline != 'em' %}` and therefore omitted. The
infectious-disease composite score tile (with its show-work popover) and
the active surveillance flags strip (H5N1, mpox, measles, enteric,
legionella) remain visible in EM mode so EM users still get operational
outbreak awareness for mass-care and shelter screening decisions. A
short note inside the panel explains that the breakdown is streamlined
in EM and that the full per-disease detail is available in PH mode. KP
HVA stays PH-only and is not surfaced in either the EM panel or the
streamlined note.

Surfaces unchanged by v28. PH `/dashboard/<jurisdiction_id>` keeps its
URL, its LHD picker, and the full biological panel. HERC
`/herc-dashboard/<id>` keeps its URL, template, and PH discipline. WEM
`/wem-dashboard/<id>` keeps its URL and reuses `herc_dashboard.html`
with EM context unchanged from v27 (only the per-region weighted sum
now includes infectious_disease at 5%). The PH vs EM comparison export
endpoint `/em-comparison-export` is unchanged structurally; only the EM
column numbers shift to reflect the redistributed EM weights.

Cache-only request path invariant is preserved end-to-end. The EM county
route does not introduce any new fetcher and does not bypass
`is_cache_only_mode()` anywhere.

Action Plan content layer (`utils/action_plan_content.py` + `data/action_plans/`, v28.3). The Action Plan page (`/action-plan/<jid>`)
historically embedded every domain's recommendation copy inline in
`templates/action_plan.html`. v28.3 introduces a discipline-aware
content layer for the Extreme Heat domain as a pilot, with the
remaining domains kept on inline copy until the pattern is extended.

Content lives in YAML so subject-matter-expert reviewers can edit
without touching code. Three files matter:

- `data/action_plans/_sources.yaml`: canonical umbrella sources
  (CDC BRACE, CDC PHEP, NIHHIS Heat.gov, NWS HeatRisk, EPA EHE
  Guidebook, EPA Reducing Heat Islands, FEMA Extreme Heat fact
  sheet, FEMA SLTT leaders guidance, FEMA Hazard Mitigation
  Planning hub, Wisconsin DHS Climate Heat, NACCHO Extreme Heat
  Toolkit). Each entry stores title, publishing org, URL, and a
  `verified` date.
- `data/action_plans/extreme_heat.yaml`: discipline -> tier ->
  list of `{text, source_id}`. Tiers are planning horizons
  (`pre_season`, `this_year`, `multi_year`), not severity bins.
  PH uses CDC PHEP capability framing; EM uses FEMA HMP element
  framing (44 CFR 201.6).
- `data/action_plans/_research_log.md`: human-readable audit
  trail mapping every source to a verification date and the
  activities it backs. Reviewers can spot-check claims without
  re-doing the research.

`utils/action_plan_content.get_domain_action_plan(domain,
discipline)` returns a template-ready dict with framework
capabilities and activity tiers, resolving each `source_id`
against `_sources.yaml`. Unknown source ids degrade gracefully to
text-only activities and emit a log warning rather than raising.
Source links open in a new tab and include publishing org +
document title so the citation is recoverable if the URL ever
breaks. Verification cadence: re-check URLs quarterly and bump the
`verified` date when re-checked.

`routes/dashboard.action_plan` passes `domain_action_plans =
{'extreme_heat': get_domain_action_plan('extreme_heat',
discipline)}` into the template. The Jinja blocks for extreme heat
render from this dict when present and fall back to the original
inline copy if the loader returned no content, so the route stays
safe even if a YAML file is corrupted.

Discipline-aware draft notice. EM mode shows a visible warning
banner at the top of the action plan because EM-tailored content
is still being built domain by domain. PH mode shows a quiet
italic footnote because PH copy is more mature but newly added
source links are still under review. Both link to a `mailto:`
feedback address (currently jdn63@georgetown.edu) so reviewers can
return structured input.

Constraint: Action Plan content is preparedness and mitigation
only. Operational response and recovery belong in incident-action
documents, not here. Verbs in YAML activities must be planning-
tense (identify, map, inventory, establish, adopt, integrate,
train) not operational (activate, deploy, open). A real-world
correctness example baked into the EM content: FEMA Hazard
Mitigation Assistance Guide v2.1 (effective 2025-01-20) removed
standalone extreme-temperature project eligibility, so EM
activities frame heat measures as components of multi-hazard
mitigation projects rather than standalone BRIC asks. This is the
kind of nuance that makes a verified-source policy worth the work.

Dashboard cache pre-warmer (`utils/dashboard_warmer.py`, v28.2). The
per-jurisdiction dashboard context is cached in the persistent cache as
`dashboard_full_v6_<discipline>_<jurisdiction_id>` with a 1-day TTL. A
cold-cache hit on a large county (Milwaukee in EM mode is the worst
case) is ~14 seconds because `process_risk_data()` + 7
`TemporalRiskComponent` calculations + `RiskPredictor` all run from
scratch. A warm hit serves in ~11 ms. To prevent users from ever paying
the cold cost, `start_dashboard_warmer(app, delay_seconds=25)` is
launched from `core.create_app()` after the scheduler init. It runs in
a daemon thread on the primary gunicorn worker, sleeps 25s to let the
app finish booting and the scheduler's own +10s warm-up complete, then
issues internal `app.test_client()` GETs against
`/dashboard/<jid>?discipline=public_health` for all 84 PH jurisdictions
and `/em-dashboard/<slug>` for all 72 EM counties. Counties are visited
in population-priority order so the user's most likely first click
lands on a warm cache fastest. `_is_already_warm()` short-circuits any
jurisdiction whose v6 cache entry still exists, so re-runs after a
gunicorn reload (the on-disk cache survives) are cheap. The warmer
issues no new request-path live HTTP: each internal GET goes through
`routes.dashboard.dashboard`, which wraps fetchers in
`cache_only_context()` exactly like a real user hit, so the cache-only
invariant is unchanged.

## Straight-Line Wind split from Thunderstorm (v28.6)

The legacy Natural Hazards `thunderstorm` domain bundled hail,
lightning, and damaging non-tornadic convective wind into one
percentile. WI emergency management directors flagged that this
hides derecho-scale wind exposure, which drives a very different
mitigation conversation (manufactured-home parks, utility hardening,
debris management) than hail or lightning. v28.6 splits the domain
in two without introducing any new external fetcher.

Internal key naming is intentionally conservative: the existing
`thunderstorm` key is retained but now means hail + lightning only;
the display label is "Hail & Lightning Risk". A new
`straight_line_wind` key carries damaging non-tornadic convective
wind (including derechos) and renders as "Straight-Line Wind Risk".
Derechos are not a separate NOAA EVENT_TYPE; they are episodes
composed of many Thunderstorm Wind / High Wind events, so they
naturally feed the new percentile. Derecho-specific context is
provided in the action plan content layer rather than as a separate
domain.

Data layer. `utils/noaa_storm_events.py` splits the legacy
`THUNDERSTORM_EVENT_TYPES` into `{Lightning, Hail}` and adds a new
`STRAIGHT_LINE_WIND_EVENT_TYPES = {Thunderstorm Wind, Strong Wind,
High Wind, Funnel Cloud}`. Both buckets are first-class entries in
`HAZARD_CATEGORIES` and the empty-county record skeleton. The
existing per-county Storm Events cache rebuilds with the new bucket
on the next scheduled refresh; until then percentiles for
straight-line wind degrade gracefully (the calculator drops the
NOAA-percentile term and re-weights the remaining exposure factors).

Risk calculation. `utils/natural_hazards_risk.py` adds
`calculate_enhanced_straight_line_wind_risk()` that mirrors the
thunderstorm calculator but uses three exposure factors:
NOAA Storm Events percentile against the wind bucket (0.55),
derecho-corridor position (0.25; high for the southern/central
counties, moderate for the west-central tier, lower for northern
WI), and climate trend from
`data/climate/natural_hazard_climate_projections.json`
(1.25 multiplier; 0.20 weight). Vulnerability is dominated by
mobile-home stock (0.25) plus tree-fall exposure, distribution-grid
vulnerability, and rural isolation. Resilience uses the inverse of
SVI socioeconomic and housing-transportation themes.

Weights. `config/risk_weights.yaml` natural_hazards_weights split
the combined 0.25 share 60/40 by WI event-volume share: wind 0.15,
hail/lightning 0.10. SVI and EM vulnerability blocks gain
`straight_line_wind` entries that mirror the thunderstorm weights.
Climate projections add a `straight_line_wind` range of [1.18, 1.30].

Composite path and rollups.
`utils/data_processor.process_risk_data()` and the second discipline-
aware path both import and call the new calculator, add it to the
`natural_hazards` subdict, expose it as `straight_line_wind_risk`
plus `_components`, `_metrics`, `_data_sources`, and
`_vulnerability_breakdown` on the result, and include it in the
percentile-ranking and component-percentile loops.
`utils/risk_alignment.py` relabels `thunderstorm` to
"Hail & Lightning Risk" and adds `straight_line_wind` as
"Straight-Line Wind Risk".
`utils/wem_risk_aggregator.py` and `utils/herc_risk_aggregator.py`
both add `straight_line_wind` to `NH_COMPONENTS`, compute the two-
stage county mean, and surface it in the aggregated natural-hazards
breakdown.
`utils/em_comparison_export.py` adds a "Straight-Line Wind" row and
relabels the existing thunderstorm row "Hail & Lightning".
`utils/hva_export.py` adds a "Straight-Line Wind (incl. Derecho)"
hazard row with property_impact 4 / human_impact 3 / business_impact 3,
reflecting the heavier impact profile derechos carry.
`utils/kp_hva_export.py` adds straight-line-wind damage thresholds
and includes it in the raw-data passthrough.

Templates. New `templates/dashboard/_tile_straight_line_wind.html`
mirrors the thunderstorm tile with derecho-corridor positioning in
the key-metrics table. The existing thunderstorm tile is relabeled
"Hail & Lightning Risk Analysis". The Natural Hazards category
include order is tornado, hail-and-lightning, straight-line-wind,
flood, winter-storm.

Action plan content. New `data/action_plans/straight_line_wind.yaml`
carries PH + EM activities across three planning horizons each.
PH content covers manufactured-home park outreach, debris-cleanup
injury surveillance, generator-CO messaging, HCC mutual aid, and
PHEP/PPHR alignment. EM content covers the WI derecho-corridor HMP
profile, NWS PDS warning tier coordination, SKYWARN spotter
activation, pre-staged debris-management contracts, wind-retrofit
pathways referencing FEMA P-361 and P-499, and Weather-Ready Nation
partnerships. Three new umbrella sources are added: `spc_derecho`
(NOAA SPC derecho reference page), `nws_skywarn` (SKYWARN program),
and `fema_debris_management` (FEMA P-325 Public Assistance Debris
Management Guide). The action plan route adds `straight_line_wind`
to both `_ap_domains` tuples so the content layer renders the new
domain alongside the existing ones.

Cache-only request-path invariant is preserved end-to-end; no new
external fetcher is introduced. Tribal-hide stopgap remains in
force.

## EVR residual-risk model vs FEMA NRI (v28.7)

CARA's natural-hazard sub-domains use an Exposure-Vulnerability-Resilience
(EVR) formulation:

    Risk = (Exposure * Vulnerability) * (2.0 - Resilience) * Health_Impact_Factor

FEMA's National Risk Index (NRI), by contrast, divides by a community
resilience term:

    NRI_Risk_Score = (Expected_Annual_Loss * Social_Vulnerability) / Community_Resilience

The two formulations diverge intentionally and the divergence is
documented here so it is not flagged as a bug on every code review.

Why CARA uses (2.0 - Resilience) as a multiplier rather than 1/Resilience
as a divisor:

1. CARA Resilience is bounded on [0, 1] with 0.5 as the neutral midpoint
   (no net amplification or dampening). The (2.0 - Resilience) form
   maps that range onto a multiplier of [1.0, 2.0] with 1.5 at neutral,
   so a fully-resilient community (Resilience = 1.0) amplifies its risk
   by 1.0x (no change) and a zero-resilience community amplifies by
   2.0x. The shape is linear and bounded, which is easier to reason
   about than 1/Resilience (which blows up as Resilience approaches 0
   and asymptotically approaches but never reaches 0 amplification as
   Resilience approaches 1).

2. NRI's divisor form is appropriate for an expected-annual-loss
   denominated in dollars where the community-resilience term is itself
   a normalized index in (0, 1]; the divisor turns "more resilient" into
   "fewer dollars of expected loss." CARA's domain scores are bounded
   percentile-style values on [0, 1] where multiplicative amplification
   on a bounded range gives more predictable downstream composition
   with the outer PHRAT weighted RMS.

3. The CARA composite is intentionally additive-in-log-space relative to
   NRI: each sub-hazard's EVR triple multiplies into a domain score
   that then feeds an outer weighted RMS over the six PHRAT domains.
   Using a divisor on Resilience inside an outer RMS would create a
   discontinuity at Resilience = 0 that an emergency planner cannot
   reason about; the linear (2.0 - Resilience) form preserves
   monotonicity, has a closed-form interpretation at every input
   value, and matches the math used in the EM-discipline weight
   block already validated against state HMP rubrics.

4. The Health_Impact_Factor term is the CARA-specific bridge from a
   damage-oriented hazard score to a public-health-oriented risk score.
   NRI does not carry a health-impact term; that is part of why CARA
   exists as a separate model rather than a re-skinned NRI.

Code reviewers and auditors comparing CARA scores to NRI for the same
county and hazard should expect different absolute numbers and a
different rank ordering at the margin. The two models are correlated
(both pull from FEMA NRI Expected Annual Loss as an exposure input
where available) but not equivalent, and the divergence is by design.

## Tiered staleness scheme (v28.7)

`utils/data_freshness.py` now classifies each cached source into one
of four tiers based on the ratio of actual age to source-specific
expected refresh window:

- green: age <= 1.0x expected window. Fresh, no badge.
- yellow: 1.0x < age <= 2.0x expected window. Slightly stale, no
  dashboard banner.
- orange: 2.0x < age <= ABSOLUTE_STALE_LIMIT_DAYS (180 days).
  Significantly stale, dashboard banner fires.
- red: age > ABSOLUTE_STALE_LIMIT_DAYS. Treated as unavailable;
  domain reports "Data unavailable" and the freshness banner fires.

`FreshnessReport.banner_warranted` returns True iff tier is orange or
red. Templates that render the freshness banner should consume this
property rather than the legacy `stale` boolean, so single-day-overshoot
caches do not trigger an alert. The `tier` field is also surfaced in
`to_dict()` for downstream UI color coding.

## CDC EPHT heat exposure source (v28.8 NIHHIS Phase A)

Until v28.8 the Extreme Heat exposure sub-formula in
`utils/climate_adjusted_risk.py` read its "annual heat days" input from
two synthetic layers:

  1. `utils/wisconsin_climate_data.get_wisconsin_heat_days()` returned a
     constant 12 statewide.
  2. `utils/extreme_heat_metrics.get_annual_heat_days()` pulled monthly
     maximums from the NCEI Climate-at-a-Glance API and used a
     monthly-max-to-daily-count heuristic ("if monthly max >= 95 F add
     15 days") to fabricate a daily count, then cached the fabricated
     value as if it were real.

v28.8 introduces `utils/cdc_epht_heat.py` as the canonical observed
source. CDC Environmental Public Health Tracking publishes two
relevant measures at county granularity for all 50 states:

  - Measure 421: Annual count of days with maximum temperature >= 90 F
    per county (NCEI nClimGrid daily series aggregated to county).
  - Measure 1064: Crude rate of emergency-department visits for
    heat-related illness per 100,000 population per county.

The scheduler entry `refresh_all_cdc_epht_heat` in
`utils/data_source_refresher.py` performs two HTTP calls per refresh
(one per measure) via the shared `http_client.fetch_json` wrapper,
parses the per-county series, retains the most recent non-null year
per county, and writes each county's payload to the persistent file
cache (`utils/persistent_cache.py`) keyed by county plus measure ID.
A single statewide DB row is also written via
`utils/data_cache_manager.save_cached_data` so the freshness panel
(`utils/data_freshness.get_all_freshness_reports`) can surface a
`cdc_epht_heat` badge under the canonical source ID.

`utils/extreme_heat_metrics.ExtremeHeatMetrics` now resolves the heat-
day input via a provenance-aware private helper
`_get_annual_heat_days_with_provenance()` that consults sources in
this order:

  1. CDC EPHT measure 421 cache for the requested county.
  2. The legacy NCEI Climate-at-a-Glance heuristic (still cache-only
     per the v28.7 explicit-failure contract).
  3. None (the v28.7 explicit-failure return; the freshness pipeline
     then renders "Data unavailable" rather than a synthetic value).

`get_wisconsin_heat_days()` (the original constant 12) is intentionally
retained, untouched, only as a deeply-buried last-resort fallback in
the elderly-population and ED-visit estimator paths in
`utils/extreme_heat_metrics.py` where no real per-county replacement is
yet wired. It is no longer consulted by the exposure sub-formula.

Provenance is threaded through every downstream layer:

  - `get_comprehensive_heat_metrics()` adds `heat_days_source` and
    `heat_days_year` fields to the metrics dict and replaces the
    generic "NOAA Climate at a Glance API" label in the per-field
    `data_sources` map with the actual source label.
  - `utils/climate_adjusted_risk.py:enhance_heat_risk_with_real_data`
    threads those two fields through into `heat_risk_data['metrics']`.
  - `utils/data_processor.py` `extreme_heat_data['metrics']` includes
    them so the template can render a "Source: ..." caption directly
    under the heat-days row in `templates/dashboard/_category_
    environmental.html`.

Source-registry settings:

  - `refresh_interval_hours = 8760` (annual). EPHT publishes once per
    year.
  - `freshness_max_age_days = 500`. EPHT lags real time by 12-24
    months, so a wider window than the standard 14-day default is
    required to keep the dashboard freshness badge from flagging an
    inherently lagged source as stale.

Known limitations and follow-ups (do not silently fix; surface
explicitly first):

  - 12-24 month publication lag is inherent. The widened freshness
    window above is correct, not a bug.
  - The 90 F threshold is the EPHT canonical cutoff; it is lower than
    the 100 F heat-index threshold Wisconsin DHS uses for advisories.
    Document this when surfacing the source caption.
  - Small-cell suppression may zero out the rural counties (Menominee,
    Florence) for some years; the fallback chain handles this by
    returning None for that county.
  - Measure 1064 (heat-related ED visit rate) is cached but not yet
    wired into `get_heat_related_ed_visits`; that estimator still
    uses a population-based proxy. Phase B follow-up.
  - The `nws_heat` advisory count and the elderly-percentage estimator
    were not touched in Phase A; both still use the v28.7 explicit-
    failure contract for the request-path cache-only invariant.


## Action-plan link checker (v28.7)

`scripts/link_check_action_plans.py` walks every URL in
`data/action_plans/_sources.yaml`, issues a HEAD (falling back to GET
on 405/501) with a short timeout, and writes a `link_check` block into
`data/action_plans/_verifier_status.json` containing the timestamp,
total / ok / failed counts, and a `link_failed` list of each broken
source ID with status code and error message.

Run on demand. The script does live HTTP and must NEVER be called from
a user-facing route; it complements (but does not replace)
`scripts/verify_action_plan_sources.py`, which validates that every
citation resolves to a registered source ID but does not check that
the underlying URL still serves.

When `link_failed` is non-empty, the offending source entries in
`_sources.yaml` should be reviewed by the methodology team. Failed
links commonly indicate a federal agency reorganization (CDC/HHS page
moves) or a state agency URL change; the fix is to update the URL in
`_sources.yaml` and re-run the script until the failed list is empty.

## Heat SVI single-pass invariant (v28.9)

Prior to v28.9, the extreme-heat domain applied CDC SVI in two distinct
places:

  1. Inside `utils/climate_adjusted_risk.py`
     `_calculate_enhanced_vulnerability()`, which already blends the
     socioeconomic, housing_transportation, household_composition, and
     minority_status SVI themes together with the Census ACS elderly
     fraction. This is the canonical EVR vulnerability term.

  2. A second-stage 70/30 weighted-average blend in
     `utils/data_processor.py` (formerly at lines 1155-1177) that re-mixed
     the EVR output with `socioeconomic_svi_factor * 0.6`.

The second pass biased heat risk upward in high-SVI counties because
the same socioeconomic SVI signal was counted twice. v28.9 removes the
second-stage blend. The invariant is:

  Heat risk = EVR(exposure, vulnerability, resilience) clamped to [0, 1],
  where SVI enters exactly once via the vulnerability term.

If a future change reintroduces a second SVI multiplier on the heat
domain, it must be reviewed against this invariant and the methodology
page updated. The `extreme_heat_risk_base` local variable is retained
as an alias of the now-final heat score solely so the show-work
breakdown's `pre_svi_score` field continues to populate; it no longer
represents a meaningful pre-SVI intermediate at this layer.

## EPHT wiring fix and heat-days source hierarchy (v28.9)

v28.8 added `utils/cdc_epht_heat.py` and made
`utils/extreme_heat_metrics.ExtremeHeatMetrics._get_annual_heat_days_with_provenance()`
prefer EPHT measure 421 over the legacy NCEI heuristic, but the actual
scoring formula in `utils/climate_adjusted_risk.py`
`_calculate_climate_adjusted_exposure()` still called
`get_wisconsin_heat_days() or 12` and therefore never consumed EPHT.
v28.9 wires the provenance-aware helper into the scoring formula
directly. Source hierarchy on the request path:

  1. CDC EPHT measure 421 cached per-county.
  2. NCEI Climate-at-a-Glance cached heuristic (cache-only, as
     established by v28.7 fix #5).
  3. Statewide constant from `utils/wisconsin_climate_data` as a
     deeply-buried last resort so a cold cache does not crash the
     dashboard.

The returned metrics dict now carries a `heat_days_source` key the
dashboard caption can surface. EPHT measure 421 counts days at or above
90 F; the NCEI heuristic targeted 100 F. Both feed the same [0, 20]
normalization band because the [0, 0.95] range was calibrated against
typical EPHT 90 F observed counts in Wisconsin (roughly 5 northern to
20 southern); the 100 F heuristic values fall inside the same band by
construction. This threshold mismatch is documented honestly on
`templates/methodology.html` and is the explicit reason the canonical
source is now EPHT 90 F rather than the legacy 100 F heuristic.

## WCAG 2.1 AA pass (v28.9)

A second pass against WCAG 2.1 AA closed the following issues across
the shared chrome and dashboard partials. None of these touch the
scoring pipeline; they are presentation-layer only.

  - 1.4.3 contrast: `.alert-warning` body text raised from #856404
    (3.8:1 on #fff3cd) to #664d03 (7.5:1 AAA);
    `.text-on-warning` switched from `var(--text-primary)` (#2c3e50,
    4.1:1 on Bootstrap warning yellow) to pure #000 (11.7:1 AAA);
    `.text-muted` and `.text-secondary` overridden in
    `static/css/accessibility.css` to #595f66 (5.0:1) so freshness
    captions and small annotations pass.
  - 1.4.3 Strategic Preparedness Baseline panel (the user-reported
    dark-on-dark bug): the small-text lines under "Aggregate Baseline"
    and "Current Acute Score" no longer carry `text-muted`, so the
    parent `text-light` cascades and gives roughly 8:1 contrast on the
    dark panel background.
  - 1.1.1 logo: the navbar `CARAacronymonly.png` `<img>` is now
    `alt=""` and `aria-hidden="true"` because the visible "CARA"
    wordmark next to it already names the brand; this avoids a
    duplicated announcement under screen readers.
  - 2.4.7 focus: the global `*:focus { outline: none }` rule was
    deleted. Keyboard focus rings now ship via `*:focus-visible`,
    matching modern browser semantics without breaking older WebViews
    that lack `:focus-visible` support.
  - 2.5.5 target size: `.show-work-btn` now reserves a 44x44 CSS-px
    minimum hit area via padding plus `min-width`/`min-height`, with
    the inner Font Awesome glyph marked `aria-hidden="true"` so the
    parent button's `aria-label` is the only announced name.
  - 4.1.2 toggle state: the discipline toggle in
    `templates/components/navigation.html` now exposes
    `aria-pressed` and `aria-current` so assistive tech reports which
    of Public Health vs Emergency Management is active.
  - 4.1.2 popover semantics: `show_work_btn` macro now declares
    `aria-haspopup="dialog"` so the popover trigger announces its
    expansion target.
  - 1.1.1 sparkline: the BSTA seasonal-curve SVG in
    `_bsta_temporal.html` carries a descriptive parent `aria-label`
    (baseline value, current-month label and value, composite), and
    inner SVG primitives are `aria-hidden="true"` so they do not
    pollute the accessibility tree.

## Hazardous Materials domains (industrial + agricultural)

The Hazardous Materials category contributes 6% of the composite,
split evenly: hazmat_industrial at 3% and hazmat_agricultural at 3%.
The split and weights are identical on the Public Health and Emergency
Management sides by design, so a PH-vs-EM comparison reflects the
difference in framing (action-plan voice and vulnerability weighting),
not a difference in weight. Both scores use the standard CARA EVR
residual-risk formula:

    Risk = (Exposure * Vulnerability) * (2.0 - Resilience) * HIF

Both calculators are cache-only safe: they perform no live HTTP. Inputs
come from local JSON seed files or from already-cached SVI and Census
helpers that themselves obey the cache-only request-path invariant.
Code lives in `utils/hazmat_industrial_risk.py` and
`utils/hazmat_agricultural_risk.py`; both are called from
`utils/data_processor.py` on the request path and surfaced through
`templates/dashboard/_category_hazardous_materials.html` and the
compact grid.

### Data maturity (read before trusting a specific number)

These two domains remain among the less data-mature in CARA, though
hazmat_industrial exposure has been upgraded to real EPA TRI and PHMSA
pipeline data. Current exposure inputs:

  - hazmat_industrial exposure now uses real EPA Toxics Release
    Inventory (TRI) facility counts for all 72 counties
    (`data/hazmat_scoping/county_tri_counts.json`), replacing the former
    Milwaukee/Dodge-only seed and the tiered proxy that covered the rest.
    On top of TRI, a real PHMSA pipeline-incident term (trailing 20-year
    counts, `data/hazmat_scoping/wi_county_pipeline_incidents.json`) adds
    a capped additive bump (max +0.15, /25 saturation) to exposure. Zero
    pipeline incidents is a real measurement, not a gap.
  - Known barrier (documented, not proxied): the EPA RMP (Risk
    Management Plan) facility dataset is not publicly queryable at
    per-county granularity (Envirofacts RMP is access-restricted), so RMP
    facility counts are not incorporated.
  - hazmat_agricultural exposure now uses real USDA NASS Census of
    Agriculture 2022 county data for all 72 counties
    (`data/hazmat_scoping/wi_county_ag_chemical.json`), replacing the
    former tier proxy. Known barrier: the WI DATCP ACCP annual summary
    is a PDF without a queryable per-county dataset, so ACCP incident
    history is not yet a signal. The tile shows the data vintage.

Vulnerability for both comes from CDC SVI 2022 themes plus Census
population; the industrial HIF and agricultural HIF are not defined in
the NRI factor table and therefore default to 1.0 (neutral) -- this is
intentional and honest, not a fabricated value.

### Resilience is statute-backed only (do not reintroduce guessed lists)

Response speed dominates consequence in a chemical release, so the
resilience term can be raised for a county with a nearby Level A
response capability. The signal is deliberately narrow:

  - hazmat_industrial adds a resilience boost ONLY for La Crosse County,
    the single county whose regional hazmat team is fixed in Wisconsin
    statute (Wis. Stat. 323.13(2)(a) authorizes no more than nine
    regional teams and mandates one in La Crosse). The full current
    roster of regional-team host counties is not published in a single
    authoritative public source, so no other county receives a
    team-based boost. This avoids asserting unverified host locations.
  - hazmat_agricultural previously added a small resilience boost for a
    17-county "UW Extension agricultural-safety footprint" list. That
    signal was removed in the v28.10 integrity audit (UW-Madison
    Extension operates in all 72 counties, so the list carried no real
    differentiation). No Extension-based boost remains.

CHEMPACK is NOT used to score any county. CHEMPACK cache locations are
confidential by federal law (42 U.S.C. 247d-6b prohibits disclosure of
storage locations, even under FOIA), and neither ASPR, Wisconsin DHS,
nor WEM publishes county-level positioning. An earlier v0 seed carried
a hardcoded eight-county CHEMPACK list mislabeled as "ASPR public
guidance"; because no lawful authoritative public source can ever back
it, the signal was removed entirely from the calculator, the displayed
methodology, and the metrics table. CHEMPACK still appears in the
Public Health action-plan content layer as a preparedness-coordination
step (verify access plans with the regional coordinator), which is
accurate because it references the program, never a location. Do not
reintroduce a CHEMPACK scoring signal or any county-level CHEMPACK
location list.

Removing the CHEMPACK boost and correcting the hazmat-team list lowered
the resilience term for the previously boosted counties, which raised
their industrial residual risk (for example Milwaukee's industrial
score rose to the 1.0 ceiling because its exposure was already maxed).
This is the correct, honest result of dropping an unearned resilience
credit. The full-dashboard cache key was bumped
(`dashboard_full_v7` to `dashboard_full_v8`) so pre-fix cached
composites are invalidated cleanly at deploy.

## Data-source integrity audit fixes (v28.10, 2026-07)

A full audit of every claimed data source found four critical
false-citation problems and several partially disclosed heuristics.
All were fixed in one pass; the full-dashboard cache key was bumped
(`dashboard_full_v8` to `dashboard_full_v9`).

1. NCES SSOCS school safety (20 percent of Active Shooter). The
   pyreadstat dependency was never installed, so the real 2.1 MB
   public-use microdata file was never read and every county received
   a hardcoded tier guess while the UI claimed "NCES SSOCS 2019-2020".
   Two deeper problems surfaced during the fix: the public-use file
   contains no state or county identifiers at all (they are suppressed
   for confidentiality), and the previous variable-name map did not
   match the file (guessed names like FR_CNTRL vs real codes like
   C0112). The processor (utils/nces_ssocs_processor.py) was rewritten:
   it now computes real national averages per school urbanicity class
   (city, suburb, town-rural pooled) from the microdata, assigns each
   Wisconsin county to a class via a disclosed CARA heuristic, and
   labels data_quality low with an explicit provenance note. Incident
   rates per 1,000 students are approximate (school size is categorical
   in the public file; category midpoints are used). Wisconsin-specific
   or county-measured SSOCS values are impossible from the public file;
   do not reintroduce claims of them.

2. UW Extension agricultural-safety county list. A 17-county
   "Extension ag-safety footprint" resilience bonus (+0.15) in
   utils/hazmat_agricultural_risk.py was fabricated: UW-Madison
   Extension operates in all 72 counties, so the signal carried no real
   differentiation. Removed from the calculator, metrics, and template.

3. Utilities domain (utils/utilities_risk.py). All four sub-risk
   data_sources lists cited federal and state feeds (DOE disturbance
   events, EPA SDWIS, WI PSC, FCC DIRS, FEMA Lifelines, EIA, USDA,
   WisDOT) that were never fetched. They now honestly state
   "CARA rule-based county proxy model" plus SVI, matching the UI
   labels which already said proxy-based estimates. The invented
   COUNTY_WATER_SYSTEM_MAP per-county system counts were removed and
   replaced with a disclosed urban/rural private-well reliance rule.

4. Correctional facility loader (load_prison_data in
   utils/data_processor.py). Docstring claimed OpenFEMA and WI DOC
   fetch; it is a static hand-maintained seed with partial coverage
   and is now labeled as such.

High-priority disclosure fixes: the tornado tile now discloses the
CARA tornado-corridor and open-terrain county-list heuristics (25
percent of tornado exposure); the winter storm tile discloses the
northern-location and lake-effect lists; the WI firearm-law score 0.65
is now labeled everywhere as a CARA in-house translation of RAND 2022
law categories (RAND publishes no such number); the vector-borne
forest-cover and deer-density seed scores are labeled as CARA-curated
v1 estimates pending re-derivation.

Medium items: the BSTA temporal 0.5 baseline fallback was already
disclosed via baseline_used_fallback; the NRI neutral fallback
(0.33/0.35/0.40) now sets an nri_neutral_fallback flag in the
natural-hazards payload (excluded from the numeric composite; note
that bool is an int subtype in Python, so the exclusion is by name).

Score effects: Active Shooter school-safety component now uses real
SSOCS class averages (city 0.54, suburb 0.46, town-rural 0.42 versus
the old guesses 0.68/0.52/0.42), and agricultural hazmat resilience
dropped by 0.15 for the 17 previously boosted counties (raising their
residual risk slightly). These are the honest results of removing
unearned or fabricated signals.
