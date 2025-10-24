# small, secure base image with Python
FROM python:3.11-slim

# Prevent Python from buffering stdout/err (useful in Cloud Run logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set workdir inside the image
WORKDIR /app

# Install system deps only if needed (kept minimal for wheel-based installs)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better build caching)
COPY requirements.txt /app/

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the app code
COPY . /app

# Cloud Run sets $PORT; default to 8080 for local docker run
ENV PORT=8080

# For Cloud Run/containers, prefer gunicorn over Flask dev server
# Your Flask instance is `app` in `penguin_app_api.py`
CMD exec gunicorn -b :$PORT penguin_app_api:app
