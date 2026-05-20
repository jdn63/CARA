# Reversal Guide: Re-enable Tribal Jurisdictions in CARA

This file documents the exact reversal steps for the v22 change that
temporarily hid the 11 Tribal jurisdictions from the public dropdown and
blocked direct URL access to Tribal dashboards while Tribal data
sovereignty protocols are finalized.

No Tribal data, calculation logic, database records, GeoJSON files, or
scheduler jobs were modified by v22. Every change is in three source
files plus a help-text string. Reversing them in order restores the
prior behavior exactly.

## Affected jurisdiction IDs

All 11 Tribal entries use IDs that begin with the letter `T`:

    T01  Bad River Band of the Lake Superior Tribe of Chippewa Indians
    T02  Forest County Potawatomi Community
    T03  Ho-Chunk Nation
    T04  Lac Courte Oreilles Band of Lake Superior Chippewa Indians
    T05  Lac du Flambeau Band of Lake Superior Chippewa Indians
    T06  Menominee Indian Tribe of Wisconsin
    T07  Oneida Nation
    T08  Red Cliff Band of Lake Superior Chippewa
    T09  Sokaogon Chippewa Community (Mole Lake Band)
    T10  St. Croix Chippewa Indians of Wisconsin
    T11  Stockbridge-Munsee Community

Any ID-prefix logic added in v22 keys on the literal leading character
`T`; reversing the changes below removes every reference to that prefix.

## Step 1: utils/data_processor.py

In `get_wi_jurisdictions()`, delete the following block that was
inserted immediately after the existing `primary` filter (look for the
`TRIBAL HIDE` marker comment):

    # TRIBAL HIDE: Temporarily exclude Tribal jurisdictions (IDs starting with 'T')
    # from the public dropdown while Tribal data sovereignty protocols are finalized.
    # To restore: remove the four lines below (the comment and the if/continue block).
    # Also restore the help text in templates/index.html and remove the guard in
    # routes/dashboard.py. See .local/tribal_access_reversal.md for full instructions.
    if str(jurisdiction.get('id', '')).startswith('T'):
        continue

After deletion, the function body proceeds directly from the
`if not jurisdiction.get('primary', True): continue` block into the
`j = dict(jurisdiction)` copy as it did before v22.

## Step 2: routes/dashboard.py

Two edits in this file.

Edit 2a (imports, line ~14): the `flash` symbol was added to the Flask
import for the redirect message. If no other route in this file uses
`flash`, restore the import line to its prior form:

    from flask import Blueprint, render_template, redirect, url_for, send_file

(If a future change introduces another use of `flash` in this file,
leave the import alone.)

Edit 2b (top of the `dashboard()` route, inside the outer `try:`):
remove the entire `TRIBAL HIDE` guard block that was inserted as the
first statement of the try. The block to delete reads exactly:

    # TRIBAL HIDE: Block direct URL access to Tribal dashboards while
    # Tribal data sovereignty protocols are finalized. To restore Tribal
    # access, remove this block (the comment and the if/flash/redirect).
    # See .local/tribal_access_reversal.md for full reversal instructions.
    if str(jurisdiction_id).startswith('T'):
        flash(
            "Tribal jurisdiction dashboards are temporarily unavailable "
            "while we finalize data access protocols with our Tribal partners.",
            "info"
        )
        return redirect(url_for('public.index'))

After deletion, the first statement inside the `try:` is the existing
`if jurisdiction_id in ID_MAPPING:` check.

## Step 3: templates/index.html

Around line 63 (inside the jurisdiction dropdown form), restore the
prior help-text string. Replace:

    Select from 84 local public health agencies

with the original wording:

    Select from 84 local public health agencies and 11 tribal health centers

## Step 4: VERSION.txt

Bump the `Push:` line to the next version (v23 or whatever the current
release sequence requires) and add a changelog entry describing the
restoration, for example:

    - v23: Restore Tribal jurisdictions in public dropdown and dashboard
      after Tribal data sovereignty protocol finalization. Reverses v22.

The v22 changelog entry can be left in place for history.

## Step 5: Delete this guide

After reversal, this file (`.local/tribal_access_reversal.md`) can be
deleted since it documents a hide that no longer exists.

## Post-reversal verification checklist

1. Start the app and open the home page. The dropdown lists 95
   jurisdictions (84 local public health agencies plus 11 Tribal
   entries) and the help text reads "Select from 84 local public
   health agencies and 11 tribal health centers".
2. Select any Tribal entry from the dropdown and confirm the dashboard
   loads (HTTP 200) and renders without a redirect to the home page.
3. Hit a Tribal dashboard URL directly (for example `/dashboard/T06`
   for Menominee) and confirm the dashboard renders.
4. Hit a non-Tribal dashboard URL (for example `/dashboard/16` for
   Milwaukee) and confirm nothing about the local-jurisdiction code
   path regressed.
5. Search the repository for the literal string `TRIBAL HIDE` to
   confirm zero matches remain.
