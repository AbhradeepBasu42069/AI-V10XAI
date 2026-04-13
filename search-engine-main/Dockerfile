# 1. Use a slim Python 3.11/3.12 image to keep the container light
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and enable unbuffered logging
# (Essential for seeing your token logs in the Cloud Console immediately)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory
WORKDIR /app

# 4. Install system dependencies if needed (usually not for Gemini, but good for stability)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy and install requirements first (leveraging Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Use the PORT environment variable provided by Cloud Run
# Cloud Run injects $PORT (default 8080) automatically.
# We use uvicorn to serve the FastAPI app.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
