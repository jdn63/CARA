# CARA Adaptation Workshop Facilitator Guide

## Adapting CARA for Subnational Healthcare Emergency Preparedness Risk Assessment

This guide walks workshop participants through obtaining, configuring, and customizing the Comprehensive Automated Risk Assessment (CARA) platform for a new jurisdiction. It is written for facilitators working with participants who have no coding experience. The guide applies to any country or subnational region.

The steps in this guide are the same regardless of how you choose to work with the code - whether on your own computer, on a cloud development platform, or any other environment that can run Python.

---

## Before the Workshop

### What You Need

- A GitHub account (free) for each participant or team -- sign up at https://github.com
- A development environment (see "Choosing Your Development Environment" below for options)
- An internet connection
- A projector or shared screen for live demonstration
- Printed or digital copies of this guide for each participant

### Choosing Your Development Environment

CARA is a Python web application backed by a PostgreSQL database. You can work with it in any environment that supports these two things. Here are the most common options:

**Option A: Your own computer (local development)**

Best for: Participants who already have some technical setup on their machines, or teams with IT support available.

Requirements:
- Python 3.9 or newer installed (https://www.python.org/downloads/)
- PostgreSQL installed and running (https://www.postgresql.org/download/)
- A text editor for editing files (Visual Studio Code is free and beginner-friendly: https://code.visualstudio.com)
- A terminal or command prompt for running commands

**Option B: Replit (cloud development platform)**

Best for: Workshops where participants do not have technical setup on their computers, or when you want everyone working in an identical environment with no installation required.

Requirements:
- A free Replit account (https://replit.com)
- A web browser

**Option C: Other cloud platforms**

CARA can also run on platforms such as Render (https://render.com), Railway (https://railway.app), PythonAnywhere (https://www.pythonanywhere.com), or GitHub Codespaces. The file-editing steps in this guide are identical regardless of platform.

### Facilitator Preparation

1. Familiarize yourself with the CARA GitHub repository structure
2. Complete the fork and setup process yourself before the workshop using whichever development environment you plan to use, so you can troubleshoot
3. Prepare a list of potential data sources relevant to the target jurisdiction (participants will also research their own)
4. Have the CARA demo site open in a browser tab to show participants what the finished product looks like

---

## Workshop Day 1: Understanding CARA and Planning Your Adaptation

### Session 1: What is CARA? (1 hour)

Walk participants through the live CARA demo. Show them:

- The home page with jurisdiction selection dropdown
- A sample jurisdiction dashboard showing risk scores across domains
- The risk score breakdown showing how individual components contribute to the overall score
- The Download Data tab with export options
- The methodology page explaining the scoring approach

Key concepts to explain:

**Risk Domains**: CARA organizes risk into separate categories (called "domains"). The template ships with these primary domains, organized into two profiles -- US State and International:

US State profile domains (default weights):
- Natural Hazards (28%): floods, tornadoes, winter storms, thunderstorms
- Mass Casualty / Violence (18%): historical incidents, community vulnerability factors
- Health Metrics / Infectious Disease (17%): respiratory illness, vaccination coverage, healthcare capacity
- Air Quality (12%): EPA monitoring, pollution exposure
- Extreme Heat (11%): heat vulnerability, urban heat island effect
- Dam Failure (7%): dam inventory, downstream population exposure
- Vector-Borne Disease (7%): disease surveillance data

International profile domains (default weights):
- Natural Hazards (25%): historical disasters, climate exposure
- Conflict / Displacement (20%): conflict event data, population displacement
- Health Metrics (17%): health system indicators, disease burden
- Mass Casualty / Violence (12%): incident data, community factors
- Air Quality (10%): monitoring and modeled exposure
- Extreme Heat (10%): heat exposure and vulnerability
- Vector-Borne Disease (6%): disease surveillance

Each primary domain gets a weight reflecting how much it contributes to the overall risk score. These weights add up to 100%. Your adaptation will select a profile and then adjust the weights to match your context.

**The PHRAT Formula**: The overall risk score is calculated using a quadratic mean:

    Total Risk = square root of (weight1 x risk1-squared + weight2 x risk2-squared + ... + weightN x riskN-squared)

This formula gives extra emphasis to domains with higher risk scores -- meaning a jurisdiction with one very high risk is scored higher than one with several moderate risks.

**Jurisdictions**: CARA maps risk at the subnational level. Your adaptation will use whatever administrative divisions make sense for your context -- counties, governorates, districts, municipalities, or other units. These are defined in a single configuration file rather than scattered across the codebase.

### Session 2: Planning Your Adaptation (2 hours)

This is the most important session. Before touching any code, the group needs to decide:

**1. What are your jurisdictions?**

Write out a complete list of subnational units you want to assess. For each jurisdiction, you need:
- A unique ID (a short text string: `district_01`, `province_north`, etc.)
- A display name
- The parent region or district it belongs to (if applicable)
- The GADM geographic identifier for boundary mapping (the facilitator can help look these up)

**2. Which profile fits your context?**

The template ships two profiles that control which domains and data connectors are active:

- `us_state`: Designed for US states and territories. Uses US-specific data sources (FEMA, CDC, EPA AirNow, NOAA/NWS). Includes dam failure. Does not include conflict or displacement.
- `international`: Designed for non-US countries and subnational regions. Uses globally available data sources (WHO GHO, ACLED, EM-DAT, World Bank, OpenAQ, NOAA GSOD). Includes conflict and displacement. Does not include dam failure or US-specific feeds.

If neither profile fits precisely, the `custom` profile lets you override individual domain weights while still using whichever connectors you enable.

**3. What risk domains matter for your context?**

The selected profile's domains may not all apply to your jurisdiction. Discuss as a group:

Domains you might keep, remove, or reweight depending on your context:
- Natural Hazards (but with locally relevant hazard types)
- Health Metrics (with locally relevant indicators)
- Extreme Heat (relevant in most climates)
- Air Quality
- Conflict / Displacement (international profile; highly relevant in fragile or conflict-affected settings)
- Mass Casualty / Violence (present in both profiles; adjust weight to context)

Domains you might add beyond the built-in set (requires facilitator-led coding in Session 10):
- Water Scarcity
- Infrastructure Damage
- Supply Chain Disruption
- Food Security

**4. What data sources are available?**

For each domain you keep or add, you need data. Discuss what is available:

International data sources that may be useful:
- INFORM Risk Index (https://drmkc.jrc.ec.europa.eu/inform-index) -- country and subnational risk indicators
- OCHA Humanitarian Data Exchange (https://data.humdata.org) -- health facilities, population, displacement data
- WHO Global Health Observatory (https://www.who.int/data/gho) -- health indicators by country
- EM-DAT International Disaster Database (https://www.emdat.be) -- historical disaster records
- World Bank Open Data (https://data.worldbank.org) -- economic and infrastructure indicators
- ACLED (https://acleddata.com) -- conflict event data (requires free account registration)
- IPC Food Security Classification (https://www.ipcinfo.org) -- food security assessments
- NASA FIRMS (https://firms.modaps.eosdis.nasa.gov) -- fire/hotspot data
- Climate Change Knowledge Portal (https://climateknowledgeportal.worldbank.org)

Local/national data sources to investigate:
- Ministry of Health records and surveillance data
- National statistics office demographic data
- Local meteorological service weather records
- Municipal infrastructure assessments
- Hospital and health facility registries
- Water utility records

For each data source, note:
- What format it is in (CSV, Excel, PDF, API, website)
- How often it is updated
- Whether it covers all your jurisdictions or only some
- Whether it is publicly accessible or requires authorization

**5. What weights should each domain have?**

As a group, decide how much each domain should contribute to the overall risk score. The weights must add up to 1.0 (100%). Document all decisions from this session. You will need them on Day 2.

---

## Workshop Day 2: Setting Up Your Own CARA Instance

### Session 3: Getting the Code (45 minutes)

There are two parts to this: first, getting your own copy of the code on GitHub; second, setting it up so you can run and edit it.

**Part 1: Fork the repository on GitHub**

This creates your own independent copy of the CARA code that you can modify freely.

1. Open a web browser and go to the CARA GitHub repository URL (provided by the facilitator)
2. Make sure you are signed in to your GitHub account
3. Click the "Fork" button in the top-right corner of the page
4. On the fork creation page:
   - Change the "Repository name" to something meaningful, like `cara-[your-country]` or `cara-[your-region]`
   - Optionally add a description
   - Click "Create fork"
5. Wait for the fork to complete. You now have your own copy of the code on GitHub

**Part 2: Set up your development environment**

Choose the option that matches your setup:

**If working on your own computer:**

1. Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux)
2. Navigate to a folder where you want to keep the project:
   ```
   cd Documents
   ```
3. Download your forked repository:
   ```
   git clone https://github.com/your-username/cara-[your-region].git
   ```
   (Replace `your-username` with your GitHub username and `cara-[your-region]` with whatever you named your fork)
4. Move into the project folder:
   ```
   cd cara-[your-region]
   ```
5. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
6. Copy the jurisdiction configuration template to create your working configuration file:
   ```
   cp config/jurisdiction.yaml.example config/jurisdiction.yaml
   ```
   (On Windows: `copy config\jurisdiction.yaml.example config\jurisdiction.yaml`)
7. Set up your PostgreSQL database:
   - Create a new database (for example, named `cara_[region]`)
   - Set the connection information as an environment variable:
     - On Mac/Linux: `export DATABASE_URL="postgresql://username:password@localhost:5432/cara_[region]"`
     - On Windows: `set DATABASE_URL=postgresql://username:password@localhost:5432/cara_[region]`
   - Replace `username` and `password` with your PostgreSQL credentials
8. Set a session secret:
   - On Mac/Linux: `export SESSION_SECRET="any-random-text-here"`
   - On Windows: `set SESSION_SECRET=any-random-text-here`
9. Start the application:
   ```
   python main.py
   ```
10. Open a web browser and go to `http://localhost:5000` -- you should see the CARA home page

**If working on Replit:**

1. Go to https://replit.com and sign in
2. Click "Create Repl" (or the + button)
3. Select "Import from GitHub"
4. Paste the URL of your forked repository
5. Click "Import from GitHub" and wait for the import to complete
6. In Replit, open the Shell tab and run:
   ```
   cp config/jurisdiction.yaml.example config/jurisdiction.yaml
   ```
7. In Replit, set up a PostgreSQL database using the Database tool in the sidebar
8. Click the "Run" button -- CARA should start and a preview window will appear

**If working on another cloud platform:**

Follow that platform's instructions for importing a GitHub repository and setting up a Python application with PostgreSQL. The key requirements are:
- Python 3.9+
- PostgreSQL database
- Copy `config/jurisdiction.yaml.example` to `config/jurisdiction.yaml` before starting
- The `DATABASE_URL` and `SESSION_SECRET` environment variables must be set
- The application starts with `python main.py` (or `gunicorn --bind 0.0.0.0:5000 main:app` for production)

**Part 3: Confirm it works**

However you set things up, verify that:
1. The application starts without errors
2. You can see the CARA home page in a browser
3. You can select one of the example jurisdictions from the template and see a dashboard

If the application does not start, the most common cause is a missing `config/jurisdiction.yaml` file. Check that you completed the copy step above, and that the `DATABASE_URL` and `SESSION_SECRET` environment variables are set. In the next sessions, you will replace the example jurisdiction data with your own.

### Session 4: Understanding the File Structure (30 minutes)

Show participants the key files and folders they will be working with. These files can be opened and edited with any text editor. Participants do not need to understand every file -- only the ones they will change.

**Files you WILL change:**

| File | What it contains | What you will do |
|------|-----------------|-----------------|
| `config/jurisdiction.yaml` | Your jurisdiction profile, geographic settings, and the full list of subdivisions (districts, counties, etc.) | Replace the example settings with your own |
| `config/risk_weights.yaml` | Domain weights and sub-domain weights, organized by profile | Change weights to match your decisions |
| `data/census/[jurisdiction]_demographics.csv` | Population and age data by subdivision | Replace with your demographic data |
| `data/svi/[jurisdiction]_vulnerability_data.json` | Social vulnerability index data | Replace with your vulnerability indicators |
| `templates/index.html` | Home page | Change title, descriptions, jurisdiction labels |
| `templates/base.html` | Page header/footer used on every page | Change application name and branding |
| `static/images/` | Logo and map images | Replace with your own logo and maps |

**Files you might change depending on your domains:**

| File | What it contains |
|------|-----------------|
| `utils/data_processor.py` | Core risk calculation logic -- change if adding domains beyond the built-in set |
| `utils/domains/natural_hazards.py` | Natural hazard calculations -- adapt hazard types |
| `templates/dashboard.html` | Dashboard layout -- update domain display sections |
| `templates/methodology.html` | Methodology explanation page |

**Files you probably will NOT change:**

| File | What it contains |
|------|-----------------|
| `main.py` | Application startup |
| `core.py` | Database and app configuration |
| `models.py` | Database table definitions |
| `gunicorn.conf.py` | Web server settings |
| `static/css/` | Visual styling |
| `static/js/` | Interactive features |
| `utils/risk_engine.py` | The PHRAT scoring formula (no need to change; reads weights from config) |
| `utils/connectors/` | Data source connectors (only change if adding a new custom connector) |

---

## Workshop Day 3: Making the Changes and Adding New Risk Domains

For all of the steps below, open each file in your text editor (Visual Studio Code, Notepad, Replit's editor, or whichever editor you are using). The changes are the same regardless of which editor or platform you use.

After making changes, save the file and restart the application to see the effect. If you are running locally, stop the application (press Ctrl+C in the terminal) and run `python main.py` again. On Replit, click the "Stop" then "Run" buttons.

### Session 5: Configure Your Jurisdiction (1 hour)

This is the first and most important change. Open `config/jurisdiction.yaml`.

All jurisdiction settings live in this single file. It controls the application name, profile, geographic boundaries, administrative structure, and the complete list of your subdivisions. You will update it in three parts.

**Part 1: Top-level settings**

Find the `jurisdiction:` block at the top of the file:

```yaml
jurisdiction:
  name: "Your Jurisdiction Name"
  short_name: "YJN"
  profile: international
  country_code: "XX"
  iso3166_1: "XX"
  language: "en"
  timezone: "UTC"
  population: 0
  area_sq_km: 0
```

Update each field:
- `name`: The full name of your project or jurisdiction (e.g., "Eastern Province Health Authority")
- `short_name`: A short abbreviation used in the interface
- `profile`: Either `us_state` or `international` (choose based on your planning in Session 2)
- `country_code` and `iso3166_1`: Your two-letter ISO country code (e.g., `LY`, `KE`, `CO`)
- `language`: The two-letter language code for your interface (e.g., `en`, `ar`, `fr`)
- `timezone`: Your local timezone in standard format (e.g., `Africa/Tripoli`, `America/Bogota`)
- `population` and `area_sq_km`: Total population and area for your jurisdiction

**Part 2: Geographic settings**

Find the `geographic:` block:

```yaml
  geographic:
    gadm_country: "XX"
    gadm_level: 2
    bounding_box:
      north: 0.0
      south: 0.0
      east: 0.0
      west: 0.0
    center:
      lat: 0.0
      lon: 0.0
```

Update each field:
- `gadm_country`: Your three-letter ISO country code for GADM boundary files (e.g., `LBY`, `KEN`, `COL`)
- `gadm_level`: The administrative level of your subdivisions. Level 1 is typically states or provinces; level 2 is typically districts or counties. Check the GADM website (https://gadm.org) if you are unsure which level applies to your subdivisions
- `bounding_box` and `center`: The geographic extent of your jurisdiction, used for map display. These are decimal degree coordinates (positive = north/east, negative = south/west)

Also update the `administrative_hierarchy:` block to use the correct terms for your context:

```yaml
  administrative_hierarchy:
    level_0: "Country"
    level_1: "Province / State"
    level_2: "District / County"
    level_3: "Municipality / Ward"
    primary_assessment_level: 2
```

Replace the level names with whatever terms are appropriate (e.g., "Governorate", "Shabiyat", "Departamento").

**Part 3: Subdivision list**

Find the `subdivisions:` list. This is the complete list of administrative units you will assess. Replace the example entries with your actual jurisdictions:

```yaml
  subdivisions:
    - id: "district_01"
      name: "District 1"
      level: 2
      gadm_gid: "XX.1.1_1"
```

For each of your subdivisions, add an entry with:
- `id`: A short unique identifier with no spaces (e.g., `district_01`, `province_north`). Can also be a number as a string: `"1"`, `"2"`.
- `name`: The full display name as it should appear on the dashboard
- `level`: The GADM level (should match `gadm_level` above)
- `gadm_gid`: The GADM geographic ID for boundary mapping. The facilitator can help look these up at https://gadm.org. If you do not have GADM IDs yet, you can leave these as placeholder values and update them before deploying.

Notes:
- There is no limit on the number of subdivisions
- Make sure the `id` value is unique across all entries
- Jurisdiction names must be spelled identically here and in all data files (even small differences will cause data mismatches)

### Session 6: Update Risk Weights (30 minutes)

Open `config/risk_weights.yaml`. This file controls how much each domain contributes to the overall score.

The weights are organized under a `profiles:` block. Find the profile that matches what you set in `jurisdiction.yaml` (either `us_state` or `international`):

```yaml
profiles:
  us_state:
    natural_hazards: 0.28
    mass_casualty: 0.18
    health_metrics: 0.17
    air_quality: 0.12
    extreme_heat: 0.11
    dam_failure: 0.07
    vector_borne_disease: 0.07

  international:
    natural_hazards: 0.25
    conflict_displacement: 0.20
    health_metrics: 0.17
    mass_casualty: 0.12
    air_quality: 0.10
    extreme_heat: 0.10
    vector_borne_disease: 0.06
```

Find the block for your selected profile and replace the values with the weights your group decided on in Day 1. For example, if you are using the international profile and want to emphasize health metrics and conflict:

```yaml
  international:
    natural_hazards: 0.20
    conflict_displacement: 0.25
    health_metrics: 0.25
    mass_casualty: 0.10
    air_quality: 0.08
    extreme_heat: 0.07
    vector_borne_disease: 0.05
```

Important rules:
- The values in your active profile must add up to exactly 1.0
- Do not change the key names (e.g., `conflict_displacement`) -- these must match the domain names used in the code
- Only modify the profile block that matches the profile you set in `jurisdiction.yaml`. Leave the others as they are.

If you want to use different weights than either built-in profile provides, switch your profile to `custom` in `jurisdiction.yaml` and fill in all values under the `custom:` block in `risk_weights.yaml`.

### Session 7: Replace Demographic Data (45 minutes)

The template stores demographic data in CSV files in the `data/census/` folder. These are plain text files that can be opened in any text editor or in a spreadsheet application like Excel or Google Sheets.

Create a new file named `data/census/[your_jurisdiction]_demographics.csv` (replace `[your_jurisdiction]` with your jurisdiction name or abbreviation, with no spaces). It should follow this structure:

```
subdivision_name,total_population,population_65_plus,pct_aged_65_plus
District 1,450000,36000,8.0
District 2,220000,17600,8.0
District 3,180000,14400,8.0
```

Keep the same column names. The `subdivision_name` values must match the `name` field in your `config/jurisdiction.yaml` subdivisions list exactly (including capitalization and spacing).

Do the same for housing and infrastructure data in `data/census/[your_jurisdiction]_housing_data.csv`. If this data is not available yet, you can create a placeholder file with the same structure and update it later.

After creating your files, open `utils/data_processor.py` and find the lines that reference the data file paths. Update the filenames to match what you created. The facilitator will help identify the exact lines to change.

### Session 8: Update the User Interface (45 minutes)

Open `templates/base.html` and change:
- The application title from "CARA" to your project name
- Any references to the reference jurisdiction in the header or footer
- The logo image if you have one (place your logo file in the `static/images/` folder)

Open `templates/index.html` and change:
- The welcome text and description
- References to specific jurisdiction counts -- update to describe your jurisdictions
- Any region grouping tabs (such as "HERC Regions") -- rename or remove these if your jurisdiction does not use similar regional structures
- Any context-specific help text

Open `templates/methodology.html` and update:
- The methodology description to reflect your domains and data sources
- The assessment framework section to reflect whichever framework you are using (WHO IHR for international; CDC PHEP for US state)
- Data source citations

### Session 9: Update the Vulnerability Index (30 minutes)

Open `data/svi/[your_jurisdiction]_vulnerability_data.json`. This file contains social vulnerability indicators for each jurisdiction. The format is:

```json
{
  "District 1": {
    "socioeconomic": 0.75,
    "household_disability": 0.65,
    "minority_language": 0.30,
    "housing_transportation": 0.80
  }
}
```

Replace with vulnerability indicators for your jurisdictions. The key names (outer level) must match the `name` values in your subdivision list. If you do not have an SVI equivalent, you can use proxy indicators such as:
- Poverty rate
- Access to healthcare facilities
- Literacy rate
- Infrastructure condition
- Distance from major hospitals

Use values between 0 and 1, where higher values indicate greater vulnerability.

After creating your file, update the path reference in `utils/data_processor.py` to point to your new file. The facilitator will help identify the line to change.

### Session 10: Adding New Risk Domains (1.5 hours)

This session is for when your adaptation needs risk domains that do not exist in the built-in set. The template uses a layered architecture: each domain is a separate module in `utils/domains/` that reads data from one or more connectors in `utils/connectors/`. This structure makes it straightforward to add new domains without changing the core risk engine.

This session requires facilitator guidance. Participants do not need to write code independently -- the facilitator demonstrates each step while participants follow along.

#### Adding a New Domain: Step-by-Step

Example: Adding a "Water Scarcity" domain.

**Step 1: Identify or create your data source**

First, determine where the data will come from:

Option A: An existing connector already fetches relevant data (check the connector files in `utils/connectors/worldwide/` or `utils/connectors/us/`).

Option B: You have a local CSV file with per-jurisdiction values. Create a folder and file for it:

```
data/water/[jurisdiction]_water_scarcity.csv
```

With columns like:
```
subdivision_name,access_to_safe_water_pct,days_of_shortage_per_year,infrastructure_damage_score
District 1,72.0,45,0.35
District 2,58.0,90,0.55
District 3,81.0,20,0.20
```

**Step 2: Create the domain module**

The facilitator will help create a new file `utils/domains/water_scarcity.py`. All domain modules follow the same pattern -- they extend `BaseDomain` from `utils/domains/base_domain.py`:

1. Read data for the requested jurisdiction
2. Normalize each indicator to a 0-1 scale using the base class helper
3. Apply sub-domain weights
4. Return a combined score between 0 and 1

The facilitator can copy an existing domain (such as `utils/domains/extreme_heat.py`) and adapt it, which is faster than writing from scratch.

**Step 3: Register the domain in the connector registry**

Open `utils/connector_registry.py`. The facilitator will add your new domain to the list of domains that get loaded for your profile. This tells the risk engine that your domain exists and should be scored.

**Step 4: Add the weight in risk_weights.yaml**

Add your new domain to the profile block in `config/risk_weights.yaml` and assign it a weight. Reduce other domain weights proportionally so the total still adds up to 1.0:

```yaml
  international:
    natural_hazards: 0.22
    conflict_displacement: 0.20
    health_metrics: 0.17
    water_scarcity: 0.10
    mass_casualty: 0.10
    air_quality: 0.08
    extreme_heat: 0.08
    vector_borne_disease: 0.05
```

**Step 5: Add a dashboard section**

In `templates/dashboard.html`, add a new card section to display the water scarcity score and its components, following the pattern of existing domain sections.

**Step 6: Update the methodology page**

Add a section to `templates/methodology.html` describing your new domain, its data sources, and how the score is calculated.

#### Removing a Domain

To remove a domain you do not need (for example, dam failure is not relevant for landlocked regions without large dams):

1. In `config/risk_weights.yaml`, remove the domain key from your active profile and redistribute its weight among the remaining domains (must still total 1.0)
2. In `templates/dashboard.html`, remove or comment out the dashboard card for that domain
3. In `templates/methodology.html`, remove the methodology description for that domain

The calculation code in `utils/domains/` can be left in place -- it simply will not be called if the weight is removed.

---

## Workshop Day 4: Data Integrity, Validation, and Ethical Considerations

A risk assessment tool is only as valuable as its data is trustworthy and its methods are transparent. These sessions help you build a tool that is honest about what it knows, what it does not know, and how it arrives at its conclusions. Skipping these steps can lead to a tool that looks authoritative but misleads its users.

### Session 11: Data Transparency Audit (30 minutes)

Every score displayed on the dashboard should be traceable back to a specific, citable data source. Walk through each file you created or edited and classify each data point into one of three categories:

**Category 1: Verified data** -- sourced from a named, citable organization with a known publication date and URL.

**Category 2: Estimated data** -- derived from proxy indicators, expert judgment, or extrapolation. Useful for planning but not independently verifiable.

**Category 3: Placeholder data** -- default values (such as 0.5) used because real data is not yet available. The system works with these values, but they carry no analytical meaning.

**Steps:**

1. Open each data file in `data/` and mark next to each column or value which category it falls into
2. Open `templates/methodology.html` and verify that every data source used in the tool is listed with:
   - The exact name of the source organization
   - The URL where the data can be accessed or verified
   - The date or version of the data you are using
   - Any license or terms of use requirements
3. For any data in Category 2 (estimated) or Category 3 (placeholder), add a visible notice. In the dashboard template (`templates/dashboard.html`), you can add a small badge or note next to scores that are not backed by verified data. For example:

```html
<span class="badge bg-warning text-dark">Preliminary estimate</span>
```

4. Check for synthetic data. The original CARA generates some synthetic historical trend data for research and demonstration purposes. Search your codebase for the word "synthetic" or "random" to find any instances. If synthetic data exists in your adaptation:
   - Label it clearly wherever it appears: "SYNTHETIC DATA -- FOR ILLUSTRATION ONLY, NOT FOR OPERATIONAL DECISIONS"
   - Add an explanation on the methodology page distinguishing synthetic data from real observations

**Discussion questions for the group:**
- Which domains have the strongest data? Which are mostly placeholders?
- Could any placeholder data be mistaken for a real measurement by someone using the tool?
- What is our plan and timeline for replacing placeholders with verified data?

### Session 12: Validation and Accuracy (30 minutes)

These steps verify that the risk scores make sense and that the math is working correctly.

**Step 1: Sanity check the scores**

Open dashboards for several jurisdictions you know well and check:
- Does the highest-risk jurisdiction in the group have the highest overall score?
- Does the lowest-risk jurisdiction have the lowest score?
- Are there any jurisdictions where all domain scores are identical? That usually means the system is using default values instead of real data for that jurisdiction.
- Are there any scores at exactly 0.0 or exactly 1.0? These extremes are suspicious and may indicate a data problem or a normalization error.

**Step 2: Verify the formula manually**

Pick one jurisdiction and walk through the PHRAT calculation by hand:

1. Write down each domain score and its weight from `config/risk_weights.yaml`
2. Square each domain score
3. Multiply each squared score by its weight
4. Add up all the weighted squared scores
5. Take the square root of the sum
6. Compare your result to what the dashboard shows

If the numbers match, the formula is working correctly. If they do not match, check whether the weights in the YAML file match the weights being used in `utils/data_processor.py`.

**Step 3: Check data consistency**

Open each data file and verify:
- Every jurisdiction in `config/jurisdiction.yaml` (under `subdivisions:`) has a corresponding row in the demographic CSV, the vulnerability JSON, and all domain data files
- Jurisdiction names are spelled identically across all files (even small differences like "Al Marj" vs "Al-Marj" will cause mismatches)
- All numerical values are within expected ranges (populations are positive, percentages are between 0 and 100, risk scores are between 0 and 1)
- No jurisdiction is listed twice with different data

**Common validation issues:**

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| A jurisdiction shows 0.5 for every domain | Jurisdiction name in data file does not match the `name` in `jurisdiction.yaml` subdivisions | Fix the spelling to match exactly |
| One jurisdiction has an unexpectedly high score | A single data point is an outlier (e.g., a damage amount not normalized) | Check raw data values and normalization |
| Two jurisdictions that should differ have identical scores | They share data because of a name mapping issue | Check that the `name` fields in `jurisdiction.yaml` match the keys in each data file |
| Score changed after updating one data file | A different domain's data file has a dependency on the same variable | Review how vulnerability indicators feed into multiple domains |

### Session 13: Ethical Data Use and Responsible Disclosure (30 minutes)

Risk assessment tools carry real responsibility. Scores can influence resource allocation, emergency response priorities, and public perception of a community. These steps address the ethical dimensions that should be considered before sharing the tool.

**Step 1: Review for potential bias**

Discuss as a group:

- Are any of your data sources or scoring methods likely to systematically score certain types of jurisdictions higher or lower in ways that do not reflect actual risk? For example:
  - Using poverty rates as a proxy for vulnerability may stigmatize lower-income communities by consistently scoring them as "higher risk"
  - Using population density as an infrastructure proxy may unfairly penalize rural areas
  - Using data from only some jurisdictions (and placeholders for others) means the tool is more accurate for some areas than others
- For each concern identified, decide whether to adjust the methodology, add a disclaimer, or both

**Step 2: Add a "Limitations and Responsible Use" section**

Open `templates/methodology.html` and add a clearly visible section near the top that states:

1. **What this tool is for**: Strategic planning, preparedness prioritization, resource allocation discussions, interagency planning workshops
2. **What this tool is NOT for**: Punitive decisions against jurisdictions, public ranking or shaming of communities, sole basis for emergency response deployment, individual-level risk assessment
3. **Known limitations**: List the specific limitations of your data (coverage gaps, timeliness, use of proxy indicators, placeholder values)
4. **Data maturity**: Clearly state which domains use verified data, which use estimates or expert judgment, and which use placeholders
5. **Relative not absolute**: Explain that risk scores are relative comparisons across jurisdictions, not absolute measurements of danger. A score of 0.7 does not mean a 70% chance of disaster.
6. **Not a replacement for local knowledge**: The tool is a decision-support aid. Local expertise, context, and professional judgment should always inform final decisions.
7. **Contact information**: Who to contact with questions about methodology or data

**Step 3: Review data sensitivity**

Discuss as a group:
- Does the tool display any data that could put individuals, communities, or organizations at risk if misused? Examples: exact locations of vulnerable facilities, detailed conflict incident coordinates, identifiable health information
- Is any of the data subject to restrictions on redistribution or public display?
- Should any data be aggregated to a higher geographic level to protect privacy or security?
- Are there any data sources where you need to add attribution or licensing notices?

For any sensitivity concerns identified, decide whether to aggregate the data, restrict access, or add appropriate warnings.

**Step 4: Add source citations**

Add a "Data Sources" section to the methodology page (or the footer) that lists every data source in one place. For each source, include:
- Organization name
- Dataset name
- URL
- Date or version used
- License or terms of use

Anyone using the tool should be able to independently verify every number by following these citations.

### Session 14: Data Governance Planning (20 minutes)

Before moving to deployment, establish practices for maintaining data quality over time.

**Step 1: Create a data freshness inventory**

Create a simple table (in a document or spreadsheet -- not necessarily in the application itself) that lists:

| Data Source | Current Version/Date | Refresh Frequency | Responsible Person | Where to Get Updates |
|-------------|---------------------|-------------------|-------------------|---------------------|
| [Source 1] | [date] | [monthly/quarterly/annually] | [name] | [URL or process] |
| [Source 2] | [date] | [as available] | [name] | [URL or process] |

**Step 2: Document the update process**

For each data source, write down:
1. Where to download or obtain fresh data
2. What format it should be in
3. Which file in the project to replace
4. How to verify the update was applied correctly (e.g., check that jurisdiction count matches, scores changed)

**Step 3: Set a review schedule**

Decide as a group:
- How often will data be refreshed? (monthly, quarterly, annually)
- Who is responsible for each data source?
- How will you track whether data is current or overdue?
- When will you review and potentially adjust domain weights based on experience?

Store this information in a document accessible to everyone who will maintain the tool.

---

## Workshop Day 5: Testing, Refinement, and Deployment

### Session 15: Testing Your Adaptation (45 minutes)

This session covers both functional testing and the data integrity checks from Day 4.

1. Start your application (or restart it if it is already running)
2. Open the home page in a browser
3. Check that the jurisdiction dropdown shows your jurisdiction names
4. Select a jurisdiction and verify the dashboard shows reasonable scores
5. Check each domain section on the dashboard for correct data
6. Test the export features
7. Verify that all data source citations appear on the methodology page
8. Confirm that placeholder values are clearly labeled as preliminary estimates
9. Check that the "Limitations and Responsible Use" section is present and accurate
10. Verify that a user can trace any displayed score back to its underlying data and methodology

Common issues and solutions:

| Problem | Likely cause | Solution |
|---------|-------------|----------|
| Application fails to start with a configuration error | `config/jurisdiction.yaml` is missing | Copy `config/jurisdiction.yaml.example` to `config/jurisdiction.yaml` |
| Jurisdiction dropdown is empty | Error in the `subdivisions:` list in `jurisdiction.yaml` | Check for typos, missing dashes, or incorrect indentation in the YAML file |
| Dashboard shows all zeros | Subdivision names in data files do not match the `name` field in `jurisdiction.yaml` | Make sure names are spelled identically in `jurisdiction.yaml` and in all CSV/JSON data files |
| Application will not start | Syntax error in a file you edited | Check the console/terminal for error messages -- the error usually names the file and line number |
| Risk scores are all the same | Weights are not set correctly | Check that the values in `risk_weights.yaml` for your active profile add up to 1.0 |

### Session 16: Refinement (45 minutes)

Based on testing, discuss as a group:
- Are the risk scores reasonable? Do high-risk areas score higher than low-risk areas?
- Are the domain weights producing the expected relative importance?
- Is any data missing or producing unexpected results?
- What additional data sources should be integrated in the future?
- Are the transparency and limitations disclosures adequate for the intended audience?

### Session 17: Deployment (30 minutes)

Once your adapted CARA is working correctly, you can make it accessible online so others in your organization can use it. There are several options:

**Option A: Replit**

If you developed on Replit, click the "Deploy" button and follow the wizard. Your application will be available at a public URL you can share.

**Option B: Render**

The CARA codebase includes a `render.yaml.example` file for deployment to Render.com (https://render.com). Before using it:
1. Copy `render.yaml.example` to `render.yaml`
2. Update the service name and any environment variable placeholders
3. Create a free Render account, connect your GitHub repository, and Render will build and deploy the application automatically

**Option C: Your organization's servers**

If your organization has its own web servers, the application can be deployed using standard Python web deployment practices. The key requirements are:
- Python 3.9+
- PostgreSQL database
- A process manager like gunicorn (included in the project)
- The `DATABASE_URL` and `SESSION_SECRET` environment variables

**Option D: Any cloud platform**

CARA is a standard Python Flask application and can run on virtually any cloud hosting platform that supports Python, including Railway, PythonAnywhere, DigitalOcean, AWS, Azure, and Google Cloud.

The facilitator can help determine which option is most appropriate for your organization's needs, technical capacity, and data sovereignty requirements.

### Saving Your Work Back to GitHub

Regardless of where you developed, it is important to save your changes back to your GitHub repository so your work is backed up and shareable:

**If working locally:**
1. Open a terminal in your project folder
2. Run these commands:
   ```
   git add .
   git commit -m "Adapted CARA for [your jurisdiction]"
   git push
   ```

**If working on Replit or another cloud platform:**
Most cloud platforms have a built-in way to push changes to GitHub. Check the platform's documentation or ask the facilitator for help.

---

## Quick Reference: File Change Checklist

Use this checklist to track your progress:

**Setup and Adaptation:**
- [ ] `config/jurisdiction.yaml.example` copied to `config/jurisdiction.yaml`
- [ ] `config/jurisdiction.yaml` -- Updated name, profile, country code, and geographic settings
- [ ] `config/jurisdiction.yaml` -- Subdivisions list replaced with your actual jurisdictions
- [ ] `config/risk_weights.yaml` -- Active profile weights updated to match your domain decisions
- [ ] `data/census/[jurisdiction]_demographics.csv` -- Created with your demographic data
- [ ] `data/census/[jurisdiction]_housing_data.csv` -- Created with your housing/infrastructure data
- [ ] `data/svi/[jurisdiction]_vulnerability_data.json` -- Created with your vulnerability indicators
- [ ] `utils/data_processor.py` -- Data file path references updated to your file names
- [ ] `templates/base.html` -- Updated application name and branding
- [ ] `templates/index.html` -- Updated welcome text and jurisdiction descriptions
- [ ] `templates/methodology.html` -- Updated methodology for your context
- [ ] `static/images/` -- Replaced logo and map images
- [ ] New risk domain data files created (if adding domains beyond the built-in set)
- [ ] New risk domain modules created in `utils/domains/` (if adding domains)
- [ ] `utils/connector_registry.py` -- New domain registered (if adding domains)
- [ ] `templates/dashboard.html` -- Updated domain display sections

**Data Integrity and Ethics:**
- [ ] Data transparency audit completed -- all data classified as verified, estimated, or placeholder
- [ ] Placeholder and estimated values labeled visibly on dashboard
- [ ] Synthetic data identified and labeled (if any)
- [ ] Score sanity check -- highest/lowest risk jurisdictions rank correctly
- [ ] PHRAT formula verified manually for at least one jurisdiction
- [ ] Data consistency check -- jurisdiction names match across `jurisdiction.yaml` and all data files
- [ ] Bias review -- discussed potential systematic scoring bias
- [ ] "Limitations and Responsible Use" section added to methodology page
- [ ] Data sensitivity review -- no harmful data exposed
- [ ] All data sources cited with organization, URL, date, and license
- [ ] Data freshness inventory created
- [ ] Data update process documented
- [ ] Review schedule established

**Final Steps:**
- [ ] Tested all jurisdictions load correctly
- [ ] Tested risk scores are reasonable
- [ ] Transparency disclosures verified
- [ ] `render.yaml.example` copied to `render.yaml` and updated (if deploying to Render)
- [ ] Saved changes to GitHub
- [ ] Deployed and shared URL

---

## Appendix A: Suggested Workshop Agenda

| Day | Session | Duration | Topic |
|-----|---------|----------|-------|
| 1 | 1 | 1 hour | What is CARA? Live demo walkthrough |
| 1 | 2 | 2 hours | Planning: profile, jurisdictions, domains, data sources, weights |
| 2 | 3 | 45 min | Getting the code and setting up your environment |
| 2 | 4 | 30 min | Understanding the file structure |
| 3 | 5 | 1 hour | Configuring your jurisdiction (jurisdiction.yaml) |
| 3 | 6 | 30 min | Updating risk weights |
| 3 | 7 | 45 min | Replacing demographic data |
| 3 | 8 | 45 min | Updating the user interface |
| 3 | 9 | 30 min | Updating vulnerability index |
| 3 | 10 | 1.5 hours | Adding/removing risk domains (advanced, facilitator-led) |
| 4 | 11 | 30 min | Data transparency audit |
| 4 | 12 | 30 min | Validation and accuracy |
| 4 | 13 | 30 min | Ethical data use and responsible disclosure |
| 4 | 14 | 20 min | Data governance planning |
| 5 | 15 | 45 min | Comprehensive testing |
| 5 | 16 | 45 min | Refinement |
| 5 | 17 | 30 min | Deployment and saving to GitHub |

---

## Appendix B: Glossary

**Domain**: A category of risk that contributes to the overall score. Examples: Natural Hazards, Health Metrics, Extreme Heat.

**Sub-domain**: A specific risk factor within a domain. Example: "Flood" is a sub-domain of "Natural Hazards."

**Weight**: A number between 0 and 1 that controls how much a domain or sub-domain contributes to the overall score. All weights in a group must add up to 1.0.

**PHRAT**: Public Health Risk Assessment Tool -- the name for the scoring formula used by CARA.

**Profile**: A named configuration (either `us_state` or `international`) that activates a specific set of domains, connectors, and assessment framework. Set in `config/jurisdiction.yaml`.

**Connector**: A software module that fetches data from a specific external source (for example, the WHO GHO connector or the ACLED connector). Connectors are in `utils/connectors/`.

**Domain module**: A software module that reads connector data and calculates a normalized risk score for a specific risk category. Domain modules are in `utils/domains/`.

**Jurisdiction**: A geographic area being assessed. Could be a county, district, governorate, municipality, or other administrative unit.

**Subdivision**: The term used in `config/jurisdiction.yaml` for the individual administrative units you are assessing. Equivalent to "jurisdiction" in common usage.

**SVI (Social Vulnerability Index)**: A set of indicators that measure how vulnerable a population is to health threats based on social factors like poverty, disability, language barriers, and housing conditions.

**EVR Framework**: Exposure-Vulnerability-Resilience -- the approach used for natural hazard risk scoring. Exposure = likelihood of the hazard occurring; Vulnerability = how susceptible the population is; Resilience = capacity to recover.

**WHO IHR**: World Health Organization International Health Regulations -- the assessment framework used by the international profile. Organizes action plans around the 13 IHR core capacity areas.

**CDC PHEP**: Centers for Disease Control and Prevention Public Health Emergency Preparedness -- the assessment framework used by the US state profile. Organizes action plans around the 15 PHEP core capabilities.

**GADM**: Database of Global Administrative Areas (https://gadm.org). Provides standardized geographic boundary files for countries and subnational units worldwide. Used by CARA to draw jurisdiction boundaries on the map.

**Repository**: A project stored on GitHub that contains all the code files, data files, and version history. Think of it as a shared folder that tracks every change.

**Fork**: Creating your own copy of a repository on GitHub so you can modify it independently without affecting the original.

**Clone**: Downloading a copy of a repository from GitHub to your own computer so you can work on it locally.

**Commit**: Saving a snapshot of your changes with a description of what you changed. Like a "save point" you can return to.

**Push**: Uploading your saved changes from your computer (or cloud platform) back to GitHub.

**CSV**: Comma-Separated Values -- a simple spreadsheet format that can be opened in Excel, Google Sheets, or any text editor. Each row is a line, and columns are separated by commas.

**YAML**: A configuration file format used for settings. Uses indentation and colons to organize data. Example: `key: value`. YAML is sensitive to indentation -- use spaces, not tabs.

**Environment variable**: A setting stored outside the code that the application reads when it starts. Used for sensitive information like database passwords and for configuration that varies between environments.

**Terminal / Command Prompt**: A text-based interface for running commands on your computer. Called "Terminal" on Mac/Linux and "Command Prompt" or "PowerShell" on Windows.

---

## Appendix C: Where to Get Help

- CARA source code documentation: See the `docs/` folder in your repository
- GitHub documentation: https://docs.github.com
- Python basics: https://www.python.org/about/gettingstarted/
- PostgreSQL documentation: https://www.postgresql.org/docs/
- Visual Studio Code getting started: https://code.visualstudio.com/docs/getstarted
- GADM administrative boundaries: https://gadm.org
- WHO Global Health Observatory API: https://www.who.int/data/gho/info/gho-odata-api
- ACLED conflict data (registration required): https://acleddata.com
- EM-DAT disaster database (registration required): https://www.emdat.be
- For questions about the CARA methodology, contact the original development team

---

*This guide was developed as part of the CARA open-source project, licensed under AGPLv3.*
*Adapt freely for your workshop context.*
