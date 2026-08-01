# tests/test_v30_nfip_climate_retirement.py
#
# v30.0 (2026-08): NFIP retirement + observed-climate replacement.
#
# Covers the semantics the release depends on:
#  - storm-damage percentile: None (no data / all-zero) vs 0.0 (true low)
#  - dam-failure flood-declaration factor mapping and neutral fallback
#  - nClimDiv snapshot loaders: real snapshot, None paths, midrank
#  - vector-borne observed-warming amplifier: neutral, linear, cap
#  - extreme-heat trend score mapping and clamps
#  - weighted-exposure renormalization (drop-and-renormalize, never
#    zero-impute)

import time

import pytest

import utils.climate_trends as ct
import utils.natural_hazards_risk as nh
from utils.dam_failure_risk import _get_flood_declaration_factor
from utils.natural_hazards_risk import (
    _get_storm_damage_percentile,
    _weighted_exposure_with_optional,
)
from utils.real_trend_calculator import calculate_extreme_heat_trend
from utils.vector_borne_disease_risk import _get_climate_multiplier


@pytest.fixture(autouse=True)
def _restore_module_caches():
    """Snapshot and restore the module-level caches these tests inject into."""
    saved_rate_cache = dict(nh._storm_rate_cache)
    saved_snapshot = ct._snapshot_cache
    saved_loaded = ct._snapshot_loaded
    yield
    nh._storm_rate_cache.clear()
    nh._storm_rate_cache.update(saved_rate_cache)
    ct._snapshot_cache = saved_snapshot
    ct._snapshot_loaded = saved_loaded


def _inject_damage_rates(rates):
    nh._storm_rate_cache['damage:flood'] = (time.time(), rates)


def _inject_climate_snapshot(counties, metadata=None):
    ct._snapshot_cache = {'counties': counties, 'metadata': metadata or {}}
    ct._snapshot_loaded = True


# ---------------------------------------------------------------------------
# Storm-damage percentile (replaced the NFIP claims percentile)
# ---------------------------------------------------------------------------

class TestStormDamagePercentile:

    def test_none_when_cache_unpopulated(self):
        _inject_damage_rates({})
        assert _get_storm_damage_percentile('Dane', 'flood') is None

    def test_none_when_statewide_all_zero(self):
        _inject_damage_rates({'Dane': 0.0, 'Vernon': 0.0, 'Door': 0.0})
        assert _get_storm_damage_percentile('Dane', 'flood') is None

    def test_zero_when_county_has_no_damage_but_state_does(self):
        # Menominee-style: zero recorded damage is a true low-loss signal
        # once other counties have real damage - NOT missing data.
        _inject_damage_rates({'Menominee': 0.0, 'Vernon': 50000.0, 'Dane': 20000.0})
        assert _get_storm_damage_percentile('Menominee', 'flood') == 0.0

    def test_midrank_percentile_for_nonzero_county(self):
        _inject_damage_rates({'A': 10.0, 'B': 20.0, 'C': 30.0, 'D': 40.0})
        # C: rank 2 below, 1 tie -> (2 + 0.5) / 4 = 0.625
        assert _get_storm_damage_percentile('C', 'flood') == pytest.approx(0.625)

    def test_top_county_near_one(self):
        _inject_damage_rates({'A': 1.0, 'B': 2.0, 'C': 3.0, 'D': 400.0})
        pct = _get_storm_damage_percentile('D', 'flood')
        assert pct == pytest.approx((3 + 0.5) / 4)


# ---------------------------------------------------------------------------
# Dam-failure flood-declaration factor (replaced the NFIP claims proxy)
# ---------------------------------------------------------------------------

def _fake_declarations(by_incident_type):
    def fake_get_cached_data(cache_type, county_name=None, **kwargs):
        assert cache_type == 'openfema_disaster_declarations'
        return {'data': {'by_incident_type': by_incident_type}}
    return fake_get_cached_data


class TestFloodDeclarationFactor:

    def test_neutral_without_app_context(self):
        assert _get_flood_declaration_factor('Dane') == 0.15

    def test_zero_declarations_scores_floor(self, app, monkeypatch):
        monkeypatch.setattr('utils.data_cache_manager.get_cached_data',
                            _fake_declarations({}))
        with app.app_context():
            assert _get_flood_declaration_factor('Florence') == pytest.approx(0.05)

    def test_two_declarations(self, app, monkeypatch):
        monkeypatch.setattr('utils.data_cache_manager.get_cached_data',
                            _fake_declarations({'Flood': 2}))
        with app.app_context():
            assert _get_flood_declaration_factor('Menominee') == pytest.approx(0.15)

    def test_eight_declarations_hits_cap(self, app, monkeypatch):
        monkeypatch.setattr('utils.data_cache_manager.get_cached_data',
                            _fake_declarations({'Flood': 6, 'Dam/Levee Break': 2}))
        with app.app_context():
            assert _get_flood_declaration_factor('Vernon') == pytest.approx(0.45)

    def test_severe_storm_type_excluded(self, app, monkeypatch):
        monkeypatch.setattr('utils.data_cache_manager.get_cached_data',
                            _fake_declarations({'Severe Storm': 9}))
        with app.app_context():
            assert _get_flood_declaration_factor('Dane') == pytest.approx(0.05)

    def test_cache_miss_is_neutral_not_low(self, app, monkeypatch):
        monkeypatch.setattr('utils.data_cache_manager.get_cached_data',
                            lambda *a, **k: None)
        with app.app_context():
            assert _get_flood_declaration_factor('Dane') == 0.15


