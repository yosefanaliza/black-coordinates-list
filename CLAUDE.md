# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Black Coordinates List is a microservices-based infrastructure system that converts IP addresses to geographic coordinates and stores them in Redis. The system emphasizes proper infrastructure construction with clear separation of responsibilities between two independent services.

## System Architecture

### Service Communication Flow
```
External Request → Service A → External API (ip-api.com)
                     ↓
                Service B → Redis (StatefulSet)
```

**Critical Design Principles:**
- Service A is an adapter layer - it NEVER touches Redis directly
- Service B is a storage layer - it NEVER contacts external APIs
- Each service only knows the minimum required for its responsibility
- Communication between services is via HTTP with explicit host/port environment variables

### Shared Models
- **Location:** `shared/models.py`
- **Purpose:** Centralized Pydantic models used by both services for consistent validation
- **Key models:**
  - `IPRequest` - IP address validation using IPv4Address type
  - `CoordinateItem` - Coordinate data with lat/lon validation
  - `CoordinateStorageResponse` - Response for storage operations
  - `AllCoordinatesResponse` - List of all stored coordinates
  - `HealthResponse` - Health check responses
  - `ExternalAPIResponse` - ip-api.com response validation
- **Import pattern:** `from shared.models import IPRequest, CoordinateItem`

### Service A (IP Resolution)
- **Location:** `service-a/app/`
- **Entry point:** `main.py` (FastAPI app)
- **Business logic:** `services.py` - Contains retry logic (MAX_RETRIES=2) for external API calls
- **Key function:** `resolve_ip()` orchestrates: API call → forward to Service B
- **External dependency:** ip-api.com (rate limit: 45 req/min)
- **Shared models used:** `IPRequest`, `CoordinateItem`, `CoordinateStorageResponse`, `ExternalAPIResponse`
- **Environment variables:**
  - `SERVICE_B_HOST` - hostname only (no protocol)
  - `SERVICE_B_PORT` - port number (default: "8000" for Docker, "80" for K8s)
  - `IP_API_TIMEOUT` - timeout in seconds (default: 5)

### Service B (Coordinate Storage)
- **Location:** `service-b/app/`
- **Entry point:** `main.py` (FastAPI app with startup/shutdown hooks)
- **Storage logic:** `storage.py` - Global Redis client pattern with connection pooling
- **Redis connection:** Uses StatefulSet with headless service
- **Shared models used:** `CoordinateItem`, `CoordinateStorageResponse`, `AllCoordinatesResponse`, `HealthResponse`
- **Environment variables:**
  - `REDIS_HOST` - For K8s: `redis-0.redis` (direct pod access via headless service)
  - `REDIS_PORT` - default: "6379"
  - `REDIS_DB` - default: "0"

### Redis (Database)
- **Deployment:** StatefulSet (not Deployment) with PersistentVolumeClaim
- **Service:** Headless service (clusterIP: None) for stable pod identity
- **Persistence:** AOF enabled (`--appendonly yes --dir /data`)
- **Volume:** 1Gi PVC per pod via volumeClaimTemplates

## Development Commands

### Local Development (Docker Compose)

```bash
# Start all services
docker-compose up --build

# Service A available at: http://localhost:8000
# Service B available at: http://localhost:8001

# Stop services
docker-compose down
```

### Building Docker Images

**IMPORTANT:** Always build from the project root directory to include the `/shared` models package.

```bash
# Build Service A (from project root)
docker build -t service-a:latest -f service-a/Dockerfile .

# Build Service B (from project root)
docker build -t service-b:latest -f service-b/Dockerfile .

# Both Dockerfiles:
# 1. Use root directory as build context (.)
# 2. Copy shared/ directory before service code
# 3. Services import with: from shared.models import ...
```

### Kubernetes/OpenShift Deployment

**Order matters** - deploy in dependency order:

```bash
# 1. Redis first (database layer)
oc apply -f k8s/redis-statefulset.yaml
oc apply -f k8s/redis-service.yaml
oc wait --for=condition=ready pod -l app=redis --timeout=60s

# 2. Service B second (depends on Redis)
oc apply -f k8s/service-b-deployment.yaml
oc apply -f k8s/service-b-service.yaml
oc wait --for=condition=ready pod -l app=service-b --timeout=60s

# 3. Service A last (depends on Service B)
oc apply -f k8s/service-a-deployment.yaml
oc apply -f k8s/service-a-service.yaml
oc wait --for=condition=ready pod -l app=service-a --timeout=60s

# 4. Create external Route (OpenShift only)
oc apply -f k8s/service-a-route.yaml
```

### Testing

```bash
# Health checks
curl http://localhost:8000/health  # Service A
curl http://localhost:8001/health  # Service B

# Resolve IP address (full flow)
curl -X POST http://localhost:8000/resolve \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'

# Retrieve all coordinates
curl http://localhost:8001/coordinates
```

### Debugging

