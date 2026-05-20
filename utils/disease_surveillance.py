"""
Disease Surveillance Module

This module provides functionality for tracking infectious disease activity
across different jurisdictions.

- Supports weekly data updates with options for more frequent updates during outbreaks
- Implements caching with appropriate expiry times for different data types
- Provides disease activity scoring based on current surveillance data
"""

import logging
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime, timedelta

# Import cache utilities
from utils.persistent_cache import (
    get_from_persistent_cache,
    set_in_persistent_cache,
    clear_cache_by_prefix
)

from utils.cache import (
    get_from_memory_cache,
    set_in_memory_cache,
    remove_from_memory_cache
)

# Import data processor for county mapping
from utils.data_processor import get_county_for_jurisdiction

logger = logging.getLogger(__name__)

# Constants
DISEASE_CACHE_PREFIX = "disease_activity_"  # Prefix for disease data cache keys
DISEASE_CACHE_EXPIRY = 7  # Default cache expiry in days

# In-memory cache for frequently accessed disease data
_disease_activity_cache = {}

def get_disease_metrics(county_name: str) -> Dict[str, Any]:
    """
    Get comprehensive disease metrics for a specific county using Wisconsin DHS surveillance data.
    
    Args:
        county_name: Name of the county
        
    Returns:
        Dictionary containing disease metrics including:
        - Influenza-like illness (ILI) activity
        - COVID-19 activity
        - RSV activity
        - Overall health risk score
    """
    try:
        # Import Wisconsin DHS scraper
        from utils.wisconsin_dhs_scraper import get_wisconsin_surveillance_data
        
        # Get statewide surveillance data from Wisconsin DHS
        surveillance_data = get_wisconsin_surveillance_data()
        
        # Extract key metrics from NSSP surveillance data
        statewide_activity = surveillance_data.get('statewide_activity', {})
        # ed_visit_data: percent of all ED visits per pathogen (CDC NSSP/ESSENCE)
        ed_visit_data = surveillance_data.get('ed_visit_data', {})
        risk_indicators = surveillance_data.get('risk_indicators', {})

        # NSSP provides a Wisconsin-statewide respiratory signal only; it
        # is applied uniformly to all 72 counties. Prior code multiplied
        # this signal by a hand-coded population-density-tier modifier
        # (0.8-1.2) that invented county-level variation not present in
        # the source data. That code path has been removed entirely
        # (review finding H4). The signal_scope and signal_granularity_note
        # fields below qualify the metric so user-facing renderers do not
        # present the statewide ILI/COVID/RSV activity scores or the
        # ed_visit_pct percentages as county-specific surveillance.

        # Extract vaccination data
        vaccination_data = surveillance_data.get('vaccination_data', {})

        nssp_scope_note = (
            'CDC NSSP Wisconsin statewide signal applied uniformly to all '
            '72 counties (no county-level NSSP data is publicly published).'
        )
        metrics = {
            'ili_activity': _map_activity_to_score(statewide_activity.get('influenza', 'low')),
            'covid_activity': _map_activity_to_score(statewide_activity.get('covid19', 'minimal')),
            'rsv_activity': _map_activity_to_score(statewide_activity.get('rsv', 'minimal')),
            # ed_visit_pct: % of total ED visits per pathogen (CDC NSSP/ESSENCE)
            # Replaces lab positivity; reflects syndromic ED burden rather than lab test rate
            'ed_visit_pct': {
                'influenza': ed_visit_data.get('influenza_percent', 1.5),
                'covid19': ed_visit_data.get('covid19_percent', 0.3),
                'rsv': ed_visit_data.get('rsv_percent', 0.5),
            },
            'vaccination_rates': {
                'flu_overall': vaccination_data.get('flu_vaccination', {}).get('overall_population', 45.6),
                'mmr_school_age': vaccination_data.get('mmr_vaccination', {}).get('children_5_18_years', 87.8),
                'school_compliance': vaccination_data.get('school_vaccination', {}).get('meeting_minimum_requirements', 86.4),
            },
            # Granularity metadata: ili/covid/rsv activity and ed_visit_pct are
            # statewide signals. Templates should qualify any per-county text.
            'signal_scope': 'statewide_wisconsin',
            'signal_granularity_note': nssp_scope_note,
            'last_updated': surveillance_data.get('last_updated', datetime.now().isoformat()),
        }

        # Risk score: NSSP combined_risk x vaccination risk multiplier.
        # No regional adjustment is applied; per review finding H4, the
        # underlying NSSP signal is statewide and the prior hand-coded
        # density-tier multiplier was removed (it invented county-level
        # variation that did not exist in the source data).
        dhs_combined_risk = risk_indicators.get('combined_risk', 0.45)
        vaccination_risk_assessment = _calculate_strategic_vaccination_risk(vaccination_data, county_name)
        base_risk_with_vaccination = dhs_combined_risk * vaccination_risk_assessment['risk_multiplier']
        acute_risk_score = min(1.0, max(0.0, base_risk_with_vaccination))

        # === STRATEGIC PREPAREDNESS BASELINE FLOOR (Option 1, 2026-05-20) ===
        # Applies a P-times-C floor so the displayed infectious-disease risk
        # never drops below a meaningful preparedness level on a quiet
        # surveillance week. See utils/strategic_baseline.py for the formula
        # and config/risk_weights.yaml -> disease_severity_profiles for the
        # cited per-disease severity inputs. The floor is unconditional
        # (CARA is effectively always in strategic_planning mode for the
        # request path; emergency_response mode was retired in 2026-05).
        try:
            from utils.strategic_baseline import compute_disease_baselines
            strategic_baseline = compute_disease_baselines(county_name)
            baseline_score = float(strategic_baseline.get('aggregate_baseline', 0.10))
        except Exception as _baseline_exc:
            logger.warning(
                f"strategic_baseline failed for {county_name}: {_baseline_exc}"
            )
            strategic_baseline = None
            baseline_score = 0.10

        # Floor: displayed score is the max of current acute and strategic
        # baseline. The acute path retains all upside; the baseline only
        # raises the floor, never lowers an active signal.
        risk_score = min(1.0, max(acute_risk_score, baseline_score))
        floor_applied = baseline_score > acute_risk_score

        # Activity level strings for display
        activity_levels = {
            'ili': statewide_activity.get('influenza', 'low'),
            'covid': statewide_activity.get('covid19', 'minimal'),
            'rsv': statewide_activity.get('rsv', 'minimal'),
            'overall': statewide_activity.get('overall', 'low'),
        }

        # Overall trend from NSSP ED visit direction per pathogen
        ed_data = surveillance_data.get('emergency_dept_data', {})
        trend_data = ed_data.get('trends', {})
        trend = _determine_overall_trend([
            trend_data.get('influenza', 'stable'),
            trend_data.get('covid19', 'stable'),
            trend_data.get('rsv', 'stable'),
        ])

        nssp_url = surveillance_data.get(
            'report_url',
            'https://data.cdc.gov/Public-Health-Surveillance/'
            '2023-Respiratory-Virus-Response-NSSP-Emergency-Dep/vutn-jzwm'
        )
        return {
            'risk_score': risk_score,
            'acute_risk_score': acute_risk_score,
            'strategic_baseline': strategic_baseline,
            'floor_applied': floor_applied,
            'metrics': metrics,
            'activity_levels': activity_levels,
            'trend': trend,
            'vaccination_risk_assessment': vaccination_risk_assessment,
            'report_date': surveillance_data.get('report_date'),
            'confidence': risk_indicators.get('confidence', 0.9),
            'last_updated': surveillance_data.get('last_updated', datetime.now().isoformat()),
            'data_sources': [
                'CDC NSSP Emergency Department Visits (data.cdc.gov/resource/vutn-jzwm)',
            ],
            'source_url': nssp_url,
        }
    except Exception as e:
        logger.error(f"Error getting disease metrics for {county_name}: {str(e)}")
        # Return empty structure with zero values
        # Get fallback vaccination risk assessment for consistency
        fallback_vaccination_assessment = _get_fallback_vaccination_risk_assessment()
        
        return {
            'risk_score': 0.45,
            'metrics': {
                'ili_activity': 0.3,
                'covid_activity': 0.1,
                'rsv_activity': 0.1,
                'ed_visit_pct': {
                    'influenza': 1.5,
                    'covid19': 0.3,
                    'rsv': 0.5,
                },
                'vaccination_rates': {
                    'flu_overall': 45.6,
                    'mmr_school_age': 87.8,
                    'school_compliance': 86.4,
                },
                # Granularity metadata (kept in fallback for shape consistency
                # with the success path; see review finding H4).
                'signal_scope': 'statewide_wisconsin',
                'signal_granularity_note': (
                    'CDC NSSP Wisconsin statewide signal applied uniformly to '
                    'all 72 counties (no county-level NSSP data is publicly '
                    'published).'
                ),
                'last_updated': datetime.now().isoformat(),
            },
            'activity_levels': {
                'ili': 'low',
                'covid': 'minimal',
                'rsv': 'minimal',
                'overall': 'low',
            },
            'trend': 'stable',
            'vaccination_risk_assessment': fallback_vaccination_assessment,
            'confidence': 0.30,
            'last_updated': datetime.now().isoformat(),
            'data_sources': ['Fallback estimates - NSSP API unavailable'],
        }

