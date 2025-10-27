#!/bin/bash

# Test script to run the server and see all logs

echo "=========================================="
echo "Testing FastAPI with Gunicorn + Uvicorn"
echo "=========================================="
echo ""

# Kill any existing servers
pkill -f "gunicorn main:app" 2>/dev/null
sleep 1

echo "Starting server in background..."
echo ""

# Activate venv and start server
source venv/bin/activate
gunicorn main:app \
    -w 2 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --log-level info 2>&1 | tee server.log &

GUNICORN_PID=$!
echo "Server started with PID: $GUNICORN_PID"
echo "Logs are being written to server.log"
echo ""
sleep 3

echo "Testing /sync-with-async endpoint..."
echo ""
curl "http://localhost:8000/sync-with-async?seconds=0.5" -s | python3 -m json.tool

echo ""
echo ""
echo "Check server.log for verbose output!"
echo "To stop: pkill -f 'gunicorn main:app'"
echo "To view logs in real-time: tail -f server.log"

