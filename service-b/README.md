# Service B - Coordinate Storage Service

## Overview
Service B is the storage and retrieval layer of the Black Coordinates List system. It receives geographic coordinates from Service A and stores them in Redis for fast retrieval.

## Responsibility
- Receive coordinates from Service A via internal HTTP endpoint
- Validate incoming coordinate data using Pydantic
- Store coordinates in Redis (Key=IP, Value=JSON)
- Provide centralized retrieval of all stored coordinates
- Health check endpoint for Kubernetes probes

## What This Service Does NOT Do
- Does not contact external services
- Does not know the data source (IP addresses, users, systems)
- Does not perform calculations or analysis
- Does not handle IP resolution

## API Endpoints

### POST /coordinates/
Store coordinates received from Service A.

**Request Body:**
```json
{
  "ip": "8.8.8.8",
  "lat": 37.751,
  "lon": -97.822,
  "city": "Kansas",
  "country": "United States"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Coordinates stored successfully",
  "ip": "8.8.8.8"
}
```

### GET /coordinates/
Retrieve all stored coordinates.

**Response:**
```json
{
  "count": 2,
  "coordinates": [
    {
      "ip": "8.8.8.8",
      "lat": 37.751,
      "lon": -97.822,
      "city": "Kansas",
      "country": "United States"
    },
    {
      "ip": "1.1.1.1",
      "lat": -37.814,
      "lon": 144.963,
      "city": "Melbourne",
      "country": "Australia"
    }
  ]
}
```

### GET /health
Health check endpoint for Kubernetes liveness and readiness probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "Service B - Coordinate Storage",
  "redis_connected": true
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis hostname | `redis` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Redis Storage Format

**Key:** IP address (e.g., `"8.8.8.8"`)
**Value:** JSON string containing coordinate data
```json
{
  "lat": 37.751,
  "lon": -97.822,
  "city": "Kansas",
  "country": "United States"
}
```

## Local Development

### Prerequisites
- Python 3.11+
- Redis running locally or via Docker

### Start Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### Install Dependencies
```bash
cd service-b
pip install -r requirements.txt
```

### Run Service
```bash
REDIS_HOST=localhost uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Docker Build

**Important:** Build from the project root to include shared models.

```bash
# From project root directory
docker build -t service-b:latest -f service-b/Dockerfile .
```

## Testing

### Test Storage
```bash
curl -X POST http://localhost:8000/coordinates/ \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "8.8.8.8",
    "lat": 37.751,
    "lon": -97.822,
    "city": "Kansas",
    "country": "United States"
  }'
```

### Test Retrieval
```bash
curl http://localhost:8000/coordinates/
```

### Test Health Check
```bash
curl http://localhost:8000/health
```

## Architecture

Service B follows a clean modular architecture:

1. **main.py** - Application entry point with logging and Redis lifecycle management
2. **server.py** - FastAPI application initialization and router registration
3. **routes/** - HTTP endpoint handlers:
   - `health.py` - GET /health endpoint
   - `coordinates.py` - POST/GET /coordinates/ endpoints
4. **storage/** - Data persistence layer:
   - `redis.py` - Redis connection and operations
5. **shared/models.py** - Shared Pydantic models imported from project root:
   - `CoordinateItem` - Coordinate data validation
   - `CoordinateStorageResponse` - Storage operation responses
   - `AllCoordinatesResponse` - Bulk retrieval responses
   - `HealthResponse` - Health check responses

This separation ensures:
- Clear responsibility boundaries with dedicated route and storage folders
- Type consistency between services via shared models
- Easy testing and maintenance
- Simplified debugging
- Future scalability

## Error Handling

- `400 Bad Request` - Invalid coordinate data (Pydantic validation)
- `500 Internal Server Error` - Redis operation failure
- `503 Service Unavailable` - Redis connection unavailable

All errors are logged with appropriate context for debugging.
