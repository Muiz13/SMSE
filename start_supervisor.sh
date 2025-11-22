#!/bin/bash
# Start script for Supervisor service (Railway compatible)
# This script properly expands $PORT environment variable

PORT=${PORT:-8000}
exec uvicorn supervisor.main:app --host 0.0.0.0 --port $PORT

