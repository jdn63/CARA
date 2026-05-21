# Action Plan Research Log

Purpose. This log is the audit trail behind every source link that
appears in the CARA Action Plans. A subject-matter-expert reviewer
should be able to read this log and, without re-doing the research,
confirm that each cited URL substantively supports the activity it
backs.

Format. One section per domain. Each source records:

- Source ID used in `data/action_plans/*.yaml`.
- Canonical URL fetched on the verification date.
- One-sentence excerpt or paraphrase from the actual fetched page
  confirming that the page covers what we cite it for.
- The activities (by tier and discipline) the source backs in CARA.

Verification policy. URLs are re-checked quarterly. When a check
succeeds, bump the `verified` date in `_sources.yaml`. When a URL
breaks, locate the replacement landing page on the same publishing
organization and update the source entry rather than removing the
citation; if no replacement exists, retire the activity.

## Extreme Heat (pilot domain, v28.3)

All sources fetched 2026-05-20. Substantive content confirmed for each.

### cdc_brace -- CDC BRACE Framework

URL: https://www.cdc.gov/climate-health/php/brace/index.html

Confirmation. CDC Climate and Health Program page documents the
five-step Building Resilience Against Climate Effects framework as
the agency's standard planning approach for climate-driven health
risks, including heat, vector-borne disease, and air quality.

URL swap 2026-05-20. The previously cited landing page
`https://www.cdc.gov/climate-health/php/programs/index.html` began
returning HTTP 404 after CDC reorganized the Climate and Health
Program section. Replacement canonical page on the same publishing
organization (CDC Climate and Health Program / BRACE Framework) is
`https://www.cdc.gov/climate-health/php/brace/index.html`, confirmed
HTTP 200 via `scripts/verify_action_plan_sources.py --source
cdc_brace`. Per the verification policy at the top of this file, the
source entry was updated rather than removed; the two pilot Extreme
Heat activities it backs (PH pre_season heat vulnerability mapping
and PH multi_year BRACE planning cadence) are unchanged.

Backs.

- PH pre_season: heat vulnerability mapping using SVI, age, chronic
  condition, and housing layers.
- PH multi_year: adopt BRACE as the standing climate-health planning
  cadence.

### cdc_phep -- CDC PHEP Cooperative Agreement and capabilities

URL: https://www.cdc.gov/readiness/php/phep/index.html

Confirmation. CDC Office of Readiness and Response landing page for
the Public Health Emergency Preparedness cooperative agreement and
the 15 PHEP capabilities national standards for SLTT public health
departments.

Backs.

- PH this_year: heat-related illness syndromic surveillance cadence
  (PHEP Capability 13).
- PH this_year: Medical Reserve Corps and partner training (PHEP
  Capability 1, 14).
- PH multi_year: longitudinal heat health outcomes monitoring with
  healthcare coalitions (PHEP Capability 13).
- PH multi_year: integrate heat-health objectives into next PHEP
  work plan.

### heat_gov -- NIHHIS Heat.gov

URL: https://www.heat.gov/

Confirmation. Heat.gov is the interagency NOAA + CDC information
system for heat-health science, mapping tools, and community heat
action plan resources, with a dedicated communities and planning
section.

Backs.

- EM pre_season: pre-positioned messaging templates aligned with NWS
  HeatRisk color tiers.
- EM multi_year: build a county heat action plan with lead
  coordinator, activation thresholds, and partner responsibilities.

### nws_heatrisk -- NOAA NWS HeatRisk

URL: https://www.wpc.ncep.noaa.gov/heatrisk/

Confirmation. NOAA Weather Prediction Center's HeatRisk product
provides a seven-day color-coded heat risk forecast integrating
temperature, local climatology, and CDC heat-health thresholds.

Backs.

- PH pre_season: integrate HeatRisk thresholds into health alert
  workflows.

### epa_ehe_guidebook -- EPA Excessive Heat Events Guidebook

URL: https://www.epa.gov/heatislands/excessive-heat-events-guidebook

Confirmation. EPA landing page for the Excessive Heat Events
Guidebook, published with federal, state, local, and academic
partners to support community officials and emergency managers in
planning for excessive heat events; the underlying PDF documents
cooling-center planning, vulnerable populations, and alert
coordination.

Backs.

- EM pre_season: cooling-center verification with backup power and
  accessibility checks.

### epa_heat_islands_guide -- EPA Reducing Urban Heat Islands

URL: https://www.epa.gov/heatislands/guide-reducing-heat-islands

