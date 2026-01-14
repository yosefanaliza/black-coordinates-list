FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Build context is root directory, so paths are relative to project root
COPY service-a/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared models package (used by both services)
# This must come before service code to be available for imports
COPY shared/ ./shared/

# Copy service-specific code
COPY service-a/app/ ./app/

EXPOSE 8000

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]