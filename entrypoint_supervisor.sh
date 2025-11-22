#!/bin/bash
set -e

# Entrypoint script for Supervisor service (Railway compatible)
# Handles PORT environment variable expansion even when Railway overrides CMD

# Set default port if not provided
PORT=${PORT:-8000}

# Export PORT so it's available to child processes
export PORT

# Log for debugging
echo "Entrypoint: PORT=${PORT}" >&2

# If arguments are provided (Railway override), process them
if [ $# -gt 0 ]; then
    # Railway might pass: uvicorn ... --port $PORT
    # We need to replace $PORT with actual value in all arguments
    ARGS=()
    for arg in "$@"; do
        # Replace $PORT (literal string) with actual port value
        case "$arg" in
            '$PORT'|'${PORT}'|\$PORT)
                ARGS+=("$PORT")
                ;;
            *)
                # Replace $PORT anywhere in the argument
                new_arg="${arg//\$PORT/$PORT}"
                ARGS+=("$new_arg")
                ;;
        esac
    done
    
    echo "Executing with expanded PORT: ${ARGS[*]}" >&2
    exec "${ARGS[@]}"
else
    # No arguments, use Python module which reads PORT from environment
    echo "No arguments, using Python module (reads PORT=${PORT} from env)" >&2
    exec python -m supervisor.main
fi

