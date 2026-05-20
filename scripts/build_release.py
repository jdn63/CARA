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
    'artifacts',
    'attached_assets',
    'cara_template',
    'exports',
    'logs',
}

EXCLUDE_FILES = {
    'CODE_REVIEW_ANALYSIS.md',
    '.DS_Store',
    'replit.md',
    'replit.nix',
    'uv.lock',
}

EXCLUDE_EXTENSIONS = {
    '.pyc',
    '.pyo',
    '.xlsx',
    '.zip',
}

EXCLUDE_PATTERNS = {
    'all_direct_imports.txt',
    'existing_routes.txt',
    'existing_utils.txt',
    'imported_routes.txt',
    'imported_utils.txt',
    'mod_direct.txt',
    'mod_from.txt',
    'pu_ssocs20.sas7bdat',
    'pu_ssocs20_ASCII.dat',
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
    print(f'Collected {len(files)} files for inclusion.')

    cara_zip_name = f'cara_wisconsin_github.zip'
    template_zip_name = f'cara_template_github.zip'

    cara_zip = build_zip(cara_zip_name, files, version)
    print(f'Created: {cara_zip}  ({cara_zip.stat().st_size // 1024} KB, {len(files)} files)')

    template_zip = build_zip(template_zip_name, files, version)
    print(f'Created: {template_zip}  ({template_zip.stat().st_size // 1024} KB, {len(files)} files)')

    print('Done.')


if __name__ == '__main__':
    main()
