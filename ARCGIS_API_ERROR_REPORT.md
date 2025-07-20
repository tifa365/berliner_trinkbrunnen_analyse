# ArcGIS API Endpoints Error Report: Berlin Trinkbrunnen Service

**Date:** 2025-01-20  
**Service:** Berlin Trinkbrunnen (Drinking Fountains)  
**Base URL:** `https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/`

## Executive Summary

Multiple ArcGIS API endpoints for the Berlin Trinkbrunnen service return **0 features** despite having valid service configuration, metadata, and spatial extent definitions. This appears to be a data availability issue rather than a technical service failure.

## Service Overview

The Berlin Trinkbrunnen service is hosted on ArcGIS Online and provides information about drinking fountains operated by Berliner Wasserbetriebe (Berlin Water Works). The service has multiple access points:

- **FeatureServer**: Standard ArcGIS REST API
- **OGCFeatureServer**: OGC API - Features compliant endpoint  
- **WFSServer**: Web Feature Service (WFS) endpoint

## Detailed Endpoint Analysis

### 1. FeatureServer Layer Information

**Endpoint:** `FeatureServer/0`
```
GET https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/FeatureServer/0?f=json
```

**Result:** ✅ **SUCCESS**
- **Status Code:** 200 OK
- **Layer Name:** "Trinkbrunnen_BWB"
- **Geometry Type:** "esriGeometryPoint"
- **Spatial Extent:** Defined (375987.32, 5805237.23, 413054.34, 5832971.34)
- **Spatial Reference:** EPSG:25833 (ETRS89 / UTM zone 33N)

**Analysis:** The layer metadata is properly configured and indicates the service should contain point features within Berlin's geographical bounds.

### 2. FeatureServer Feature Count

**Endpoint:** `FeatureServer/0/query` (Count Only)
```bash
curl -G "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/FeatureServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "returnCountOnly=true" \
  --data-urlencode "f=json"
```

**Result:** ❌ **EMPTY DATASET**
```json
{"count": 0}
```

**Analysis:** Despite valid service configuration, the actual feature count is 0, indicating an empty dataset.

### 3. FeatureServer Feature Query

**Endpoint:** `FeatureServer/0/query` (Get Features)
```bash
curl -G "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/FeatureServer/0/query" \
  --data-urlencode "where=1=1" \
  --data-urlencode "f=json" \
  --data-urlencode "outFields=*"
```

**Result:** ❌ **QUERY FAILURE**
```json
{
  "error": {
    "code": 400,
    "message": "Cannot perform query. Invalid query parameters.",
    "details": ["Unable to perform query. Please check your parameters."]
  }
}
```

**Analysis:** The query fails with a generic error message. This could be due to:
- Empty dataset causing query engine issues
- Restrictive query permissions
- Service configuration problems

### 4. OGC Feature Server Collections

**Endpoint:** `OGCFeatureServer/collections`
```
GET https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/OGCFeatureServer/collections?f=json
```

**Result:** ✅ **SUCCESS**
```json
{
  "collections": [{
    "id": "0",
    "title": "Trinkbrunnen_BWB",
    "extent": {
      "spatial": {
        "bbox": [[13.167545420697646, 52.3833332065121, 13.72233062797553, 52.639745263132106]],
        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
      }
    }
  }]
}
```

**Analysis:** The OGC collections endpoint properly reports the collection with valid spatial extent in WGS84 coordinates.

### 5. OGC Feature Server Items

**Endpoint:** `OGCFeatureServer/collections/0/items`

#### 5.1 JSON Format Request
```bash
curl "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/OGCFeatureServer/collections/0/items?f=json&limit=10"
```

**Result:** ❌ **QUERY FAILURE**
```json
{
  "error": {
    "code": 400,
    "message": "Cannot perform query. Invalid query parameters.",
    "details": ["Unable to perform query. Please check your parameters."]
  }
}
```

#### 5.2 GeoJSON Format Request
```bash
curl "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/OGCFeatureServer/collections/0/items?f=application/geo+json&limit=10"
```

**Result:** ❌ **QUERY FAILURE**
```json
{
  "error": {
    "code": 400,
    "message": "Cannot perform query. Invalid query parameters.",
    "details": ["Unable to perform query. Please check your parameters."]
  }
}
```

#### 5.3 No Parameters Request
```bash
curl "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/OGCFeatureServer/collections/0/items"
```

**Result:** ❌ **QUERY FAILURE**
```json
{
  "error": {
    "code": 400,
    "message": "Cannot perform query. Invalid query parameters.",
    "details": ["Unable to perform query. Please check your parameters."]
  }
}
```

