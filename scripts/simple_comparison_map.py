import json
import folium
from folium import plugins
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

def create_simple_comparison_map():
    """Create a simple comparison map with BWB and OSM fountains in different colors"""
    
    print("Creating simple comparison map...")
    
    # Load BWB data
    with open('../data/berlin_trinkbrunnen_wfs.json', 'r', encoding='utf-8') as f:
        bwb_data = json.load(f)
    
    # Get OSM data
    print("Fetching OSM drinking fountains...")
    tags = {'amenity': 'drinking_water'}
    osm_gdf = ox.features_from_place("Berlin, Germany", tags=tags)
    
    # Convert OSM to points
    osm_points = []
    for idx, row in osm_gdf.iterrows():
        geom = row.geometry
        if geom.geom_type == 'Point':
            osm_points.append([geom.y, geom.x])
        else:
            centroid = geom.centroid
            osm_points.append([centroid.y, centroid.x])
    
    # Extract BWB points
    bwb_points = []
    for feature in bwb_data['features']:
        coords = feature['geometry']['coordinates']
        bwb_points.append([coords[1], coords[0]])  # [lat, lon]
    
    # Calculate center
    all_lats = [p[0] for p in osm_points + bwb_points]
    all_lons = [p[1] for p in osm_points + bwb_points]
    center = [sum(all_lats)/len(all_lats), sum(all_lons)/len(all_lons)]
    
    # Create map
    m = folium.Map(location=center, zoom_start=11, tiles='OpenStreetMap')
    
    # Add BWB fountains (red)
    for point in bwb_points:
        folium.CircleMarker(
            location=point,
            radius=5,
            popup="BWB Official",
            tooltip="BWB Fountain",
            color='white',
            weight=1,
            fillColor='red',
            fillOpacity=0.8
        ).add_to(m)
    
    # Add OSM fountains (blue)
    for point in osm_points:
        folium.CircleMarker(
            location=point,
            radius=5,
            popup="OSM Community",
            tooltip="OSM Fountain", 
            color='white',
            weight=1,
            fillColor='blue',
            fillOpacity=0.8
        ).add_to(m)
    
    # Add legend
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 15px">
    <h4 style="margin: 0 0 10px 0;">🚰 Trinkbrunnen</h4>
    <p style="margin: 5px 0;"><span style="color: red;">●</span> BWB Official: {len(bwb_points)}</p>
    <p style="margin: 5px 0;"><span style="color: blue;">●</span> OSM Community: {len(osm_points)}</p>
    <hr style="margin: 10px 0;">
    <p style="margin: 3px 0; font-size: 12px;">Red = Official Data</p>
    <p style="margin: 3px 0; font-size: 12px;">Blue = Community Data</p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add location button (my current location)
    plugins.LocateControl().add_to(m)
    
    # Save
    map_file = 'bwb_vs_osm_simple.html'
    m.save(map_file)
    
    print(f"Simple comparison map saved: {map_file}")
    print(f"BWB (red): {len(bwb_points)} fountains")
    print(f"OSM (blue): {len(osm_points)} fountains")
    
    return map_file

if __name__ == "__main__":
    create_simple_comparison_map()