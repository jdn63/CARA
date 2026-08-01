"""Guards for the bundled GVA Wisconsin export and incident density scoring.

The legacy bundled file was a truncated national reports-page export
(Sep-Dec 2023 only, 1 Wisconsin incident). These tests pin the complete
2016-2026 Wisconsin query export and the honest denominators used to
score it.
"""

import json
import math
from collections import Counter

import pytest

BAKED = 'data/gva_reports/gva_data_wisconsin.json'


def _load():
    with open(BAKED) as f:
        return json.load(f)


def test_baked_file_integrity():
    data = _load()
    ids = [i['incident_id'] for i in data['incidents']]
    assert len(ids) == 71
    assert len(set(ids)) == 71, "duplicate incident IDs survived the bake"
    assert all(i['state'] == 'Wisconsin' for i in data['incidents'])
    assert data['coverage']['start'] == '2016-01-01'
    assert data['coverage']['end'] >= '2026-08-01'
    # Madison Oct 2023 mass shooting — present in the query export,
    # missing from the truncated legacy reports-page file.
    assert '2727876' in set(ids)


def test_dates_are_iso_and_inside_coverage():
    data = _load()
    for incident in data['incidents']:
        date = incident['date']
        assert len(date) == 10 and date[4] == '-' and date[7] == '-', date
        assert data['coverage']['start'] <= date <= data['coverage']['end'], date


def test_county_attribution():
    data = _load()
    counts = Counter(i.get('county') or i.get('derived_county') for i in data['incidents'])
    assert None not in counts, "incident with no county attribution"
    assert counts['Milwaukee'] == 48  # includes the Wauwatosa-noted incident
    assert counts['Kenosha'] == 6
    assert counts['Dane'] == 6       # Madison 5 + Middleton 1
    assert counts['Racine'] == 3
    assert counts['Rock'] == 3       # Beloit, Janesville, Clinton
    assert counts['Waukesha'] == 1   # Hartland 2022 — mapping gap fixed
    assert counts['Marathon'] == 1   # Rothschild
    assert counts['Chippewa'] == 1   # Chippewa Falls
    assert counts['La Crosse'] == 1
    assert counts['Fond du Lac'] == 1


def test_density_uses_real_census_population():
    from utils.gva_data_processor import get_incident_density_score

    score, metrics = get_incident_density_score('Milwaukee')
    assert metrics['incidents_total'] == 48
    # Census 2020 count from the provenance-tracked snapshot,
    # not the retired 945000 hardcoded guess.
    assert metrics['county_population'] == 939489
    expected = math.tanh((48 / 939489 * 100000) / 20)
    assert score == pytest.approx(expected, abs=1e-6)
    assert metrics['trend'] == 'increasing'


def test_zero_incident_county_reports_honest_window():
    from utils.gva_data_processor import get_incident_density_score

    score, metrics = get_incident_density_score('Forest')
    assert score == 0.0
    assert metrics['incidents_total'] == 0
    assert metrics['coverage_start'] == '2016-01-01'
    assert metrics['county_population'] > 0


def test_zero_incident_county_scores_zero():
    from utils.active_shooter_risk import ActiveShooterRiskModel

    model = ActiveShooterRiskModel()
    score, metrics = model.get_historical_incident_density('Forest')
    assert score == 0.0
    assert metrics['data_quality'] == 'high'
    assert 'no qualifying gva incidents' in metrics['data_notes'].lower()
    assert 'proxy' not in metrics['data_notes'].lower()
    assert metrics['incidents_total'] == 0


def test_unknown_county_fails_loudly():
    from utils.gva_data_processor import get_incident_density_score

    with pytest.raises(ValueError):
        get_incident_density_score('Atlantis')


def test_cross_file_dedupe_and_coverage_fallback(monkeypatch, tmp_path):
    """Duplicate incident IDs across baked files count once; when a file has
    no coverage block, the window derives from earliest AND latest dates."""
    import utils.gva_data_processor as gdp

    shared = {'incident_id': 'X1', 'date': '2018-05-01', 'state': 'Wisconsin',
              'city': 'Madison', 'derived_county': 'Dane', 'killed': 4, 'injured': 0}
    file_a = {'incidents': [shared,
              {'incident_id': 'X2', 'date': '2024-02-01', 'state': 'Wisconsin',
               'city': 'Milwaukee', 'derived_county': 'Milwaukee', 'killed': 0, 'injured': 5}]}
    file_b = {'incidents': [dict(shared)]}
    (tmp_path / 'a.json').write_text(json.dumps(file_a))
    (tmp_path / 'b.json').write_text(json.dumps(file_b))
    monkeypatch.setattr(gdp, 'DATA_DIR', str(tmp_path))

    incidents, stats = gdp.get_incident_data_for_location('Wisconsin')
    assert stats['total_incidents'] == 2, "duplicate incident ID was double-counted"
    assert stats['coverage_start'] == '2018-05-01', "fallback start must be the earliest date"
    assert stats['coverage_end'] == '2024-02-01'
    assert stats['coverage_years'] == pytest.approx(5.8, abs=0.1)
