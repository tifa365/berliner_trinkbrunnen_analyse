import json
import pandas as pd
import geopandas as gpd
import osmnx as ox
import folium
from folium import plugins
import numpy as np
from shapely.geometry import Point
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

def fetch_osm_drinking_fountains():
    """Fetch drinking fountain data from OpenStreetMap for Berlin"""
    
    print("Fetching drinking fountains from OpenStreetMap...")
    
    # Define Berlin boundary
    berlin = ox.geocode_to_gdf("Berlin, Germany")
    
    # Define tags for drinking fountains
    tags = {
        'amenity': 'drinking_water'
    }
    
    try:
        # Fetch drinking water features
        drinking_water = ox.features_from_place("Berlin, Germany", tags=tags)
        
        print(f"Found {len(drinking_water)} drinking water features in OSM")
        
        # Convert to points (some might be polygons)
        points = []
        for idx, row in drinking_water.iterrows():
            geom = row.geometry
            if geom.geom_type == 'Point':
                points.append({
                    'osm_id': row.name[1] if isinstance(row.name, tuple) else row.name,
                    'osm_type': row.name[0] if isinstance(row.name, tuple) else 'unknown',
                    'lat': geom.y,
                    'lon': geom.x,
                    'name': row.get('name', ''),
                    'operator': row.get('operator', ''),
                    'source': row.get('source', ''),
                    'description': row.get('description', ''),
                    'website': row.get('website', ''),
                    'geometry': geom
                })
            elif geom.geom_type in ['Polygon', 'MultiPolygon']:
                # Use centroid for polygons
                centroid = geom.centroid
                points.append({
                    'osm_id': row.name[1] if isinstance(row.name, tuple) else row.name,
                    'osm_type': row.name[0] if isinstance(row.name, tuple) else 'unknown',
                    'lat': centroid.y,
                    'lon': centroid.x,
                    'name': row.get('name', ''),
                    'operator': row.get('operator', ''),
                    'source': row.get('source', ''),
                    'description': row.get('description', ''),
                    'website': row.get('website', ''),
                    'geometry': centroid
                })
        
        osm_df = pd.DataFrame(points)
        print(f"Converted to {len(osm_df)} point features")
        
        return osm_df
        
    except Exception as e:
        print(f"Error fetching OSM data: {str(e)}")
        return pd.DataFrame()

