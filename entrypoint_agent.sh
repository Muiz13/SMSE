#!/bin/bash
# Entrypoint script for Agent service (Railway compatible)
# Handles PORT environment variable expansion even when Railway overrides CMD

# Set default port if not provided
PORT=${PORT:-8001}

# Export PORT so it's available to child processes
export PORT

# If arguments are provided (Railway override), replace $PORT and execute
if [ $# -gt 0 ]; then
    # Process arguments and replace $PORT with actual value
    ARGS=()
    for arg in "$@"; do
        if [ "$arg" = "\$PORT" ] || [ "$arg" = '$PORT' ]; then
            ARGS+=("$PORT")
        elif [[ "$arg" == *"\$PORT"* ]] || [[ "$arg" == *'$PORT'* ]]; then
            # Replace $PORT in the argument string
            ARGS+=("${arg//\$PORT/$PORT}")
        else
            ARGS+=("$arg")
        fi
    done
    exec "${ARGS[@]}"
else
    # No arguments, use default start script
    exec uvicorn agents.smart_campus_energy_agent.main:app --host 0.0.0.0 --port $PORT
fi

