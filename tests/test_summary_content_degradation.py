"""Graceful-degradation tests for the Summary plain-language content loader.

The Summary page copy lives in an editable YAML file
(`data/summary_content/summary_content.yaml`) so non-developers can revise
the wording. If that file is later edited badly -- removed, made malformed,
or stripped of a domain block -- the loader in `utils/summary_content.py`
must fall back to generic copy instead of raising into the request and
taking the page down.

These tests lock that safety net in place. They point the loader at a
controlled YAML path (or a missing/malformed one) and assert that every
public entry point returns safe fallbacks rather than crashing. They also
confirm the public_health vs em override blocks resolve to the correct
discipline-specific copy.

To run: pytest tests/test_summary_content_degradation.py -v
"""
import textwrap

import pytest

from utils import summary_content as sc


@pytest.fixture
def content_file(tmp_path, monkeypatch):
    """Point the loader at a temp YAML path and clear its in-process cache.

    Returns a writer callable. Call it with a YAML string to populate the
    file, or with None to leave the path non-existent (missing-file case).
    The lru_cache is cleared before and after each test so writes take
    effect and no state leaks between tests.
    """
    path = tmp_path / "summary_content.yaml"
    monkeypatch.setattr(sc, "_CONTENT_PATH", str(path))
    sc.reset_cache()

    def _write(yaml_text):
        if yaml_text is None:
            return
        path.write_text(textwrap.dedent(yaml_text), encoding="utf-8")
        sc.reset_cache()

    yield _write
    sc.reset_cache()


class TestMissingFile:
    """A missing YAML file must degrade to fallback copy, never raise."""

    def test_page_meta_uses_fallbacks(self, content_file):
        content_file(None)  # path does not exist
        meta = sc.get_summary_page_meta("public_health")
        assert meta["purpose"] == sc._FALLBACK_PAGE["purpose"]
        assert meta["scale_note"] == sc._FALLBACK_PAGE["scale_note"]
        assert meta["draft_banner"] == sc._FALLBACK_PAGE["draft_banner"]

    def test_cards_use_generated_labels_and_empty_content(self, content_file):
        content_file(None)
        cards = sc.build_top_risk_cards({"extreme_heat": 0.8}, "public_health")
        assert len(cards) == 1
        card = cards[0]
        assert card["label"] == "Extreme Heat"  # generated from the key
        assert card["why"] == ""
        assert card["impacts"] == ""
        assert card["populations"] == []
        assert card["note"] is None
        assert card["level"] == "High"  # scoring still works


class TestMalformedYaml:
    """Malformed or non-dict YAML must be swallowed into fallback copy."""

    def test_invalid_syntax_falls_back(self, content_file):
        content_file("::: this is : not [ valid yaml")
        meta = sc.get_summary_page_meta("em")
        assert meta["purpose"] == sc._FALLBACK_PAGE["purpose"]
        cards = sc.build_top_risk_cards({"flood": 0.5}, "em")
        assert cards[0]["label"] == "Flood"
        assert cards[0]["why"] == ""

    def test_non_dict_top_level_falls_back(self, content_file):
        content_file("just a bare string")  # parses to a str, not a dict
        meta = sc.get_summary_page_meta("public_health")
        assert meta["purpose"] == sc._FALLBACK_PAGE["purpose"]
        assert sc.build_top_risk_cards({"tornado": 0.9}, "public_health")[0][
            "label"
        ] == "Tornado"

    def test_empty_file_falls_back(self, content_file):
        content_file("")  # parses to None -> {}
        meta = sc.get_summary_page_meta("public_health")
        assert meta["scale_note"] == sc._FALLBACK_PAGE["scale_note"]


class TestDomainWithNoAuthoredCopy:
    """A domain absent from the YAML must yield a generated label + blanks."""

    YAML = """
        page:
          purpose_public_health: A purpose.
          scale_note: A scale note.
          draft_banner: A draft banner.
        domains:
          flood:
            label: Flooding
            why: Flood why.
            impacts: Flood impacts.
            populations:
              - Flood people
    """

    def test_unauthored_domain_degrades(self, content_file):
        content_file(self.YAML)
        cards = sc.build_top_risk_cards({"cybersecurity": 0.7}, "public_health")
        card = cards[0]
        assert card["label"] == "Cybersecurity"  # generated from the key
        assert card["why"] == ""
        assert card["impacts"] == ""
        assert card["populations"] == []
        assert card["note"] is None

    def test_authored_domain_still_resolves(self, content_file):
        content_file(self.YAML)
        cards = sc.build_top_risk_cards({"flood": 0.7}, "public_health")
        card = cards[0]
        assert card["label"] == "Flooding"
        assert card["why"] == "Flood why."
        assert card["impacts"] == "Flood impacts."
        assert card["populations"] == ["Flood people"]


class TestEmptyScores:
    """An empty (or None) scores map must produce no cards, never raise."""

    def test_empty_dict(self, content_file):
        content_file(None)
        assert sc.build_top_risk_cards({}, "public_health") == []

    def test_none_scores(self, content_file):
        content_file(None)
        assert sc.build_top_risk_cards(None, "em") == []

    def test_non_numeric_scores_are_dropped(self, content_file):
        content_file(None)
        scores = {"flood": "high", "tornado": None, "winter_storm": True}
        assert sc.build_top_risk_cards(scores, "public_health") == []


class TestDisciplineOverrideResolution:
    """public_health vs em override blocks resolve to the right copy."""

    YAML = """
        page:
          purpose_public_health: Public health purpose.
          purpose_em: Emergency management purpose.
          scale_note: Scale note.
          draft_banner: Draft banner.
        domains:
          flood:
            label: Flooding
            why: Shared why.
            impacts: Shared impacts.
            populations:
              - Shared population
            public_health:
              impacts: Public health impacts.
            em:
              impacts: Emergency management impacts.
              populations:
                - EM-specific population
    """

    def test_page_purpose_is_discipline_specific(self, content_file):
        content_file(self.YAML)
        assert sc.get_summary_page_meta("public_health")["purpose"] == (
            "Public health purpose."
        )
        assert sc.get_summary_page_meta("em")["purpose"] == (
            "Emergency management purpose."
        )

    def test_public_health_override_resolves(self, content_file):
        content_file(self.YAML)
        card = sc.build_top_risk_cards({"flood": 0.5}, "public_health")[0]
        assert card["impacts"] == "Public health impacts."
        assert card["why"] == "Shared why."  # no override -> shared default
        assert card["populations"] == ["Shared population"]  # not overridden

    def test_em_override_resolves(self, content_file):
        content_file(self.YAML)
        card = sc.build_top_risk_cards({"flood": 0.5}, "em")[0]
        assert card["impacts"] == "Emergency management impacts."
        assert card["why"] == "Shared why."  # no override -> shared default
        assert card["populations"] == ["EM-specific population"]  # overridden

    def test_unknown_discipline_defaults_to_public_health(self, content_file):
        content_file(self.YAML)
        card = sc.build_top_risk_cards({"flood": 0.5}, "something_else")[0]
        assert card["impacts"] == "Public health impacts."
