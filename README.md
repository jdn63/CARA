# CARA - Comprehensive Automated Risk Assessment

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A comprehensive geospatial health and emergency preparedness risk assessment platform designed for Wisconsin public health departments, serving 95 jurisdictions including 11 tribal nations.

## Overview

CARA provides multi-domain risk scoring, scheduled data integration from authoritative sources, and actionable preparedness guidance to public health officials across Wisconsin. The platform enhances public health emergency response and strategic planning capabilities with data-driven insights aligned with CDC Public Health Emergency Preparedness (PHEP) capabilities.

### Key Features

- ** Comprehensive Coverage**: All 95 Wisconsin public health jurisdictions (84 local health departments + 11 tribal nations) with 101 county-level entries for risk mapping across 7 HERC regions
- ** Multi-Domain Risk Assessment**: 5 primary domains (natural hazards, infectious disease, active shooter, extreme heat, air quality) plus supplementary assessments modeled from proxy indicators (cybersecurity, utilities)
- ** Real Data Integration**: Pre-cached data from OpenFEMA APIs, NOAA Storm Events Database, Wisconsin DHS, EPA AirNow, and local Census/FEMA NRI CSV files no modeled placeholders
- ** Performance-Optimized**: Full dashboard context caching delivers near-instant load times after initial cache build
- ** Strategic Planning Mode**: Long-term risk assessment optimized for annual preparedness planning cycles
- ** PHEP Alignment**: Full integration with CDC Public Health Emergency Preparedness capabilities
- ** Automated Action Plans**: Customized preparedness recommendations with implementation timelines
- ** Interactive Visualization**: Geospatial mapping, risk distribution charts, and trend analysis

## Architecture

### Backend
- **Framework**: Flask (Python) with Blueprint architecture and application factory pattern
- **Database**: PostgreSQL with PostGIS extension for geospatial data
- **Data Processing**: Pandas, NumPy, GeoPandas for data manipulation
- **Scheduling**: APScheduler for automated data refreshes
- **APIs**: RESTful integration with multiple government data sources

### Frontend
- **Templates**: Jinja2 with Bootstrap 5 responsive design
- **Visualization**: Chart.js for interactive charts, Folium for mapping
- **Accessibility**: WCAG 2.1 AA compliant design with screen reader support
- **Performance**: Lazy loading, caching, and optimized asset delivery

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS extension
- Required API keys (see Configuration section)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/cara-wisconsin.git
cd cara-wisconsin
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export DATABASE_URL="postgresql://username:password@localhost/cara_db"
export SESSION_SECRET="your-secret-key-here"
export AIRNOW_API_KEY="your-airnow-api-key"
# Add other required API keys
```

4. **Configure environment variables** (see .env.example)
```bash
cp .env.example .env
# Edit .env with your actual values
```

5. **Initialize the database**
```bash
python -c "from core import create_app; app = create_app(); app.app_context().push(); from core import db; db.create_all()"
```

6. **Run the application**
```bash
python main.py
```

The application will be available at `http://localhost:5000`

## Deployment

### Render Deployment

The project includes a `render.yaml` configuration file for easy deployment to Render:

1. **Connect to GitHub**: Link your Render account to your GitHub repository
2. **Environment Variables**: Set the following in Render dashboard:
- `DATABASE_URL`: Your PostgreSQL connection string
- `SESSION_SECRET`: Secure random string (auto-generated)
- `AIRNOW_API_KEY`: Your EPA AirNow API key

3. **Deploy**: Render will automatically deploy using the configuration in `render.yaml`

The application uses Gunicorn with 2 workers and 120-second timeout for production-ready performance.

## Risk Assessment Framework

CARA employs a sophisticated multi-dimensional risk assessment methodology using 5 primary risk domains:

### Risk Domains (5 Primary + 2 Supplementary)

| Domain | Weight | Description |
|--------|--------|-------------|
| **Natural Hazards** | 33% | Flood, tornado, winter storm, thunderstorm (EVR framework with real NOAA/OpenFEMA data) |
| **Health Metrics** | 20% | Infectious disease surveillance and vaccination rates |
| **Active Shooter** | 20% | Community violence risk assessment |
| **Extreme Heat** | 13% | Heat vulnerability and climate-adjusted risk |
| **Air Quality** | 14% | Environmental health and AQI assessment |
| **Cybersecurity** | Supplementary (proxy indicators) | Critical infrastructure cyber threats |
| **Utilities Risk** | Supplementary (proxy indicators) | Electrical, water/sewer, supply chain, fuel shortage |

The 5 primary domains are aggregated using the **PHRAT quadratic mean formula** (p=2), which appropriately emphasizes higher-risk domains rather than averaging them away. Cybersecurity and Utilities are assessed separately as supplementary domains modeled from proxy indicators and are not included in the PHRAT composite score.

### Temporal Framework (BSTA)

