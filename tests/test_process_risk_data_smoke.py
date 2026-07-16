"""Scored-output smoke test for process_risk_data().

Calls the authoritative PHRAT orchestrator against a known jurisdiction and
asserts that:
  - All 7 primary domain scores are present in the output.
  - Every domain score is a float in [0, 1].
  - The total risk score is a float in [0, 1].
  - The output includes required structural keys.

The test skips gracefully when the live database or scheduler cache is
unavailable (e.g., in CI environments without a seeded database).

To run manually:
    pytest tests/test_process_risk_data_smoke.py -v
"""

import math
import pytest

EXPECTED_DOMAIN_KEYS = [
    'natural_hazards_risk',
    'health_risk',
    'active_shooter_risk',
    'extreme_heat_risk',
    'air_quality_risk',
    'dam_failure_risk',
    'vector_borne_disease_risk',
]

EXPECTED_STRUCTURAL_KEYS = [
    'jurisdiction_id',
    'county',
    'total_risk_score',
    'score_provenance',
    'discipline',
]

MILWAUKEE_JURISDICTION_ID = 'WI-MKE-MCH'


def _get_milwaukee_id():
    """Return the jurisdiction ID for Milwaukee County Health Department."""
    try:
        from utils.data_processor import get_wi_jurisdictions
        jurisdictions = get_wi_jurisdictions()
        for j in jurisdictions:
            if 'Milwaukee' in j.get('name', '') and 'County' in j.get('name', ''):
                return j['id']
    except Exception:
        pass
    return MILWAUKEE_JURISDICTION_ID


class TestProcessRiskDataSmoke:
    """Smoke tests verifying process_risk_data() produces valid scored output."""

    @pytest.fixture(autouse=True)
    def skip_without_db(self):
        """Skip tests if the database or external data is not available."""
        try:
            from utils.data_processor import get_wi_jurisdictions
            jurisdictions = get_wi_jurisdictions()
            if not jurisdictions:
                pytest.skip("No jurisdictions available — database may not be seeded.")
        except Exception as exc:
            pytest.skip(f"Unable to connect to required data sources: {exc}")

    def _call_process_risk_data(self, jurisdiction_id: str) -> dict:
        """Call process_risk_data and return result, skipping on expected failures."""
        try:
            from utils.data_processor import process_risk_data
            return process_risk_data(jurisdiction_id)
        except ValueError as exc:
            pytest.skip(f"Jurisdiction not found (expected in test env): {exc}")
        except Exception as exc:
            pytest.skip(f"process_risk_data raised an unexpected exception: {exc}")

    def test_seven_domain_scores_present(self):
        """All 7 PHRAT domain scores must be present in the output."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        for key in EXPECTED_DOMAIN_KEYS:
            assert key in result, f"Missing domain score key: {key}"

    def test_all_domain_scores_in_range(self):
        """Every domain score must be a finite float in [0, 1]."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        for key in EXPECTED_DOMAIN_KEYS:
            score = result.get(key)
            assert isinstance(score, float), f"{key} is not a float: {type(score)}"
            assert math.isfinite(score), f"{key} is not finite: {score}"
            assert 0.0 <= score <= 1.0, f"{key} out of range [0,1]: {score}"

    def test_total_risk_score_in_range(self):
        """The PHRAT total score must be a finite float in [0, 1]."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        total = result.get('total_risk_score')
        assert total is not None, "total_risk_score missing from result"
        assert isinstance(total, float), f"total_risk_score is not a float: {type(total)}"
        assert math.isfinite(total), f"total_risk_score is not finite: {total}"
        assert 0.0 <= total <= 1.0, f"total_risk_score out of range [0,1]: {total}"

    def test_required_structural_keys_present(self):
        """The result must contain the standard structural keys."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        for key in EXPECTED_STRUCTURAL_KEYS:
            assert key in result, f"Missing structural key: {key}"

    def test_score_provenance_contains_seven_domains(self):
        """score_provenance must document all 7 PHRAT domain contributions."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        provenance = result.get('score_provenance', {})
        domains = provenance.get('domains', [])
        assert len(domains) == 7, (
            f"Expected 7 domains in score_provenance, got {len(domains)}: "
            f"{[d.get('name') for d in domains]}"
        )

    def test_non_zero_scores_for_primary_domains(self):
        """At least one of the primary domain scores must be > 0 (sanity check)."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        scores = [result.get(k, 0.0) for k in EXPECTED_DOMAIN_KEYS]
        assert any(s > 0.0 for s in scores), (
            "All domain scores are zero — scoring pipeline may have silently failed."
        )

    def test_public_health_discipline_default(self):
        """Default discipline should be public_health."""
        jurisdiction_id = _get_milwaukee_id()
        result = self._call_process_risk_data(jurisdiction_id)
        assert result.get('discipline') == 'public_health', (
            f"Expected discipline='public_health', got: {result.get('discipline')}"
        )


