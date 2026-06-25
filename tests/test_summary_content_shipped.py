"""Positive-coverage tests for the SHIPPED Summary content file.

The graceful-degradation tests in `test_summary_content_degradation.py`
prove the Summary page survives a *broken or missing* content file by
falling back to generic copy. That protects against crashes, but it does
NOT catch a quieter failure: an editor deleting one hazard's wording from
an otherwise-valid file. In that case the page stays up but silently shows
a bare, generic card for a real hazard, with no warning to anyone.

These tests close that gap. They load the actual shipped file
(`data/summary_content/summary_content.yaml`) and assert that every domain
the Summary page can surface has non-empty authored `why`, `impacts`, and
`populations` in BOTH the public_health and em disciplines. A content edit
that drops authored copy for a hazard fails CI here instead of quietly
degrading the live page.

To run: pytest tests/test_summary_content_shipped.py -v
"""
import os

import pytest
import yaml

from utils import summary_content as sc


# Domains the Summary page can surface. REGION_DOMAINS covers the
# jurisdiction / EM county / regional (HERC/WEM) cards; the two hazmat
# domains are additionally surfaced on jurisdiction summaries but are not
# rolled up regionally, so they are not part of REGION_DOMAINS.
HAZMAT_DOMAINS = ("hazmat_industrial", "hazmat_agricultural")
EXPECTED_DOMAINS = tuple(sc.REGION_DOMAINS) + HAZMAT_DOMAINS

# A surfaced description must be more than a one-word stub. ~40 chars is
# enough to require a real sentence without being so strict it rejects a
# legitimately terse-but-written line.
_MIN_PROSE_CHARS = 40

# Every surfaced domain should name at least two affected population
# groups; a single bullet reads as a placeholder rather than guidance.
_MIN_POPULATIONS = 2

# Population bullets are legitimately short (e.g. "Young children and
# infants"), so they only need to clear a low anti-stub floor that still
# rejects one-word filler like "x" or "n/a".
_MIN_POPULATION_ENTRY_CHARS = 10

# Case-insensitive markers that signal unfinished or filler copy. Matched
# as substrings so "TODO:", "(TBD)", "FIXME!", etc. are all caught.
_PLACEHOLDER_MARKERS = ("todo", "tbd", "fixme", "lorem ipsum", "placeholder")


def _find_placeholder(text: str):
    """Return the first placeholder marker found in `text`, or None."""
    if not text:
        return None
    lowered = text.lower()
    for marker in _PLACEHOLDER_MARKERS:
        if marker in lowered:
            return marker
    return None


@pytest.fixture(autouse=True)
def _use_real_shipped_file():
    """Ensure the loader reads the real shipped YAML, not a test temp path.

    Clears the in-process cache before and after so a stale cache from
    another test (which may have repointed `_CONTENT_PATH`) cannot leak in.
    """
    sc.reset_cache()
    yield
    sc.reset_cache()


