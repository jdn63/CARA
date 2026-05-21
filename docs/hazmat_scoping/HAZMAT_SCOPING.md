# Hazardous Materials Risk Domain - Scoping Note

Status: DRAFT for work group review
Author: CARA development (agent-assisted scoping pass)
Date: 2026-05-20
Companion artifacts:
- `docs/hazmat_scoping/source_check_results.md` (auto-generated data
  source availability check)
- `docs/hazmat_scoping/county_comparison_v0.md` (3-county exploratory
  comparison)
- `data/hazmat_scoping/source_check.json` (machine-readable check output)
- `data/hazmat_scoping/county_tri_counts.json` (real Wisconsin TRI
  facility counts pulled during this scoping pass)

This note proposes a Hazardous Materials (hazmat) exposure risk domain
for CARA. Scope is feasibility, methodology, and a v0 composite formula
the work group can review before any production build begins. No risk
weights, fetchers, or templates have been changed.

## 1. Problem statement

Wisconsin county Emergency Management directors and local public health
agencies have asked for a hazmat exposure indicator. The two operational
concerns driving the ask are:

- Transportation hazmat exposure (rail, highway, pipeline) crossing
  populated jurisdictions, especially Class I rail corridors carrying
  crude oil, ethanol, anhydrous ammonia, and chlorine.
- Fixed-facility chemical exposure (RMP and EPCRA Tier II facilities,
  plus the agricultural chemical handling that is heavily concentrated
  in rural Wisconsin).

The existing CARA domain set (11 domains as of v28.3) has no dedicated
hazmat indicator. Active Shooter, Cybersecurity, and Utilities each
cover adjacent ground but none capture chemical release exposure.

## 2. Feasibility verdict

Feasible. Five public datasets with confirmed Wisconsin coverage are
sufficient to build a defensible composite. Two additional datasets
(EPA RMP facility-level, Wisconsin Tier II full export) are
access-restricted but their aggregate counts are publicly available and
substitutable.

Confirmed by the source check script:

- EPA TRI facilities by county: live, queryable, returns real Wisconsin
  numbers (Milwaukee 336 facilities, Dodge 49, Crawford 0 in latest
  reporting year).
- FRA North American Rail Network: ArcGIS Feature Server live, supports
  state-filtered GeoJSON export of all Wisconsin rail lines.
- USGS Pesticide National Synthesis Project: county-level annual
  estimates 1992-2019 for hundreds of active ingredients, free CSV.
- PHMSA National Pipeline Mapping System: public viewer available,
  county-level pipeline mileage available from PHMSA Annual Report CSVs
  (separate from the restricted NPMS GIS download).
- USDA NASS Quick Stats: free API key, county-level Census of
  Agriculture covering acres in production, fertilizer expenditure,
  CAFO counts.

Restricted but workable:

- EPA RMP facility-level data: pulled from public APIs in 2023. State
  totals remain in the EPA RMP National Overview. For Wisconsin this is
  approximately 280 active RMP facilities statewide. CARA can use the
  state total as a weighting constant and treat TRI + Tier II as the
  per-county fixed-facility signal.
- PHMSA Hazardous Materials Incident Reports: bulk CSV is public but
  the PHMSA portal WAF blocks scripted access. Operationally this means
  a manual quarterly download into `data/phmsa/` rather than an
  automated scheduler fetch. Volume is roughly 350-500 reportable WI
  incidents per year, well within manageable scope.

## 3. Proposed v0 composite

Three sub-pathways, each rendered as a sub-score, combined into the
domain score using the standard CARA Exposure-Vulnerability-Resilience
(EVR) shape.

### Exposure (50% of domain score)

The exposure layer is the union of three sub-pathways, each normalized
to a 0-1 scale across the 72 counties, then combined as a weighted
maximum (not a sum) so a county with one severe pathway is not masked
by zeros on the others.

| Sub-pathway | Indicator | Source | Weight within exposure |
|---|---|---|---|
| Transportation - rail | Population within 1 mile of Class I rail line, multiplied by historical PHMSA hazmat incident rate for that corridor | FRA Rail Network + PHMSA OHMS + ACS block-group population | 0.40 |
| Fixed facilities | (TRI facility count per 10k population) + (EPA RMP statewide share allocated to county by TRI weight) | EPA TRI + EPA RMP National Overview | 0.35 |
| Agricultural chemicals | USGS PNSP pesticide use intensity (kg active ingredient per square km of cropland) | USGS PNSP + USDA NASS cropland acres | 0.25 |

Pipeline mileage is held out of v0 because PHMSA pipeline data and
incident histories overlap significantly with the rail sub-pathway in
the corridors that matter most (Mississippi River, I-94, US-53). v1
revision can add pipeline mileage as a fourth sub-pathway if the work
group sees a defensible split from rail.

### Vulnerability (30% of domain score)

Reuses the existing CARA vulnerability inputs to avoid maintaining a
second SVI pipeline. The hazmat-specific tweak is adding linguistic
isolation explicitly because shelter-in-place orders depend on language
access at the household level.

| Indicator | Source | Already in CARA |
|---|---|---|
| CDC SVI overall | CDC ATSDR SVI | Yes |
| Age 65+ share | ACS 5-year | Yes |
| Linguistic isolation (households with limited English) | ACS 5-year | Yes (utils/svi_data.py) |
| Population density | TIGER + ACS | Yes |

### Resilience (20% of domain score)

| Indicator | Source | Already in CARA |
|---|---|---|
| Distance to nearest WEM Regional Hazmat Team (Type I or II) | WEM hazmat teams roster, geocoded | No - new |
| Local fire department NFPA 472 certification level | WisDOT / DSPS / IAFC mutual aid | No - new (coverage uneven) |
| Hospital decon capability | Wisconsin Hospital Association directory | Partially (CARA tracks hospital capacity) |

