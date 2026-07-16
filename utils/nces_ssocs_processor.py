"""
NCES SSOCS school safety metrics processor.

Data source: NCES School Survey on Crime and Safety (SSOCS) 2019-2020
public-use microdata file (data/nces/pu_ssocs20.sav, 2,370 schools).

IMPORTANT LIMITATIONS (disclosed in every metrics payload):

1. The public-use SSOCS file contains NO state or county identifiers
   (they are suppressed for confidentiality). It is therefore impossible
   to compute Wisconsin-specific or county-specific values from this file.
2. What CARA does instead: it computes national averages for each school
   urbanicity class (city, suburb, town, rural) directly from the
   microdata, then assigns each Wisconsin county to an urbanicity class
   using a CARA-defined heuristic. The class averages are measured data;
   the county-to-class assignment is a heuristic.
3. Incident rates per 1,000 students are approximate because the public
   file reports school size only as a category (FR_SIZE); category
   midpoints are used to estimate enrollment.
"""

import os
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / 'data' / 'nces'
SSOCS_SPSS_PATH = DATA_DIR / 'pu_ssocs20.sav'

# Real variable names from the SSOCS 2019-2020 public-use file
# (verified against the file's embedded variable labels).
SAFETY_VARIABLES = {
    'building_access_control': 'C0112',   # Building access controlled (locked/monitored doors)
    'random_metal_detector': 'C0120',     # Random metal detector checks
    'security_cameras': 'C0146',          # Security cameras monitor the school
    'armed_officers': 'C0624',            # Sworn law enforcement officers carry firearms
    'active_shooter_plan': 'C0155',       # Written plan for active shooter
    'lockdown_drills': 'C0165',           # Drilled students on lockdown plan
    'threat_assessment': 'C0600',         # Have a threat assessment team
    'mental_health_diagnostic': 'C0661',  # Diagnostic mental health assessment available
    'mental_health_treatment': 'C0667',   # Treatment for mental health disorders available
    'violent_incidents': 'VIOINC20',      # Total violent incidents recorded
    'serious_violent_incidents': 'SVINC20',
    'weapon_discipline': 'DISWEAP20',     # Disciplinary actions for weapon possession
    'urbanicity': 'FR_URBAN',             # 1=City, 2=Suburb, 3=Town, 4=Rural
    'size_category': 'FR_SIZE',           # 1=<300, 2=300-499, 3=500-999, 4=1000+
}

# Enrollment midpoints for FR_SIZE categories (approximation; the public
# file does not include exact enrollment).
SIZE_MIDPOINTS = {1: 150, 2: 400, 3: 750, 4: 1500}

# CARA heuristic: Wisconsin county -> SSOCS urbanicity class.
# 'city' = urban core, 'suburb' = metro/suburban, everything else pooled
# as 'town_rural'. This assignment is a CARA judgment call, not NCES data.
CITY_COUNTIES = ['Milwaukee']
SUBURB_COUNTIES = [
    'Dane', 'Brown', 'Racine', 'Kenosha', 'Waukesha', 'Outagamie', 'Rock',
    'Marathon', 'La Crosse', 'Washington', 'Sheboygan', 'Winnebago',
    'Ozaukee', 'St. Croix', 'Eau Claire',
]

_COUNTY_HEURISTIC_NOTE = (
    'County value is the national SSOCS average for the urbanicity class '
    'CARA assigns to this county (city / suburb / town-rural). The class '
    'averages are computed from real SSOCS microdata; the county-to-class '
    'assignment is a CARA heuristic because the public-use file contains '
    'no state or county identifiers.'
)

_SOURCE_LABEL = (
    'NCES SSOCS 2019-2020 public-use microdata (national, by school '
    'urbanicity class; no state/county identifiers in public file)'
)

# Static published national figures used ONLY if the microdata file
# cannot be read. These come from published SSOCS 2019-20 tables.
DEFAULT_SAFETY_SCORES = {
    'overall_safety_score': 0.55,
    'access_control_pct': 92.0,
    'armed_security_pct': 48.0,
    'drills_pct': 95.5,
    'threat_assessment_pct': 71.3,
    'mental_health_services_pct': 55.2,
    'incident_rate': 21.3,
    'weapon_incident_rate': 0.9,
    'data_sources': [
        'Published national averages, NCES SSOCS 2019-2020 (microdata file unavailable)'
    ],
    'data_quality': 'low',
    'data_notes': (
        'SSOCS microdata could not be read; static published national '
        'averages used with no county variation.'
    ),
}

_MISSING_CODES = [-1, -2, -9]

# FR_URBAN codes pooled into CARA classes
_URBAN_CLASS_CODES = {
    'city': [1],
    'suburb': [2],
    'town_rural': [3, 4],
}


