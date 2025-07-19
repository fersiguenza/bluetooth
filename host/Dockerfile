FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install blueutil equivalent for Linux (bluez-tools)
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    bluez-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables for authentication (can be overridden)
ENV BT_USERNAME=admin
ENV BT_PASSWORD=bluetooth123
ENV BT_API_KEY=bluetooth-switch-secure-api-key-change-me
ENV SECRET_KEY=bluetooth-switch-docker-secret-key

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5002/api/status || exit 1

# Run the application
CMD ["python3", "app.py"]
