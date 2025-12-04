#!/usr/bin/env python3
"""
Filter Building_Footprints to only include buildings in the Marina neighborhood.
"""

import json
from shapely.geometry import shape, Point, MultiPolygon, Polygon
from shapely.ops import unary_union

def get_marina_polygon(neighborhoods_file):
    """Extract the Marina neighborhood polygon."""
    with open(neighborhoods_file, 'r') as f:
        data = json.load(f)
    
    for feature in data['features']:
        name = feature['properties'].get('neighborhood') or feature['properties'].get('nhood')
        if name == 'Marina':
            return shape(feature['geometry'])
    
    raise ValueError("Marina neighborhood not found!")

def get_building_centroid(geometry):
    """Get the centroid of a building geometry."""
    geom = shape(geometry)
    return geom.centroid

def filter_buildings(buildings_file, marina_polygon, output_file):
    """Filter buildings to only those within Marina."""
    
    # Read the buildings file line by line to handle large file
    print("Reading buildings file...")
    
    with open(buildings_file, 'r') as f:
        content = f.read()
    
    data = json.loads(content)
    total = len(data['features'])
    print(f"Total buildings: {total}")
    
    marina_buildings = []
    
    for i, feature in enumerate(data['features']):
        if i % 10000 == 0:
            print(f"Processing {i}/{total}...")
        
        try:
            centroid = get_building_centroid(feature['geometry'])
            if marina_polygon.contains(centroid):
                marina_buildings.append(feature)
        except Exception as e:
            # Skip problematic geometries
            continue
    
    print(f"Found {len(marina_buildings)} buildings in Marina")
    
    # Save filtered data
    output_data = {
        "type": "FeatureCollection",
        "features": marina_buildings
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f)
    
    print(f"Saved to {output_file}")

if __name__ == '__main__':
    neighborhoods_file = 'SanFrancisco.Neighborhoods.json'
    buildings_file = 'Building_Footprints_20251202.geojson'
    output_file = 'Marina_Buildings.geojson'
    
    print("Loading Marina neighborhood boundary...")
    marina_polygon = get_marina_polygon(neighborhoods_file)
    print(f"Marina polygon loaded: {marina_polygon.geom_type}")
    
    filter_buildings(buildings_file, marina_polygon, output_file)

