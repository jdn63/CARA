"""
Gun Violence Archive (GVA) Data Processor

Processes the bundled Wisconsin GVA query export (mass shootings + mass
murders, GVA definitions) into county-level incident density signals for
the active shooter risk model.

GVA has no public API. Refresh procedure (manual):
1. Run a query at gunviolencearchive.org/query with rules
   State = Wisconsin, Incident Characteristics = Mass Shooting OR
   Mass Murder (set the form to match ANY rule, not ALL — the ALL
   default returns only the intersection of the characteristics).
2. Export as CSV and re-bake with process_gva_file().
Do not use the pre-built gunviolencearchive.org/reports page: its yearly
exports lag years behind the query database and truncate part-way (the
legacy bundled file covered only Sep-Dec 2023 with 1 Wisconsin incident).
"""

import os
import json
import logging
import csv
import math
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

# Import Wisconsin city-to-county mapping
from utils.wisconsin_mapping import get_county_for_city

# Set up logging
logger = logging.getLogger(__name__)

DATA_DIR = 'data/gva_reports'
_STALENESS_THRESHOLD_MONTHS = 18

# County populations come from the bundled USDA ERS RUCC snapshot
# (Census 2020 counts) — the same provenance-tracked file used by the
# lethal means component. No guessed populations.
_POPULATION_SNAPSHOT = 'data/usda_rucc/wi_rucc_2023.json'

_population_cache: Optional[Dict[str, int]] = None
_staleness_logged = False


def _load_county_populations() -> Dict[str, int]:
    """Load Census 2020 county populations (lowercase county name -> int)."""
    global _population_cache
    if _population_cache is None:
        with open(_POPULATION_SNAPSHOT, 'r') as f:
            snapshot = json.load(f)
        counties = snapshot.get('counties', {})
        populations = {}
        for name, record in counties.items():
            population = record.get('population_2020')
            if not isinstance(population, int) or population <= 0:
                raise ValueError(
                    f"Invalid population_2020 for county '{name}' in {_POPULATION_SNAPSHOT}"
                )
            populations[name.strip().lower()] = population
        if len(populations) != 72:
            raise ValueError(
                f"Expected 72 county populations in {_POPULATION_SNAPSHOT}, "
                f"found {len(populations)}"
            )
        _population_cache = populations
    return _population_cache