- **Baseline (60%)**: Long-term structural risk factors
- **Seasonal (25%)**: Predictable cyclical variations
- **Trend (15%)**: Medium-term directional changes
- **Acute (0%)**: Short-term event-driven spikes (Strategic Planning Mode)

### Social Vulnerability Integration

All risk calculations incorporate CDC Social Vulnerability Index (SVI) factors:
- Socioeconomic status
- Household composition & disability
- Minority status & language
- Housing type & transportation

## Configuration

### Required API Keys

Add these environment variables for full functionality:

```bash
# Air Quality Data
AIRNOW_API_KEY=your_airnow_api_key

# Weather Data
OPENWEATHER_API_KEY=your_openweather_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/cara_db

# Security
SESSION_SECRET=your_secure_session_secret
```

### Data Sources

CARA integrates with multiple authoritative data sources, all pre-fetched by scheduled background jobs and cached locally (no external API calls during user assessments):

- **OpenFEMA APIs (keyless)**: Disaster Declarations Summaries v2, NFIP Redacted Claims v2, Hazard Mitigation Assistance Projects v4 weekly refresh, PostgreSQL cache
- **NOAA NCEI Storm Events Database**: Bulk CSV downloads of Wisconsin storm events (tornado, flood, thunderstorm, winter storm) with property damage, injuries, fatalities weekly refresh, local file cache
- **Wisconsin DHS**: Disease surveillance and health metrics (cached PDF extraction)
- **CDC**: Social Vulnerability Index and PHEP guidelines
- **FEMA NRI**: National Risk Index data (local CSV files)
- **EPA AirNow**: Air quality monitoring (daily scheduler cache, requires API key)
- **NOAA/NWS**: Heat forecasting and weather alerts
- **Census Bureau**: Demographic and housing data (local CSV files)

## Usage

### Web Interface

1. **Home Page**: Select from 95 Wisconsin jurisdictions
2. **Dashboard**: View comprehensive risk assessment with interactive charts
3. **Action Plans**: Download customized preparedness recommendations
4. **Methodology**: Detailed documentation of risk calculation methods
5. **HERC Integration**: Regional health coordination dashboard

### API Endpoints

```python
# Historical risk data
GET /api/historical-data/{jurisdiction_id}

# Predictive risk analysis
GET /api/predictive-analysis/{jurisdiction_id}

# HERC regional data
GET /api/herc-region/{region_id}
GET /api/herc-regions

# WEM regional data
GET /api/wem-region/{region_id}
GET /api/wem-regions

# GeoJSON boundaries
GET /api/herc-boundaries
GET /api/wem-boundaries

# Scheduler management
GET /api/scheduler-status
POST /api/refresh-data/{source}
```

## Enhanced Infectious Disease Framework

Version 2.0.0 introduces comprehensive infectious disease risk assessment:

- **Surveillance Integration**: Wisconsin DHS disease activity monitoring (weekly PDF extraction, cached)
- **Strategic Vaccination Assessment**: County-level vaccination rate analysis
- **Outbreak Multipliers**: Dynamic risk adjustments for active disease outbreaks
- **Enhanced Metrics**: Detailed breakdown of infectious disease risk components

## Security

CARA implements comprehensive security measures:

- **Environment-based Secrets**: No hardcoded API keys or credentials
- **Input Validation**: All user inputs sanitized and validated
- **XSS Protection**: Template rendering with proper escaping
- **Database Security**: Parameterized queries and connection pooling
- **Error Handling**: Graceful degradation without information disclosure

## Data Scraping & Ethics

CARA includes a scraper for publicly accessible Wisconsin DHS respiratory surveillance reports. The scraper is designed to be respectful and transparent:

- **Opt-in by default**: Scraping is disabled unless `ENABLE_SCRAPERS=1` is explicitly set. In production, the application uses cached or fallback data.
- **Caching with TTL**: Fetched data is cached locally. Cache freshness is controlled by `CACHE_TTL_HOURS` (default: 24 hours), so DHS servers are not hit on every request.
- **Rate-limited & polite**: A configurable delay (`REQUEST_DELAY_SECONDS`, default: 1.5s) is applied between requests. On 429 (Too Many Requests) or 503 (Service Unavailable) responses, the scraper backs off with exponential retry (up to `REQUEST_MAX_RETRIES`, default: 3).
- **Identified**: All requests include a `User-Agent` header identifying the scraper and providing contact information (configurable via `SCRAPER_USER_AGENT`).
- **Public data only**: The scraper accesses only publicly available DHS surveillance PDFs and web pages. No authentication or restricted resources are accessed.

| Environment Variable | Default | Description |
|---|---|---|
| `ENABLE_SCRAPERS` | `0` | Set to `1` to enable DHS scraping |
| `CACHE_TTL_HOURS` | `24` | Max age of cached data before re-fetch |
| `REQUEST_DELAY_SECONDS` | `1.5` | Delay between HTTP requests |
| `REQUEST_MAX_RETRIES` | `3` | Max retry attempts on transient errors |
| `SCRAPER_USER_AGENT` | `CARA-WI-DHS-Scraper/1.0 (...)` | User-Agent header for requests |