```bash
# View logs (Docker Compose)
docker-compose logs -f service-a
docker-compose logs -f service-b

# View logs (Kubernetes/OpenShift)
oc logs -l app=service-a --tail=100
oc logs -l app=service-b --tail=100
oc logs redis-0 --tail=100

# Access Redis directly
oc exec -it redis-0 -- redis-cli
> KEYS *
> GET coordinates:8.8.8.8

# Test internal connectivity
oc exec -it deployment/service-a -- curl http://service-b:8000/health
```

## Important Configuration Details

### Environment Variable Pattern
Service A constructs the full URL in code:
```python
service_b_host = os.getenv("SERVICE_B_HOST", "service-b")
service_b_port = os.getenv("SERVICE_B_PORT", "8000")
url = f"http://{service_b_host}:{service_b_port}/coordinates"
```

### Docker vs Kubernetes Differences

| Component | Docker Compose | Kubernetes |
|-----------|---------------|------------|
| Service B Port | 8000 (direct) | 80 (via Service abstraction) |
| Service B Host | service-b:8000 | service-b (port 80) |
| Redis Host | redis | redis-0.redis (StatefulSet pod) |
| External Access | NodePort 30081 | Route with TLS edge termination |

### Redis StatefulSet Details
- Pod name is stable: `redis-0`
- Headless service enables direct pod DNS: `redis-0.redis`
- PVC name follows pattern: `redis-data-redis-0`
- AOF persistence ensures data durability across restarts

## Code Structure Patterns

### Shared Models Structure
```
shared/
  __init__.py   # Empty, makes shared a Python package
  models.py     # All Pydantic models shared between services
                # IPRequest - IP validation with IPv4Address
                # CoordinateItem - Coordinate data model
                # CoordinateStorageResponse - Storage operation response
                # AllCoordinatesResponse - Bulk retrieval response
                # HealthResponse - Health check model
                # ExternalAPIResponse - ip-api.com response validation
```

### Service A Structure
```
service-a/
  app/
    main.py     # FastAPI app, startup validation of env vars
    routes.py   # Thin HTTP layer, imports from shared.models
    services.py # resolve_ip() orchestration
                # call_external_ip_api() with retry logic
                # forward_to_service_b() HTTP POST
  Dockerfile    # Build context: root (.), copies shared/ then app/
  requirements.txt
```

### Service B Structure
```
service-b/
  app/
    main.py     # FastAPI app, connects Redis on startup
    routes.py   # Thin HTTP layer, imports from shared.models
    storage.py  # Global Redis client pattern
                # store_coordinates() Redis SET
                # get_all_coordinates() Redis KEYS + MGET
  Dockerfile    # Build context: root (.), copies shared/ then app/
  requirements.txt
```

**Import Pattern:**
- Both services import shared models: `from shared.models import IPRequest, CoordinateItem`
- No local schemas.py files needed - all models centralized in shared/models.py
- Ensures type consistency between service communication

## Common Issues & Solutions

### Service A returns 503
- Check Service B is running: `oc get pods -l app=service-b`
- Verify SERVICE_B_HOST/PORT environment variables
- Test internal connectivity: `oc exec deployment/service-a -- curl http://service-b:8000/health`

### Service B can't connect to Redis
- Verify Redis StatefulSet pod: `oc get pods redis-0`
- Check REDIS_HOST is set to `redis-0.redis` (not just `redis`)
- Test Redis: `oc exec redis-0 -- redis-cli ping`

### OpenShift Route returns 503
- Verify Route has TLS termination configured (check `oc describe route`)
- Route must have: `tls.termination: edge` and `tls.insecureEdgeTerminationPolicy: Redirect`
- Check endpoints exist: `oc get endpoints service-a` (should show pod IP)

### External API rate limit (45/min exceeded)
- ip-api.com rate limits are per IP
- Implement request throttling
- Consider caching frequent lookups
- For production, upgrade to premium tier

## Deployment Checklist

When deploying changes:
1. **Build images from root directory** to include shared models: `docker build -f service-a/Dockerfile .`
2. Update Docker images with new tags (e.g., `v2`, `v3`)
3. Push images to registry (Docker Hub or OpenShift internal registry)
4. Update deployment YAMLs with new image tags
5. Apply in correct order: Redis → Service B → Service A
6. Verify each component before deploying the next: `oc wait --for=condition=ready pod -l app=<name>`
7. Check logs immediately after deployment

**Important:** If you modify shared models, rebuild and redeploy BOTH services even if their service-specific code hasn't changed.

## API Response Patterns

### Service A Success Response
```json
{
  "success": true,
  "message": "IP resolved and coordinates stored successfully",
  "ip": "8.8.8.8",
  "coordinates": {"lat": 37.751, "lon": -97.822}
}
```

### Service A Error Codes
- 400: Invalid IP format (Pydantic validation)
- 502: External API failure (ip-api.com down/error)
- 503: Service B unreachable or timeout
- 500: Unexpected internal error

### Service B Storage Format
Redis key pattern: `coordinates:{ip}`
Value: JSON string with timestamp
```json
{
  "ip": "8.8.8.8",
  "lat": 37.751,
  "lon": -97.822,
  "city": "Kansas",
  "country": "United States",
  "timestamp": "2024-01-12T10:30:45"
}
```