def _parse_gva_date(raw: str) -> str:
    """Normalize a GVA date string to ISO YYYY-MM-DD. Fails loudly."""
    value = (raw or '').strip()
    for fmt in ('%B %d, %Y', '%d-%b-%y', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized GVA date format: {raw!r}")


def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _check_staleness(latest_incident_date: Optional[str]) -> None:
    """Warn once per process if the newest incident is older than the threshold."""
    global _staleness_logged
    if _staleness_logged or not latest_incident_date:
        return
    _staleness_logged = True
    try:
        latest = datetime.strptime(latest_incident_date, '%Y-%m-%d')
    except ValueError:
        logger.warning(f"Could not parse latest GVA incident date: {latest_incident_date!r}")
        return
    now = datetime.now()
    months_elapsed = (now.year - latest.year) * 12 + (now.month - latest.month)
    if months_elapsed > _STALENESS_THRESHOLD_MONTHS:
        logger.warning(
            f"Newest bundled GVA incident is from {latest_incident_date} "
            f"({months_elapsed} months ago). Refresh via the GVA query tool "
            f"export procedure in utils/gva_data_processor.py."
        )


def _incident_county(incident: Dict[str, Any]) -> Optional[str]:
    """Resolve an incident to a county name (no ' County' suffix)."""
    county = incident.get('county') or incident.get('derived_county')
    if county:
        return county.replace(' County', '').strip()
    city = incident.get('city') or ''
    if city:
        return get_county_for_city(city)
    return None


def get_incident_data_for_location(location: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Get gun violence incident data for a specific location.

    Args:
        location: County name or 'Wisconsin' for state-level data

    Returns:
        Tuple of (incidents, stats). Stats include the coverage window of
        the bundled dataset even when the location has zero incidents, so
        callers can report honest denominators.
    """
    ensure_data_directory()

    is_state = location.lower() == 'wisconsin'
    if not is_state:
        location = location.replace(' County', '').strip()

    all_incidents: List[Dict[str, Any]] = []
    coverage_start: Optional[str] = None
    coverage_end: Optional[str] = None
    latest_incident: Optional[str] = None
    earliest_incident: Optional[str] = None
    seen_ids: set = set()

    try:
        for filename in sorted(os.listdir(DATA_DIR)):
            if not filename.endswith('.json'):
                continue
            try:
                with open(os.path.join(DATA_DIR, filename), 'r') as f:
                    data = json.load(f)

                file_coverage = data.get('coverage') or {}
                if file_coverage.get('start'):
                    coverage_start = min(filter(None, [coverage_start, file_coverage['start']]))
                if file_coverage.get('end'):
                    coverage_end = max(filter(None, [coverage_end, file_coverage['end']]))

                for incident in data.get('incidents', []):
                    if incident.get('state') != 'Wisconsin':
                        continue
                    incident_id = incident.get('incident_id') or incident.get('id')
                    if incident_id:
                        if incident_id in seen_ids:
                            # Same incident baked into more than one file —
                            # count it once so rates are not silently inflated.
                            continue
                        seen_ids.add(incident_id)
                    incident_date = incident.get('date')
                    if incident_date:
                        latest_incident = max(filter(None, [latest_incident, incident_date]))
                        earliest_incident = min(filter(None, [earliest_incident, incident_date]))
                    if is_state:
                        all_incidents.append(incident)
                        continue
                    county = _incident_county(incident)
                    if county and county.lower() == location.lower():
                        all_incidents.append(incident)
            except Exception as e:
                logger.error(f"Error processing {filename}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error scanning data directory: {str(e)}")

    # Fall back to observed incident dates if files carry no coverage block
    if not coverage_start and earliest_incident:
        coverage_start = earliest_incident
    if not coverage_end and latest_incident:
        coverage_end = latest_incident

    _check_staleness(latest_incident)

    coverage_years = None
    if coverage_start and coverage_end:
        try:
            delta = (datetime.strptime(coverage_end, '%Y-%m-%d')
                     - datetime.strptime(coverage_start, '%Y-%m-%d'))
            coverage_years = max(round(delta.days / 365.25, 1), 0.1)
        except ValueError:
            coverage_years = None

    stats = {
        'total_incidents': len(all_incidents),
        'incidents_by_year': {},
        'fatalities': sum(incident.get('killed', 0) for incident in all_incidents),
        'injuries': sum(incident.get('injured', 0) for incident in all_incidents),
        'coverage_start': coverage_start,
        'coverage_end': coverage_end,
        'coverage_years': coverage_years,
        'latest_incident_date': latest_incident,
        'data_sources': ['Gun Violence Archive Wisconsin query export 2016-2026 '
                         '(mass shootings + mass murders)'],
    }

    for incident in all_incidents:
        incident_date = incident.get('date') or ''
        year = incident_date[:4]
        if len(year) == 4 and year.isdigit():
            stats['incidents_by_year'][year] = stats['incidents_by_year'].get(year, 0) + 1
        else:
            logger.warning(f"Incident with unparseable date skipped in year stats: {incident_date!r}")

    return all_incidents, stats


def get_incident_density_score(location: str) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate an incident density score from the bundled GVA export.

    Score = tanh(cumulative_incidents_per_100k / 20), capped at 1.0.
    The rate is cumulative over the dataset coverage window (~10.6 years),
    per 100k residents (Census 2020). 0.5 is reached near 12 per 100k.

    Raises ValueError for unknown counties (no silent default population).

    Returns:
        Tuple of (score, metrics_dict)
    """
    incidents, stats = get_incident_data_for_location(location)

    populations = _load_county_populations()
    if location.lower() == 'wisconsin':
        population = sum(populations.values())
    else:
        key = location.replace(' County', '').strip().lower()
        if key not in populations:
            raise ValueError(
                f"Unknown county '{location}': no Census 2020 population on record"
            )
        population = populations[key]

    base_metrics = {
        'coverage_start': stats.get('coverage_start'),
        'coverage_end': stats.get('coverage_end'),
        'coverage_years': stats.get('coverage_years'),
        'county_population': population,
        'population_source': 'Census 2020 (bundled USDA ERS RUCC 2023 snapshot)',
        'data_sources': stats['data_sources'],
    }

    if not incidents:
        return 0.0, {
            **base_metrics,
            'incidents_total': 0,
            'incidents_per_100k': 0.0,
            'trend': 'no recorded incidents',
            'fatalities': 0,
            'injuries': 0,
        }

    incidents_total = len(incidents)
    per_100k_rate = (incidents_total / population) * 100000

    yearly_data = stats.get('incidents_by_year', {})
    years = sorted(yearly_data.keys())
    if len(years) >= 3:
        first_half = sum(yearly_data.get(year, 0) for year in years[:len(years) // 2])
        second_half = sum(yearly_data.get(year, 0) for year in years[len(years) // 2:])
        if second_half > first_half * 1.2:
            trend = 'increasing'
        elif second_half < first_half * 0.8:
            trend = 'decreasing'
        else:
            trend = 'stable'
    else:
        trend = 'insufficient data'

    score = min(1.0, math.tanh(per_100k_rate / 20))

    return score, {
        **base_metrics,
        'incidents_total': incidents_total,
        'incidents_per_100k': round(per_100k_rate, 1),
        'trend': trend,
        'fatalities': stats.get('fatalities', 0),
        'injuries': stats.get('injuries', 0),
    }


def process_gva_file(file_path_or_object, provenance_note: str = '',
                     coverage_start: str = '2016-01-01',
                     coverage_end: Optional[str] = None) -> str:
    """
    Bake a GVA query-tool CSV export into the bundled JSON dataset.

    Non-Wisconsin rows are dropped, duplicate incident IDs are merged,
    dates are normalized to ISO, and counties are derived from cities at
    bake time so runtime lookups are deterministic.

    Args:
        file_path_or_object: Path to the CSV file or file-like object
        provenance_note: Where the export came from (recorded in the JSON)
        coverage_start: Start of the query window used for the export
        coverage_end: End of coverage; defaults to the bake date

    Returns:
        Output filename within data/gva_reports/
    """
    ensure_data_directory()

    if isinstance(file_path_or_object, str):
        file_obj = open(file_path_or_object, 'r', encoding='utf-8-sig')
    else:
        file_obj = file_path_or_object.stream if hasattr(file_path_or_object, 'stream') else file_path_or_object

    field_mappings = {
        'Incident ID': 'incident_id',
        'Incident Date': 'date',
        'State': 'state',
        'City Or County': 'city_or_county',
        'Address': 'address',
        'Victims Killed': 'killed',
        'Victims Injured': 'injured',
        'Operations': 'operations',
    }

    incidents_by_id: Dict[str, Dict[str, Any]] = {}
    dropped_non_wi = 0
    unresolved_cities = set()

    try:
        for row in csv.DictReader(file_obj):
            incident = {mapped: row[original]
                        for original, mapped in field_mappings.items() if original in row}

            if incident.get('state') != 'Wisconsin':
                dropped_non_wi += 1
                continue

            incident['date'] = _parse_gva_date(incident.get('date', ''))

            for num_field in ('killed', 'injured'):
                try:
                    incident[num_field] = int(incident.get(num_field, 0))
                except (ValueError, TypeError):
                    logger.warning(f"Non-numeric {num_field} in incident "
                                   f"{incident.get('incident_id')!r}; recording 0")
                    incident[num_field] = 0

            location = incident.get('city_or_county', '')
            if ' County' in location:
                incident['county'] = location.replace(' County', '').strip()
            elif location:
                incident['city'] = location
                county = get_county_for_city(location)
                if county:
                    incident['derived_county'] = county
                else:
                    unresolved_cities.add(location)

            incident['id'] = incident.get('incident_id')
            if incident.get('incident_id'):
                incidents_by_id[incident['incident_id']] = incident
    finally:
        if isinstance(file_path_or_object, str):
            file_obj.close()

    if unresolved_cities:
        logger.warning(
            f"GVA bake: no county mapping for {sorted(unresolved_cities)} — "
            f"add them to utils/wisconsin_mapping.py and re-bake"
        )

    incidents = sorted(incidents_by_id.values(), key=lambda i: i['date'])

    output_data = {
        'source': 'Gun Violence Archive',
        'description': 'Wisconsin incidents matching GVA Mass Shooting (4+ shot) '
                       'or Mass Murder (4+ killed) definitions',
        'coverage': {
            'start': coverage_start,
            'end': coverage_end or datetime.now().date().isoformat(),
        },
        'provenance': {
            'method': 'Manual export from gunviolencearchive.org/query '
                      '(State = Wisconsin; Incident Characteristics = Mass Shooting OR Mass Murder)',
            'note': provenance_note,
            'dropped_non_wisconsin_rows': dropped_non_wi,
        },
        'processed_date': datetime.now().isoformat(),
        'total_incidents': len(incidents),
        'incidents': incidents,
    }

    output_filename = 'gva_data_wisconsin.json'
    with open(os.path.join(DATA_DIR, output_filename), 'w') as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"Baked {len(incidents)} Wisconsin GVA incidents to {output_filename} "
                f"(dropped {dropped_non_wi} non-WI rows)")
    return output_filename