Confirmation. EPA compendium of strategies for reducing urban heat
island intensity covering trees and vegetation, green roofs, cool
roofs, cool pavements, and smart growth, with implementation
guidance for local governments.

Backs.

- EM this_year: adopt or update building, zoning, and site-plan
  provisions supporting cool-roof, cool-pavement, and tree-canopy
  practices.
- EM multi_year: multi-year urban heat-island reduction strategy.

### fema_extreme_heat_factsheet -- FEMA Extreme Heat HMA Fact Sheet

URL: https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf

Confirmation. FEMA fact sheet "Mitigating the Risk of Extreme
Temperatures with Hazard Mitigation Assistance Funds" describes
eligible HMA-funded heat mitigation measures.

Important policy update captured in source notes. The HMA Program
and Policy Guide v2.1 (effective 2025-01-20) removed standalone
extreme-temperature and standalone air-quality project eligibility.
Heat mitigation measures now must be integrated into multi-hazard
mitigation projects to remain HMA-eligible. Activities in CARA that
reference this source frame heat measures as components of
multi-hazard projects, not as standalone funding asks.

Backs.

- EM this_year: integrate extreme-heat resilience into upcoming
  multi-hazard mitigation projects to preserve HMA eligibility.
- EM multi_year: long-term retrofit pathway bundling cooling
  upgrades with energy-resilience improvements.

### fema_extreme_temps_sltt -- FEMA SLTT Leaders Guidance

URL: https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf

Confirmation. FEMA cross-functional leadership guidance for state,
local, tribal, and territorial officials on preparing for and
reducing the impact of extreme heat and cold, covering coordination
with health, utilities, and emergency-management partners.

Backs.

- EM pre_season: confirm coordination roles with health department,
  utilities, school districts, and Wisconsin Emergency Management
  region staff.
- EM this_year: utility resilience priorities (transformer upgrades,
  vegetation management, demand response).
- Winter storm EM: utility resilience and backup-power priorities.

### fema_hmp_guide -- FEMA Hazard Mitigation Planning hub

URL: https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning

Confirmation. FEMA's authoritative hub for the Local Mitigation
Planning Policy Guide, 44 CFR Part 201 requirements, and the
5-year mitigation-plan update cycle.

Backs.

- EM framework_capabilities (multiple domains): 44 CFR 201.6 plan
  element references.
- EM pre_season (multiple domains): confirm the local HMP profile
  is within the 5-year update cycle.
- EM this_year (multiple domains): update county risk assessment
  with hazard-specific exposed populations and critical facilities.
- EM multi_year (multiple domains): cross-jurisdictional planning
  with neighboring counties and the WEM region.

### wi_dhs_climate_heat -- Wisconsin DHS Climate and Health: Extreme Heat

URL: https://www.dhs.wisconsin.gov/climate/heat.htm

Confirmation. Wisconsin Department of Health Services state-level
guidance on extreme heat impacts, advisory thresholds, vulnerable
populations, and resources for residents and health professionals.

Backs.

- PH pre_season: refresh multilingual heat-health messaging
  appropriate for Wisconsin communities.
- PH this_year: coordinate with weatherization and utility programs
  to identify residents without reliable cooling.

### naccho_heat_toolkit -- NACCHO Extreme Heat Toolkit

URL: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module

Confirmation. NACCHO toolbox entry for the Extreme Heat Toolkit and
Training Module published with the Minnesota Department of Health,
aimed at local health departments and including planning
checklists and vulnerable-population outreach strategies.

Backs.

- PH pre_season: confirm cooling-shelter inventory with hours,
  accessibility, transportation access, pet policies.
- PH this_year: MOUs with aging services, home-healthcare, and
  community health workers for wellness-check outreach.
- PH multi_year: community health worker program with seasonal
  surge capacity for heat advisories.

## 2026-05-20 addendum: primary HMA v2.1 citation

Added source `fema_hma_guide_v2_1` pointing to FEMA's Hazard Mitigation
Assistance Program and Policy Guide hub. The HMA Guide v2.1 (effective
2025-01-20) is the primary policy document that removed standalone
extreme-temperature project eligibility from BRIC/FMA/HMGP. The EM
multi-hazard-integration activity in `extreme_heat.yaml` now cites this
primary source instead of the 2022 FEMA fact sheet (which retains its
own citation for eligible mitigation measure types and bundling
guidance, where it remains authoritative).

URL verified 2026-05-20: https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide

