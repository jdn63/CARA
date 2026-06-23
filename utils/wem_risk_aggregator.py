"""
WEM (Wisconsin Emergency Management) Risk Aggregation Module

Mirrors utils/herc_risk_aggregator.py but rolls risk up to the 6 WEM
regions and uses the Emergency Management discipline weights from
config/risk_weights.yaml (em_overall_risk_weights, em_natural_hazards_*).

Aggregation is two-stage county mean (within-county then across-county),
matching the HERC pattern so a county with multiple local health
departments does not over-weight the regional rollup.

Phase 1 caveats:
- In-memory cache only (no HERCRiskCache-style DB cache yet). A WEM
  dashboard cold-load triggers process_risk_data() for every jurisdiction
  in the region under cache_only_context, so the cost is bounded by
  whatever is already cached in the per-domain on-disk stores.
- Discipline is hard-coded to 'em' here; calling code that wants Public
  Health rollups uses the existing HERC aggregator. The cache key is
  scoped per-discipline so this module never shares cells with HERC.
"""

import logging
import time
from collections import defaultdict
from math import isfinite
from statistics import mean
from typing import Any, Dict, List, Optional

from utils.jurisdictions_code import jurisdictions
from utils.jurisdiction_mapping_code import jurisdiction_mapping
from utils.wem_data import get_all_wem_regions
from utils.data_processor import process_risk_data
from utils.config_manager import get_config_manager
from utils.regional_aggregation import (
    aggregate_detail_blocks,
    build_regional_provenance,
    build_regional_data_quality,
    UTILITIES_SUBKEYS,
)

logger = logging.getLogger(__name__)

_DISCIPLINE = 'em'

# (jurisdiction_id, discipline) -> cached risk dict (with _cached_at)
_jurisdiction_cache: Dict[str, Dict[str, Any]] = {}
_JURISDICTION_TTL = 1800  # 30 min
_JURISDICTION_MAX = 150

# wem_id -> cached aggregate (with _cached_at)
_wem_cache: Dict[str, Dict[str, Any]] = {}
_WEM_TTL = 3600  # 1 hour
_WEM_MAX = 10  # only 7 regions


def _jcache_key(jurisdiction_id: str) -> str:
    return f"{_DISCIPLINE}:{jurisdiction_id}"


def _evict_oldest(cache: Dict[str, Any], max_size: int) -> None:
    if len(cache) >= max_size:
        oldest = min(cache, key=lambda k: cache[k].get('_cached_at', 0))
        del cache[oldest]


def _get_cached_jurisdiction(jurisdiction_id: str) -> Optional[Dict[str, Any]]:
    entry = _jurisdiction_cache.get(_jcache_key(jurisdiction_id))
    if entry and time.time() - entry.get('_cached_at', 0) < _JURISDICTION_TTL:
        return entry
    return None


def _cache_jurisdiction(jurisdiction_id: str, payload: Dict[str, Any]) -> None:
    _evict_oldest(_jurisdiction_cache, _JURISDICTION_MAX)
    payload['_cached_at'] = time.time()
    _jurisdiction_cache[_jcache_key(jurisdiction_id)] = payload


