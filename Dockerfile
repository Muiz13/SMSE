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

# Make start scripts executable (for manual use)
RUN chmod +x /app/start_supervisor.sh /app/start_agent.sh

# Expose ports (default: 8000 for supervisor, 8001 for agent)
EXPOSE 8000 8001

# Default command (can be overridden in docker-compose)
# Use Python module to properly handle PORT env var (reads from environment)
CMD ["python", "-m", "supervisor.main"]