Re-verification cadence: quarterly.

## Task #9 expansion (all remaining domains)

The remaining nine action-plan domains (flood, tornado, winter_storm,
thunderstorm, dam_failure, vector_borne_disease, air_quality,
active_shooter, cybersecurity, infectious-disease "health") were
migrated from inline template copy to the YAML + source-citation
pattern established by the Extreme Heat pilot.

All new sources listed below were added to `_sources.yaml` with
`verified: 2026-05-20`. URLs are canonical landing pages on federal,
state, or recognized national-association websites. The quarterly
re-verification job (separate task) is the authoritative confirmation
that each link still resolves and substantively covers the cited
content; this log records the editorial basis for the initial
selection.

### Cross-domain Public Health sources

- `naccho_pphr` -- Project Public Health Ready hub
  (https://www.naccho.org/programs/public-health-preparedness/pphr).
  Backs `multi_year` activities across every PH domain that commit
  to integrating the domain's preparedness objectives into PPHR
  re-recognition documentation.

- `hhs_aspr_tracie` -- ASPR TRACIE healthcare-emergency-preparedness
  information gateway (https://asprtracie.hhs.gov/). Backs PH
  activities involving healthcare coalitions, medical surge,
  patient tracking, and continuity for medically dependent
  populations (flood, tornado, winter_storm, thunderstorm,
  dam_failure, air_quality, active_shooter, health).

- `samhsa_dtac` -- SAMHSA Disaster Behavioral Health Information
  Series / Disaster Technical Assistance Center
  (https://www.samhsa.gov/dtac). Backs PH activities on crisis
  counseling, behavioral-health surge, and long-term recovery
  monitoring (flood, tornado, dam_failure, active_shooter,
  air_quality, etc.).

- `nctsn_pfa` -- NCTSN / NCPTSD Psychological First Aid Field
  Operations Guide
  (https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition).
  Backs PH training activities for psychological first aid in
  tornado and active_shooter.

- `cdc_nssp` -- National Syndromic Surveillance Program
  (https://www.cdc.gov/nssp/index.html). Backs PH pre_season
  activities verifying ED-data syndromic feeds for heat illness,
  CO poisoning, respiratory illness, waterborne illness, and
  cardiovascular events (winter_storm, flood, thunderstorm,
  air_quality, cybersecurity continuity, dam_failure).

- `cdc_nndss` -- National Notifiable Diseases Surveillance System
  (https://www.cdc.gov/nndss/index.html). Backs PH pre_season for
  vector_borne_disease and the multi_year scalable-surveillance
  activity in `health`.

- `cdc_han` -- CDC Health Alert Network
  (https://emergency.cdc.gov/han/). Backs PH activities verifying
  clinician HAN distribution lists across winter_storm, tornado,
  thunderstorm, active_shooter, vector_borne_disease, and health.

- `cdc_cerc` -- Crisis and Emergency Risk Communication
  (https://emergency.cdc.gov/cerc/). Backs PH activities in the
  `health` domain involving pre-scripted messaging, spokesperson
  training, and risk-communication programs.

- `mrc_program` -- Medical Reserve Corps program
  (https://aspr.hhs.gov/MRC/Pages/default.aspx). Backs PH training
  activities that name MRC roles (winter_storm, active_shooter,
  health).

- `wi_dhs_preparedness` -- Wisconsin Public Health Preparedness
  Program (https://www.dhs.wisconsin.gov/preparedness/index.htm).
  Backs PH this_year coordination activities with WI DHS regional
  preparedness staff across multiple domains.

- `wi_dhs_communicable`, `wi_dhs_tickborne`, `wi_dhs_mosquito` --
  Wisconsin DHS disease-program landing pages. Back the `health`
  data-sharing activity and the `vector_borne_disease` PH
  activities respectively.

- `cdc_lyme`, `cdc_westnile`, `cdc_vector_borne` -- CDC program
  pages backing vector_borne_disease PH activities on clinician
  training and surveillance.

- `cdc_wildfire_smoke`, `epa_airnow`, `epa_smoke_ready` -- back
  air_quality PH and EM activities on sensitive-group guidance,
  cleaner-air spaces, AQI-tied alerting, and outreach.

- `cdc_carbon_monoxide`, `cdc_winter_weather` -- back winter_storm
  PH activities on CO messaging and integrated winter planning.

- `cdc_floods_health` -- backs PH activities on private-well
  sampling, wound and waterborne illness, and post-flood food
  safety in flood, thunderstorm, and dam_failure.

- `cdc_tornado_health` -- backs PH pre_season messaging in tornado.

- `cdc_lightning` -- backs PH activities in thunderstorm on
  lightning-injury messaging and surveillance.

- `cdc_violence_prevention`, `samhsa_mass_violence`,
  `stop_the_bleed` -- back active_shooter PH activities on
  upstream violence prevention, behavioral-health response, and
  mass-casualty bleeding-control preparedness.

- `hhs_405d`, `hhs_ocr_hipaa_security`, `nist_csf_2`,
  `cisa_phi_sector`, `cisa_cpg`, `cisa_shields_up` -- back
  cybersecurity PH and EM activities on cybersecurity practices,
  HIPAA Security Rule compliance, the NIST CSF 2.0 reference
  framework, CISA sector engagement, CISA CPGs, and standing
  Shields Up posture.

### Cross-domain Emergency Management sources

- `fema_cpg_101` -- CPG 101, Developing and Maintaining EOPs
  (https://www.fema.gov/emergency-managers/national-preparedness/plan).
  Backs `health` EM activities on biological-incident annex
  exercises and EOP refresh schedules.

- `fema_cpg_201` -- CPG 201 THIRA/SPR Guide
  (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment).
  Backs `health` EM activities on THIRA/SPR updates incorporating
  recent biological incidents.

- `fema_ndrf` -- National Disaster Recovery Framework
  (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery).
  Backs `health` EM activity integrating the Health and Social
  Services Recovery Support Function into county recovery planning.

- `fema_npg` -- National Preparedness Goal and Core Capabilities
  (https://www.fema.gov/emergency-managers/national-preparedness/goal).
  Backs `health` EM framework reference and pre_season activities
  framing the biological-incident annex against the cross-mission
  Core Capabilities.

- `noaa_wrn` -- NOAA Weather-Ready Nation
  (https://www.weather.gov/wrn/). Backs EM messaging-template and
  ambassador-partnership activities across flood, tornado,
  winter_storm, thunderstorm, dam_failure, air_quality, and
  vector_borne_disease.

- `nws_stormready` -- NWS StormReady Community Program
  (https://www.weather.gov/stormready/). Backs EM activities on
  adopting or renewing StormReady designation across flood,
  tornado, winter_storm, and thunderstorm.

- `fema_p_361` -- FEMA P-361 Safe Rooms for Tornadoes and
  Hurricanes (https://www.fema.gov/emergency-managers/risk-management/safe-rooms).
  Backs tornado EM pre_season and this_year activities on safe-room
  verification and the construction-priority HMA pipeline.

- `fema_dam_safety`, `wi_dnr_dams`, `asdso` -- back dam_failure EM
  activities on EAP currency, inundation mapping, state
  inspection cycles, and ongoing ASDSO/DNR partnership.

- `fema_nfip`, `fema_floodplain` -- back flood EM activities on
  NFIP participation, CRS class improvements, floodplain-management
  ordinance currency, and acquisition/elevation strategies. Also
  back vector_borne_disease EM stormwater-and-habitat activities
  and thunderstorm EM drainage activities.

- `ready_winter` -- Ready.gov Winter Weather
  (https://www.ready.gov/winter-weather). Backs winter_storm PH
  pre_season warming-center inventory and EM pre_season verification.

- `wem_resources`, `wem_preparedness` -- Wisconsin Emergency
  Management hub pages. Back EM pre_season coordination roles and
  multi_year cross-jurisdictional planning activities across every
  EM domain.

- `cisa_active_shooter`, `fbi_active_shooter`, `alerrt`,
  `fema_p_1000` -- back active_shooter EM activities on
  preparedness annexes, integrated active-attack response training,
  Run-Hide-Fight messaging, and safer-schools integration.

- `cisa_cpg`, `cisa_shields_up`, `cisa_phi_sector`, `nist_csf_2`,
  `hhs_405d` -- back cybersecurity EM framework reference and
  activities on baseline performance goals, MFA, vulnerability
  management, and segmentation/zero-trust strategy.

### Reuse from the Extreme Heat pilot

The pilot sources `cdc_phep`, `cdc_brace`, `fema_hmp_guide`,
`fema_hma_guide_v2_1`, and `fema_extreme_temps_sltt` are reused
across the expanded domains where they substantively cover the
cited activity (PHEP capability statements, BRACE climate-adaptation
planning for vector_borne_disease, HMP elements as the EM framework
across natural-hazard domains, the HMA v2.1 multi-hazard integration
constraint for any mitigation funding ask, and the SLTT extreme-
temperatures guidance for winter_storm utility resilience).

### Verification posture

The verification dates in `_sources.yaml` reflect the editorial
selection date for these new entries (2026-05-20). The standing
quarterly re-verification task is the authoritative mechanism for
re-confirming each URL on the cadence required by the verification
policy at the top of this log.

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 35 returned HTTP 200, 29 failed, 9 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- cdc_brace: HTTP 404 (https://www.cdc.gov/climate-health/php/programs/index.html)
- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 64 sources. Result: 36 returned HTTP 200, 28 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 40 returned HTTP 200, 38 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: HTTP 404 (https://www.cdc.gov/orr/readiness/chempack/index.html)
- cdc_sns: HTTP 404 (https://www.cdc.gov/orr/readiness/stockpile/index.html)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- atsdr_mhmi: HTTP 404 (https://www.atsdr.cdc.gov/mhmi/index.html)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- epcra_tier2: HTTP 404 (https://www.epa.gov/epcra/epcra-sections-311-312-tier-i-and-tier-ii-reporting)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- wem_serb: HTTP 404 (https://wem.wi.gov/resources/state-emergency-response-board/)
- niosh_ag: HTTP 404 (https://www.cdc.gov/niosh/agforfish/default.html)
- wi_datcp_agchem: HTTP 404 (https://datcp.wi.gov/Pages/Programs_Services/AgriculturalChemicals.aspx)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 40 returned HTTP 200, 38 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: HTTP 404 (https://www.cdc.gov/orr/readiness/chempack/index.html)
- cdc_sns: HTTP 404 (https://www.cdc.gov/orr/readiness/stockpile/index.html)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- atsdr_mhmi: HTTP 404 (https://www.atsdr.cdc.gov/mhmi/index.html)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- epcra_tier2: HTTP 404 (https://www.epa.gov/epcra/epcra-sections-311-312-tier-i-and-tier-ii-reporting)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- wem_serb: HTTP 404 (https://wem.wi.gov/resources/state-emergency-response-board/)
- niosh_ag: HTTP 404 (https://www.cdc.gov/niosh/agforfish/default.html)
- wi_datcp_agchem: HTTP 404 (https://datcp.wi.gov/Pages/Programs_Services/AgriculturalChemicals.aspx)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 42 returned HTTP 200, 36 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- epcra_tier2: HTTP 404 (https://www.epa.gov/epcra/epcra-sections-311-312-tier-i-and-tier-ii-reporting)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- wem_serb: HTTP 404 (https://wem.wi.gov/resources/state-emergency-response-board/)
- wi_datcp_agchem: HTTP 404 (https://datcp.wi.gov/Pages/Programs_Services/AgriculturalChemicals.aspx)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 44 returned HTTP 200, 34 failed, 12 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- samhsa_dtac: ReadTimeout: HTTPSConnectionPool(host='www.samhsa.gov', port=443): Read timed out. (read timeout=20) (https://www.samhsa.gov/dtac)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: ReadTimeout: HTTPSConnectionPool(host='www.samhsa.gov', port=443): Read timed out. (read timeout=20) (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 44 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- naccho_pphr: HTTP 522 (https://www.naccho.org/programs/public-health-preparedness/pphr)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 78 sources. Result: 45 returned HTTP 200, 33 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-20 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 13 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 15 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 15 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 14 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 21 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- nws_stormready: https://www.weather.gov/stormready/
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/

## 2026-05-21 quarterly re-verification round

Ran `scripts/verify_action_plan_sources.py` against 81 sources. Result: 47 returned HTTP 200, 34 failed, 20 showed content drift since the previous round.

Failed URLs requiring reviewer action:

- heat_gov: HTTP 403 (https://www.heat.gov/)
- fema_extreme_heat_factsheet: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_extreme-heat-fact-sheet_102022.pdf)
- fema_extreme_temps_sltt: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_guidance-extreme-temperatures-state-local-tribal-territorial-leaders.pdf)
- fema_hma_guide_v2_1: HTTP 403 (https://www.fema.gov/grants/mitigation/hazard-mitigation-assistance-guide)
- fema_hmp_guide: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/hazard-mitigation-planning)
- cdc_han: HTTP 404 (https://emergency.cdc.gov/han/)
- mrc_program: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MRC/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MRC/Pages/default.aspx)
- wi_dhs_communicable: HTTP 403 (https://www.dhs.wisconsin.gov/disease/communicable.htm)
- cdc_vector_borne: HTTP 404 (https://www.cdc.gov/ncezid/dvbd/index.html)
- cdc_wildfire_smoke: HTTP 404 (https://www.cdc.gov/wildfires/safety/wildfire-smoke-and-your-health.html)
- cdc_winter_weather: HTTP 404 (https://www.cdc.gov/disasters/winter/index.html)
- cdc_tornado_health: HTTP 404 (https://www.cdc.gov/disasters/tornadoes/index.html)
- samhsa_mass_violence: HTTP 404 (https://www.samhsa.gov/mental-health/mass-violence)
- hhs_ocr_hipaa_security: HTTP 403 (https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- cisa_phi_sector: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/healthcare-and-public-health-sector)
- cisa_cpg: HTTP 403 (https://www.cisa.gov/cross-sector-cybersecurity-performance-goals)
- cisa_shields_up: HTTP 403 (https://www.cisa.gov/shields-up)
- cisa_active_shooter: HTTP 403 (https://www.cisa.gov/topics/physical-security/active-shooter-preparedness)
- fbi_active_shooter: HTTP 403 (https://www.fbi.gov/how-we-can-help-you/active-shooter-safety-resources)
- fema_p_1000: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/earthquake/training/p-1000)
- fema_cpg_101: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/plan)
- fema_cpg_201: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/risk-capability-assessment)
- fema_ndrf: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/frameworks/recovery)
- fema_npg: HTTP 403 (https://www.fema.gov/emergency-managers/national-preparedness/goal)
- fema_p_361: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/safe-rooms)
- fema_dam_safety: HTTP 403 (https://www.fema.gov/emergency-managers/risk-management/dam-safety)
- fema_nfip: HTTP 403 (https://www.fema.gov/flood-insurance)
- fema_floodplain: HTTP 403 (https://www.fema.gov/floodplain-management)
- cdc_chempack: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /CHEMPACK/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/CHEMPACK/Pages/default.aspx)
- cdc_sns: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /SNS/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/SNS/Pages/default.aspx)
- aspr_mcm: SSLError: HTTPSConnectionPool(host='aspr.hhs.gov', port=443): Max retries exceeded with url: /MCM/Pages/default.aspx (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1016)'))) (https://aspr.hhs.gov/MCM/Pages/default.aspx)
- dot_erg: HTTP 403 (https://www.phmsa.dot.gov/hazmat/erg/emergency-response-guidebook-erg)
- cisa_chem: HTTP 403 (https://www.cisa.gov/topics/critical-infrastructure-security-and-resilience/critical-infrastructure-sectors/chemical-sector)
- fema_debris_management: HTTP 403 (https://www.fema.gov/sites/default/files/documents/fema_325_public-assistance-debris-management-guide_06-30-2021.pdf)

Content drift detected (substantive review recommended; page body changed since the last recorded hash):

- epa_ehe_guidebook: https://www.epa.gov/heatislands/excessive-heat-events-guidebook
- epa_heat_islands_guide: https://www.epa.gov/heatislands/guide-reducing-heat-islands
- wi_dhs_climate_heat: https://www.dhs.wisconsin.gov/climate/heat.htm
- naccho_heat_toolkit: https://www.naccho.org/resource-hub-articles/extreme-heat-toolkit-and-training-module
- naccho_pphr: https://www.naccho.org/programs/public-health-preparedness/pphr
- hhs_aspr_tracie: https://asprtracie.hhs.gov/
- samhsa_dtac: https://www.samhsa.gov/dtac
- nctsn_pfa: https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition
- wi_dhs_preparedness: https://www.dhs.wisconsin.gov/preparedness/index.htm
- wi_dhs_tickborne: https://www.dhs.wisconsin.gov/tick/index.htm
- wi_dhs_mosquito: https://www.dhs.wisconsin.gov/mosquito/index.htm
- epa_airnow: https://www.airnow.gov/
- epa_smoke_ready: https://www.epa.gov/smoke-ready-toolbox-wildfires
- stop_the_bleed: https://www.stopthebleed.org/
- nist_csf_2: https://www.nist.gov/cyberframework
- asdso: https://damsafety.org/
- wi_dnr_dams: https://dnr.wisconsin.gov/topic/Dams
- ready_winter: https://www.ready.gov/winter-weather
- wem_resources: https://wem.wi.gov/
- wem_preparedness: https://wem.wi.gov/preparedness/
