from fastapi import FastAPI
from .routes import coordinates, health
# Create FastAPI application
app = FastAPI(
    title="Service A - IP Resolution",
    description="IP resolution service that receives IP addresses, converts them to geographic coordinates using external API, and forwards to storage service.",
    version="1.0.0"
)

# Include routers
app.include_router(coordinates.router)
app.include_router(health.router)