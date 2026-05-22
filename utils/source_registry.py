"""
Canonical data-source registry for CARA.

Single source of truth for every external data source that CARA depends
on. Every other module that needs to identify a source (the scheduler,
the cache layer, the freshness calculator, the cache-only request
context) MUST use the canonical IDs defined here. A startup assertion
(validate_all_namespaces) refuses to boot if any namespace contains an
ID that is not in the canonical set.

Background: prior to this module, CARA carried four parallel naming
schemes for the same upstream source (e.g. SVI was 'svi_data' in the
scheduler config, 'cdc_svi' in the cache, 'cdc_svi' in the freshness
table, and 'cdc_svi_bulk'/'cdc_svi_per_county'/'cdc_svi_legacy_api' in
the new cache-only telemetry). That made it impossible to confidently
answer 'when was this domain last refreshed' for any given dashboard
field. The canonical scheme uses one short stable ID per upstream feed.

Dynamic parameter convention: when a fetcher needs to disambiguate a
specific instance of a source (e.g. AirNow has one cache per county),
the convention is '<canonical_id>:<param>' (single colon, then arbitrary
text). Validation strips everything from the first colon onward before
checking membership.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceSpec:
    """Canonical metadata for one data source.

    Attributes:
        display_name: Human-readable label for the UI.
        description: One-line description for the scheduler admin page.
        module: Dotted path to the module that owns the live-HTTP
            refresh function. Used by the scheduler to import and call.
        function: Name of the refresh function inside `module`. Must
            take zero arguments and return a dict summary.
        refresh_interval_hours: How often the scheduler should attempt
            a refresh.
        freshness_max_age_days: Default maximum acceptable age before
            the cache is considered stale. Overridable per call.
        legacy_aliases: Tuple of old names that this canonical ID
            absorbs. Used by the on-disk-config migration and by the
            cache-table source_type migration.
    """
    display_name: str
    description: str
    module: str
    function: str
    refresh_interval_hours: int
    freshness_max_age_days: int
    legacy_aliases: Tuple[str, ...] = ()


# Canonical sources. Adding a new external feed to CARA requires adding
# an entry here AND providing the refresh function it points to.
CANONICAL_SOURCES: Dict[str, SourceSpec] = {
    # CDC and federal health surveillance
    'svi': SourceSpec(
        display_name='CDC Social Vulnerability Index',
        description='County-level SVI percentiles (annual)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_svi',
        refresh_interval_hours=8760,
        freshness_max_age_days=400,
        legacy_aliases=('cdc_svi', 'svi_data'),
    ),
    'nssp': SourceSpec(
        display_name='CDC NSSP Respiratory ED Visits',
        description='Weekly percent of ED visits for flu/COVID/RSV (Fridays)',
        module='utils.data_source_refresher',
        function='refresh_all_nssp_respiratory',
        refresh_interval_hours=168,
        freshness_max_age_days=10,
        legacy_aliases=('cdc_nssp', 'cdc_nssp_respiratory', 'nssp_respiratory'),
    ),
    'nndss': SourceSpec(
        display_name='CDC NNDSS Communicable Disease',
        description='Weekly nationally notifiable disease case counts (Tuesdays)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_nndss_communicable',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
        legacy_aliases=('cdc_nndss_communicable',),
    ),
    'nhsn': SourceSpec(
        display_name='CDC NHSN Hospital Capacity',
        description='Weekly hospital respiratory data (Wednesdays)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_nhsn_hospital',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
        legacy_aliases=('cdc_nhsn_hospital',),
    ),
    'h5n1': SourceSpec(
        display_name='USDA APHIS H5N1 HPAI Detections',
        description='Weekly H5N1 livestock + poultry detections (Wisconsin filter)',
        module='utils.data_source_refresher',
        function='refresh_all_h5n1',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
    ),
    'mpox': SourceSpec(
        display_name='CDC Mpox State Surveillance',
        description='Weekly mpox state-level case counts',
        module='utils.data_source_refresher',
        function='refresh_all_mpox',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
    ),
    'nndss_enteric': SourceSpec(
        display_name='CDC NNDSS Enteric + Legionellosis (Wisconsin)',
        description='Weekly NNDSS counts for enteric/waterborne diseases + Legionellosis',
        module='utils.data_source_refresher',
        function='refresh_all_nndss_enteric',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
    ),
    'places_copd': SourceSpec(
        display_name='CDC PLACES COPD Prevalence',
        description='Model-based BRFSS COPD prevalence per county (annual)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_places_copd',
        refresh_interval_hours=8760,
        freshness_max_age_days=400,
        legacy_aliases=('cdc_places',),
    ),
    'places_mhlth': SourceSpec(
        display_name='CDC PLACES Mental Health Distress',
        description='Model-based BRFSS frequent mental distress per county (annual)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_places_mhlth',
        refresh_interval_hours=8760,
        freshness_max_age_days=400,
    ),

    # Wisconsin-specific
    'dhs_health': SourceSpec(
        display_name='WI DHS Health Metrics (umbrella)',
        description='Per-county WI DHS health metrics including MMR (weekly)',
        module='utils.data_source_refresher',
        function='refresh_all_dhs_health',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
    ),
    'mmr': SourceSpec(
        display_name='WI DHS WIR MMR Immunization',
        description='County MMR (1) coverage for 24-month olds (annual)',
        module='utils.data_source_refresher',
        function='refresh_all_wi_dhs_mmr',
        refresh_interval_hours=720,
        freshness_max_age_days=60,
        legacy_aliases=('wi_dhs_immunization', 'wi_dhs_wir_mmr_county'),
    ),
    'chr': SourceSpec(
        display_name='County Health Rankings',
        description='Annual BRFSS-based county health metrics (March release)',
        module='utils.data_source_refresher',
        function='refresh_all_county_health_rankings',
        refresh_interval_hours=8760,
        freshness_max_age_days=400,
        legacy_aliases=('county_health_rankings',),
    ),
    'hvi': SourceSpec(
        display_name='WI DHS Heat Vulnerability Index',
        description='Block-group HVI aggregated to county (quarterly)',
        module='utils.data_source_refresher',
        function='refresh_all_wi_dhs_hvi',
        refresh_interval_hours=2160,
        freshness_max_age_days=120,
        legacy_aliases=('wi_dhs_hvi', 'wi_dhs_hvi_bulk'),
    ),
    'vbd': SourceSpec(
        display_name='WI DHS EPHT Vector-Borne Disease',
        description='County-level Lyme and WNV incidence (weekly CSV refresh)',
        module='utils.vbd_data_fetcher',
        function='refresh_all_dhs_vbd_surveillance',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
        legacy_aliases=('dhs_vbd_surveillance', 'wi_dhs_lyme', 'wi_dhs_wnv'),
    ),

    # Environmental / weather
    'airnow': SourceSpec(
        display_name='EPA AirNow Air Quality',
        description='Daily AQI per county (daily refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_epa_air_quality',
        refresh_interval_hours=24,
        freshness_max_age_days=2,
        legacy_aliases=('epa_air_quality',),
    ),
    # Per review finding M6 (2026-05-20): freshness_max_age_days
    # relaxed from 2 to 10 days so the schedule cadence (refresh
    # every 168 h via refresh_all_nws_forecasts) and the stale
    # threshold are internally consistent. A single missed weekly
    # refresh used to mark the source stale within 48 hours even
    # when the scheduler was healthy. 10 days = the 7-day cadence
    # plus a 3-day grace window before the dashboard banner flags
    # the source as stale.
    'nws_heat': SourceSpec(
        display_name='NWS Heat Advisories and Forecasts',
        description='Active heat advisories and heat days per county',
        module='utils.data_source_refresher',
        function='refresh_all_nws_forecasts',
        refresh_interval_hours=168,
        freshness_max_age_days=10,
        legacy_aliases=('nws_forecast', 'noaa_nws_forecast'),
    ),
    # v28.8: CDC Environmental Public Health Tracking (EPHT) replaces
    # the synthetic statewide heat-days proxy and the NCEI Climate-at-
    # a-Glance monthly-max heuristic as the primary source for the
    # Extreme Heat exposure metric. EPHT publishes annually with a
    # ~12-24 month lag; freshness_max_age_days is widened to 500 days
    # so the dashboard does not flag an inherently lagged source as
    # stale. See utils/cdc_epht_heat.py and ARCHITECTURE.md.
    'cdc_epht_heat': SourceSpec(
        display_name='CDC EPHT Heat Exposure',
        description='Annual days >=90F + heat-related ED visit rate per county (annual)',
        module='utils.data_source_refresher',
        function='refresh_all_cdc_epht_heat',
        refresh_interval_hours=8760,
        freshness_max_age_days=500,
    ),
    'storm_events': SourceSpec(
        display_name='NOAA Storm Events Database',
        description='Bulk historical severe weather events (weekly refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_noaa_storm_events',
        refresh_interval_hours=168,
        freshness_max_age_days=90,
        legacy_aliases=('noaa_storm_events',),
    ),

    # FEMA / USACE federal hazard
    'nri': SourceSpec(
        display_name='FEMA National Risk Index',
        description='Annual county-level natural hazard risk indices',
        module='utils.data_source_refresher',
        function='refresh_all_fema_nri',
        refresh_interval_hours=8760,
        freshness_max_age_days=400,
        legacy_aliases=('fema_nri',),
    ),
    'dam_inventory': SourceSpec(
        display_name='USACE NID / WI DNR Dam Inventory',
        description='Wisconsin dams with hazard classifications (weekly refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_nid_dam_inventory',
        refresh_interval_hours=168,
        freshness_max_age_days=60,
        legacy_aliases=('nid_dam_inventory', 'wi_dnr_dams', 'usace_nid'),
    ),
    'fema_declarations': SourceSpec(
        display_name='OpenFEMA Disaster Declarations',
        description='Federal disaster declarations per county (weekly refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_openfema_declarations',
        refresh_interval_hours=168,
        freshness_max_age_days=14,
        legacy_aliases=('openfema_declarations', 'openfema_disaster_declarations',
                        'open_fema_declarations'),
    ),
    'fema_nfip': SourceSpec(
        display_name='OpenFEMA NFIP Claims',
        description='NFIP flood insurance claims per county (weekly refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_openfema_nfip',
        refresh_interval_hours=168,
        freshness_max_age_days=30,
        legacy_aliases=('openfema_nfip', 'openfema_nfip_claims', 'open_fema_nfip'),
    ),
    'fema_hma': SourceSpec(
        display_name='OpenFEMA Hazard Mitigation Assistance',
        description='Hazard mitigation project awards per county (weekly refresh)',
        module='utils.data_source_refresher',
        function='refresh_all_openfema_hma',
        refresh_interval_hours=168,
        freshness_max_age_days=30,
        legacy_aliases=('openfema_hma', 'openfema_hma_projects'),
    ),

    # Other federal
    'hifld_correctional': SourceSpec(
        display_name='HIFLD Correctional Facilities',
        description='ArcGIS feed of correctional facility locations',
        module='utils.data_source_refresher',
        function='refresh_all_hifld_correctional',
        refresh_interval_hours=2160,
        freshness_max_age_days=180,
    ),

    # Internal audit jobs (not upstream feeds, but produce dated
    # artifacts CARA depends on and surface through the same freshness
    # plumbing as external sources).
    'action_plan_source_verifier': SourceSpec(
        display_name='Action Plan Citation Verifier',
        description='Quarterly re-verification that action-plan citation URLs still resolve',
        module='utils.data_source_refresher',
        function='refresh_action_plan_source_verifier',
        refresh_interval_hours=2160,
        freshness_max_age_days=100,
    ),
}


CANONICAL_IDS: FrozenSet[str] = frozenset(CANONICAL_SOURCES.keys())


# Build a flat alias->canonical map for fast migration lookups.
_ALIAS_TO_CANONICAL: Dict[str, str] = {}
for _cid, _spec in CANONICAL_SOURCES.items():
    _ALIAS_TO_CANONICAL[_cid] = _cid
    for _alias in _spec.legacy_aliases:
        if _alias in _ALIAS_TO_CANONICAL and _ALIAS_TO_CANONICAL[_alias] != _cid:
            raise RuntimeError(
                f"Source registry: alias '{_alias}' is claimed by both "
                f"'{_ALIAS_TO_CANONICAL[_alias]}' and '{_cid}'. "
                f"Each legacy alias may map to exactly one canonical ID."
            )
        _ALIAS_TO_CANONICAL[_alias] = _cid


def canonicalize(label: str) -> Optional[str]:
    """Map any known label (canonical or legacy alias, with or without
    a ':param' suffix) to its canonical ID. Returns None if the label
    is not recognized so callers can decide whether to raise or warn.
    """
    if not label:
        return None
    base = label.split(':', 1)[0]
    return _ALIAS_TO_CANONICAL.get(base)


def assert_canonical(label: str, namespace: str) -> str:
    """Strict version of canonicalize. Returns the canonical ID and
    raises ValueError if the label is not in the registry. `namespace`
    is a short tag (e.g. 'scheduler_config', 'cache.source_type',
    'freshness', 'blocked_fetch') used only to make the error message
    actionable.
    """
    canonical = canonicalize(label)
    if canonical is None:
        raise ValueError(
            f"Unknown data source '{label}' used in {namespace}. "
            f"Add it to utils.source_registry.CANONICAL_SOURCES "
            f"(or list it as a legacy_alias of an existing entry)."
        )
    return canonical


def migrate_cache_source_types() -> Dict[str, int]:
    """One-shot DB migration: rewrite legacy source_type values in
    the data_source_cache table to their canonical IDs.

    Idempotent: rows already on canonical IDs are not touched. Returns
    a dict mapping {canonical_id: rows_renamed} for logging. Safe to
    call on every app boot; the typical no-op case issues one SELECT
    and returns immediately.

    Implementation uses a raw SQL UPDATE through the SQLAlchemy session
    so we do not depend on Alembic being run; the column is a free-form
    string and the data is recoverable from upstream if anything goes
    wrong, so this is the right tradeoff.
    """
    try:
        from core import db
        from sqlalchemy import text
    except ImportError:
        logger.error("migrate_cache_source_types: core/db not importable")
        return {}

    # Find rows whose source_type is a known legacy alias.
    legacy_aliases = [
        alias for alias, cid in _ALIAS_TO_CANONICAL.items() if alias != cid
    ]
    if not legacy_aliases:
        return {}

    session = db.session
    try:
        existing = session.execute(
            text(
                "SELECT source_type, COUNT(*) AS n FROM data_source_cache "
                "WHERE source_type = ANY(:aliases) GROUP BY source_type"
            ),
            {"aliases": legacy_aliases},
        ).fetchall()
    except Exception as exc:
        logger.warning(
            "migrate_cache_source_types: SELECT failed (%s); skipping migration", exc
        )
        return {}

    if not existing:
        return {}

    renamed: Dict[str, int] = {}
    for row in existing:
        legacy = row[0]
        n = row[1]
        canonical = _ALIAS_TO_CANONICAL.get(legacy)
        if canonical is None or canonical == legacy:
            continue
        try:
            session.execute(
                text(
                    "UPDATE data_source_cache SET source_type = :canonical "
                    "WHERE source_type = :legacy"
                ),
                {"canonical": canonical, "legacy": legacy},
            )
            renamed[canonical] = renamed.get(canonical, 0) + n
            logger.info(
                "migrate_cache_source_types: %s -> %s (%d rows)",
                legacy, canonical, n,
            )
        except Exception as exc:
            logger.error(
                "migrate_cache_source_types: UPDATE %s -> %s failed: %s; "
                "rolling back all renames in this batch",
                legacy, canonical, exc,
            )
            session.rollback()
            # Return {} after rollback: the prior in-loop UPDATEs were
            # part of the same uncommitted transaction and are now
            # undone, so callers must not be told they succeeded.
            return {}

    try:
        session.commit()
    except Exception as exc:
        logger.error("migrate_cache_source_types: commit failed: %s", exc)
        session.rollback()
        return {}

    return renamed


def validate_all_namespaces() -> List[str]:
    """Startup-time check that every place CARA stores a source ID
    uses something the registry recognizes. Returns a list of human-
    readable warning strings; an empty list means all clear.

    Callers (currently core.py during app boot) should log the result
    and, in strict mode, refuse to boot if any warning is returned.
    """
    warnings: List[str] = []

    # Non-source background jobs that legitimately live in the
    # scheduler config but are not external data feeds. They are
    # exempt from the canonical-ID rule.
    NON_SOURCE_JOBS = {'herc_risk_cache'}

    # Scheduler config on disk
    try:
        from utils.data_refresh_scheduler import load_scheduler_config
        cfg = load_scheduler_config()
        for sid in cfg.get('data_sources', {}).keys():
            if sid in NON_SOURCE_JOBS:
                continue
            if canonicalize(sid) is None:
                warnings.append(
                    f"scheduler_config: unknown source '{sid}'"
                )
    except (ImportError, OSError, ValueError) as exc:
        warnings.append(f"scheduler_config: failed to load ({exc})")

    # Freshness defaults
    try:
        from utils.data_freshness import DEFAULT_FRESHNESS_DAYS
        for sid in DEFAULT_FRESHNESS_DAYS.keys():
            if canonicalize(sid) is None:
                warnings.append(
                    f"freshness.DEFAULT_FRESHNESS_DAYS: unknown source '{sid}'"
                )
    except ImportError as exc:
        warnings.append(f"freshness: failed to import ({exc})")

    return warnings