## Contributing

We welcome contributions from the public health and emergency management community!

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Include unit tests for new features

## Documentation

- **[Risk Assessment Methodology](docs/risk_assessment_methodology.md)**: Detailed calculation methods
- **[API Management Guide](docs/api_management_guide.md)**: API integration best practices
- **[Data Sources Analysis](docs/data_sources_comprehensive_analysis.md)**: Complete data source documentation
- **[Temporal Framework](docs/temporal_framework_usage_strategy.md)**: Strategic planning implementation

## Version History

### Version 2.4 - Real Data Integration & Performance (February 2026)
- **REAL DATA**: Replaced modeled metrics with real cached data from OpenFEMA APIs (Disaster Declarations, NFIP Claims, Hazard Mitigation Projects) and NOAA NCEI Storm Events Database
- **EVR FRAMEWORK**: Exposure-Vulnerability-Resilience methodology for all natural hazard types with health impact factors, using real event counts and damage data
- **PERFORMANCE**: Full dashboard context caching (risk data + predictions + temporal analysis) for near-instant cached load times
- **DATA FRESHNESS**: New data freshness tracking module with source-specific staleness detection
- **COUNTY BASELINES**: YAML-based county-specific baseline scores for cybersecurity and extreme heat domains with documented proxy indicator rationale
- **TESTING**: 29 golden file tests verifying score reproducibility, formula consistency, and pipeline determinism
- **PRODUCTION**: Optimized gunicorn configuration (2 workers, reload disabled, INFO logging)
- **LICENSING**: AGPLv3 license to ensure open-source availability and prevent commercial exploitation

### Version 2.3 - Configurable Risk Assessment Framework (September 2025)
- **CONFIGURATION**: YAML-based risk weight configuration system with jurisdiction-specific overrides
- **NORMALIZATION**: Advanced Z-score normalization and scaling across all risk domains
- **EXPLAINABILITY**: Comprehensive contribution logging and variable analysis for transparency
- **HVA EXPORT**: Kaiser Permanente HVA-compatible Excel exports for hospital preparedness planning
- **ARCHITECTURE**: Blueprint pattern with modular routes and application factory structure

### Version 1.9.0 (May 4, 2025)
- **NEW**: Persistent caching system with data source-appropriate refresh cycles
- **NEW**: Advanced data validation and API error handling
- Enhanced SVI data retrieval with comprehensive validation

[View Complete Version History](docs/version_history.md)

## PHEP Capabilities Integration

CARA fully aligns with CDC Public Health Emergency Preparedness Cooperative Agreement 2024-2028:

**Foundational Capabilities:**
- Community Preparedness
- Emergency Operations Coordination
- Information Sharing
- Responder Safety and Health

**Incident-Specific Capabilities:**
- Medical Countermeasure Dispensing
- Public Health Surveillance
- Medical Surge
- Nonpharmaceutical Interventions

## Research Context

CARA is a research project developed at Georgetown University to support Wisconsin public health preparedness. Users should verify critical information with authoritative sources before making major operational decisions.

## How to Cite CARA

If you use CARA in academic research, policy analysis, reports, or operational planning documents, please cite it as software.

**Recommended citation (APA-style):**

> Niedermeier, J. (2026). *CARA: Comprehensive Automated Risk Assessment* (Version 2.4) [Software]. https://github.com/jdn63/CARA

**BibTeX:**

```bibtex
@software{cara_2026,
author = {Niedermeier, Jaime},
title = {CARA: Comprehensive Automated Risk Assessment},
year = {2026},
version = {2.4},
url = {https://github.com/jdn63/CARA}
}
```

**Acknowledgment guidance:**

When used in operational or policy contexts, users are encouraged to acknowledge CARA as:

> "An open-source public health preparedness risk assessment tool developed for jurisdiction-level strategic planning."

CARA is intended to support preparedness planning, risk awareness, and policy analysis. It should not be used as the sole basis for emergency response or enforcement decisions without corroborating authoritative sources. All data is pre-cached by scheduled background jobs scores reflect the most recent cache refresh, not live conditions.

## Support

For technical support or questions:
- **Issues**: Create a GitHub issue with detailed description
- **Documentation**: Check the [docs/](docs/) directory
- **Community**: Join our discussions for best practices sharing

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** - see the [LICENSE](LICENSE) file for details. This ensures that CARA remains free and open-source, and that any modifications or network deployments must also share their source code.

## Acknowledgments

- **Wisconsin Department of Health Services** for surveillance data and guidance
- **CDC** for Public Health Emergency Preparedness framework
- **FEMA** for natural hazard risk indices
- **Georgetown University** for research support and development
- **Wisconsin public health community** for feedback and testing

---

**Built for Wisconsin Public Health Preparedness**