# ---------------------------------------------------------------------------
# nClimDiv snapshot loaders
# ---------------------------------------------------------------------------

class TestClimateTrendLoaders:

    def test_real_snapshot_covers_all_counties(self):
        snapshot = ct.load_climate_trends()
        assert len(snapshot.get('counties', {})) == 72

    def test_real_snapshot_dane_percentile_in_range(self):
        pct = ct.get_precip_trend_percentile('Dane')
        assert pct is not None
        assert 0.0 <= pct <= 1.0

    def test_unknown_county_returns_none(self):
        assert ct.get_precip_trend_percentile('Notacounty') is None
        assert ct.get_precip_trend_info('Notacounty') is None
        assert ct.get_tavg_trend_info('Notacounty') is None

    def test_empty_snapshot_returns_none(self):
        _inject_climate_snapshot({})
        assert ct.get_precip_trend_percentile('Dane') is None

    def test_small_snapshot_suppressed(self):
        # Fewer than 10 counties cannot support a statewide percentile.
        counties = {f'C{i}': {'pcp': {'ratio': 1.0 + i / 100}} for i in range(5)}
        _inject_climate_snapshot(counties)
        assert ct.get_precip_trend_percentile('C2') is None

    def test_midrank_convention(self):
        counties = {f'C{i}': {'pcp': {'ratio': 1.0 + i / 100}} for i in range(11)}
        _inject_climate_snapshot(counties)
        # C5 is the median of 11 -> (5 + 0.5) / 11
        assert ct.get_precip_trend_percentile('C5') == pytest.approx(5.5 / 11)

    def test_tavg_info_has_delta(self):
        info = ct.get_tavg_trend_info('Dane')
        assert info is not None
        assert 'delta_f' in info
        assert info['baseline_period'] == '1951-2000'


# ---------------------------------------------------------------------------
# Vector-borne observed-warming amplifier
# ---------------------------------------------------------------------------

class TestVectorBorneWarmingAmplifier:

    def test_neutral_when_snapshot_missing(self):
        _inject_climate_snapshot({})
        assert _get_climate_multiplier('Dane') == 1.0

    def test_linear_from_observed_delta(self):
        _inject_climate_snapshot({
            'Dane': {'tavg': {'ratio': 1.0, 'baseline_mean': 43.0,
                              'recent_mean': 45.0}},
        })
        # +2.0 F -> 1.0 + 2.0 * 0.05 = 1.10
        assert _get_climate_multiplier('Dane') == pytest.approx(1.10)

    def test_cooling_never_discounts(self):
        _inject_climate_snapshot({
            'Bayfield': {'tavg': {'ratio': 1.0, 'baseline_mean': 41.0,
                                  'recent_mean': 40.0}},
        })
        assert _get_climate_multiplier('Bayfield') == 1.0

    def test_capped_at_one_twenty(self):
        _inject_climate_snapshot({
            'Hot': {'tavg': {'ratio': 1.0, 'baseline_mean': 40.0,
                             'recent_mean': 50.0}},
        })
        assert _get_climate_multiplier('Hot') == pytest.approx(1.20)

    def test_real_snapshot_within_bounds(self):
        mult = _get_climate_multiplier('Dane')
        assert 1.0 <= mult <= 1.20


# ---------------------------------------------------------------------------
# Extreme-heat trend from observed warming
# ---------------------------------------------------------------------------

class TestExtremeHeatTrend:

    def test_score_matches_documented_mapping(self):
        info = ct.get_tavg_trend_info('Dane')
        assert info is not None
        expected = max(0.35, min(0.85, 0.5 + info['delta_f'] * 0.15))
        result = calculate_extreme_heat_trend('Dane')
        assert result['score'] == pytest.approx(expected, abs=0.001)
        assert 'nClimDiv' in result['data_source']

    def test_clamped_to_bounds(self):
        _inject_climate_snapshot({
            'Hot': {'tavg': {'ratio': 1.0, 'baseline_mean': 40.0,
                             'recent_mean': 50.0}},
        })
        assert calculate_extreme_heat_trend('Hot')['score'] == pytest.approx(0.85)

    def test_neutral_when_unavailable(self):
        _inject_climate_snapshot({})
        result = calculate_extreme_heat_trend('Dane')
        assert result['score'] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Drop-and-renormalize weighting (core missing-data invariant)
