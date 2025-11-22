#!/bin/bash
# Start script for Agent service (Railway compatible)
# This script properly expands $PORT environment variable

PORT=${PORT:-8001}
exec uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port $PORT