class WEMRiskAggregator:
    """Roll constituent jurisdiction risk up to the 6 WEM regions under EM weights."""

    def __init__(self):
        self.wem_regions = get_all_wem_regions()

    def get_jurisdictions_for_wem_region(self, wem_id: str) -> List[Dict[str, Any]]:
        region = next((r for r in self.wem_regions if r.get('id') == wem_id), None)
        if not region:
            logger.error(f"WEM region not found: {wem_id}")
            return []
        counties = set(region.get('counties', []))
        out: List[Dict[str, Any]] = []
        for j in jurisdictions:
            county = jurisdiction_mapping.get(j['id'])
            if county in counties:
                out.append(j)
        logger.info(
            f"WEM region {wem_id} ({region.get('name')}): {len(out)} jurisdictions "
            f"across {len(counties)} counties"
        )
        return out

    def calculate_wem_region_risk(self, wem_id: str) -> Optional[Dict[str, Any]]:
        try:
            cached = _wem_cache.get(wem_id)
            if cached and time.time() - cached.get('_cached_at', 0) < _WEM_TTL:
                logger.info(f"Returning cached WEM risk data for region {wem_id}")
                return cached

            region = next((r for r in self.wem_regions if r.get('id') == wem_id), None)
            if not region:
                return None

            region_jurisdictions = self.get_jurisdictions_for_wem_region(wem_id)
            if not region_jurisdictions:
                logger.warning(f"No jurisdictions in WEM region {wem_id}")
                return None

            DOMAINS = (
                'natural_hazards', 'health_metrics', 'active_shooter',
                'extreme_heat', 'air_quality', 'cybersecurity',
                'utilities', 'dam_failure', 'vector_borne_disease',
                'infectious_disease',
                'hazmat_industrial', 'hazmat_agricultural',
            )
            NH_COMPONENTS = ('flood', 'tornado', 'winter_storm', 'thunderstorm', 'straight_line_wind')
            TEMPORAL_HAZARDS = (
                'flood', 'tornado', 'winter_storm', 'extreme_heat',
                'thunderstorm', 'health', 'active_shooter',
            )
            TEMPORAL_COMPONENTS = ('baseline', 'seasonal', 'trend', 'acute')

            domain_by_county: Dict[str, Dict[str, List[float]]] = defaultdict(
                lambda: defaultdict(list)
            )
            nh_by_county: Dict[str, Dict[str, List[float]]] = defaultdict(
                lambda: defaultdict(list)
            )
            temporal_by_county: Dict[str, Dict[str, Dict[str, List[float]]]] = defaultdict(
                lambda: defaultdict(
                    lambda: {k: [] for k in ('composite_scores',) + TEMPORAL_COMPONENTS}
                )
            )
            total_by_county: Dict[str, List[float]] = defaultdict(list)
            # county -> list of full per-jurisdiction risk_data dicts, used by
            # the shared regional-aggregation core to roll up the detail
            # blocks (components, metrics, provenance, freshness).
            risk_by_county: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
            successful = 0

            for j in region_jurisdictions:
                try:
                    jid = j['id']
                    county = (
                        jurisdiction_mapping.get(jid) or j.get('county') or jid
                    )
                    cached_j = _get_cached_jurisdiction(jid)
                    if cached_j:
                        risk_data = cached_j['risk_data']
                        domain_scores = cached_j['domain_scores']
                    else:
                        # EM discipline -- this is the only meaningful difference
                        # from the HERC aggregator. process_risk_data() enters
                        # cache_only_context() internally, so no live HTTP fires.
                        risk_data = process_risk_data(jid, discipline=_DISCIPLINE)
                        domain_scores = {
                            # No 0.0 defaults: an absent domain stays absent
                            # (None) so it is excluded from the regional
                            # composite and weight renormalization rather than
                            # being coerced into a fabricated zero.
                            'natural_hazards': risk_data.get('natural_hazards_risk'),
                            'health_metrics': risk_data.get('health_risk'),
                            'active_shooter': risk_data.get('active_shooter_risk'),
                            'extreme_heat': risk_data.get('extreme_heat_risk'),
                            'air_quality': risk_data.get('air_quality_risk'),
                            'cybersecurity': risk_data.get('cybersecurity_risk'),
                            'utilities': (risk_data.get('utilities') or {}).get('overall'),
                            'dam_failure': risk_data.get('dam_failure_risk'),
                            'vector_borne_disease': risk_data.get('vector_borne_disease_risk'),
                            # infectious_disease at the jurisdiction level is the
                            # same signal as health_risk (acute infectious-disease
                            # composite score). It is given a separate, smaller
                            # weight in EM mode -- see em_overall_risk_weights.
                            'infectious_disease': risk_data.get('health_risk'),
                            'hazmat_industrial': risk_data.get('hazmat_industrial_risk'),
                            'hazmat_agricultural': risk_data.get('hazmat_agricultural_risk'),
                        }
                        _cache_jurisdiction(jid, {
                            'risk_data': risk_data,
                            'domain_scores': domain_scores,
                        })

                    for d in DOMAINS:
                        domain_by_county[county][d].append(domain_scores.get(d))

                    nh_detail = risk_data.get('natural_hazards', {}) or {}
                    for comp in NH_COMPONENTS:
                        nh_by_county[county][comp].append(nh_detail.get(comp, 0.0))

                    temporal_detail = risk_data.get('temporal_risk_detail', {}) or {}
                    for hz in TEMPORAL_HAZARDS:
                        hd = temporal_detail.get(hz)
                        if isinstance(hd, dict):
                            bucket = temporal_by_county[county][hz]
                            bucket['composite_scores'].append(
                                hd.get('composite_score', 0.0)
                            )
                            comps = hd.get('temporal_components', {}) or {}
                            for ck in TEMPORAL_COMPONENTS:
                                bucket[ck].append(comps.get(ck, 0.0))

                    total_by_county[county].append(risk_data.get('total_risk_score', 0.0))
                    risk_by_county[county].append(risk_data)
                    successful += 1

                except Exception as e:
                    logger.warning(
                        f"Failed EM risk calc for jurisdiction {j.get('id')}: {e}"
                    )
                    continue

            if successful == 0:
                logger.error(f"No successful EM calculations for WEM region {wem_id}")
                return None

            def _two_stage(by_county: Dict[str, Dict[str, List[float]]], key: str):
                """Within-county mean, then across-county mean.

                Only real, finite values are counted; ``None``/NaN/inf samples
                are skipped so a missing domain is never coerced into a
                fabricated 0.0. Returns ``None`` when no county has any real
                value for the key, so the provenance builder excludes it from
                the composite and from weight renormalization (matching the
                per-jurisdiction ``_domain_available`` rule).
                """
                county_means = []
                for _c, dmap in by_county.items():
                    vals = [
                        v for v in (dmap.get(key) or [])
                        if isinstance(v, (int, float))
                        and not isinstance(v, bool)
                        and isfinite(v)
                    ]
                    if vals:
                        county_means.append(mean(vals))
                return mean(county_means) if county_means else None

            natural_hazards_avg = _two_stage(domain_by_county, 'natural_hazards')
            health_avg = _two_stage(domain_by_county, 'health_metrics')
            active_shooter_avg = _two_stage(domain_by_county, 'active_shooter')
            extreme_heat_avg = _two_stage(domain_by_county, 'extreme_heat')
            air_quality_avg = _two_stage(domain_by_county, 'air_quality')
            cybersecurity_avg = _two_stage(domain_by_county, 'cybersecurity')
            utilities_avg = _two_stage(domain_by_county, 'utilities')
            dam_failure_avg = _two_stage(domain_by_county, 'dam_failure')
            vbd_avg = _two_stage(domain_by_county, 'vector_borne_disease')
            infectious_disease_avg = _two_stage(domain_by_county, 'infectious_disease')
            hazmat_industrial_avg = _two_stage(domain_by_county, 'hazmat_industrial')
            hazmat_agricultural_avg = _two_stage(domain_by_county, 'hazmat_agricultural')

            flood_avg = _two_stage(nh_by_county, 'flood')
            tornado_avg = _two_stage(nh_by_county, 'tornado')
            winter_storm_avg = _two_stage(nh_by_county, 'winter_storm')
            thunderstorm_avg = _two_stage(nh_by_county, 'thunderstorm')
            straight_line_wind_avg = _two_stage(nh_by_county, 'straight_line_wind')

            unique_counties_count = len(domain_by_county)

            # EM weighted linear sum -- uses em_overall_risk_weights from
            # config/risk_weights.yaml. Mirrors HERC aggregator's linear
            # sum (note: jurisdiction-level PHRAT quadratic mean is in
            # data_processor.py; rollups use the simpler linear sum).
            cfg = get_config_manager()
            em_weights = cfg.get_em_overall_weights() if hasattr(
                cfg, 'get_em_overall_weights'
            ) else None
            if not em_weights:
                # Fallback: read directly from YAML block we know exists.
                import yaml
                try:
                    with open('config/risk_weights.yaml') as f:
                        em_weights = yaml.safe_load(f).get('em_overall_risk_weights', {})
                except Exception:
                    em_weights = {}

            # Only domains that carry real data participate; weights are
            # renormalized over that surviving set so an unavailable domain is
            # excluded rather than coerced to a fabricated 0.0. This mirrors
            # build_regional_provenance, which is the authoritative total.
            _em_domain_scores = {
                'natural_hazards': natural_hazards_avg,
                'health_metrics': health_avg,
                'active_shooter': active_shooter_avg,
                'extreme_heat': extreme_heat_avg,
                'air_quality': air_quality_avg,
                'utilities': utilities_avg,
                'dam_failure': dam_failure_avg,
                'vector_borne_disease': vbd_avg,
                'infectious_disease': infectious_disease_avg,
                'hazmat_industrial': hazmat_industrial_avg,
                'hazmat_agricultural': hazmat_agricultural_avg,
            }
            _em_defaults = {
                'natural_hazards': 0.32, 'health_metrics': 0.10,
                'active_shooter': 0.13, 'extreme_heat': 0.13,
                'air_quality': 0.08, 'utilities': 0.10, 'dam_failure': 0.08,
                'vector_borne_disease': 0.06, 'infectious_disease': 0.05,
                'hazmat_industrial': 0.03, 'hazmat_agricultural': 0.03,
            }

            def _avail_score(v):
                return (
                    isinstance(v, (int, float))
                    and not isinstance(v, bool)
                    and isfinite(v)
                )

            _present_weight = sum(
                em_weights.get(k, _em_defaults[k])
                for k, score in _em_domain_scores.items()
                if _avail_score(score)
            )
            total_risk = (
                sum(
                    em_weights.get(k, _em_defaults[k]) * score
                    for k, score in _em_domain_scores.items()
                    if _avail_score(score)
                ) / _present_weight
            ) if _present_weight > 0 else 0.0

            aggregated = {
                'wem_id': wem_id,
                'herc_id': wem_id,  # alias so the shared region template can use risk_data.herc_id
                'name': region.get('name'),
                'counties': region.get('counties', []),
                'jurisdiction_count': len(region_jurisdictions),
                'unique_counties_count': unique_counties_count,
                'aggregation_method': 'two_stage_county_mean',
                'successful_calculations': successful,
                'discipline': _DISCIPLINE,
                'region_kind': 'WEM',

                'total_risk_score': round(total_risk, 4),

                'natural_hazards_risk': natural_hazards_avg,
                'health_risk': health_avg,
                'active_shooter_risk': active_shooter_avg,
                'extreme_heat_risk': extreme_heat_avg,
                'air_quality_risk': air_quality_avg,
                'cybersecurity_risk': cybersecurity_avg,
                'utilities_risk': utilities_avg,
                'dam_failure_risk': dam_failure_avg,
                'vector_borne_disease_risk': vbd_avg,

                'flood_risk': flood_avg,
                'tornado_risk': tornado_avg,
                'winter_storm_risk': winter_storm_avg,
                'thunderstorm_risk': thunderstorm_avg,
                'straight_line_wind_risk': straight_line_wind_avg,

                'natural_hazards': {
                    'flood': flood_avg,
                    'tornado': tornado_avg,
                    'winter_storm': winter_storm_avg,
                    'thunderstorm': thunderstorm_avg,
                    'straight_line_wind': straight_line_wind_avg,
                },
            }

            temporal_risk_data: Dict[str, Any] = {}
            for hz in TEMPORAL_HAZARDS:
                comp_county_means = []
                component_county_means: Dict[str, List[float]] = {
                    k: [] for k in TEMPORAL_COMPONENTS
                }
                for _c, hazard_map in temporal_by_county.items():
                    bucket = hazard_map.get(hz)
                    if not bucket or not bucket['composite_scores']:
                        continue
                    comp_county_means.append(mean(bucket['composite_scores']))
                    for ck in TEMPORAL_COMPONENTS:
                        if bucket[ck]:
                            component_county_means[ck].append(mean(bucket[ck]))
                if comp_county_means:
                    temporal_risk_data[hz] = {
                        'composite_score': mean(comp_county_means),
                        'temporal_components': {
                            ck: (
                                mean(component_county_means[ck])
                                if component_county_means[ck] else 0.0
                            )
                            for ck in TEMPORAL_COMPONENTS
                        },
                    }
            aggregated['temporal_risk_data'] = temporal_risk_data

            # Roll up the supporting detail blocks (component boxes, metric
            # tables, nested utilities) via the shared regional-aggregation
            # core so the WEM dashboard popovers and tiles show real
            # county-balanced values instead of empty or placeholder data.
            try:
                aggregated.update(aggregate_detail_blocks(risk_by_county))
            except Exception as detail_exc:
                logger.warning(
                    f"Failed to aggregate detail blocks for WEM region "
                    f"{wem_id}: {detail_exc}"
                )

            # Honest regional score-provenance trace (linear weighted sum of
            # the aggregated domain scores under EM weights).
            try:
                utilities_block = aggregated.get('utilities') or {}
                utilities_sub_scores = {
                    k: utilities_block[k]
                    for k in UTILITIES_SUBKEYS
                    if isinstance(utilities_block.get(k), (int, float))
                } or None
                aggregated['score_provenance'] = build_regional_provenance(
                    {
                        'natural_hazards': natural_hazards_avg,
                        'health_metrics': health_avg,
                        'active_shooter': active_shooter_avg,
                        'extreme_heat': extreme_heat_avg,
                        'air_quality': air_quality_avg,
                        'cybersecurity': cybersecurity_avg,
                        'dam_failure': dam_failure_avg,
                        'vector_borne_disease': vbd_avg,
                        'infectious_disease': infectious_disease_avg,
                        'hazmat_industrial': hazmat_industrial_avg,
                        'hazmat_agricultural': hazmat_agricultural_avg,
                        'utilities': utilities_avg,
                    },
                    weights=em_weights,
                    discipline_label='Emergency Management',
                    unique_counties_count=unique_counties_count,
                    jurisdiction_count=len(region_jurisdictions),
                    nh_sub_components={
                        'flood': flood_avg,
                        'tornado': tornado_avg,
                        'winter_storm': winter_storm_avg,
                        'thunderstorm': thunderstorm_avg,
                        'straight_line_wind': straight_line_wind_avg,
                    },
                    utilities_sub_components=utilities_sub_scores,
                )
                # The provenance builder is the single source of truth for the
                # composite total, so the headline score can never diverge from
                # the trace shown to reviewers.
                _prov_total = aggregated['score_provenance'].get(
                    'total_risk_score'
                )
                if _prov_total is not None:
                    aggregated['total_risk_score'] = round(_prov_total, 4)
            except Exception as prov_exc:
                logger.warning(
                    f"Failed to build regional provenance for WEM region "
                    f"{wem_id}: {prov_exc}"
                )

            # Regional data quality with most-conservative source freshness.
            try:
                aggregated['data_quality'] = build_regional_data_quality(
                    risk_by_county,
                    discipline_label='Emergency Management',
                    unique_counties_count=unique_counties_count,
                    jurisdiction_count=len(region_jurisdictions),
                )
            except Exception as dq_exc:
                logger.warning(
                    f"Failed to build regional data quality for WEM region "
                    f"{wem_id}: {dq_exc}"
                )

            _evict_oldest(_wem_cache, _WEM_MAX)
            aggregated['_cached_at'] = time.time()
            _wem_cache[wem_id] = aggregated

            logger.info(
                f"Calculated WEM region {wem_id} EM risk: total={aggregated['total_risk_score']:.3f}"
            )
            return aggregated

        except Exception as e:
            logger.error(f"Error calculating WEM region risk for {wem_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return None


def get_wem_region_risk(wem_id: str) -> Optional[Dict[str, Any]]:
    """Convenience entry point used by routes."""
    return WEMRiskAggregator().calculate_wem_region_risk(wem_id)