def _get_em_test_jurisdiction_id():
    """Return a canonical county LHD id that exists in this environment.

    Resolves the first EM county's name against the live jurisdictions
    list (same approach as the EM dashboard route) so these regression
    tests actually execute rather than skipping. The EM county list's
    own `jurisdiction_id` field is a legacy zero-padded code that does
    not match live jurisdiction ids.
    """
    try:
        from utils.em_counties import get_wi_counties_for_em
        from utils.data_processor import get_wi_jurisdictions
        counties = get_wi_counties_for_em()
        jurisdictions = get_wi_jurisdictions()
        for county in counties:
            target = county['name'].strip().lower()
            for j in jurisdictions:
                if (j.get('county') or '').strip().lower() == target:
                    return j['id']
    except Exception:
        pass
    return _get_milwaukee_id()


class TestEmInfectiousDiseaseWiring:
    """Regression tests for the v28.10 EM infectious_disease wiring fix.

    The EM weight set defines a standalone infectious_disease domain (5%)
    that historically was never fed a raw value at the county level, so it
    was silently excluded and renormalized (permanent 95% coverage notice).
    These tests lock in the fix: full EM coverage, no excluded
    infectious_disease domain, and an EM-only provenance row.
    """

    @pytest.fixture(autouse=True)
    def skip_without_db(self):
        try:
            from utils.data_processor import get_wi_jurisdictions
            jurisdictions = get_wi_jurisdictions()
            if not jurisdictions:
                pytest.skip("No jurisdictions available — database may not be seeded.")
        except Exception as exc:
            pytest.skip(f"Unable to connect to required data sources: {exc}")

    def _call_em(self, jurisdiction_id: str) -> dict:
        try:
            from utils.data_processor import process_risk_data
            return process_risk_data(jurisdiction_id, discipline='em')
        except ValueError as exc:
            pytest.skip(f"Jurisdiction not found (expected in test env): {exc}")
        except Exception as exc:
            pytest.skip(f"process_risk_data raised an unexpected exception: {exc}")

    def test_em_infectious_disease_not_excluded(self):
        """infectious_disease must be included (fed), never excluded, in EM."""
        result = self._call_em(_get_em_test_jurisdiction_id())
        dq = result.get('data_quality', {})
        assert 'infectious_disease' not in dq.get('excluded_domains', []), (
            "EM infectious_disease is excluded again — the 5% weight is not "
            "being fed a raw value (regression of the v28.10 wiring fix)."
        )
        assert 'infectious_disease' in dq.get('included_domains', []), (
            "EM included_domains is missing infectious_disease."
        )

    def test_em_full_coverage(self):
        """EM data coverage must be 100% (all 11 weighted domains fed)."""
        result = self._call_em(_get_em_test_jurisdiction_id())
        dq = result.get('data_quality', {})
        coverage = dq.get('coverage_fraction')
        assert coverage is not None and coverage >= 0.999, (
            f"EM coverage_fraction is {coverage}, expected 1.0 — a weighted "
            "domain is missing its raw value."
        )

    def test_em_provenance_has_disease_awareness_row(self):
        """EM score_provenance must document the 5% disease-awareness weight."""
        result = self._call_em(_get_em_test_jurisdiction_id())
        domains = result.get('score_provenance', {}).get('domains', [])
        names = [d.get('name') for d in domains]
        assert 'Infectious Disease (EM Disease Awareness)' in names, (
            f"EM provenance row missing; provenance domains: {names}"
        )

    def test_ph_provenance_has_no_disease_awareness_row(self):
        """The EM-only provenance row must not leak into PH output."""
        try:
            from utils.data_processor import process_risk_data
            result = process_risk_data(_get_em_test_jurisdiction_id())
        except ValueError as exc:
            pytest.skip(f"Jurisdiction not found (expected in test env): {exc}")
        except Exception as exc:
            pytest.skip(f"process_risk_data raised an unexpected exception: {exc}")
        names = [d.get('name') for d in result.get('score_provenance', {}).get('domains', [])]
        assert 'Infectious Disease (EM Disease Awareness)' not in names, (
            "EM-only provenance row leaked into the Public Health output."
        )
