"""Tests for the read-only local-signal derivation layer.

These cover two things:
  1. `derive_local_signals` in isolation against synthetic risk_data dicts:
     correct drivers/populations when fields are present, empty lists when
     absent, and the guard behaviour for booleans, None, and the regional
     "Varies across N counties" placeholder.
  2. A route-level guarantee that, for inputs whose cached data carries real
     local signals, at least one derived signal actually reaches the rendered
     Summary page (jurisdiction and region).

These assert behaviour, never scores: nothing here changes a risk value.

To run: pytest tests/test_summary_signals.py -v
"""

from __future__ import annotations

import re

from utils.summary_signals import derive_local_signals


class TestDriverDerivation:
    def test_flood_drivers_from_real_fields(self):
        rd = {
            "flood_metrics": {
                "historical_flood_events": 19,
                "federal_flood_declarations": 3,
                "data_period": "2006-2026",
            }
        }
        out = derive_local_signals("flood", rd)
        joined = " ".join(out["drivers"])
        assert "19 recorded flood events" in joined
        assert "since 2006-2026" in joined
        assert "3 federal flood disaster declarations" in joined
        # NFIP claims driver retired 2026-08 (insurance participation, not
        # hazard); it must never resurface.
        assert "flood-insurance claims" not in joined

    def test_dam_failure_drivers(self):
        rd = {
            "dam_failure_metrics": {
                "total_dams": 800,
                "high_hazard_dams": 35,
                "modeled_population_at_risk": 4377,
            }
        }
        out = derive_local_signals("dam_failure", rd)
        joined = " ".join(out["drivers"])
        assert "800 dams nearby" in joined
        assert "35 rated high-hazard" in joined
        assert "4,377 residents" in joined

    def test_vbd_drivers_and_populations(self):
        rd = {
            "vbd_metrics": {
                "lyme_incidence_rate": 163.78,
                "lyme_disease_tier": "high",
                "forest_cover_pct": 51.13,
                "outdoor_workforce_pct": 14.2,
                "elderly_vulnerability_pct": 21.0,
            }
        }
        out = derive_local_signals("vector_borne_disease", rd)
        drivers = " ".join(out["drivers"])
        assert "164 Lyme cases per 100,000" in drivers
        assert "Lyme risk tier rated high" in drivers
        assert "51% forest cover" in drivers
        pops = out["populations"]
        assert any("wooded areas" in p for p in pops)
        assert any("Outdoor workers" in p for p in pops)

    def test_health_statewide_labelled(self):
        rd = {
            "health_metrics": {
                "activity_levels": {"overall": "High"},
                "vaccination_risk_assessment": {
                    "herd_immunity_gaps": {"mmr_gap": 8.4}
                },
            },
            "nndss_data": {"outbreak_flags": {"measles": True, "mumps": False}},
        }
        out = derive_local_signals("health", rd)
        joined = " ".join(out["drivers"])
        assert "statewide respiratory illness activity is high" in joined
        assert "statewide MMR coverage gap of about 8 points" in joined
        assert "active statewide surveillance flag: measles" in joined


class TestPopulationDerivation:
    def test_natural_hazard_populations(self):
        rd = {
            "flood_metrics": {
                "elderly_vulnerability_pct": 22.0,
                "mobile_home_vulnerability_pct": 11.0,
            },
            "flood_vulnerability_breakdown": {
                "socioeconomic_svi": 0.71,
                "housing_transportation_svi": 0.65,
            },
        }
        pops = derive_local_signals("flood", rd)["populations"]
        # capped at 3
        assert len(pops) == 3
        assert any("Older adults" in p for p in pops)
        assert any("manufactured or mobile homes" in p for p in pops)

    def test_below_threshold_emits_nothing(self):
        rd = {
            "flood_metrics": {
                "elderly_vulnerability_pct": 12.0,
                "mobile_home_vulnerability_pct": 2.0,
            },
            "flood_vulnerability_breakdown": {
                "socioeconomic_svi": 0.3,
                "housing_transportation_svi": 0.2,
            },
        }
        assert derive_local_signals("flood", rd)["populations"] == []


class TestGuards:
    def test_empty_when_fields_absent(self):
        out = derive_local_signals("flood", {})
        assert out == {"drivers": [], "populations": []}

    def test_proxy_domain_emits_nothing(self):
        # cybersecurity has no genuine local signal; emit nothing rather
        # than dress proxy values up as local data.
        rd = {"cyber_metrics": {"critical_vulnerabilities": 9}}
        out = derive_local_signals("cybersecurity", rd)
        assert out == {"drivers": [], "populations": []}

    def test_varies_placeholder_skipped(self):
        # Regional aggregation writes this into non-uniform string fields.
        rd = {
            "hazmat_industrial_metrics": {
                "industrial_tier": "Varies across 15 counties"
            },
            "hazmat_industrial_exposure_factors": {},
        }
        assert derive_local_signals("hazmat_industrial", rd)["drivers"] == []

    def test_boolean_and_none_skipped(self):
        rd = {
            "flood_metrics": {
                "historical_flood_events": True,   # not a real count
                "storm_damage_percentile": None,
                "federal_flood_declarations": 0,   # zero -> skip
            }
        }
        assert derive_local_signals("flood", rd)["drivers"] == []

    def test_non_dict_input_safe(self):
        assert derive_local_signals("flood", None) == {
            "drivers": [], "populations": []
        }
        assert derive_local_signals("", {}) == {"drivers": [], "populations": []}

    def test_extreme_heat_low_skipped(self):
        rd = {"extreme_heat_metrics": {"risk_level": "Low"}}
        assert derive_local_signals("extreme_heat", rd)["drivers"] == []
        rd2 = {"extreme_heat_metrics": {"risk_level": "Very High"}}
        out = derive_local_signals("extreme_heat", rd2)
        assert any("Very High" in d for d in out["drivers"])


