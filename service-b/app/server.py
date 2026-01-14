from fastapi import FastAPI
from .routes import coordinates, health

# Create FastAPI application
app = FastAPI(
    title="Service B - Coordinate Storage",
    description="Storage service for geographic coordinates. Receives coordinates from Service A and stores them in Redis.",
    version="1.0.0"
)

# Include routers
app.include_router(health.router)
app.include_router(coordinates.router)