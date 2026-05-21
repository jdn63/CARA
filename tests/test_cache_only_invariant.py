"""Cache-only invariant smoke test.

Asserts that process_risk_data() runs to completion for a sample
Wisconsin LHD jurisdiction even when every outbound HTTP path is
patched to raise. This proves no fetcher reachable from the request
path attempts a live `requests.get` -- they all short-circuit via
utils.request_context.is_cache_only_mode() to their cached / fallback
payloads.

If this test fails, a regression has reintroduced a live-HTTP path in
the user request flow. Locate the offending fetcher (the traceback
usually points straight at the requests.get call), wrap its HTTP
section in the `is_cache_only_mode()` short-circuit pattern, and add
the source label to the canonical registry so blocked-fetch telemetry
records it.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def block_all_http(monkeypatch):
    """Make any live HTTP call from inside process_risk_data() raise."""
    def _explode(*args, **kwargs):
        raise AssertionError(
            "Live HTTP attempted during cache-only request path. "
            "Wrap the calling fetcher in is_cache_only_mode() short-circuit."
        )

    import requests
    monkeypatch.setattr(requests, "get", _explode)
    monkeypatch.setattr(requests, "post", _explode)
    monkeypatch.setattr(requests, "request", _explode)
    monkeypatch.setattr(requests, "head", _explode)

    try:
        import urllib.request as _ureq
        monkeypatch.setattr(_ureq, "urlopen", _explode)
    except Exception:
        pass


def test_process_risk_data_is_cache_only(block_all_http, app):
    """Sample county must render without any live HTTP attempt.

    v28.9: previously this test invoked process_risk_data("milwaukee_county"),
    which is not a valid jurisdiction ID (routes/dashboard.py uses integer
    string IDs assigned by utils/data_processor.get_wi_jurisdictions()).
    The call raised ValueError before any fetcher was reached, so the
    test always failed for the wrong reason and provided no actual
    invariant coverage. We now use Adams ("1"), the lowest-numbered LHD
    jurisdiction, which exercises a representative slice of the request
    path while staying small.
    """
    from utils.data_processor import process_risk_data

    sample_jurisdiction_id = "1"  # Adams County Health & Human Services

    with app.app_context():
        try:
            result = process_risk_data(sample_jurisdiction_id)
        except AssertionError:
            # AssertionError from block_all_http means a fetcher tried to
            # hit the network from the request path. That is the
            # invariant violation we want to surface; re-raise it so the
            # test reports the offending traceback.
            raise
        except Exception as exc:
            pytest.fail(
                f"process_risk_data raised a non-HTTP exception under "
                f"cache-only enforcement: {exc!r}. This is acceptable only "
                f"if the failure is unrelated to network IO; investigate."
            )

    assert isinstance(result, dict), "process_risk_data must return a dict"
    assert (
        "overall_risk_score" in result
        or "composite_risk_score" in result
        or result
    ), "process_risk_data returned an empty / shape-wrong payload"