class NCESSchoolSafetyProcessor:
    """
    Computes national and urbanicity-class school safety averages from the
    SSOCS 2019-2020 public-use microdata, and serves per-county metrics
    via a disclosed county-to-urbanicity heuristic.
    """

    def __init__(self):
        self.data = None
        self.meta = None
        self.class_metrics = {}
        self.national_metrics = {}
        self.loaded = self._load_data()

    def _load_data(self):
        try:
            if not os.path.exists(SSOCS_SPSS_PATH):
                logger.warning("SSOCS microdata file not found; using published defaults")
                return False
            import pyreadstat
            self.data, self.meta = pyreadstat.read_sav(str(SSOCS_SPSS_PATH))
            logger.info(f"Loaded SSOCS microdata: {len(self.data)} schools")
            self.national_metrics = self._compute_metrics(self.data)
            for cls, codes in _URBAN_CLASS_CODES.items():
                subset = self.data[self.data['FR_URBAN'].isin(codes)]
                self.class_metrics[cls] = self._compute_metrics(subset)
                logger.info(
                    f"SSOCS urbanicity class '{cls}': {len(subset)} schools, "
                    f"safety score {self.class_metrics[cls]['overall_safety_score']}"
                )
            return True
        except Exception as e:
            logger.error(f"Error loading SSOCS microdata: {e}")
            return False

    def _pct_yes(self, df, var):
        """Percent of schools answering Yes (=1) on a 1/2-coded item."""
        if var not in df.columns or len(df) == 0:
            return 0.0
        valid = df[~df[var].isin(_MISSING_CODES)]
        if len(valid) == 0:
            return 0.0
        return float((valid[var] == 1).sum()) / len(valid) * 100.0

    def _rate_per_1000(self, df, var):
        """Incidents per 1,000 students using FR_SIZE midpoint enrollment."""
        if var not in df.columns or len(df) == 0:
            return 0.0
        valid = df[~df[var].isin(_MISSING_CODES)].copy()
        if len(valid) == 0:
            return 0.0
        enrollment = valid['FR_SIZE'].map(SIZE_MIDPOINTS).fillna(500).sum()
        if enrollment == 0:
            return 0.0
        return float(valid[var].sum()) / enrollment * 1000.0

    def _compute_metrics(self, df):
        m = {
            'access_control_pct': round(self._pct_yes(df, 'C0112'), 1),
            'random_metal_detector_pct': round(self._pct_yes(df, 'C0120'), 1),
            'security_cameras_pct': round(self._pct_yes(df, 'C0146'), 1),
            'armed_security_pct': round(self._pct_yes(df, 'C0624'), 1),
            'written_plan_pct': round(self._pct_yes(df, 'C0155'), 1),
            'drills_pct': round(self._pct_yes(df, 'C0165'), 1),
            'threat_assessment_pct': round(self._pct_yes(df, 'C0600'), 1),
            'mental_health_diagnostic_pct': round(self._pct_yes(df, 'C0661'), 1),
            'mental_health_treatment_pct': round(self._pct_yes(df, 'C0667'), 1),
            'incident_rate': round(self._rate_per_1000(df, 'VIOINC20'), 1),
            'serious_incident_rate': round(self._rate_per_1000(df, 'SVINC20'), 2),
            'weapon_incident_rate': round(self._rate_per_1000(df, 'DISWEAP20'), 2),
        }
        m['overall_safety_score'] = self._calculate_safety_score(m)
        return m

    def _calculate_safety_score(self, metrics):
        """
        Composite 0-1 score; higher = higher risk / lower safety.
        60% incident rates, 40% (inverted) preparedness/security measures.
        """
        security_score = 1.0 - (
            (metrics.get('access_control_pct', 0) / 100 * 0.2)
            + (metrics.get('armed_security_pct', 0) / 100 * 0.15)
            + (metrics.get('drills_pct', 0) / 100 * 0.1)
            + (metrics.get('threat_assessment_pct', 0) / 100 * 0.2)
            + (metrics.get('mental_health_diagnostic_pct', 0) / 100 * 0.15)
            + (metrics.get('mental_health_treatment_pct', 0) / 100 * 0.15)
        )
        incident_score = min(1.0, (
            (min(metrics.get('incident_rate', 0), 50) / 50 * 0.6)
            + (min(metrics.get('weapon_incident_rate', 0), 5) / 5 * 0.4)
        ))
        return round(incident_score * 0.6 + security_score * 0.4, 2)

    def _county_class(self, county_name):
        if county_name in CITY_COUNTIES:
            return 'city'
        if county_name in SUBURB_COUNTIES:
            return 'suburb'
        return 'town_rural'

    def get_school_safety_metrics(self, county_name):
        if not self.loaded or not self.class_metrics:
            return dict(DEFAULT_SAFETY_SCORES)
        cls = self._county_class(county_name)
        metrics = dict(self.class_metrics[cls])
        metrics['urbanicity_class'] = cls
        metrics['data_sources'] = [_SOURCE_LABEL]
        metrics['data_quality'] = 'low'
        metrics['data_notes'] = _COUNTY_HEURISTIC_NOTE
        return metrics


def get_school_safety_metrics(county_name):
    """
    Get school safety metrics for a Wisconsin county.

    Returns a dict with overall_safety_score, component percentages,
    approximate incident rates, and honest provenance labels.
    """
    try:
        if not hasattr(get_school_safety_metrics, '_processor'):
            get_school_safety_metrics._processor = NCESSchoolSafetyProcessor()
        return get_school_safety_metrics._processor.get_school_safety_metrics(county_name)
    except Exception as e:
        logger.error(f"Error getting school safety metrics for {county_name}: {e}")
        return dict(DEFAULT_SAFETY_SCORES)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    processor = NCESSchoolSafetyProcessor()
    for county in ['Milwaukee', 'Dane', 'Waukesha', 'Ashland']:
        m = processor.get_school_safety_metrics(county)
        logger.info(f"{county}: class={m.get('urbanicity_class')} score={m['overall_safety_score']}")
