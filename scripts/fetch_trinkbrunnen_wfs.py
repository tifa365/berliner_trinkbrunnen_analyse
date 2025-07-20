import requests
import json

def fetch_trinkbrunnen_from_wfs():
    """Fetch all drinking fountains from Berlin's WFS (Web Feature Service)"""
    
    # WFS endpoint URL
    wfs_url = "http://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer"
    
    # WFS GetFeature request parameters
    params = {
        'service': 'WFS',
        'version': '2.0.0',
        'request': 'GetFeature',
        'typeName': 'Trinkbrunnen_BWB:Trinkbrunnen_BWB',
        'outputFormat': 'GEOJSON',  # Request GeoJSON format
        'maxFeatures': '10000'  # Set high limit to get all features
    }
    
    print("Fetching Trinkbrunnen data from WFS...")
    print(f"URL: {wfs_url}")
    print(f"Parameters: {params}")
    
    try:
        response = requests.get(wfs_url, params=params, timeout=30)
        
        if response.status_code == 200:
            print(f"Success! Response size: {len(response.text)} characters")
            
            # Try to parse as JSON
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                print("Response is not valid JSON. Checking if it's XML...")
                # Check if response contains XML error
                if 'xml' in response.text.lower() and 'error' in response.text.lower():
                    print("WFS returned an XML error:")
                    print(response.text[:1000])
                else:
                    print("Response preview:")
                    print(response.text[:500])
                return None
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except requests.exceptions.Timeout:
        print("Request timed out after 30 seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        return None

def try_alternative_formats():
    """Try different output formats to see what works"""
    
    wfs_url = "http://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer"
    
    formats_to_try = [
        'GEOJSON',
        'ESRIGEOJSON', 
        'GML32',
        'CSV',
        'KML'
    ]
    
    for format_name in formats_to_try:
        print(f"\nTrying format: {format_name}")
        
        params = {
            'service': 'WFS',
            'version': '2.0.0',
            'request': 'GetFeature',
            'typeName': 'Trinkbrunnen_BWB:Trinkbrunnen_BWB',
            'outputFormat': format_name,
            'maxFeatures': '5'  # Just get a few to test
        }
        
        try:
            response = requests.get(wfs_url, params=params, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Success! Content type: {response.headers.get('content-type', 'unknown')}")
                print(f"Response preview: {response.text[:200]}...")
                
                if format_name in ['GEOJSON', 'ESRIGEOJSON']:
                    try:
                        data = response.json()
                        if 'features' in data:
                            print(f"Found {len(data['features'])} features")
                            return format_name, data
                    except json.JSONDecodeError:
                        print("Not valid JSON")
            else:
                print(f"Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return None, None

def main():
    print("Fetching Trinkbrunnen from WFS (Web Feature Service)...")
    print("="*60)
    
    # First try to get all data
    data = fetch_trinkbrunnen_from_wfs()
    
    if data is None:
        print("\nFirst attempt failed. Trying alternative formats...")
        working_format, data = try_alternative_formats()
        
        if working_format:
            print(f"\nFound working format: {working_format}")
            print("Fetching all data with working format...")
            
            # Now fetch all data with the working format
            wfs_url = "http://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer"
            params = {
                'service': 'WFS',
                'version': '2.0.0',
                'request': 'GetFeature',
                'typeName': 'Trinkbrunnen_BWB:Trinkbrunnen_BWB',
                'outputFormat': working_format,
                'maxFeatures': '10000'
            }
            
            response = requests.get(wfs_url, params=params, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = None
    
    if data and 'features' in data:
        feature_count = len(data['features'])
        print(f"\nSuccessfully fetched {feature_count} Trinkbrunnen from WFS!")
        
        # Save to JSON file
        with open('../data/berlin_trinkbrunnen_wfs.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Data saved to ../data/berlin_trinkbrunnen_wfs.json")
        
        # Display some sample data
        if feature_count > 0:
            print("\nSample of first drinking fountain:")
            sample = data['features'][0]
            print(json.dumps(sample, indent=2, ensure_ascii=False))
            
            # Show available properties
            if 'properties' in sample:
                print(f"\nAvailable properties: {list(sample['properties'].keys())}")
            
            # Show geometry type
            if 'geometry' in sample:
                print(f"Geometry type: {sample['geometry'].get('type', 'Unknown')}")
        
        print(f"\nTotal number of Trinkbrunnen in Berlin (from WFS): {feature_count}")
    else:
        print("\nFailed to fetch data from WFS. The service might be unavailable or require different parameters.")
        if data:
            print("Response structure:")
            print(json.dumps(data, indent=2)[:500])

if __name__ == "__main__":
    main()