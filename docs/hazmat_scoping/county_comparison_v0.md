# Hazmat domain - 3-county exploratory comparison (v0)

Status: DRAFT for work group review
Date: 2026-05-20
Companion: see `HAZMAT_SCOPING.md` for the methodology this comparison
applies. See `data/hazmat_scoping/county_tri_counts.json` for the
machine-readable inputs.

The purpose of this comparison is to confirm that the proposed v0
composite produces a defensible spatial pattern across three Wisconsin
counties chosen for very different exposure profiles. If the composite
ranks them in an order the work group recognizes as plausible, the
direction is sound. If it does not, the formula needs revision before
any production build.

## Counties

| County | FIPS | Profile | 2020 population (Census) | Land area (sq mi) |
|---|---|---|---|---|
| Milwaukee | 55079 | Urban / industrial | 939,489 | 241 |
| Crawford | 55023 | Rural rail corridor (BNSF Mississippi River line) | 16,131 | 571 |
| Dodge | 55027 | Agriculture-intensive | 87,633 | 882 |

## Exposure layer - raw inputs

The numbers in this table are the actual public values pulled or
estimated during this scoping pass. TRI counts are live from EPA
Envirofacts. Rail mileage and PHMSA incident estimates are placeholders
derived from public summary statistics; v1 will replace them with
script-computed values from the FRA GeoJSON and the PHMSA CSV.

| Indicator | Milwaukee | Crawford | Dodge | Source |
|---|---|---|---|---|
| EPA TRI facilities (latest reporting year) | 336 | 0 | 49 | EPA Envirofacts, pulled 2026-05-20 |
| TRI facilities per 10k population | 3.58 | 0.00 | 5.59 | computed |
| Estimated Class I rail miles (statewide ~3,400 mi across 72 counties; values are illustrative placeholders pending FRA GIS join) | approx 75 | approx 32 | approx 50 | FRA Rail Network (placeholder) |
| PHMSA hazmat incidents on rail corridors, 5-year sum (illustrative placeholder, full WI volume is ~350-500 per year all modes) | high | moderate | moderate | PHMSA OHMS (placeholder) |
| USGS PNSP pesticide use (kg active ingredient per sq km of cropland, statewide median ~ illustrative) | low (limited cropland) | moderate | high (intensive corn-soy) | USGS PNSP (placeholder) |
| EPA RMP facilities (state total ~280; allocation by TRI weight is a v0 approximation) | high concentration | very low | moderate | EPA RMP National Overview |

The illustrative placeholders are explicitly labeled. They will be
replaced with computed values in week 1 of the v1 build (FRA GeoJSON
intersect with county boundaries, PHMSA CSV filter and count, USGS
PNSP CSV join to USDA cropland acres). The composite below is run with
qualitative bands so the work group can sanity-check the direction
without waiting for those compute steps.

## Composite walk-through (qualitative v0)

Applying the formula proposed in section 3 of HAZMAT_SCOPING.md:

    exposure_sub = weighted_max(rail_sub, fixed_facility_sub, ag_chem_sub)
    domain_risk = exposure_sub
                  x (1 + vulnerability_uplift)
                  / (1 + resilience_adjustment)
                  x health_impact_factor

| County | Rail sub | Fixed facility sub | Ag chem sub | Driving sub | Vulnerability (SVI-derived) | Resilience (WEM team distance + hospital) | Direction |
|---|---|---|---|---|---|---|---|
| Milwaukee | high | high | low | fixed facility | moderate (urban poverty pockets) | high (WEM Region 4 host, multiple hospitals) | High exposure offset by high resilience. Net: HIGH risk, but with strong response capacity. |
| Crawford | moderate (BNSF MR corridor) | low | moderate | rail | moderate-high (rural, older, low income) | low (long distance to nearest WEM Type I team, single critical-access hospital) | Moderate exposure amplified by low resilience. Net: MODERATE-HIGH risk, the kind of profile EM directors most want flagged. |
| Dodge | moderate | moderate | high | ag chem | moderate | moderate | Distributed exposure across all three sub-pathways, ag chem dominant. Net: MODERATE risk, the typical Wisconsin ag county profile. |

## Sanity check

The ranking that v0 produces (Milwaukee high, Crawford moderate-high,
Dodge moderate) is consistent with how Wisconsin emergency management
practitioners typically describe these counties:

- Milwaukee has the densest concentration of regulated chemical
  facilities in the state, plus heavy freight rail. Its risk is high
  on the exposure side but its response capacity is also among the
  state's best, which is exactly what the EVR formula captures.
- Crawford is the kind of small-population rail-corridor county that
  EM directors have specifically flagged as a gap in current CARA
  scoring. The BNSF Mississippi River line carries crude oil and
  ethanol unit trains through a county with 16k people and one
  critical-access hospital. v0 correctly elevates it relative to its
  population.
- Dodge represents the ag-intensive profile where exposure is real
  but distributed - no single major facility, but high pesticide
  loading, multiple Tier II facilities, and the I-41 / WIS-26 freight
  corridor. v0 places it in the middle, which matches practitioner
  intuition.

If the work group's read of the three counties does not match this
direction, the most likely lever is the weighted-max combining
function in the exposure layer. A sum-based combiner would push
Milwaukee further up and pull Crawford down; a maximum-only combiner
would do the opposite.

## What v0 deliberately does NOT do

- No production code changes. This comparison is paper-only until the
  work group approves direction.
- No new fetchers added to `utils/`. The TRI numbers were pulled with
  a one-shot scoping script (`scripts/hazmat_scoping_check.py`) that
  does not touch the request path or the CARA cache.
- No new risk weight redistribution in `config/risk_weights.yaml`.
  The 6% proposal in HAZMAT_SCOPING.md is a starting point for work
  group discussion, not an applied change.
- No new dashboard tile or action plan YAML. Those are v1 deliverables
  conditional on work group sign-off.

## Recommended work group decision points

1. Approve, revise, or reject the v0 composite shape (3 exposure
   sub-pathways combined with weighted maximum).
2. Decide combined vs. split (hazmat_industrial vs. hazmat_agricultural).
3. Approve the proposed 6% overall weight or specify an alternative.
4. Approve the resilience layer scope (WEM team distance only for v0,
   add NFPA 472 cert and hospital decon in v1).
5. Decide whether to pursue an EPA RMP Reading Room request now or
   accept the TRI-weighted RMP allocation as v0's compromise.