# A driver phrase that proves real local data reached the page: a digit
# followed by descriptive text the authored YAML copy does not contain.
_LOCAL_SIGNAL_RE = re.compile(
    r"(recorded (flood|tornado|severe winter|severe thunderstorm|damaging wind) "
    r"|dams nearby|Lyme cases per|EPA-tracked|residents modeled|"
    r"federal .* declarations|forest cover|"
    r"Heat Vulnerability Index rated|coverage gap of about)"
)


class TestSignalsReachRenderedPage:
    """At least one derived local signal must reach the rendered Summary."""

    def test_jurisdiction_summary_has_local_signal(self, client):
        body = client.get("/print-summary/1").get_data(as_text=True)
        assert _LOCAL_SIGNAL_RE.search(body), (
            "jurisdiction summary rendered no derived local signal"
        )

    # Minimal but internally consistent NOAA storm summary fixture,
    # seeded per county as needed: per-category counts sum to
    # total_events, which matches the yearly series (20 years at 6
    # events/year).
    _STORM_SUMMARY_FIXTURE = {
        "events_by_year": {str(y): 6 for y in range(2006, 2026)},
        "total_events": 120,
        "years_covered": "2006-2025",
        "total_property_damage": 25000000.0,
        "total_crop_damage": 0,
        "total_fatalities": 0,
        "total_injuries": 0,
        "tornado_magnitudes": {},
        "by_category": {
            "flood": {"event_count": 40, "property_damage": 12000000.0,
                      "crop_damage": 0, "injuries": 0, "fatalities": 0,
                      "event_types": {"Flood": 30, "Flash Flood": 10}},
            "tornado": {"event_count": 8, "property_damage": 5000000.0,
                        "crop_damage": 0, "injuries": 0, "fatalities": 0,
                        "event_types": {"Tornado": 8}},
            "winter": {"event_count": 30, "property_damage": 3000000.0,
                       "crop_damage": 0, "injuries": 0, "fatalities": 0,
                       "event_types": {"Winter Storm": 30}},
            "thunderstorm": {"event_count": 22, "property_damage": 2000000.0,
                             "crop_damage": 0, "injuries": 0, "fatalities": 0,
                             "event_types": {"Thunderstorm Wind": 22}},
            "straight_line_wind": {"event_count": 20,
                                   "property_damage": 3000000.0,
                                   "crop_damage": 0, "injuries": 0,
                                   "fatalities": 0,
                                   "event_types": {"High Wind": 20}},
        },
    }

    @staticmethod
    def _reset_hazard_module_caches():
        """Clear utils.natural_hazards_risk module-level caches.

        Earlier route renders in this process may have cached statewide
        rates, per-county lookups (including None results), and WEM
        regional aggregates from an empty test database; without a
        reset, seeded cache rows are never re-read. Called again at
        teardown so later tests start from a deterministic cold state.
        """
        import utils.natural_hazards_risk as nh
        import utils.wem_risk_aggregator as wra
        nh.reset_rate_caches()
        nh._real_data_cache.clear()
        wra._jurisdiction_cache.clear()
        wra._wem_cache.clear()

    def _seed_storm_cache(self, app, counties):
        """Seed NOAA storm-events cache rows through the app's own cache
        write path (mirroring the warm production cache), then reset the
        hazard module caches so the seeded rows are actually read."""
        with app.app_context():
            from utils.data_cache_manager import save_cached_data
            for county in counties:
                assert save_cached_data(
                    "noaa_storm_events",
                    self._STORM_SUMMARY_FIXTURE,
                    county_name=county,
                    api_source="test-fixture",
                ), f"failed to seed NOAA storm-events cache for {county}"
        self._reset_hazard_module_caches()

    def test_em_county_summary_has_local_signal(self, client, app):
        # v30.1: the EM top-risk ranking excludes the acute disease domains
        # ('health', 'vector_borne_disease'), whose drivers derive from
        # bundled data files. The domains that rank under EM derive their
        # drivers from cached NOAA data instead, so seed Adams storm data
        # before rendering.
        self._seed_storm_cache(app, ["Adams"])
        try:
            body = client.get("/em-print-summary/adams").get_data(as_text=True)
            assert _LOCAL_SIGNAL_RE.search(body)
        finally:
            self._reset_hazard_module_caches()

    def test_herc_region_summary_has_local_signal(self, client):
        body = client.get("/herc-print-summary/1").get_data(as_text=True)
        assert _LOCAL_SIGNAL_RE.search(body), (
            "HERC region summary rendered no derived local signal"
        )

    def test_wem_region_summary_has_local_signal(self, client, app):
        # WEM regions render under the EM discipline, so the v30.1
        # top-risk exclusion applies here too: seed storm data for every
        # county in the southeast region so the hazard cards that now
        # rank carry derivable local signals.
        from utils.wem_data import get_all_wem_regions
        region = next(
            r for r in get_all_wem_regions() if r["id"] == "southeast"
        )
        counties = [
            c["name"] if isinstance(c, dict) else c
            for c in region.get("counties", [])
        ]
        assert counties, "southeast WEM region resolved no counties"
        self._seed_storm_cache(app, counties)
        try:
            body = client.get(
                "/wem-print-summary/southeast"
            ).get_data(as_text=True)
            assert _LOCAL_SIGNAL_RE.search(body)
        finally:
            self._reset_hazard_module_caches()