**Analysis:** All OGC Feature Server item requests fail with the same generic error, regardless of format or parameters.

### 6. WFS Server Check

**Endpoint:** `WFSServer` (Non-existent)
```bash
curl -s "https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/WFSServer?service=WFS&version=2.0.0&request=GetCapabilities"
```

**Result:** ❌ **SERVICE NOT FOUND**
```html
<div class='restErrors'>
Unsupported service type: WFSServer<br/>
</div>
```

**Analysis:** The WFS endpoint does not exist on this ArcGIS Server instance.

## Working Alternative: Dedicated WFS Server

**Endpoint:** `http://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer`

**Result:** ✅ **SUCCESS** - 244 features retrieved
```json
{
  "type": "FeatureCollection",
  "features": [244 drinking fountain features with complete attributes and coordinates]
}
```

## Error Pattern Analysis

### 1. Service Architecture Issues

The Trinkbrunnen service appears to have a **split architecture**:
- **Metadata services** (FeatureServer info, OGC collections) work correctly
- **Data retrieval services** (queries, items) consistently fail
- **Dedicated WFS server** on different subdomain works perfectly

### 2. Possible Root Causes

#### A. Empty Dataset Theory
- **Evidence:** Count query returns 0
- **Contradiction:** WFS on different server has 244 features
- **Conclusion:** Data exists but not accessible via this service instance

#### B. Service Configuration Issues
- **Evidence:** Generic "Invalid query parameters" errors across all endpoints
- **Analysis:** Suggests service-level configuration problems rather than parameter issues

#### C. Permissions/Security Restrictions
- **Evidence:** Metadata accessible, but data queries blocked
- **Analysis:** Could indicate read restrictions on feature data

#### D. Data Synchronization Issues
- **Evidence:** WFS has current data (244 features), FeatureServer reports 0
- **Analysis:** Possible synchronization lag or separate data sources

### 3. Error Message Analysis

The consistent error message across multiple endpoints:
```json
{
  "code": 400,
  "message": "Cannot perform query. Invalid query parameters.",
  "details": ["Unable to perform query. Please check your parameters."]
}
```

This generic message appears regardless of:
- Query syntax (simple `where=1=1` vs complex queries)
- Output format (JSON, GeoJSON, etc.)
- Parameter presence (with/without parameters)
- HTTP method (GET vs POST)

This suggests a **service-level issue** rather than client-side parameter problems.

## Service Comparison Summary

| Service Type | Endpoint | Status | Feature Count | Notes |
|-------------|----------|---------|---------------|-------|
| FeatureServer | `/FeatureServer/0` | ✅ Metadata Only | 0 | Service info works, queries fail |
| OGC Features | `/OGCFeatureServer` | ✅ Metadata Only | 0 | Collections work, items fail |
| WFS (Same Server) | `/WFSServer` | ❌ Not Available | N/A | Service type not supported |
| WFS (Dedicated) | `dservices-eu1.../WFSServer` | ✅ Full Access | 244 | Complete working service |

## Recommendations

### 1. For Data Access
- **Use the dedicated WFS server** at `dservices-eu1.arcgis.com` for reliable data access
- The WFS provides complete, up-to-date data with 244 features

### 2. For Service Administrators
- **Investigate data synchronization** between WFS and FeatureServer instances
- **Review service configuration** for query parameter handling
- **Check data permissions** on the FeatureServer instance
- **Verify dataset population** on the main service instance

### 3. For API Consumers
- **Implement fallback logic** to try WFS when FeatureServer queries fail
- **Cache successful responses** due to unreliable primary service
- **Monitor service status** as this appears to be an ongoing infrastructure issue

## Technical Specifications

### Working WFS Configuration
```
URL: http://dservices-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/services/Trinkbrunnen_BWB/WFSServer
Version: 2.0.0
Output Format: GEOJSON
Feature Type: Trinkbrunnen_BWB:Trinkbrunnen_BWB
CRS: EPSG:4326 (WGS84)
```

### Failed Services Configuration
```
Base URL: https://services-eu1.arcgis.com/A6FVvQQnrSyq47GD/arcgis/rest/services/Trinkbrunnen_BWB/
FeatureServer: /FeatureServer/0
OGC Server: /OGCFeatureServer
```

## Conclusion

The Berlin Trinkbrunnen ArcGIS service exhibits a **service fragmentation pattern** where metadata services function correctly but data retrieval consistently fails across multiple API standards (REST, OGC). The dedicated WFS server provides a reliable alternative, suggesting the data exists but the primary service instance has configuration or synchronization issues that prevent proper data access.

This represents a **critical service availability issue** that requires administrative intervention to resolve the data access problems on the primary ArcGIS service endpoints.