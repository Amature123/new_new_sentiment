# Use Python 3.11 as base image
FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements first
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY models/ /app/models/

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh


# Expose ports for FastAPI
EXPOSE 8000