# ---------------------------------------------------------------------------

class TestWeightedExposureRenormalization:

    def test_all_present_is_plain_weighted_sum(self):
        score = _weighted_exposure_with_optional(
            {'a': 0.5, 'b': 1.0}, {'a': 0.5, 'b': 0.5})
        assert score == pytest.approx(0.75)

    def test_none_term_redistributes_weight(self):
        # b missing: a's weight scales from 0.5 to the full 1.0 target.
        score = _weighted_exposure_with_optional(
            {'a': 0.8, 'b': None}, {'a': 0.5, 'b': 0.5})
        assert score == pytest.approx(0.8)

    def test_none_is_not_zero(self):
        # Zero-imputing b would give 0.4; dropping must give 0.8.
        dropped = _weighted_exposure_with_optional(
            {'a': 0.8, 'b': None}, {'a': 0.5, 'b': 0.5})
        imputed = _weighted_exposure_with_optional(
            {'a': 0.8, 'b': 0.0}, {'a': 0.5, 'b': 0.5})
        assert dropped == pytest.approx(0.8)
        assert imputed == pytest.approx(0.4)

    def test_all_none_returns_boost_only(self):
        score = _weighted_exposure_with_optional(
            {'a': None, 'b': None}, {'a': 0.5, 'b': 0.5}, additive_boost=0.1)
        assert score == pytest.approx(0.1)

    def test_boost_clamped_to_one(self):
        score = _weighted_exposure_with_optional(
            {'a': 1.0}, {'a': 1.0}, additive_boost=0.5)
        assert score == 1.0


# ---------------------------------------------------------------------------
# Hazard-specific NOAA trend (category branch must read by_category)
# ---------------------------------------------------------------------------

def _fake_storm_summary(per_year_recent, per_year_hist):
    """15 years of events with a category split: flood dominates, tornado
    is a single event in the whole record."""
    from datetime import datetime
    cy = datetime.now().year
    events_by_year = {}
    for y in range(cy - 15, cy - 5):
        events_by_year[str(y)] = per_year_hist
    for y in range(cy - 5, cy):
        events_by_year[str(y)] = per_year_recent
    total = sum(events_by_year.values())
    return {
        'events_by_year': events_by_year,
        'total_events': total,
        'years_covered': f'{cy - 15}-{cy - 1}',
        'by_category': {
            'flood': {'event_count': int(total * 0.5), 'property_damage': 1000000},
            'tornado': {'event_count': 1, 'property_damage': 0},
        },
    }


class TestNaturalHazardTrendCategorySpecific:

    def test_common_category_gets_real_trend(self, monkeypatch):
        from utils.real_trend_calculator import calculate_natural_hazard_trend
        monkeypatch.setattr(
            'utils.noaa_storm_events.get_county_storm_summary',
            lambda county: _fake_storm_summary(per_year_recent=15, per_year_hist=5))
        res = calculate_natural_hazard_trend('Vernon', 'flood')
        # Statewide-typical category with a 3x recent increase: real signal.
        assert res['score'] > 0.5
        assert 'Neutral' not in res['description']

    def test_rare_category_goes_neutral_not_inherited(self, monkeypatch):
        from utils.real_trend_calculator import calculate_natural_hazard_trend
        monkeypatch.setattr(
            'utils.noaa_storm_events.get_county_storm_summary',
            lambda county: _fake_storm_summary(per_year_recent=15, per_year_hist=5))
        res = calculate_natural_hazard_trend('Vernon', 'tornado')
        # One tornado in 15 years: the county must NOT inherit the
        # all-hazard increase; the apportioned rate is below the
        # meaningful-baseline threshold, so the trend is neutral.
        assert res['score'] == pytest.approx(0.5)

    def test_stable_category_is_stable(self, monkeypatch):
        from utils.real_trend_calculator import calculate_natural_hazard_trend
        monkeypatch.setattr(
            'utils.noaa_storm_events.get_county_storm_summary',
            lambda county: _fake_storm_summary(per_year_recent=10, per_year_hist=10))
        res = calculate_natural_hazard_trend('Vernon', 'flood')
        assert res['score'] == pytest.approx(0.5, abs=0.05)


class TestRetiredLabelsAbsent:

    def test_no_projection_provenance_in_hazard_module(self):
        import inspect
        import utils.natural_hazards_risk as mod
        src = inspect.getsource(mod)
        assert 'IPCC' not in src
        assert 'NOAA/IPCC Climate Projections' not in src
