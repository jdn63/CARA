# Hazmat Scoping Pass

Scoping deliverable for a proposed Hazardous Materials risk domain.
No production code, fetchers, weights, or templates were changed by
this pass. Three artifacts:

1. `HAZMAT_SCOPING.md` - methodology proposal, v0 composite formula,
   concerns and open questions for the work group.
2. `county_comparison_v0.md` - 3-county exploratory walk-through
   (Milwaukee, Crawford, Dodge) applying the v0 composite.
3. `source_check_results.md` - auto-generated availability check for
   each candidate public data source. Regenerate with
   `python scripts/hazmat_scoping_check.py`.

Machine-readable inputs are under `data/hazmat_scoping/`.

Recommended reading order: README -> HAZMAT_SCOPING -> county_comparison_v0
-> source_check_results.
