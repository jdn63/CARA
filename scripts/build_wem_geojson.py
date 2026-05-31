"""One-shot: build data/geojson/wisconsin_wem_regions.geojson by grouping
county polygons under their WEM region. No shapely dependency: each region
becomes a MultiPolygon whose member polygons are the constituent county
geometries (county boundaries remain visible inside a region, which is
acceptable for the WEM regional surface and visually informative).

Run: python -m scripts.build_wem_geojson
"""

import json
import os
import sys
from collections import defaultdict

WI_COUNTIES = 'data/tribal/wisconsin_counties.geojson'
OUT = 'data/geojson/wisconsin_wem_regions.geojson'


def main():
    sys.path.insert(0, os.path.abspath('.'))
    from utils.wem_data import get_all_wem_regions

    regions = get_all_wem_regions()
    county_to_region = {}
    region_meta = {}
    for r in regions:
        rid = r['id']
        region_meta[rid] = {
            'id': rid,
            'name': r['name'],
            'color': r.get('color', '#666666'),
            'counties': r.get('counties', []),
        }
        for c in r.get('counties', []):
            county_to_region[c] = rid

    with open(WI_COUNTIES) as f:
        counties_gj = json.load(f)

    # region_id -> list of (polygon coordinates, geometry type)
    grouped = defaultdict(list)
    unmatched = []
    for feat in counties_gj['features']:
        name = feat['properties'].get('NAME')
        rid = county_to_region.get(name)
        if not rid:
            unmatched.append(name)
            continue
        geom = feat['geometry']
        gtype = geom['type']
        if gtype == 'Polygon':
            grouped[rid].append(geom['coordinates'])
        elif gtype == 'MultiPolygon':
            grouped[rid].extend(geom['coordinates'])
        else:
            print(f"Skipping unsupported geometry type {gtype} for {name}")

    if unmatched:
        print(f"WARNING: unmatched counties in GeoJSON: {unmatched}")

    features = []
    for rid in sorted(grouped.keys()):
        meta = region_meta[rid]
        features.append({
            'type': 'Feature',
            'properties': {
                'wem_id': rid,
                'name': meta['name'],
                'color': meta['color'],
                'counties': meta['counties'],
                'county_count': len(meta['counties']),
            },
            'geometry': {
                'type': 'MultiPolygon',
                'coordinates': grouped[rid],
            },
        })

    out_gj = {'type': 'FeatureCollection', 'features': features}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(out_gj, f)
    print(f"Wrote {len(features)} WEM region features to {OUT}")


if __name__ == '__main__':
    main()
