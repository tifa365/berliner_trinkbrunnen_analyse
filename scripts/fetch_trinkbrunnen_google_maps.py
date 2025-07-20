import requests
import json
import re

def extract_features_from_kml_response(response_text):
    """Extract feature IDs from the KML overlay service response"""
    # Find the array of feature IDs
    match = re.search(r'\[\[(.*?)\]\]', response_text)
    if not match:
        return []
    
    # Extract all feature IDs (strings starting with 'g')
    feature_ids = re.findall(r'"(g[a-z0-9]+)"', match.group(0))
    return feature_ids

def fetch_feature_details(feature_id, kml_id, api_key):
    """Fetch details for a specific feature from Google Maps API"""
    url = f"https://maps.googleapis.com/maps/api/js/KmlOverlayService.GetFeature"
    params = {
        '1s': f'kml:{kml_id}',
        '2s': feature_id,
        '3m2': '',
        '1sks': '',
        '2sts': '58433143',
        '1skv': '',
        '2s': '3',
        '1sapi': '',
        '1sclient': '',
        'callback': '_xdc_._callback',
        'key': api_key,
        'token': '125045'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'DNT': '1'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            # Extract JSON data from JSONP response
            text = response.text
            # Remove the callback wrapper
            json_match = re.search(r'_xdc_\._callback\s*&&\s*_xdc_\._callback\s*\((.*)\)', text)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
    except Exception as e:
        print(f"Error fetching feature {feature_id}: {str(e)}")
    
    return None

def parse_kml_overlay_file():
    """Parse the existing KmlOverlayService file to extract feature IDs"""
    with open('../data/raw/KmlOverlayService (1).js', 'r') as f:
        content = f.read()
    
    # Extract the KML ID
    kml_match = re.search(r'"kml:([^"]+)"', content)
    kml_id = kml_match.group(1) if kml_match else None
    
    # Extract all feature IDs
    feature_ids = re.findall(r'"(g[a-z0-9]+)"', content)
    
    # Extract bounding box
    bbox_match = re.search(r'\[\[([0-9.]+),([0-9.]+)\],\[([0-9.]+),([0-9.]+)\]\]', content)
    bbox = None
    if bbox_match:
        bbox = {
            'south': float(bbox_match.group(1)),
            'west': float(bbox_match.group(2)),
            'north': float(bbox_match.group(3)),
            'east': float(bbox_match.group(4))
        }
    
    return kml_id, feature_ids, bbox

def fetch_tile_data(kml_id, tile_coords, api_key):
    """Fetch map tile data containing feature information"""
    base_url = "https://maps.google.com/maps/vt"
    
    # Construct the protobuf parameter
    pb = f"!1m5!1m4!1i10!2i{tile_coords[0]}!3i{tile_coords[1]}!4i256!2m15!1e2!2skml%3A{kml_id}!4m2!1sks!2sts%3A58433143!4m2!1skv!2s3!4m2!1sapi!2s3!4m2!1sclient!2s2!5i1!3m3!2sde!3sUS!5e18!4e0!5m1!1e3!23i46991212!23i47054750"
    
    params = {
        'pb': pb,
        'key': api_key
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'DNT': '1'
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print(f"Error fetching tile {tile_coords}: {str(e)}")
    
    return None

def main():
    print("Extracting Trinkbrunnen data from Google Maps KML...")
    print("="*60)
    
    # Parse the existing file
    kml_id, feature_ids, bbox = parse_kml_overlay_file()
    
    print(f"Found KML ID: {kml_id}")
    print(f"Found {len(feature_ids)} feature IDs")
    print(f"Bounding box: {bbox}")
    
    # Create a simple JSON structure with the available data
    trinkbrunnen_data = {
        "type": "FeatureCollection",
        "properties": {
            "name": "Trinkbrunnen Berlin",
            "source": "Google Maps KML",
            "kml_id": kml_id,
            "feature_count": len(feature_ids),
            "bbox": bbox
        },
        "features": []
    }
    
    # Add features with IDs (coordinates would need to be fetched from tiles or individual requests)
    for i, feature_id in enumerate(feature_ids):
        feature = {
            "type": "Feature",
            "id": feature_id,
            "properties": {
                "id": feature_id,
                "index": i + 1
            },
            "geometry": {
                "type": "Point",
                "coordinates": None  # Would need to be extracted from tile data
            }
        }
        trinkbrunnen_data["features"].append(feature)
    
    # Save to JSON file
    with open('berlin_trinkbrunnen_google_maps.json', 'w', encoding='utf-8') as f:
        json.dump(trinkbrunnen_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(feature_ids)} Trinkbrunnen feature IDs to berlin_trinkbrunnen_google_maps.json")
    print(f"Total number of Trinkbrunnen in Berlin (from Google Maps): {len(feature_ids)}")
    
    # Note about limitations
    print("\nNote: This extracts feature IDs from the KML overlay.")
    print("To get exact coordinates and properties for each fountain,")
    print("additional requests to Google Maps API would be needed.")

if __name__ == "__main__":
    main()