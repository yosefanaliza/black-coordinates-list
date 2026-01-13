FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements relative to the build context (root)
COPY service-b/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the shared package
COPY shared/ ./shared/

# Copy the service code (the app folder)
COPY service-b/app/ ./app/

EXPOSE 8000

# Start from the app module
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]