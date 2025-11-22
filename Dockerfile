# Dockerfile for SCEMS Multi-Agent System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/sample_data /app/supervisor /app/agents

# Expose ports (default: 8000 for supervisor, 8001 for agent)
EXPOSE 8000 8001

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "uvicorn", "supervisor.main:app", "--host", "0.0.0.0", "--port", "8000"]

