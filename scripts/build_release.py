"""
CARA Release Build Script

Builds versioned zip archives for the two public GitHub repositories:
  - CARA (full production codebase)
  - CARA-template (public template release)

Run from the project root:
  python scripts/build_release.py [--version 2.5]

The script applies a consistent include/exclude pattern to both archives,
preventing stale or internal files from being included.
"""

import argparse
import os
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    '.agents',
    '.git',
    '.local',
    '.pytest_cache',
    '__pycache__',
    'agents',          # Replit internal metadata
    'artifacts',
    'attached_assets',
    'cache',           # data/cache — generated cache files, never shipped
    'cara_template',
    'exports',
    'logs',
    'screenshots',     # development screenshots
}

EXCLUDE_FILES = {
    'CODE_REVIEW_ANALYSIS.md',
    '.DS_Store',
    'replit.md',
    'replit.nix',
    'uv.lock',
    'UPGRADE_PLAN.md',
}

EXCLUDE_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.xlsx',
    '.zip',
    # Raw statistical dataset formats and research artifacts. The runtime only
    # needs the SPSS .sav file (data/nces/pu_ssocs20.sav); every other format
    # (.dta Stata, .sas7bdat SAS, .dat ASCII) and the import scripts
    # (.do/.sas/.sps) are redundant copies of the same data and must never ship.
    # .pdf covers research codebooks/papers that are not part of the web app.
    '.pdf',
    '.dta',
    '.sas7bdat',
    '.dat',
    '.do',
    '.sas',
    '.sps',
}

EXCLUDE_PATTERNS = {
    'all_direct_imports.txt',
    'existing_routes.txt',
    'existing_utils.txt',
    'imported_routes.txt',
    'imported_utils.txt',
    'mod_direct.txt',
    'mod_from.txt',
    # NCES distribution readme that duplicates data/nces/README.md.
    'pu_ssocs20_readme.txt',
}

ALLOWED_HIDDEN_NAMES = {'.env.example', '.gitignore', '.gitattributes', '.github'}


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if set(parts) & EXCLUDE_DIRS:
        return True
    # Exclude anything inside a hidden directory (any path part starting
    # with '.' that isn't an allowlisted name). Catches .cache, .config,
    # .pythonlibs, .upm, .pytest_cache, etc. without needing to enumerate.
    for part in parts[:-1]:
        if part.startswith('.') and part not in ALLOWED_HIDDEN_NAMES:
            return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    if rel_path.suffix in EXCLUDE_EXTENSIONS:
        return True
    if name in EXCLUDE_PATTERNS:
        return True
    # Per-region statistics JSON files (data/wem, data/herc) are empty
    # placeholders regenerated on demand at runtime; never ship them.
    if name.startswith('region_') and name.endswith('_statistics.json'):
        return True
    # config/jurisdiction.yaml is a deployment-specific runtime artifact (the
    # template ships only jurisdiction.yaml.example + config/samples/). It can
    # be created on disk by smoke runs; never ship or commit it.
    if rel_path.as_posix() == 'config/jurisdiction.yaml':
        return True
    if name.startswith('.') and name not in ALLOWED_HIDDEN_NAMES:
        return True
    if rel_path.name == 'tribal_territories.json':
        stat = (ROOT / rel_path).stat()
        if stat.st_size == 0 or stat.st_size < 10:
            return True
    return False


def collect_files():
    collected = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if should_exclude(rel):
            continue
        collected.append((path, rel))
    return collected


def collect_template_files():
    """
    Collect files for the CARA-template release.

    The template lives in cara_template/ (which collect_files() deliberately
    excludes from the Wisconsin archive). The template zip must be rooted at
    cara_template/ so the archive contents sit at the top level, exactly as the
    CARA-template GitHub repository expects. The same exclude rules apply, with
    paths evaluated relative to the template directory.
    """
    base = ROOT / 'cara_template'
    collected = []
    for path in sorted(base.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(base)
        if should_exclude(rel):
            continue
        collected.append((path, rel))
    return collected


def build_zip(output_name: str, files: list, version: str) -> Path:
    out_path = ROOT / output_name
    skipped = 0
    with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for abs_path, rel_path in files:
            try:
                zf.write(abs_path, rel_path)
            except ValueError as e:
                # zipfile rejects timestamps before 1980. Rewrite using
                # the current mtime instead of dropping the file.
                if 'timestamps before 1980' in str(e):
                    with open(abs_path, 'rb') as src:
                        info = zipfile.ZipInfo(str(rel_path))
                        info.compress_type = zipfile.ZIP_DEFLATED
                        zf.writestr(info, src.read())
                    skipped += 1
                else:
                    raise
    if skipped:
        print(f'  Note: rewrote {skipped} files with pre-1980 timestamps.')
    return out_path


def main():
    parser = argparse.ArgumentParser(description='Build CARA release zip archives.')
    parser.add_argument('--version', default=None, help='Version string (e.g. 2.5)')
    args = parser.parse_args()

    version = args.version or 'dev'
    today = date.today().isoformat()

    print(f'Building CARA release archives — version {version}, date {today}')
    print(f'Root: {ROOT}')

    files = collect_files()
    print(f'Collected {len(files)} files for the Wisconsin archive.')

    template_files = collect_template_files()
    print(f'Collected {len(template_files)} files for the template archive.')

    cara_zip_name = f'cara_wisconsin_updated.zip'
    template_zip_name = f'cara_template_updated.zip'

    cara_zip = build_zip(cara_zip_name, files, version)
    print(f'Created: {cara_zip}  ({cara_zip.stat().st_size // 1024} KB, {len(files)} files)')

    template_zip = build_zip(template_zip_name, template_files, version)
    print(f'Created: {template_zip}  ({template_zip.stat().st_size // 1024} KB, {len(template_files)} files)')

    print('Done.')


if __name__ == '__main__':
    main()