def _load_raw():
    """Load the shipped YAML directly (independent of the loader's logic)."""
    with open(sc._CONTENT_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_shipped_file_exists():
    assert os.path.isfile(sc._CONTENT_PATH), (
        f"Shipped Summary content file is missing at {sc._CONTENT_PATH}"
    )


def test_shipped_file_parses_to_expected_shape():
    data = _load_raw()
    assert isinstance(data, dict), (
        "Shipped Summary content must parse to a dict (mapping)."
    )
    assert isinstance(data.get("page"), dict), (
        "Shipped Summary content must have a 'page' block (mapping)."
    )
    assert isinstance(data.get("domains"), dict), (
        "Shipped Summary content must have a 'domains' block (mapping)."
    )


def test_page_block_has_authored_purpose_for_both_disciplines():
    data = _load_raw()
    page = data.get("page", {})
    for key in ("purpose_public_health", "purpose_em", "scale_note", "draft_banner"):
        value = page.get(key)
        assert isinstance(value, str) and value.strip(), (
            f"page.{key} is missing or empty in the shipped Summary content."
        )


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
@pytest.mark.parametrize("discipline", sc.VALID_DISCIPLINES)
def test_every_surfaced_domain_has_authored_copy(domain, discipline):
    """Each surfaced domain must resolve to non-empty why/impacts/populations.

    Goes through the same `_resolve_domain_content` the request path uses,
    so a dropped shared default (with no discipline override to cover it)
    fails here naming the exact domain and discipline.
    """
    content = sc._resolve_domain_content(domain, discipline)

    assert content["why"], (
        f"Missing authored 'why' for domain '{domain}' in discipline "
        f"'{discipline}' (shipped Summary content)."
    )
    assert content["impacts"], (
        f"Missing authored 'impacts' for domain '{domain}' in discipline "
        f"'{discipline}' (shipped Summary content)."
    )
    assert content["populations"], (
        f"Missing authored 'populations' for domain '{domain}' in discipline "
        f"'{discipline}' (shipped Summary content)."
    )


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
@pytest.mark.parametrize("discipline", sc.VALID_DISCIPLINES)
def test_every_surfaced_domain_copy_is_substantive(domain, discipline):
    """Authored copy must be real prose, not a one-character stub.

    A non-empty check (see test_every_surfaced_domain_has_authored_copy)
    passes for a value like "x" or "TBD". This raises the bar: the `why`
    and `impacts` must each clear a minimum length, and each domain must
    name at least two affected population groups, in BOTH disciplines.
    """
    content = sc._resolve_domain_content(domain, discipline)

    why = content["why"]
    assert len(why) >= _MIN_PROSE_CHARS, (
        f"'why' for domain '{domain}' in discipline '{discipline}' is too "
        f"short to be real copy ({len(why)} chars, need >= {_MIN_PROSE_CHARS}): "
        f"{why!r}"
    )

    impacts = content["impacts"]
    assert len(impacts) >= _MIN_PROSE_CHARS, (
        f"'impacts' for domain '{domain}' in discipline '{discipline}' is too "
        f"short to be real copy ({len(impacts)} chars, need >= "
        f"{_MIN_PROSE_CHARS}): {impacts!r}"
    )

    populations = content["populations"]
    assert len(populations) >= _MIN_POPULATIONS, (
        f"'populations' for domain '{domain}' in discipline '{discipline}' "
        f"has only {len(populations)} entry/entries, need >= "
        f"{_MIN_POPULATIONS}: {populations!r}"
    )
    for i, entry in enumerate(populations):
        assert len(entry) >= _MIN_POPULATION_ENTRY_CHARS, (
            f"populations[{i}] for domain '{domain}' in discipline "
            f"'{discipline}' is too short to be real copy ({len(entry)} "
            f"chars, need >= {_MIN_POPULATION_ENTRY_CHARS}): {entry!r}"
        )


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
@pytest.mark.parametrize("discipline", sc.VALID_DISCIPLINES)
def test_no_placeholder_markers_in_resolved_domain_copy(domain, discipline):
    """Resolved domain copy must not contain placeholder/filler markers.

    Goes through `_resolve_domain_content` (the request path) so a marker
    in either a shared default or a discipline override is caught and the
    failure names the exact domain, discipline, and field.
    """
    content = sc._resolve_domain_content(domain, discipline)

    for field in ("label", "why", "impacts", "note"):
        value = content.get(field) or ""
        marker = _find_placeholder(value)
        assert marker is None, (
            f"Placeholder marker '{marker}' found in '{field}' for domain "
            f"'{domain}' in discipline '{discipline}': {value!r}"
        )

    for i, entry in enumerate(content["populations"]):
        marker = _find_placeholder(entry)
        assert marker is None, (
            f"Placeholder marker '{marker}' found in populations[{i}] for "
            f"domain '{domain}' in discipline '{discipline}': {entry!r}"
        )


@pytest.mark.parametrize("discipline", sc.VALID_DISCIPLINES)
def test_no_placeholder_markers_in_page_block(discipline):
    """Page-level copy (purpose, scale note, draft banner) must be real."""
    meta = sc.get_summary_page_meta(discipline)
    for key in ("purpose", "scale_note", "draft_banner"):
        value = meta.get(key) or ""
        marker = _find_placeholder(value)
        assert marker is None, (
            f"Placeholder marker '{marker}' found in page '{key}' for "
            f"discipline '{discipline}': {value!r}"
        )


def test_no_placeholder_markers_in_authored_yaml():
    """Scan the raw shipped YAML for placeholder/filler markers anywhere.

    Belt-and-suspenders alongside the resolved-copy checks: catches a
    marker left in a field the resolver does not surface (e.g. an unused
    override block) so filler never ships in the authored file at all.
    """
    data = _load_raw()

    page = data.get("page", {})
    if isinstance(page, dict):
        for key, value in page.items():
            if isinstance(value, str):
                marker = _find_placeholder(value)
                assert marker is None, (
                    f"Placeholder marker '{marker}' found in authored "
                    f"page.{key}: {value!r}"
                )

    domains = data.get("domains", {})
    assert isinstance(domains, dict)
    for domain, block in domains.items():
        if not isinstance(block, dict):
            continue
        for field, value in block.items():
            if isinstance(value, str):
                marker = _find_placeholder(value)
                assert marker is None, (
                    f"Placeholder marker '{marker}' found in authored "
                    f"domains.{domain}.{field}: {value!r}"
                )
            elif isinstance(value, list):
                for i, entry in enumerate(value):
                    if isinstance(entry, str):
                        marker = _find_placeholder(entry)
                        assert marker is None, (
                            f"Placeholder marker '{marker}' found in authored "
                            f"domains.{domain}.{field}[{i}]: {entry!r}"
                        )
            elif isinstance(value, dict):
                for sub, subval in value.items():
                    items = subval if isinstance(subval, list) else [subval]
                    for i, entry in enumerate(items):
                        if isinstance(entry, str):
                            marker = _find_placeholder(entry)
                            assert marker is None, (
                                f"Placeholder marker '{marker}' found in "
                                f"authored domains.{domain}.{field}.{sub}"
                                f"[{i}]: {entry!r}"
                            )


@pytest.mark.parametrize("domain", EXPECTED_DOMAINS)
def test_every_surfaced_domain_block_exists_in_yaml(domain):
    """Each surfaced domain must have an actual block in the shipped YAML.

    `_resolve_domain_content` synthesizes a label from the key when a domain
    is absent, so this guards against a whole domain block being deleted
    (which the copy assertions above would also catch, but this names the
    failure more directly).
    """
    data = _load_raw()
    domains = data.get("domains", {})
    assert domain in domains, (
        f"Domain '{domain}' has no block in the shipped Summary content."
    )
    assert isinstance(domains[domain], dict), (
        f"Domain '{domain}' block must be a mapping in the shipped content."
    )
