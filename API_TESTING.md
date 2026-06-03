## Smart Traffic Bandung - API Testing Guide

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "Smart Traffic Bandung API"
}
```

---

### 1. Get All CCTV

**Request:**
```bash
curl -X GET http://localhost:8000/cctv \
  -H "Accept: application/json"
```

**Response Example:**
```json
[
  {
    "id": 1,
    "cctv_id": "1",
    "cctv_name": "CCTV Pendopo",
    "lat": -6.9147,
    "lng": 107.6098,
    "stream_cctv": "http://example.com/stream.m3u8",
    "dinas": "Dishub",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

---

### 2. Get CCTV Detail

**Request:**
```bash
curl -X GET http://localhost:8000/cctv/1 \
  -H "Accept: application/json"
```

**Response Example:**
```json
{
  "id": 1,
  "cctv_id": "1",
  "cctv_name": "CCTV Pendopo",
  "lat": -6.9147,
  "lng": 107.6098,
  "stream_cctv": "http://example.com/stream.m3u8",
  "dinas": "Dishub",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### 3. Analyze Traffic (AI Detection)

**Request:**
```bash
curl -X GET http://localhost:8000/analyze/1 \
  -H "Accept: application/json"
```

**Response Example:**
```json
{
  "cctv_name": "CCTV Pendopo",
  "cctv_id": "1",
  "vehicle_count": 35,
  "status": "LANCAR",
  "car_count": 20,
  "motorcycle_count": 12,
  "bus_count": 2,
  "truck_count": 1,
  "confidence_score": 0.87,
  "timestamp": "2024-01-01T10:30:00"
}
```

**Status Legend:**
- `LANCAR` (Green): < 40 vehicles
- `PADAT` (Yellow): 40-70 vehicles
- `MACET` (Red): > 70 vehicles

---

### 4. Get Analysis History

**Request:**
```bash
curl -X GET "http://localhost:8000/analyze/history/1?hours=24" \
  -H "Accept: application/json"
```

**Parameters:**
- `cctv_id` (path): CCTV ID
- `hours` (query, optional): Number of hours to look back (default: 24)

**Response:**
```json
[
  {
    "cctv_name": "CCTV Pendopo",
    "cctv_id": "1",
    "vehicle_count": 35,
    "status": "LANCAR",
    "car_count": 20,
    "motorcycle_count": 12,
    "bus_count": 2,
    "truck_count": 1,
    "confidence_score": 0.87,
    "timestamp": "2024-01-01T10:30:00"
  },
  {
    "cctv_name": "CCTV Pendopo",
    "cctv_id": "1",
    "vehicle_count": 52,
    "status": "PADAT",
    "car_count": 30,
    "motorcycle_count": 18,
    "bus_count": 3,
    "truck_count": 1,
    "confidence_score": 0.85,
    "timestamp": "2024-01-01T10:25:00"
  }
]
```

---

### 5. Get Latest Analysis for All CCTV

**Request:**
```bash
curl -X GET http://localhost:8000/analyze/latest \
  -H "Accept: application/json"
```

**Response:**
```json
[
  {
    "cctv_name": "CCTV Pendopo",
    "cctv_id": "1",
    "vehicle_count": 35,
    "status": "LANCAR",
    "car_count": 20,
    "motorcycle_count": 12,
    "bus_count": 2,
    "truck_count": 1,
    "confidence_score": 0.87,
    "timestamp": "2024-01-01T10:30:00"
  },
  {
    "cctv_name": "CCTV Alun-Alun",
    "cctv_id": "2",
    "vehicle_count": 78,
    "status": "MACET",
    "car_count": 45,
    "motorcycle_count": 28,
    "bus_count": 4,
    "truck_count": 1,
    "confidence_score": 0.82,
    "timestamp": "2024-01-01T10:29:00"
  }
]
```

---

## Common Error Responses

### 404 Not Found
```json
{
  "detail": "CCTV not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error analyzing traffic: <error message>"
}
```

---

## Using with Python Requests

```python
import requests

# Get all CCTVs
response = requests.get('http://localhost:8000/cctv')
cctvs = response.json()
print(f"Found {len(cctvs)} CCTV cameras")

# Analyze first CCTV
if cctvs:
    cctv_id = cctvs[0]['id']
    response = requests.get(f'http://localhost:8000/analyze/{cctv_id}')
    analysis = response.json()
    print(f"Status: {analysis['status']}")
    print(f"Vehicles: {analysis['vehicle_count']}")

# Get history
response = requests.get(f'http://localhost:8000/analyze/history/{cctv_id}?hours=24')
history = response.json()
print(f"Found {len(history)} records in last 24 hours")
```

---

## Using with JavaScript/Fetch

```javascript
// Get all CCTVs
async function getAllCCTV() {
  const response = await fetch('http://localhost:8000/cctv');
  const cctvs = await response.json();
  return cctvs;
}

// Analyze traffic
async function analyzeTraffic(cctvId) {
  const response = await fetch(`http://localhost:8000/analyze/${cctvId}`);
  const analysis = await response.json();
  return analysis;
}

// Get history
async function getHistory(cctvId, hours = 24) {
  const response = await fetch(
    `http://localhost:8000/analyze/history/${cctvId}?hours=${hours}`
  );
  const history = await response.json();
  return history;
}

// Usage
(async () => {
  const cctvs = await getAllCCTV();
  if (cctvs.length > 0) {
    const analysis = await analyzeTraffic(cctvs[0].id);
    console.log(`Status: ${analysis.status}`);
    console.log(`Vehicles: ${analysis.vehicle_count}`);
  }
})();
```

---

## Testing with Thunder Client / Postman

### Import Collection

Create a new collection and add these requests:

1. **Get All CCTV**
   - Method: GET
   - URL: `http://localhost:8000/cctv`

2. **Analyze Traffic**
   - Method: GET
   - URL: `http://localhost:8000/analyze/{{cctv_id}}`
   - Set `cctv_id` variable in environment

3. **Get History**
   - Method: GET
   - URL: `http://localhost:8000/analyze/history/{{cctv_id}}?hours=24`

4. **Get Latest**
   - Method: GET
   - URL: `http://localhost:8000/analyze/latest`

---

## Performance Metrics

### Response Times (Typical)
- `/cctv`: 100-200ms
- `/analyze/{id}`: 5-30s (depends on stream availability and YOLO processing)
- `/analyze/latest`: 50-100ms
- `/analyze/history/{id}`: 100-300ms

### Tips for Better Performance
1. Cache results locally
2. Implement pagination for history
3. Use WebSocket for real-time updates
4. Optimize YOLO model size