def load_bwb_data():
    """Load the official BWB Trinkbrunnen data"""
    
    print("Loading official BWB Trinkbrunnen data...")
    
    with open('../data/berlin_trinkbrunnen_wfs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    bwb_points = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        props = feature['properties']
        
        bwb_points.append({
            'bwb_id': props.get('oid', ''),
            'nummer': props.get('trinkbrunnennummer', ''),
            'typ': props.get('typ', ''),
            'strasse': props.get('strasse', ''),
            'einbaujahr': props.get('einbaujahr', ''),
            'betriebszustand': props.get('betriebszustand', ''),
            'lat': coords[1],
            'lon': coords[0],
            'geometry': Point(coords[0], coords[1])
        })
    
    bwb_df = pd.DataFrame(bwb_points)
    print(f"Loaded {len(bwb_df)} BWB Trinkbrunnen")
    
    return bwb_df

def find_matches(osm_df, bwb_df, max_distance_m=50):
    """Find matches between OSM and BWB data based on proximity"""
    
    print(f"\nFinding matches within {max_distance_m}m...")
    
    matches = []
    osm_matched = set()
    bwb_matched = set()
    
    for i, osm_row in osm_df.iterrows():
        osm_point = (osm_row['lat'], osm_row['lon'])
        
        closest_distance = float('inf')
        closest_bwb_idx = None
        
        for j, bwb_row in bwb_df.iterrows():
            if j in bwb_matched:
                continue
                
            bwb_point = (bwb_row['lat'], bwb_row['lon'])
            distance = geodesic(osm_point, bwb_point).meters
            
            if distance < max_distance_m and distance < closest_distance:
                closest_distance = distance
                closest_bwb_idx = j
        
        if closest_bwb_idx is not None:
            matches.append({
                'osm_idx': i,
                'bwb_idx': closest_bwb_idx,
                'distance_m': closest_distance,
                'osm_id': osm_row['osm_id'],
                'bwb_id': bwb_df.iloc[closest_bwb_idx]['bwb_id'],
                'osm_operator': osm_row['operator'],
                'bwb_typ': bwb_df.iloc[closest_bwb_idx]['typ']
            })
            osm_matched.add(i)
            bwb_matched.add(closest_bwb_idx)
    
    matches_df = pd.DataFrame(matches)
    
    # Identify unmatched entries
    osm_unmatched = osm_df[~osm_df.index.isin(osm_matched)].copy()
    bwb_unmatched = bwb_df[~bwb_df.index.isin(bwb_matched)].copy()
    
    print(f"Found {len(matches_df)} matches")
    print(f"OSM unmatched: {len(osm_unmatched)}")
    print(f"BWB unmatched: {len(bwb_unmatched)}")
    
    return matches_df, osm_unmatched, bwb_unmatched

def create_comparison_map(osm_df, bwb_df, matches_df, osm_unmatched, bwb_unmatched):
    """Create a Folium map comparing OSM and BWB data"""
    
    print("\nCreating comparison map...")
    
    # Calculate map center
    all_lats = list(osm_df['lat']) + list(bwb_df['lat'])
    all_lons = list(osm_df['lon']) + list(bwb_df['lon'])
    center_lat = sum(all_lats) / len(all_lats)
    center_lon = sum(all_lons) / len(all_lons)
    
    # Create base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add tile layers
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
    
    # Create feature groups for different datasets
    bwb_group = folium.FeatureGroup(name='BWB Official (244)', show=True)
    osm_group = folium.FeatureGroup(name='OSM Data', show=True)
    matches_group = folium.FeatureGroup(name='Matches', show=True)
    
    # Add BWB unmatched fountains (red)
    for idx, row in bwb_unmatched.iterrows():
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 250px;">
            <h4 style="color: red; margin-bottom: 10px;">🚰 BWB Only</h4>
            <p><b>Type:</b> {row['typ']}</p>
            <p><b>Number:</b> {row['nummer']}</p>
            <p><b>Street:</b> {row['strasse']}</p>
            <p><b>Year:</b> {row['einbaujahr']}</p>
            <p><b>Status:</b> {row['betriebszustand']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"BWB Only: {row['typ']}",
            color='white',
            weight=2,
            fillColor='red',
            fillOpacity=0.8
        ).add_to(bwb_group)
    
    # Add OSM unmatched fountains (blue)
    for idx, row in osm_unmatched.iterrows():
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 250px;">
            <h4 style="color: blue; margin-bottom: 10px;">💧 OSM Only</h4>
            <p><b>OSM ID:</b> {row['osm_id']}</p>
            <p><b>Name:</b> {row['name'] or 'N/A'}</p>
            <p><b>Operator:</b> {row['operator'] or 'N/A'}</p>
            <p><b>Source:</b> {row['source'] or 'N/A'}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"OSM Only: {row['name'] or 'Drinking Water'}",
            color='white',
            weight=2,
            fillColor='blue',
            fillOpacity=0.8
        ).add_to(osm_group)
    
    # Add matched fountains (green)
    for idx, match in matches_df.iterrows():
        osm_row = osm_df.iloc[match['osm_idx']]
        bwb_row = bwb_df.iloc[match['bwb_idx']]
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 300px;">
            <h4 style="color: green; margin-bottom: 10px;">✅ Matched</h4>
            <p><b>Distance:</b> {match['distance_m']:.1f}m</p>
            <hr>
            <h5>BWB Data:</h5>
            <p><b>Type:</b> {bwb_row['typ']}</p>
            <p><b>Street:</b> {bwb_row['strasse']}</p>
            <p><b>Number:</b> {bwb_row['nummer']}</p>
            <hr>
            <h5>OSM Data:</h5>
            <p><b>OSM ID:</b> {osm_row['osm_id']}</p>
            <p><b>Operator:</b> {osm_row['operator'] or 'N/A'}</p>
            <p><b>Name:</b> {osm_row['name'] or 'N/A'}</p>
        </div>
        """
        
        # Use BWB coordinates as the primary location
        folium.CircleMarker(
            location=[bwb_row['lat'], bwb_row['lon']],
            radius=8,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"Match: {bwb_row['typ']}",
            color='white',
            weight=2,
            fillColor='green',
            fillOpacity=0.8
        ).add_to(matches_group)
        
        # Draw line between matched points if they're far apart
        if match['distance_m'] > 10:
            folium.PolyLine(
                locations=[[bwb_row['lat'], bwb_row['lon']], [osm_row['lat'], osm_row['lon']]],
                color='green',
                weight=2,
                opacity=0.6
            ).add_to(matches_group)
    
    # Add feature groups to map
    bwb_group.add_to(m)
    osm_group.add_to(m)
    matches_group.add_to(m)
    
    # Add legend
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 15px">
    <h4 style="margin: 0 0 10px 0;">🚰 Trinkbrunnen Comparison</h4>
    
    <h5 style="margin: 10px 0 5px 0;">Statistics:</h5>
    <p style="margin: 3px 0;"><span style="color: green;">●</span> Matches: {len(matches_df)}</p>
    <p style="margin: 3px 0;"><span style="color: red;">●</span> BWB Only: {len(bwb_unmatched)}</p>
    <p style="margin: 3px 0;"><span style="color: blue;">●</span> OSM Only: {len(osm_unmatched)}</p>
    
    <hr style="margin: 10px 0;">
    <p style="margin: 3px 0;"><b>Total BWB:</b> {len(bwb_df)}</p>
    <p style="margin: 3px 0;"><b>Total OSM:</b> {len(osm_df)}</p>
    
    <hr style="margin: 10px 0;">
    <p style="margin: 3px 0; font-size: 12px;">Coverage: {len(matches_df)/len(bwb_df)*100:.1f}%</p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add location button (my current location)
    plugins.LocateControl().add_to(m)
    
    # Add fullscreen
    plugins.Fullscreen().add_to(m)
    
    # Save map
    map_file = 'trinkbrunnen_osm_vs_bwb_comparison.html'
    m.save(map_file)
    
    print(f"Comparison map saved as: {map_file}")
    return map_file

def generate_analysis_report(osm_df, bwb_df, matches_df, osm_unmatched, bwb_unmatched):
    """Generate a detailed analysis report"""
    
    print("\n" + "="*60)
    print("TRINKBRUNNEN DATA COMPARISON ANALYSIS")
    print("="*60)
    
    print(f"\n📊 DATASET OVERVIEW:")
    print(f"BWB Official Data:     {len(bwb_df):3d} fountains")
    print(f"OSM Community Data:    {len(osm_df):3d} fountains")
    print(f"Matches found:         {len(matches_df):3d} fountains")
    print(f"Coverage rate:         {len(matches_df)/len(bwb_df)*100:5.1f}%")
    
    print(f"\n🔍 DETAILED BREAKDOWN:")
    print(f"BWB fountains in OSM:  {len(matches_df):3d} ({len(matches_df)/len(bwb_df)*100:5.1f}%)")
    print(f"BWB fountains missing: {len(bwb_unmatched):3d} ({len(bwb_unmatched)/len(bwb_df)*100:5.1f}%)")
    print(f"OSM additional fountains: {len(osm_unmatched):3d}")
    
    if len(matches_df) > 0:
        print(f"\n📏 MATCH QUALITY:")
        print(f"Average distance:      {matches_df['distance_m'].mean():5.1f}m")
        print(f"Median distance:       {matches_df['distance_m'].median():5.1f}m")
        print(f"Max distance:          {matches_df['distance_m'].max():5.1f}m")
        
        close_matches = len(matches_df[matches_df['distance_m'] <= 10])
        print(f"Very close matches (≤10m): {close_matches} ({close_matches/len(matches_df)*100:.1f}%)")
    
    # Analyze BWB fountain types in unmatched
    if len(bwb_unmatched) > 0:
        print(f"\n🚰 MISSING BWB FOUNTAIN TYPES:")
        missing_types = bwb_unmatched['typ'].value_counts()
        for typ, count in missing_types.items():
            print(f"  {typ:15}: {count:3d}")
    
    # Analyze OSM operators
    if len(osm_df) > 0:
        print(f"\n💧 OSM FOUNTAIN OPERATORS:")
        operators = osm_df['operator'].value_counts()
        for operator, count in operators.head(5).items():
            if operator:
                print(f"  {operator:20}: {count:3d}")
    
    print(f"\n📅 BWB INSTALLATION YEARS:")
    years = bwb_df['einbaujahr'].value_counts().sort_index()
    for year, count in years.tail(5).items():
        if year and year != 'null':
            print(f"  {year}: {count:3d} fountains")

def main():
    print("Comparing OSM and BWB Trinkbrunnen data for Berlin...")
    print("="*60)
    
    try:
        # Load BWB data
        bwb_df = load_bwb_data()
        
        # Fetch OSM data
        osm_df = fetch_osm_drinking_fountains()
        
        if len(osm_df) == 0:
            print("❌ No OSM data found. Cannot perform comparison.")
            return
        
        # Find matches
        matches_df, osm_unmatched, bwb_unmatched = find_matches(osm_df, bwb_df)
        
        # Create comparison map
        map_file = create_comparison_map(osm_df, bwb_df, matches_df, osm_unmatched, bwb_unmatched)
        
        # Generate analysis report
        generate_analysis_report(osm_df, bwb_df, matches_df, osm_unmatched, bwb_unmatched)
        
        print(f"\n✅ Analysis complete! View the interactive map: {map_file}")
        
    except FileNotFoundError:
        print("❌ Error: ../data/berlin_trinkbrunnen_wfs.json not found!")
        print("Please run fetch_trinkbrunnen_wfs.py first to download the BWB data.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()