# Service A - IP Resolution Service

## Overview
Service A is the entry point and IP resolution layer of the Black Coordinates List system. It receives IP addresses from external sources, resolves them to geographic coordinates using an external geolocation API, and forwards the data to Service B for storage.

## Responsibility
- Expose API endpoint for receiving IP addresses
- Validate IP address format using Pydantic
- Call external geolocation service (ip-api.com) for IP to coordinates conversion
- Handle external API failures and timeouts with retry logic
- Forward resolved coordinates to Service B via internal HTTP
- Provide health check endpoint for Kubernetes probes

## What This Service Does NOT Do
- Does not store data or access Redis directly
- Does not perform data retrieval operations
- Does not make decisions or analyze data
- Does not display information to end users

## API Endpoints

### POST /resolve
Resolve an IP address to geographic coordinates and store them.

**Request Body:**
```json
{
  "ip": "8.8.8.8"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "IP resolved and coordinates stored successfully",
  "ip": "8.8.8.8",
  "coordinates": {
    "lat": 37.751,
    "lon": -97.822
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid IP format
- `502 Bad Gateway` - External API failed to resolve IP
- `503 Service Unavailable` - Service B unreachable or external API timeout
- `500 Internal Server Error` - Unexpected error

### GET /health
Health check endpoint for Kubernetes liveness and readiness probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "Service A - IP Resolution"
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_B_URL` | URL of Service B | Required (no default) |
| `IP_API_TIMEOUT` | Timeout for external API calls (seconds) | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |

## External API Integration

Service A integrates with **ip-api.com** for IP geolocation:

**Endpoint:** `http://ip-api.com/json/{ip}`

**Features:**
- Free service, no API key required
- Rate limit: 45 requests/minute
- Returns latitude, longitude, city, country, and more

**Example Response:**
```json
{
  "status": "success",
  "lat": 37.751,
  "lon": -97.822,
  "city": "Kansas",
  "country": "United States",
  "query": "8.8.8.8"
}
```

**Error Handling:**
- 2 retry attempts on failure
- 5-second timeout per request
- Logs all failures for debugging

## Local Development

### Prerequisites
- Python 3.11+
- Service B running (for full integration testing)

### Install Dependencies
```bash
cd service-a
pip install -r requirements.txt
```

### Run Service
```bash
SERVICE_B_URL=http://localhost:8000 uvicorn app.main:app --reload --port 8001
```

The service will be available at `http://localhost:8001`

### API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Docker Build

```bash
cd service-a
docker build -t service-a:latest -f app/Dockerfile .
```

## Testing

### Test IP Resolution (with Service B running)
```bash
curl -X POST http://localhost:8001/resolve \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'
```

### Test Invalid IP
```bash
curl -X POST http://localhost:8001/resolve \
  -H "Content-Type: application/json" \
  -d '{"ip": "999.999.999.999"}'
```

### Test Health Check
```bash
curl http://localhost:8001/health
```

## Architecture

Service A follows a clean three-layer architecture:

1. **routes.py** - Thin HTTP endpoint layer (no business logic)
2. **services.py** - Business logic:
   - `call_external_ip_api()` - External API integration
   - `forward_to_service_b()` - Internal service communication
   - `resolve_ip()` - Main orchestration logic
3. **schemas.py** - Data validation and models (Pydantic)

This separation ensures:
- Clear responsibility boundaries
- Easy testing with mocked dependencies
- Simplified debugging and logging
- Future scalability

## Data Flow

1. **External Request** → POST /resolve with IP address
2. **Validation** → Pydantic validates IP format
3. **External API Call** → GET to ip-api.com/json/{ip}
4. **Response Processing** → Extract lat, lon, city, country
5. **Forward to Service B** → POST to Service B /coordinates
6. **Response to Client** → Return success/failure status

## Error Handling

Service A implements comprehensive error handling:

### External API Errors
- **Timeout** → Retry up to 2 times, then return 503
- **Connection Error** → Log and return 502
- **Invalid Response** → Log and return 502

### Service B Errors
- **Timeout** → Log and return 503
- **Connection Error** → Log and return 503
- **HTTP Error** → Log and return 500

### Validation Errors
- **Invalid IP Format** → Return 400 with error details
- **IP Out of Range** → Return 400 with error details

All errors are logged with full context for debugging.

## IP Validation

Service A validates IP addresses using Pydantic:

**Valid Format:** `X.X.X.X` where each X is 0-255

**Examples:**
- ✅ `8.8.8.8`
- ✅ `192.168.1.1`
- ✅ `1.1.1.1`
- ❌ `999.999.999.999` (octets > 255)
- ❌ `192.168.1` (incomplete)
- ❌ `not.an.ip.addr` (non-numeric)

## Integration with Service B

Service A communicates with Service B via HTTP POST:

**Endpoint:** `{SERVICE_B_URL}/coordinates`

**Payload:**
```json
{
  "ip": "8.8.8.8",
  "lat": 37.751,
  "lon": -97.822,
  "city": "Kansas",
  "country": "United States"
}
```

**Configuration:**
- Timeout: 10 seconds
- No retries (Service B should be reliable in same cluster)
- Async HTTP client (httpx)

## Logging

All operations are logged with appropriate levels:

- `INFO` - Successful operations, API calls
- `WARNING` - Retry attempts, Service B failures
- `ERROR` - Fatal errors, all retry attempts failed

**Log Format:**
```
[2024-01-12 10:30:45] [INFO] [service-a] Received IP resolution request for: 8.8.8.8
[2024-01-12 10:30:45] [INFO] [service-a] Calling external API for IP: 8.8.8.8
[2024-01-12 10:30:46] [INFO] [service-a] External API response for 8.8.8.8: success
[2024-01-12 10:30:46] [INFO] [service-a] Forwarding coordinates to Service B for IP: 8.8.8.8
[2024-01-12 10:30:46] [INFO] [service-a] Successfully forwarded coordinates for IP: 8.8.8.8 to Service B
```
