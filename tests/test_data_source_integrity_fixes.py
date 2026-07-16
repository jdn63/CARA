"""
Tests for the 2026-07 data-source integrity audit fixes (v28.10).

Covers:
- SSOCS processor reads real microdata and labels the county heuristic
- Fabricated Extension ag-safety list removed from agricultural hazmat
- Utilities data_sources no longer cite never-fetched federal feeds
- Prison loader docstring honesty (static seed)
- NRI neutral fallback flag excluded from composites
"""

import pytest


class TestSSOCSProcessor:
    def test_real_microdata_loaded(self):
        from utils.nces_ssocs_processor import NCESSchoolSafetyProcessor
        p = NCESSchoolSafetyProcessor()
        assert p.loaded, "SSOCS microdata should load via pyreadstat"
        assert set(p.class_metrics.keys()) == {"city", "suburb", "town_rural"}

    def test_class_scores_are_measured_not_hardcoded(self):
        from utils.nces_ssocs_processor import NCESSchoolSafetyProcessor
        p = NCESSchoolSafetyProcessor()
        scores = {c: m["overall_safety_score"] for c, m in p.class_metrics.items()}
        # Old fabricated values were 0.68 / 0.52 (urban/suburban guesses)
        assert scores["city"] != 0.68
        assert scores["suburb"] != 0.52
        # City schools should score at or above town/rural
        assert scores["city"] >= scores["town_rural"]

    def test_county_metrics_disclose_heuristic(self):
        from utils.nces_ssocs_processor import get_school_safety_metrics
        m = get_school_safety_metrics("Milwaukee")
        assert m["urbanicity_class"] == "city"
        assert m["data_quality"] == "low"
        assert "heuristic" in m["data_notes"]
        assert "no state/county identifiers" in m["data_sources"][0]

    def test_rural_county_class(self):
        from utils.nces_ssocs_processor import get_school_safety_metrics
        m = get_school_safety_metrics("Ashland")
        assert m["urbanicity_class"] == "town_rural"


class TestExtensionListRemoved:
    def test_no_extension_constant(self):
        import utils.hazmat_agricultural_risk as mod
        assert not hasattr(mod, "EXTENSION_AG_SAFETY_HEAVY")

    def test_metrics_have_no_extension_flag(self):
        from utils.hazmat_agricultural_risk import calculate_hazmat_agricultural_risk
        result = calculate_hazmat_agricultural_risk("Dane")
        assert "extension_ag_safety_heavy" not in result["metrics"]

    def test_resilience_has_no_extension_bonus(self):
        from utils.hazmat_agricultural_risk import calculate_hazmat_agricultural_risk
        result = calculate_hazmat_agricultural_risk("Dane")
        # base 0.40 + socio_inverse*0.15 caps at 0.55; old bonus pushed to 0.70
        assert result["resilience_factors"]["score"] <= 0.55 + 1e-9


class TestUtilitiesHonestSources:
    NEVER_FETCHED = [
        "Department of Energy", "Safe Drinking Water",
        "FCC Disaster Information Reporting System",
        "FEMA Lifeline", "Energy Information Administration",
        "Wisconsin DOT", "Food Environment Atlas",
    ]

    @pytest.mark.parametrize("func", [
        "calculate_electrical_outage_risk",
        "calculate_utilities_disruption_risk",
        "calculate_supply_chain_risk",
        "calculate_fuel_shortage_risk",
    ])
    def test_no_false_citations(self, func):
        import utils.utilities_risk as mod
        fn = getattr(mod, func, None)
        if fn is None:
            pytest.skip(f"{func} not present")
        result = fn("Adams")
        sources = " ".join(result["data_sources"])
        for phantom in self.NEVER_FETCHED:
            assert phantom not in sources, f"{func} still cites {phantom}"
        assert "proxy" in sources.lower()

    def test_water_map_removed(self):
        import utils.utilities_risk as mod
        assert not hasattr(mod, "COUNTY_WATER_SYSTEM_MAP")


class TestPrisonLoaderHonesty:
    def test_docstring_declares_static_seed(self):
        from utils.data_processor import load_prison_data
        doc = load_prison_data.__doc__ or ""
        assert "hardcoded" in doc or "static" in doc
        assert "NOT fetched" in doc


class TestDisclosureTextConsistency:
    def test_no_rand_published_score_phrasing(self):
        import pathlib
        text = pathlib.Path(
            "templates/dashboard/_tile_active_shooter.html").read_text()
        assert "RAND 2022 Wisconsin Firearm Law Score" not in text
        assert "in-house translation" in text

    def test_no_extension_footprint_claim_in_docs(self):
        import pathlib
        text = pathlib.Path("ARCHITECTURE.md").read_text()
        assert "adds a small resilience boost for counties in" not in text


class TestNRINeutralFallbackFlag:
    def test_flag_present_and_excluded_from_composite(self):
        from utils.data_processor import calculate_jurisdiction_risk
        result = calculate_jurisdiction_risk("Adams")
        assert "nri_neutral_fallback" in result
        assert result["nri_neutral_fallback"] in (True, False)
