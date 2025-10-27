#!/bin/bash

# Simple startup script for the FastAPI server with Gunicorn + uvloop

# Default values
WORKERS=${WORKERS:-2}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
PRELOAD=${PRELOAD:-""}  # Use PRELOAD=1 to enable preload

echo "Starting FastAPI server with Gunicorn + Uvicorn + uvloop..."
echo "Workers: $WORKERS"
echo "Address: $HOST:$PORT"

if [[ "$PRELOAD" == "1" ]]; then
    echo "Using --preload (shared memory via copy-on-write)"
    PRELOAD_FLAG="--preload"
else
    echo "Not using --preload"
    PRELOAD_FLAG=""
fi

echo ""
echo "Install dependencies first: pip install -r requirements.txt"
echo ""

# Check if venv is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Virtual environment not detected!"
    echo "Please activate venv first: source venv/bin/activate"
    exit 1
fi

gunicorn main:app \
    $PRELOAD_FLAG \
    -w $WORKERS \
    -k uvicorn.workers.UvicornWorker \
    -b $HOST:$PORT \
    --timeout 120 \
    --keepalive 2 \
    --log-level info

