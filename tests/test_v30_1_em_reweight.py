"""v30.1 EM strategic reweight tests.

The Emergency Management discipline weight set deemphasizes the disease
and health family (8% combined) in favor of core infrastructure domains,
and the EM top-risk ranking never includes the acute disease domains
(infectious disease via the 'health' key, and vector-borne disease),
because CARA's EM view is a long-term strategic planning lens rather
than an acute surveillance tracker.
"""
import math

import pytest

from utils.config_manager import get_config_manager
from utils.summary_content import (
    EM_TOP_RISK_EXCLUDED_DOMAINS,
    build_top_risk_cards,
)


class TestEmWeightSet:

    def _weights(self):
        w = get_config_manager().get_em_overall_weights()
        assert w, 'EM weight set missing from config'
        return w

    def test_em_weights_sum_to_one(self):
        w = self._weights()
        assert math.isclose(sum(w.values()), 1.0, abs_tol=1e-9)

    def test_disease_family_deemphasized_to_8_percent(self):
        w = self._weights()
        family = (
            w['health_metrics']
            + w['infectious_disease']
            + w['vector_borne_disease']
        )
        assert math.isclose(family, 0.08, abs_tol=1e-9)

    def test_core_em_domains_carry_freed_weight(self):
        w = self._weights()
        assert w['natural_hazards'] == pytest.approx(0.32)
        assert w['utilities'] == pytest.approx(0.12)
        assert w['dam_failure'] == pytest.approx(0.10)
        assert w['extreme_heat'] == pytest.approx(0.10)
        assert w['hazmat_industrial'] == pytest.approx(0.045)
        assert w['hazmat_agricultural'] == pytest.approx(0.045)


class TestEmTopRiskExclusion:
    # Acute disease domains deliberately given the HIGHEST scores so a
    # score-ranked list would put them first if the exclusion regressed.
    SCORES = {
        'health': 0.95,
        'vector_borne_disease': 0.90,
        'flood': 0.50,
        'tornado': 0.40,
        'extreme_heat': 0.35,
        'air_quality': 0.30,
        'dam_failure': 0.25,
    }

    def test_em_top5_never_contains_acute_disease_domains(self):
        cards = build_top_risk_cards(self.SCORES, 'em', limit=5)
        keys = [c['key'] for c in cards]
        assert 'health' not in keys
        assert 'vector_borne_disease' not in keys
        assert len(keys) == 5
        assert keys[0] == 'flood'

    def test_public_health_ranking_unchanged(self):
        cards = build_top_risk_cards(self.SCORES, 'public_health', limit=5)
        keys = [c['key'] for c in cards]
        assert keys[0] == 'health'
        assert 'vector_borne_disease' in keys

    def test_unknown_discipline_treated_as_public_health(self):
        cards = build_top_risk_cards(self.SCORES, None, limit=5)
        keys = [c['key'] for c in cards]
        assert 'health' in keys

    def test_exclusion_constant_scoped_to_acute_domains(self):
        assert EM_TOP_RISK_EXCLUDED_DOMAINS == {
            'health', 'vector_borne_disease',
        }


class TestMethodologyWeightLabels:
    """The methodology page must stay consistent with config/risk_weights.yaml.

    Expected strings are derived from the yaml itself, so this test
    self-updates when weights are retuned: it catches copy drift on the
    methodology page, not intentional weight changes.
    """

    @staticmethod
    def _pct(value):
        p = value * 100
        if abs(p - round(p)) > 1e-9:
            return f"{p:.1f}%"
        return f"{int(round(p))}%"

    def test_domain_headers_and_tables_match_config(self, client):
        import yaml

        with open("config/risk_weights.yaml") as f:
            cfg = yaml.safe_load(f)
        ph = cfg["overall_risk_weights"]
        em = cfg["em_overall_risk_weights"]

        body = client.get("/methodology").get_data(as_text=True)

        # Every configured weight must appear somewhere as a percent string.
        for label, weights in (("PH", ph), ("EM", em)):
            for key, val in weights.items():
                assert self._pct(val) in body, (
                    f"{label} weight {key} ({self._pct(val)}) missing from "
                    "the methodology page"
                )

        # Domain section headers disclose both discipline weights. The EM
        # figure for the combined Health Metrics / Infectious Disease domain
        # is health_metrics + infectious_disease (disease awareness).
        headers = [
            f"Natural Hazards Domain ({self._pct(ph['natural_hazards'])} of "
            f"Overall under Public Health; {self._pct(em['natural_hazards'])} "
            "under Emergency Management)",
            "Health Metrics / Infectious Disease Domain "
            f"({self._pct(ph['health_metrics'])} of Overall under Public "
            "Health; "
            f"{self._pct(em['health_metrics'] + em['infectious_disease'])} "
            "under Emergency Management)",
            f"Vector-Borne Disease Domain "
            f"({self._pct(ph['vector_borne_disease'])} of Overall under "
            f"Public Health; {self._pct(em['vector_borne_disease'])} under "
            "Emergency Management)",
            f"Active Shooter Domain ({self._pct(ph['active_shooter'])} of "
            f"Overall under Public Health; {self._pct(em['active_shooter'])} "
            "under Emergency Management)",
            f"Air Quality Domain ({self._pct(ph['air_quality'])} of Overall "
            f"under Public Health; {self._pct(em['air_quality'])} under "
            "Emergency Management)",
            f"Dam Failure Domain ({self._pct(ph['dam_failure'])} of Overall "
            f"under Public Health; {self._pct(em['dam_failure'])} under "
            "Emergency Management)",
            "Utilities Domain (Supplementary under Public Health; "
            f"{self._pct(em['utilities'])} under Emergency Management)",
        ]
        if ph["extreme_heat"] == em["extreme_heat"]:
            headers.append(
                f"Extreme Heat Domain ({self._pct(ph['extreme_heat'])} of "
                "Overall under both Public Health and Emergency Management)"
            )
        else:
            headers.append(
                f"Extreme Heat Domain ({self._pct(ph['extreme_heat'])} of "
                f"Overall under Public Health; {self._pct(em['extreme_heat'])} "
                "under Emergency Management)"
            )
        for header in headers:
            assert header in body, f"methodology header missing or stale: {header}"