Resilience layer is the thinnest and where v0 carries the most
methodological risk. Recommendation: ship v0 with WEM hazmat team
distance only, document the other two indicators as v1 follow-on once
the work group confirms a defensible data source for each.

## 4. EVR formula and weight against existing domains

The CARA EVR shape is:

    risk = exposure x (1 + vulnerability_uplift) / (1 + resilience_adjustment) x health_impact_factor

Applied with the existing CARA conventions:

- exposure is normalized 0-1 across the 72 counties using percentile
  ranking, same as natural hazards.
- vulnerability and resilience use the same SVI-derived adjusters that
  Flood and Tornado use; no new vulnerability framework is introduced.
- health_impact_factor for hazmat defaults to 1.20 (matching the
  Tornado / Winter Storm health-multiplier range) pending work group
  review of acute health consequence severity.

Overall risk weight for hazmat in the CARA composite: proposed at 6% in
both PH and EM modes (taken proportionally from existing slack and from
natural_hazards which currently absorbs all-hazards weight). Exact
redistribution to be decided by the work group; this scoping note does
not pre-empt that decision.

## 5. Action plan content - already strong source coverage

Hazmat preparedness has more well-developed federal framework material
than any of the existing CARA domains. Source pre-verification will be
fast.

- FEMA Comprehensive Preparedness Guide 101 (CPG-101) - all-hazards
  planning baseline, hazmat-specific annex examples.
- EPA Risk Management Program (RMP) Guidance for Implementation -
  prevention and emergency response planning.
- DOT Emergency Response Guidebook (ERG) - the operational hazmat
  reference for first responders, updated every 4 years.
- EPCRA / SARA Title III requirements - LEPC planning, Tier II
  reporting, public information.
- NIMS ICS-300 / 400 - command structure for multi-jurisdictional
  hazmat response.
- CISA Chemical Sector resources - cybersecurity and physical security
  guidance for chemical facilities (cross-references the existing CARA
  Cybersecurity domain action plan).
- EPA Wisconsin Region 5 emergency response coordinator contact
  framework.
- WEM SERC and Wisconsin DNR Tier II compliance guidance.

Discipline split would mirror the existing Action Plan pattern:

- Public Health: PHEP Capability 14 (Responder Safety and Health),
  Capability 10 (Medical Surge), and Capability 8 (Medical
  Countermeasure Dispensing) for chemical exposure events.
- Emergency Management: FEMA Core Capabilities Public Information and
  Warning, Operational Coordination, On-Scene Security and Protection;
  CISA Chemical Sector CPGs; NIMS ICS structure.

## 6. Concerns and open questions for the work group

1. Double-counting with the existing Utilities domain. Pipeline
   incidents arguably belong to both. Recommendation: hazmat owns
   "release and acute exposure", utilities keeps "service disruption".
   Work group sign-off needed.

2. Rural-vs-urban gradient mismatch between rail/RMP signals (urban) and
   agricultural chemical signals (rural). v0 composes them with weighted
   maximum (not sum) to avoid masking. The work group should decide
   whether to instead split into two sibling domains:
   "hazmat_industrial" and "hazmat_agricultural". Reasons to split:
   different response capabilities (urban fire hazmat team vs. ag
   extension and DATCP), different action plans, different SME audiences.
   Reasons to keep combined: simpler dashboard, mirrors how FEMA
   typically scopes a single hazmat hazard.

3. PHMSA incident counts at the county scale are sparse for low-
   population rural counties (Crawford had zero TRI facilities in the
   latest reporting year and likely zero or one PHMSA incidents in a
   given year). The mitigation is to use corridor-level incident rates
   assigned to counties via line intersection, not raw county counts.

4. RMP facility-level access. The 2023 EPA restriction limits CARA to
   state-total counts allocated by proxy (TRI). If the work group
   considers this an acceptable methodological compromise, v0 ships;
   otherwise the EPA RMP Reading Room request process becomes a
   prerequisite and shifts v0 timeline by approximately 8-12 weeks of
   EPA processing time.

5. Action plan citation discipline. CARA's existing rule is one
   sourced link per activity, verified by `verify_action_plan_sources.py`.
   Hazmat citations need the same standard; LEPC and SERC URLs are
   notoriously prone to drift and the quarterly re-verifier will flag
   them frequently. Acceptable given the existing process, just
   something to staff for.

6. Tribal jurisdictions. The v22 stopgap hides 11 Tribal jurisdictions
   from the public picker. The hazmat domain should respect that hide.
   No special case needed since the domain attaches to the same
   jurisdiction list.

## 7. Recommended next steps

If the work group approves the scoping direction, a v1 build would be
approximately 3 weeks of work in this order:

1. Week 1: pull and persist the four primary datasets (TRI via
   Envirofacts API, FRA rail GeoJSON, USGS PNSP CSV, manual PHMSA
   incident CSV drop). Build the cache-only fetchers following the
   established `is_cache_only_mode()` pattern.

2. Week 2: implement the exposure sub-pathway calculators, the EVR
   composite, and the percentile ranking. Wire to a new
   `utils/hazmat_risk.py` module with the same shape as
   `utils/vector_borne_disease_risk.py`. Update
   `config/risk_weights.yaml` with the work-group-approved overall
   weight redistribution.

3. Week 3: add the dashboard tile, the action plan YAML content for
   both disciplines, and the source verifier coverage. Run the existing
   verify_action_plan_sources.py to confirm clean cites. Bump VERSION
   to v29 with full changelog entry.

If the work group rejects or substantially revises the scoping
direction, this note serves as the record of what was considered and
why, so the next iteration starts from a known baseline.
