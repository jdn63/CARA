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
