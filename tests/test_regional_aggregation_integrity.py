"""Integrity tests for the shared regional-aggregation core.

These tests verify that the regional (HERC + WEM) composite never fabricates a
zero for a domain that is genuinely absent. An absent domain (missing key, None,
NaN, or infinity) must be excluded from the composite and the weights must
renormalize over only the domains that carry real data -- mirroring the
per-jurisdiction _domain_available semantics in utils/data_processor.py.

To run: pytest tests/test_regional_aggregation_integrity.py -v
"""
import math

from utils.regional_aggregation import build_regional_provenance, _is_available


class TestIsAvailable:
    """_is_available is the single gate that decides whether a domain counts."""

    def test_real_numbers_are_available(self):
        assert _is_available(0.0) is True
        assert _is_available(0.25) is True
        assert _is_available(1) is True

    def test_absent_or_non_finite_are_not_available(self):
        assert _is_available(None) is False
        assert _is_available(float('nan')) is False
        assert _is_available(float('inf')) is False
        assert _is_available(float('-inf')) is False

    def test_non_numeric_is_not_available(self):
        assert _is_available('0.2') is False
        assert _is_available({}) is False
        assert _is_available([]) is False

    def test_bool_is_not_treated_as_number(self):
        assert _is_available(True) is False
        assert _is_available(False) is False


class TestDomainExclusionRenormalizes:
    """A genuinely-absent domain must drop out and weights must renormalize."""

    WEIGHTS = {
        'natural_hazards': 0.26,
        'health_metrics': 0.16,
        'active_shooter': 0.17,
        'extreme_heat': 0.10,
        'air_quality': 0.11,
        'dam_failure': 0.07,
        'vector_borne_disease': 0.07,
    }

    def _full_scores(self):
        return {
            'natural_hazards': 0.4,
            'health_metrics': 0.3,
            'active_shooter': 0.5,
            'extreme_heat': 0.2,
            'air_quality': 0.25,
            'dam_failure': 0.1,
            'vector_borne_disease': 0.15,
        }

    def _manual_total(self, scores):
        num = sum(self.WEIGHTS[k] * v for k, v in scores.items()
                  if _is_available(v) and k in self.WEIGHTS)
        den = sum(self.WEIGHTS[k] for k, v in scores.items()
                  if _is_available(v) and k in self.WEIGHTS)
        return num / den if den else None

    def test_missing_key_is_excluded(self):
        scores = self._full_scores()
        del scores['active_shooter']  # key entirely absent
        p = build_regional_provenance(
            scores, weights=self.WEIGHTS, discipline_label='Public Health',
            unique_counties_count=5, jurisdiction_count=8)
        names = [d['name'] for d in p['domains']]
        assert 'Active Shooter' not in names
        assert abs(p['verification']['weights_sum'] - (0.94 - 0.17)) < 1e-9
        assert abs(p['total_risk_score'] - round(self._manual_total(scores), 4)) < 1e-3

    def test_none_value_is_excluded(self):
        scores = self._full_scores()
        scores['active_shooter'] = None
        p = build_regional_provenance(
            scores, weights=self.WEIGHTS, discipline_label='Public Health',
            unique_counties_count=5, jurisdiction_count=8)
        names = [d['name'] for d in p['domains']]
        assert 'Active Shooter' not in names
        assert abs(p['verification']['weights_sum'] - 0.77) < 1e-9

    def test_nan_and_inf_are_excluded(self):
        scores = self._full_scores()
        scores['active_shooter'] = float('nan')
        scores['health_metrics'] = float('inf')
        p = build_regional_provenance(
            scores, weights=self.WEIGHTS, discipline_label='Public Health',
            unique_counties_count=5, jurisdiction_count=8)
        names = [d['name'] for d in p['domains']]
        assert 'Active Shooter' not in names
        assert 'Health Metrics' not in names

    def test_full_set_uses_all_weights(self):
        scores = self._full_scores()
        p = build_regional_provenance(
            scores, weights=self.WEIGHTS, discipline_label='Public Health',
            unique_counties_count=5, jurisdiction_count=8)
        assert abs(p['verification']['weights_sum'] - 0.94) < 1e-9
        assert abs(p['total_risk_score'] - round(self._manual_total(scores), 4)) < 1e-3