def _map_activity_to_score(activity_level: str) -> float:
    """Map DHS activity level strings to numeric scores (0.0-1.0)"""
    activity_mapping = {
        'minimal': 0.1,
        'low': 0.3,
        'moderate': 0.6,
        'high': 0.8,
        'very_high': 1.0
    }
    return activity_mapping.get(activity_level.lower(), 0.4)

def _calculate_strategic_vaccination_risk(
    vaccination_data: Dict[str, Any],
    county_name: str,
    surveillance_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate strategic vaccination risk assessment for policy decision-making.

    Herd immunity gap analysis applies to MMR (measles: 95% threshold) and
    seasonal influenza (70% threshold).  COVID-19 is tracked separately as a
    coverage/preparedness metric; no fixed herd-immunity threshold is applied
    because SARS-CoV-2 immune-escape variants (XBB, JN.1, KP.3, XEC, LP.8)
    have made a stable population threshold scientifically indeterminate
    (CDC/WHO guidance updated 2022-2024).

    Active outbreak detection:
      - ``active_measles_outbreak`` is a live STATEWIDE WISCONSIN signal
        sourced from CDC NNDSS Weekly Data (see utils/nndss_communicable.py).
        It fires True when CDC reports any indigenous WI measles case in
        the last 4 reported weeks, any indigenous YTD case where YTD is
        running at or ahead of the prior year, or more than 2 imported
        cases in the last 4 reported weeks. Because NNDSS is published at
        state-level only (county-level WEDSS data is not publicly
        accessible), the same flag is applied uniformly to all 72
        counties; downstream consumers must label any rendered policy
        text as a statewide signal, not a county-specific outbreak.

    Args:
        vaccination_data: Vaccination data from Wisconsin DHS
        county_name: County name for potential county-specific adjustments
        surveillance_data: Optional full surveillance dict; reserved for
            future dynamic outbreak detection.

    Returns:
        Comprehensive vaccination risk assessment with policy indicators
    """
    if not vaccination_data:
        return _get_fallback_vaccination_risk_assessment()

    # Extract vaccination rates
    flu_vaccination = vaccination_data.get('flu_vaccination', {})
    mmr_vaccination = vaccination_data.get('mmr_vaccination', {})
    school_vaccination = vaccination_data.get('school_vaccination', {})

    school_compliance = school_vaccination.get('meeting_minimum_requirements', 86.4)

    # Flu vaccination: prefer county-specific CHR data (BRFSS survey, all-ages seasonal)
    # WI range: 22% (Taylor/Polk) to 69% (Dane). Fallback: WI mean 45.6%.
    statewide_flu_default = flu_vaccination.get('overall_population', 45.6)
    try:
        from utils.health_metrics_data import get_flu_vaccination_rate
        county_flu_rate = get_flu_vaccination_rate(county_name)
        if county_flu_rate is not None:
            flu_rate = county_flu_rate
            logger.info(
                f"Strategic vaccination risk using county flu rate for {county_name}: "
                f"{flu_rate:.1f}% (CHR)"
            )
        else:
            flu_rate = statewide_flu_default
    except Exception:
        flu_rate = statewide_flu_default

    # MMR rate: prefer county-specific WI DHS WIR data (24-month olds) when available
    statewide_mmr_default = mmr_vaccination.get('children_5_18_years', 87.8)
    try:
        from utils.dhs_data import _fetch_mmr_county_data
        mmr_county_rates = _fetch_mmr_county_data()
        county_key = county_name.strip().title() if county_name else ""
        if county_key and county_key in mmr_county_rates:
            mmr_rate = mmr_county_rates[county_key]
            logger.info(
                f"Strategic vaccination risk using county MMR rate for {county_key}: "
                f"{mmr_rate:.1f}% (WI DHS WIR)"
            )
        else:
            mmr_rate = statewide_mmr_default
    except Exception:
        mmr_rate = statewide_mmr_default
    
    # === HERD IMMUNITY GAP ANALYSIS ===
    # Thresholds apply only to pathogens for which a stable population-level
    # protection threshold is scientifically established:
    #   - Measles (MMR): 95% (R0 ~12-18, high aerosol transmission)
    #   - Seasonal influenza: 70% (ACIP target; lower R0, antigenic drift)
    #
    # COVID-19 vaccination is not included: SARS-CoV-2 immune-escape variants
    # have invalidated any fixed herd-immunity threshold. No current data source
    # provides reliable county-level COVID vaccination coverage.
    herd_immunity_thresholds = {
        'mmr': 95.0,  # Measles: 95% for community protection (CDC/ACIP)
        'flu': 70.0,  # Seasonal flu: 70% community protection target (ACIP)
    }

    # Calculate gaps from herd immunity thresholds (MMR and flu only)
    gaps = {
        'mmr_gap': max(0, herd_immunity_thresholds['mmr'] - mmr_rate),
        'flu_gap': max(0, herd_immunity_thresholds['flu'] - flu_rate),
        'school_compliance_gap': max(0, 90.0 - school_compliance),
    }

    # === OUTBREAK RISK INDICATORS ===
    # Granular measles flags from CDC NNDSS Weekly Data. See
    # utils/nndss_communicable.py for the full data flow. Three flags
    # are now exposed because the prior umbrella flag conflated three
    # operationally distinct signals (CDC/CSTE distinguishes acute
    # local transmission from import pressure from year-to-date
    # elevated incidence; each drives a different response posture):
    #
    #   active_local_transmission  - indigenous case in last 4 weeks
    #                                (the only signal that warrants
    #                                acute "active outbreak" language)
    #   import_pressure_elevated   - more than 2 imported cases in
    #                                last 4 weeks (NOT itself an
    #                                outbreak; elevates spread risk)
    #   ytd_elevated               - indigenous YTD case AND YTD >=
    #                                prior YTD (year-level vulnerability)
    #
    # GRANULARITY: All three are statewide signals applied uniformly
    # to all 72 counties (WEDSS county-level case data is not publicly
    # accessible).
    try:
        from utils.nndss_communicable import get_measles_outbreak_flags
        _measles_flags = get_measles_outbreak_flags()
        active_local_transmission = _measles_flags['active_local_transmission']
        import_pressure_elevated = _measles_flags['import_pressure_elevated']
        ytd_elevated = _measles_flags['ytd_elevated']
        active_measles_outbreak = _measles_flags['active_measles_outbreak']
        outbreak_signal_source = 'cdc_nndss'
    except Exception as exc:
        logger.warning(f"NNDSS measles flags unavailable, defaulting to False: {exc}")
        active_local_transmission = False
        import_pressure_elevated = False
        ytd_elevated = False
        active_measles_outbreak = False
        outbreak_signal_source = 'unavailable'
    outbreak_conditions = {
        # Umbrella flag (OR of the three granular flags) - kept for
        # backward compatibility with templates and downstream consumers.
        'active_measles_outbreak': active_measles_outbreak,
        # Granular flags - new code should prefer these so that import
        # pressure and YTD-elevated incidence are not mislabeled as
        # active community transmission.
        'active_local_transmission': active_local_transmission,
        'import_pressure_elevated': import_pressure_elevated,
        'ytd_elevated': ytd_elevated,
        # Granularity metadata: NNDSS publishes WI at state level only;
        # the same signal is broadcast to all 72 counties. Downstream
        # renderers must use these fields to qualify any user-facing text.
        'outbreak_signal_scope': 'statewide_wisconsin',
        'outbreak_signal_source': outbreak_signal_source,
        'below_measles_threshold': mmr_rate < 95.0,
        'school_vulnerability': school_compliance < 90.0,
        'multiple_gaps': sum(1 for gap in gaps.values() if gap > 5.0) >= 2,
    }

    # === SCHOOL VULNERABILITY INDEX ===
    # Pure vaccination-compliance signal (MMR + school compliance gaps).
    # Intentionally does NOT incorporate the live outbreak flag: the
    # outbreak signal is applied to the multiplier directly below, and
    # folding it into the school index as well caused the same statewide
    # signal to be counted three times in the multiplier (review H1).
    school_vulnerability_score = _calculate_school_vulnerability_index(
        mmr_rate, school_compliance
    )

    # === STRATEGIC RISK MULTIPLIER CALCULATION ===
    # Increases risk when vaccination gaps below critical thresholds are present
    base_multiplier = 1.0

    # MMR gap penalty (4% increase per percentage point below 95% threshold)
    if gaps['mmr_gap'] > 5.0:
        base_multiplier += gaps['mmr_gap'] * 0.04

    if gaps['school_compliance_gap'] > 5.0:
        base_multiplier += gaps['school_compliance_gap'] * 0.02

    # Outbreak pathway: mutually exclusive, severity-ordered contributions
    # from the three granular NNDSS flags, capped at +0.30 total. Replaces
    # the prior triple-count (direct +0.30 boost AND +0.40 inside school
    # index AND +0.20 from school index breaching 0.7) flagged in review H1.
    # Only fires when local population immunity is also inadequate
    # (MMR < 95%); a strong-immunity county does not get the boost.
    outbreak_boost = 0.0
    if outbreak_conditions['below_measles_threshold']:
        if active_local_transmission:
            outbreak_boost = 0.30   # acute local community spread
        elif import_pressure_elevated:
            outbreak_boost = 0.15   # sustained import pressure (not local spread)
        elif ytd_elevated:
            outbreak_boost = 0.10   # year-level elevated incidence only
    outbreak_boost = min(0.30, outbreak_boost)

    # === ADDITIONAL OUTBREAK FLAGS (v1 Shape A: H5N1, mpox, enteric, legionella)
    # Lightweight statewide outbreak flags that nudge the infectious_disease
    # Acute signal. Each flag fetcher is cache-only-safe (see
    # utils/request_context.py); live HTTP is performed exclusively by the
    # corresponding scheduler jobs in utils/data_source_refresher.py.
    #
    # Stacking rule (per design decision #1): one big outbreak still
    # dominates, but concurrent smaller signals are visible:
    #   stacked = min(0.40, max_individual + 0.05 * (other_active_flag_count))
    #
    # Isolated to infectious_disease (design decision #5); these flags do
    # NOT cross-contaminate active_shooter, natural_hazards, or any other
    # domain.
    #
    # Granularity: all v1 flags are statewide Wisconsin (design decision
    # #2). The dashboard partial templates/dashboard/_active_surveillance_flags.html
    # surfaces a "WI statewide" badge on every row.
    try:
        from utils.h5n1_surveillance import get_h5n1_outbreak_flags
        from utils.mpox_surveillance import get_mpox_outbreak_flags
        from utils.nndss_enteric import (
            get_enteric_outbreak_flags,
            get_legionella_outbreak_flags,
        )
        h5n1_flags = get_h5n1_outbreak_flags()
        mpox_flags = get_mpox_outbreak_flags()
        enteric_flags = get_enteric_outbreak_flags()
        legionella_flags = get_legionella_outbreak_flags()
    except Exception as exc:
        logger.warning(
            f"v1 outbreak flags unavailable, defaulting to none: {exc}"
        )
        _empty = lambda src: {
            'tier': 'none', 'boost': 0.0, 'active': False,
            'source': 'unavailable', 'source_label': src,
            'detail': 'Flag module unavailable', 'signal_scope': 'statewide_wisconsin',
            'last_updated': None,
        }
        h5n1_flags = _empty('USDA APHIS HPAI')
        mpox_flags = {**_empty('CDC Mpox surveillance'), 'tier': 'baseline'}
        enteric_flags = {**_empty('CDC NNDSS enteric subset'), 'agents_elevated': [], 'agents': {}}
        legionella_flags = _empty('CDC NNDSS Legionellosis')

    # Surface the new flags on outbreak_conditions for templates / downstream.
    outbreak_conditions['h5n1'] = h5n1_flags
    outbreak_conditions['mpox'] = mpox_flags
    outbreak_conditions['enteric'] = enteric_flags
    outbreak_conditions['legionella'] = legionella_flags

    # Compute the stacked outbreak boost. The measles outbreak_boost above
    # is already gated by below_measles_threshold; we feed it into the
    # stack as the measles contribution.
    _flag_boosts = [
        ('measles', outbreak_boost),
        ('h5n1', float(h5n1_flags.get('boost', 0.0) or 0.0)),
        ('mpox', float(mpox_flags.get('boost', 0.0) or 0.0)),
        ('enteric', float(enteric_flags.get('boost', 0.0) or 0.0)),
        ('legionella', float(legionella_flags.get('boost', 0.0) or 0.0)),
    ]
    _active = [(name, b) for name, b in _flag_boosts if b > 0]
    if _active:
        _max_b = max(b for _, b in _active)
        _others = len(_active) - 1
        stacked_outbreak_boost = min(0.40, _max_b + 0.05 * _others)
    else:
        stacked_outbreak_boost = 0.0
    outbreak_conditions['stacked_outbreak_boost'] = stacked_outbreak_boost
    outbreak_conditions['active_flag_count'] = len(_active)
    outbreak_conditions['active_flag_names'] = [n for n, _ in _active]

    # Apply the stacked boost in place of the measles-only boost.
    base_multiplier += stacked_outbreak_boost

    # School vulnerability emergency adjustment (pure undervaccination
    # signal; no longer compounds with the outbreak boost above).
    if school_vulnerability_score > 0.7:
        base_multiplier += 0.2

    # Multiple simultaneous gaps create compounding risk
    if outbreak_conditions['multiple_gaps']:
        base_multiplier += 0.15

    # Cap the multiplier to prevent extreme values
    risk_multiplier = min(2.0, max(0.7, base_multiplier))

    # === POLICY DECISION INDICATORS ===
    policy_flags = []

    if gaps['mmr_gap'] > 3.0:
        policy_flags.append({
            'level': 'HIGH_PRIORITY',
            'issue': 'MMR vaccination below herd immunity threshold',
            'gap': f"{gaps['mmr_gap']:.1f} percentage points below 95% threshold",
            'action_needed': 'Immediate school-based vaccination campaigns'
        })

    # Policy flags now reflect the granular CSTE-aligned classification.
    # Only true active local transmission warrants EMERGENCY language;
    # import pressure and YTD elevated incidence are operationally
    # distinct and surface at lower priority levels. Wording and
    # severity are also gated by below_measles_threshold so that a
    # county at or above 95% MMR is not described as having inadequate
    # immunity (keeps policy text consistent with the multiplier
    # pathway, which only fires when immunity is also inadequate).
    below_threshold = outbreak_conditions['below_measles_threshold']
    if active_local_transmission:
        if below_threshold:
            policy_flags.append({
                'level': 'EMERGENCY',
                'issue': 'Active local measles transmission in Wisconsin with inadequate local population immunity',
                'gap': f"Population immunity at {mmr_rate:.1f}%, need 95% for control",
                'action_needed': 'Emergency vaccination orders, school exclusion policies',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, indigenous case in last 4 weeks)',
            })
        else:
            policy_flags.append({
                'level': 'HIGH_PRIORITY',
                'issue': 'Active local measles transmission in Wisconsin (local immunity meets the 95% threshold)',
                'gap': f"Population immunity at {mmr_rate:.1f}%; threshold met but active spread observed",
                'action_needed': 'Targeted contact tracing, ring vaccination, monitor for community spread',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, indigenous case in last 4 weeks)',
            })
    elif import_pressure_elevated:
        if below_threshold:
            policy_flags.append({
                'level': 'HIGH_PRIORITY',
                'issue': 'Elevated measles import pressure in Wisconsin with inadequate local population immunity (no current local transmission)',
                'gap': f"Population immunity at {mmr_rate:.1f}%, need 95% to prevent spread from imports",
                'action_needed': 'Heightened surveillance, traveler screening, school MMR catch-up campaigns',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, >2 imported cases in last 4 weeks)',
            })
        else:
            policy_flags.append({
                'level': 'MEDIUM_PRIORITY',
                'issue': 'Elevated measles import pressure in Wisconsin (no current local transmission)',
                'gap': f"Population immunity at {mmr_rate:.1f}% (threshold met); maintain vigilance",
                'action_needed': 'Heightened surveillance and traveler screening',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, >2 imported cases in last 4 weeks)',
            })
    elif ytd_elevated:
        if below_threshold:
            policy_flags.append({
                'level': 'MEDIUM_PRIORITY',
                'issue': 'Year-to-date measles incidence elevated vs prior year with inadequate local population immunity (no active local transmission)',
                'gap': f"Population immunity at {mmr_rate:.1f}%, need 95% to maintain control",
                'action_needed': 'Maintain enhanced surveillance, target catch-up vaccination',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, YTD indigenous cases >= prior YTD)',
            })
        else:
            policy_flags.append({
                'level': 'SEASONAL_PRIORITY',
                'issue': 'Year-to-date measles incidence elevated vs prior year (no active local transmission)',
                'gap': f"Population immunity at {mmr_rate:.1f}% (threshold met)",
                'action_needed': 'Continue routine surveillance',
                'signal_scope': 'statewide_wisconsin (CDC NNDSS, YTD indigenous cases >= prior YTD)',
            })

    if school_vulnerability_score > 0.6:
        policy_flags.append({
            'level': 'MEDIUM_PRIORITY', 
            'issue': 'School vaccination compliance below protective levels',
            'gap': f"School compliance at {school_compliance}%, target 90%+",
            'action_needed': 'Enhanced school entry requirements, compliance monitoring'
        })
    
    if gaps['flu_gap'] > 10.0:
        policy_flags.append({
            'level': 'SEASONAL_PRIORITY',
            'issue': 'Influenza vaccination below community protection threshold',
            'gap': f"{gaps['flu_gap']:.1f} percentage points below 70% threshold", 
            'action_needed': 'Targeted flu vaccination campaigns for vulnerable populations'
        })
    
    return {
        'risk_multiplier': risk_multiplier,
        'herd_immunity_gaps': gaps,
        'outbreak_conditions': outbreak_conditions,
        'school_vulnerability_score': school_vulnerability_score,
        'policy_decision_flags': policy_flags,
        'strategic_priority': _determine_strategic_priority(policy_flags),
        'framework_type': 'strategic_vaccination_risk_v2.2',
    }

def _calculate_school_vulnerability_index(mmr_rate: float, school_compliance: float) -> float:
    """Calculate school-specific vulnerability to disease outbreaks.

    Pure structural undervaccination signal: a function of MMR coverage
    and school-entry compliance only. Intentionally does NOT take the
    live outbreak flag as input. The outbreak signal is applied to the
    risk multiplier directly by the caller; folding it in here as well
    caused the same statewide flag to be counted three times in the
    final multiplier (see review finding H1).
    """

    # Base vulnerability from vaccination gaps
    base_vulnerability = 0.0

    # MMR gap creates direct vulnerability (measles spreads rapidly in schools)
    if mmr_rate < 95.0:
        mmr_vulnerability = (95.0 - mmr_rate) / 95.0  # Normalized gap
        base_vulnerability += mmr_vulnerability * 0.6  # 60% weight for MMR gap

    # School compliance gap indicates systemic issues
    if school_compliance < 90.0:
        compliance_vulnerability = (90.0 - school_compliance) / 90.0
        base_vulnerability += compliance_vulnerability * 0.3  # 30% weight for compliance

    # Age-based transmission amplification (schools have higher transmission)
    school_amplification_factor = 1.2

    final_vulnerability = min(1.0, base_vulnerability * school_amplification_factor)
    return final_vulnerability

def _determine_strategic_priority(policy_flags: List[Dict[str, str]]) -> str:
    """Determine overall strategic priority based on policy flags"""
    
    if any(flag['level'] == 'EMERGENCY' for flag in policy_flags):
        return 'EMERGENCY_RESPONSE_REQUIRED'
    elif any(flag['level'] == 'HIGH_PRIORITY' for flag in policy_flags):
        return 'HIGH_PRIORITY_INTERVENTION'
    elif any(flag['level'] == 'MEDIUM_PRIORITY' for flag in policy_flags):
        return 'TARGETED_IMPROVEMENTS_NEEDED'
    elif any(flag['level'] == 'SEASONAL_PRIORITY' for flag in policy_flags):
        return 'SEASONAL_PLANNING_FOCUS'
    else:
        return 'MAINTENANCE_MONITORING'

def _get_fallback_vaccination_risk_assessment() -> Dict[str, Any]:
    """Fallback assessment when vaccination data is unavailable"""
    return {
        'risk_multiplier': 1.2,
        'herd_immunity_gaps': {
            'mmr_gap': 7.2,
            'flu_gap': 17.9,
            'school_compliance_gap': 3.6,
        },
        'outbreak_conditions': {
            'active_measles_outbreak': False,
            'active_local_transmission': False,
            'import_pressure_elevated': False,
            'ytd_elevated': False,
            'outbreak_signal_scope': 'statewide_wisconsin',
            'outbreak_signal_source': 'unavailable',
            'below_measles_threshold': True,
            'school_vulnerability': True,
            'multiple_gaps': True,
        },
        'school_vulnerability_score': 0.55,
        'policy_decision_flags': [{
            'level': 'HIGH_PRIORITY',
            'issue': 'Vaccination surveillance data unavailable',
            'gap': 'Data gaps compromise outbreak response planning',
            'action_needed': 'Restore vaccination surveillance data connection'
        }],
        'strategic_priority': 'HIGH_PRIORITY_INTERVENTION',
        'framework_type': 'strategic_vaccination_risk_v2.2_fallback',
    }

def _calculate_vaccination_protection(vaccination_data: Dict[str, Any], county_name: str) -> float:
    """
    Calculate vaccination protection factor (0.0-1.0) based on vaccination rates
    
    Args:
        vaccination_data: Vaccination data from Wisconsin DHS
        county_name: County name for potential county-specific adjustments
        
    Returns:
        Protection factor (0.0 = no protection, 1.0 = maximum protection)
    """
    if not vaccination_data:
        return 0.3  # Default moderate protection when data unavailable
    
    # Extract vaccination rates
    flu_vaccination = vaccination_data.get('flu_vaccination', {})
    mmr_vaccination = vaccination_data.get('mmr_vaccination', {})
    school_vaccination = vaccination_data.get('school_vaccination', {})
    
    # Calculate weighted protection scores (flu 40%, MMR 30%, school compliance 30%)
    # COVID-19 vaccination removed: no reliable county-level current data source;
    # SARS-CoV-2 immune escape has invalidated fixed herd-immunity thresholds.
    protection_scores = []
    
    # Flu vaccination (current season relevance) - 40%
    flu_rate = flu_vaccination.get('overall_population', 52.1) / 100.0
    protection_scores.append(flu_rate * 0.4)
    
    # MMR vaccination (community immunity) - 30%
    mmr_rate = mmr_vaccination.get('children_5_18_years', 87.8) / 100.0
    protection_scores.append(mmr_rate * 0.3)
    
    # School vaccination compliance (overall herd immunity) - 30%
    school_rate = school_vaccination.get('meeting_minimum_requirements', 86.4) / 100.0
    protection_scores.append(school_rate * 0.3)
    
    # Calculate overall protection factor
    overall_protection = sum(protection_scores)
    
    # Apply county adjustments for urban vs rural vaccination patterns
    county_adjustment = _get_county_vaccination_adjustment(county_name)
    adjusted_protection = overall_protection * county_adjustment
    
    # Ensure protection factor stays within bounds
    return max(0.0, min(1.0, adjusted_protection))

def _get_county_vaccination_adjustment(county_name: str) -> float:
    """Get county-specific vaccination adjustment factor"""
    # Urban counties typically have higher vaccination rates
    urban_counties = [
        'milwaukee', 'dane', 'brown', 'racine', 'kenosha',
        'rock', 'winnebago', 'waukesha', 'outagamie'
    ]
    
    # Rural counties may have lower vaccination rates
    rural_counties = [
        'forest', 'florence', 'iron', 'vilas', 'oneida',
        'lincoln', 'langlade', 'menominee', 'taylor'
    ]
    
    county_key = county_name.lower().replace(' ', '_').replace('county', '').strip()
    
    if county_key in urban_counties:
        return 1.05  # 5% higher vaccination rates in urban areas
    elif county_key in rural_counties:
        return 0.95  # 5% lower vaccination rates in rural areas
    else:
        return 1.0   # Default for other counties

def _get_activity_level(score: float) -> str:
    """Convert a 0-1 score to an activity level string"""
    if score >= 0.6:
        return "high"
    elif score >= 0.3:
        return "moderate"
    else:
        return "low"

def _determine_overall_trend(trends: List[str]) -> str:
    """Determine overall trend from multiple trend indicators"""
    trend_counts = {
        'increasing': 0,
        'stable': 0,
        'decreasing': 0
    }
    
    for trend in trends:
        if trend in trend_counts:
            trend_counts[trend] += 1
    
    # Return the most common trend, defaulting to stable in case of ties
    if trend_counts['increasing'] > trend_counts['stable'] and trend_counts['increasing'] > trend_counts['decreasing']:
        return 'increasing'
    elif trend_counts['decreasing'] > trend_counts['stable'] and trend_counts['decreasing'] > trend_counts['increasing']:
        return 'decreasing'
    else:
        return 'stable'

def get_disease_activity(jurisdiction_id: str, disease_type: str) -> Dict[str, Any]:
    """
    Get disease activity data for a specific jurisdiction and disease type.
    
    Args:
        jurisdiction_id: The jurisdiction ID
        disease_type: The type of disease (flu, covid, rsv, etc.)
        
    Returns:
        Disease activity data dictionary
    """
    # Generate cache key
    cache_key = f"{DISEASE_CACHE_PREFIX}{disease_type}_{jurisdiction_id}"
    
    # Try memory cache first
    cached_data = get_from_memory_cache(cache_key)
    if cached_data:
        logger.debug(f"Retrieved {disease_type} data for {jurisdiction_id} from memory cache")
        return cached_data
    
    # Try persistent cache next
    cached_data = get_from_persistent_cache(cache_key, max_age_days=DISEASE_CACHE_EXPIRY)
    if cached_data:
        # Store in memory cache for faster access next time
        set_in_memory_cache(cache_key, cached_data)
        logger.debug(f"Retrieved {disease_type} data for {jurisdiction_id} from persistent cache")
        return cached_data
    
    # If not in cache, fetch from data source
    try:
        # Fetch real disease activity data from DHS for Wisconsin counties
        from utils.dhs_data import get_county_disease_data
        
        # Get county name from jurisdiction ID
        from utils.data_processor import get_county_for_jurisdiction
        county_name = get_county_for_jurisdiction(jurisdiction_id)
        
        if not county_name:
            county_name = "Milwaukee"  # Fallback to a major county if we can't determine the county
            logger.warning(f"Could not determine county for jurisdiction {jurisdiction_id}, using {county_name}")
        
        # Get disease activity data for the county
        dhs_data = get_county_disease_data(county_name, disease_type)
        
        # Format activity data
        activity_data = {
            'jurisdiction_id': jurisdiction_id,
            'disease_type': disease_type,
            'activity_level': dhs_data.get('activity_level', 'moderate'),
            'cases_per_100k': dhs_data.get('cases_per_100k', 20.0),
            'trend': dhs_data.get('trend', 'stable'),
            'last_updated': dhs_data.get('last_updated', datetime.now().isoformat()),
            'source': 'Wisconsin DHS Disease Surveillance',
            'data_quality': dhs_data.get('data_quality', 'high')
        }
        
        # Cache the data
        set_in_memory_cache(cache_key, activity_data)
        set_in_persistent_cache(cache_key, activity_data, expiry_days=DISEASE_CACHE_EXPIRY)
        
        logger.info(f"Fetched new {disease_type} data for {jurisdiction_id}")
        return activity_data
    except Exception as e:
        logger.error(f"Error fetching {disease_type} data for {jurisdiction_id}: {str(e)}")
        return {
            'jurisdiction_id': jurisdiction_id,
            'disease_type': disease_type,
            'activity_level': 'unknown',
            'error': str(e),
        }

def calculate_infectious_disease_risk(jurisdiction_id: str) -> Dict[str, Any]:
    """
    Calculate infectious disease risk for dashboard integration
    
    This function integrates the enhanced strategic vaccination risk framework
    with the existing dashboard pipeline.
    """
    # Get the county name from jurisdiction ID  
    from utils.data_processor import get_county_for_jurisdiction
    county_name = get_county_for_jurisdiction(jurisdiction_id)
    
    if not county_name:
        county_name = "Milwaukee"  # Fallback
    
    # Use the enhanced disease metrics with strategic vaccination framework
    enhanced_metrics = get_disease_metrics(county_name)
    
    # Return in the format expected by data_processor
    return enhanced_metrics

def get_disease_risk_score(jurisdiction_id: str) -> Dict[str, Any]:
    """
    Calculate overall infectious disease risk score for a jurisdiction
    based on current disease activity.
    
    Risk is calculated using:  
    - ILI Activity (30%)
    - COVID-19 Activity (30%)
    - RSV Activity (20%)
    - Vaccination Rate (20%)
    
    Args:
        jurisdiction_id: The jurisdiction ID
        
    Returns:
        Dictionary with risk scores and component data
    """
    try:
        # Get activity data for different disease types
        flu_data = get_disease_activity(jurisdiction_id, 'flu')
        covid_data = get_disease_activity(jurisdiction_id, 'covid')
        rsv_data = get_disease_activity(jurisdiction_id, 'rsv')
        
        # Calculate risk components based on real data
        # Convert cases_per_100k to a risk value between 0-1
        # Lower risk: <10 cases per 100k, Higher risk: >50 cases per 100k
        def calculate_risk_from_cases(data):
            cases = data.get('cases_per_100k', 25.0)
            # Apply a sigmoid function to normalize between 0 and 1
            # This gives a smooth transition between low and high risk
            import math
            normalized = 1.0 / (1.0 + math.exp(-0.05 * (cases - 30)))
            return max(0.1, min(0.9, normalized))  # Ensure value stays in reasonable range
        
        # Apply risk calculation to each disease type
        flu_risk = calculate_risk_from_cases(flu_data)
        covid_risk = calculate_risk_from_cases(covid_data)
        rsv_risk = calculate_risk_from_cases(rsv_data)
        
        # Get vaccination data from dhs_data module
        from utils.dhs_data import get_vaccination_rate
        county_name = get_county_for_jurisdiction(jurisdiction_id)
        
        # Handle case where county mapping is not found
        if not county_name:
            county_name = "Milwaukee"  # Default to a major county
            logger.warning(f"Could not determine county for vaccination data {jurisdiction_id}, using {county_name}")
            
        vax_rate = get_vaccination_rate(county_name)
        
        # Lower vaccination rates correspond to higher risk
        vaccination_risk = max(0.1, min(0.9, 1.0 - (vax_rate / 100.0)))
        
        # Calculate exposure, vulnerability, and resilience components for standardized risk formula

        # Exposure: Disease activity levels (higher activity = higher exposure)
        exposure_score = (flu_risk * 0.4) + (covid_risk * 0.4) + (rsv_risk * 0.2)

        # --- Vulnerability: vaccination gap + COPD respiratory burden ---
        # Base: MMR vaccination gap (primary driver)
        base_vulnerability = vaccination_risk

        # COPD modifier: counties with high COPD have more severe respiratory outcomes.
        # WI range: 4.1% (Waukesha) to 10.2% (Forest). Adds up to +0.15 vulnerability.
        try:
            from utils.health_metrics_data import get_copd_prevalence
            copd_pct = get_copd_prevalence(county_name) or 7.0
        except Exception:
            copd_pct = 7.0
        copd_normalized = max(0.0, min(1.0, (copd_pct - 4.0) / 6.5))
        copd_vulnerability_add = copd_normalized * 0.15

        vulnerability_score = min(0.9, base_vulnerability + copd_vulnerability_add)

        # --- Resilience: vaccination protection + primary care access ---
        # Base: inverse of vaccination gap
        base_resilience = 1.0 - vaccination_risk

        # Primary care modifier: counties with very low physician density cannot
        # manage outbreak surge. WI range: 9.6/100k (Adams) to 173.8/100k (Ashland).
        # Adds up to +0.15 resilience for counties at or above 100/100k.
        try:
            from utils.health_metrics_data import get_primary_care_access
            pc_per_100k = get_primary_care_access(county_name) or 65.0
        except Exception:
            pc_per_100k = 65.0
        pc_normalized = min(1.0, pc_per_100k / 100.0)
        pc_resilience_add = pc_normalized * 0.15

        resilience_score = max(0.1, base_resilience + pc_resilience_add)
        
        # Apply the corrected standardized risk formula
        from utils.risk_calculation import calculate_residual_risk
        overall_risk = calculate_residual_risk(
            exposure=exposure_score,
            vulnerability=vulnerability_score,
            resilience=resilience_score,
            health_impact_factor=1.5  # Infectious disease has maximum health impacts
        )
        
        # Prepare result
        result = {
            'overall_risk': overall_risk,
            'components': {
                'flu': {
                    'risk': flu_risk,
                    'activity_level': flu_data.get('activity_level', 'unknown'),
                    'trend': flu_data.get('trend', 'unknown'),
                },
                'covid': {
                    'risk': covid_risk,
                    'activity_level': covid_data.get('activity_level', 'unknown'),
                    'trend': covid_data.get('trend', 'unknown'),
                },
                'rsv': {
                    'risk': rsv_risk,
                    'activity_level': rsv_data.get('activity_level', 'unknown'),
                    'trend': rsv_data.get('trend', 'unknown'),
                },
                'vaccination': {
                    'risk': vaccination_risk,
                    'coverage': '65%',  # Example value
                },
            },
            'last_updated': datetime.now().isoformat(),
        }
        
        return result
    except Exception as e:
        logger.error(f"Error calculating disease risk for {jurisdiction_id}: {str(e)}")
        # Return fallback with error information
        return {
            'overall_risk': 0.5,  # Moderate default
            'error': str(e),
            'last_updated': datetime.now().isoformat(),
        }

def clear_disease_cache() -> Tuple[int, int]:
    """
    Clear all disease surveillance caches (both in-memory and persistent)
    
    Returns:
        Tuple of (memory_cache_count, persistent_cache_count) entries cleared
    """
    # Clear memory cache
    memory_count = 0
    keys_to_remove = []
    
    for key in _disease_activity_cache:
        if key.startswith(DISEASE_CACHE_PREFIX):
            keys_to_remove.append(key)
            memory_count += 1
    
    for key in keys_to_remove:
        remove_from_memory_cache(key)
    
    # Clear persistent cache
    persistent_count = clear_cache_by_prefix(DISEASE_CACHE_PREFIX)
    
    logger.info(f"Cleared disease surveillance caches: {memory_count} in-memory, {persistent_count} persistent")
    return memory_count, persistent_count
