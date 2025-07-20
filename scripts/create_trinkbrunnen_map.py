import json
import folium
from folium import plugins
import webbrowser
import os

def create_trinkbrunnen_map():
    """Create an interactive Folium map of all Berlin Trinkbrunnen"""
    
    # Load the WFS data
    print("Loading Trinkbrunnen data from WFS...")
    with open('../data/berlin_trinkbrunnen_wfs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    features = data['features']
    print(f"Loaded {len(features)} Trinkbrunnen")
    
    # Calculate map center from all coordinates
    lats = []
    lons = []
    for feature in features:
        coords = feature['geometry']['coordinates']
        lons.append(coords[0])
        lats.append(coords[1])
    
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    print(f"Map center: {center_lat:.6f}, {center_lon:.6f}")
    
    # Create the base map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add tile layers
    folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('cartodbdark_matter', name='CartoDB Dark').add_to(m)
    
    # Define colors for different fountain types
    type_colors = {
        'Kaiser Brunnen': 'blue',
        'Wiener Brunnen': 'green', 
        'Botsch Brunnen': 'red',
        'Bituma-Brunnen': 'purple',
        'Unknown': 'gray'
    }
    
    # Count fountain types
    type_counts = {}
    
    # Add markers for each Trinkbrunnen
    for i, feature in enumerate(features):
        coords = feature['geometry']['coordinates']
        props = feature['properties']
        
        # Get fountain type and count
        fountain_type = props.get('typ', 'Unknown')
        type_counts[fountain_type] = type_counts.get(fountain_type, 0) + 1
        
        # Get color for this type
        color = type_colors.get(fountain_type, 'gray')
        
        # Create popup content
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 300px;">
            <h4 style="color: {color}; margin-bottom: 10px;">🚰 {fountain_type}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="font-weight: bold; padding: 3px;">Nummer:</td><td style="padding: 3px;">{props.get('trinkbrunnennummer', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Straße:</td><td style="padding: 3px;">{props.get('strasse', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Einbaujahr:</td><td style="padding: 3px;">{props.get('einbaujahr', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Betriebszustand:</td><td style="padding: 3px;">{props.get('betriebszustand', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Eigentümer:</td><td style="padding: 3px;">{props.get('eigentuemer', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Koordinaten:</td><td style="padding: 3px;">{coords[1]:.6f}, {coords[0]:.6f}</td></tr>
            </table>
        </div>
        """
        
        # Create marker
        folium.CircleMarker(
            location=[coords[1], coords[0]],  # folium expects [lat, lon]
            radius=6,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{fountain_type} - {props.get('strasse', 'N/A')}",
            color='white',
            weight=1,
            fillColor=color,
            fillOpacity=0.8
        ).add_to(m)
    
    # Add marker clusters for better performance
    marker_cluster = plugins.MarkerCluster(name="Trinkbrunnen Cluster").add_to(m)
    
    # Add clustered markers
    for feature in features:
        coords = feature['geometry']['coordinates']
        props = feature['properties']
        fountain_type = props.get('typ', 'Unknown')
        color = type_colors.get(fountain_type, 'gray')
        
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 300px;">
            <h4 style="color: {color}; margin-bottom: 10px;">🚰 {fountain_type}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="font-weight: bold; padding: 3px;">Nummer:</td><td style="padding: 3px;">{props.get('trinkbrunnennummer', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Straße:</td><td style="padding: 3px;">{props.get('strasse', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Einbaujahr:</td><td style="padding: 3px;">{props.get('einbaujahr', 'N/A')}</td></tr>
                <tr><td style="font-weight: bold; padding: 3px;">Betriebszustand:</td><td style="padding: 3px;">{props.get('betriebszustand', 'N/A')}</td></tr>
            </table>
        </div>
        """
        
        folium.Marker(
            location=[coords[1], coords[0]],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{fountain_type}",
            icon=folium.Icon(color=color, icon='tint', prefix='fa')
        ).add_to(marker_cluster)
    
    # Add legend
    legend_html = f"""
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4 style="margin: 0 0 10px 0;">🚰 Trinkbrunnen Berlin</h4>
    <p style="margin: 5px 0;"><b>Gesamt: {len(features)} Brunnen</b></p>
    """
    
    for fountain_type, count in sorted(type_counts.items()):
        color = type_colors.get(fountain_type, 'gray')
        legend_html += f'<p style="margin: 3px 0;"><span style="color: {color};">●</span> {fountain_type}: {count}</p>'
    
    legend_html += """
    <hr style="margin: 10px 0;">
    <p style="margin: 3px 0; font-size: 12px;">Daten: Berliner Wasserbetriebe</p>
    <p style="margin: 3px 0; font-size: 12px;">Quelle: WFS API</p>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add fullscreen button
    plugins.Fullscreen().add_to(m)
    
    # Add measure tool
    plugins.MeasureControl().add_to(m)
    
    # Add search functionality
    # plugins.Search(layer=marker_cluster, search_label='tooltip').add_to(m)
    
    # Save the map
    map_file = 'berlin_trinkbrunnen_map.html'
    m.save(map_file)
    
    print(f"\nMap saved as: {map_file}")
    print(f"Map contains {len(features)} Trinkbrunnen")
    
    # Print statistics
    print("\nTrinkbrunnen Statistics:")
    print("-" * 30)
    for fountain_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(features)) * 100
        print(f"{fountain_type:15}: {count:3d} ({percentage:5.1f}%)")
    
    # Get absolute path for opening
    abs_path = os.path.abspath(map_file)
    print(f"\nMap file location: {abs_path}")
    
    return map_file

def main():
    print("Creating interactive Folium map of Berlin Trinkbrunnen...")
    print("="*60)
    
    try:
        map_file = create_trinkbrunnen_map()
        print(f"\n✅ Success! Interactive map created: {map_file}")
        print("\nMap features:")
        print("- 🗺️  Interactive markers with detailed information")
        print("- 🔍  Clustered view for better performance")
        print("- 🎨  Color-coded by fountain type")
        print("- 📊  Legend with statistics")
        print("- 🔧  Measurement tools")
        print("- 📱  Fullscreen mode")
        print("- 🗂️  Multiple tile layers")
        
    except FileNotFoundError:
        print("❌ Error: ../data/berlin_trinkbrunnen_wfs.json not found!")
        print("Please run fetch_trinkbrunnen_wfs.py first to download the data.")
    except Exception as e:
        print(f"❌ Error creating map: {str(e)}")

if __name__ == "__main__":
    main()