#!/bin/bash

echo "=========================================="
echo "Testing FastAPI with uvloop + Gunicorn"
echo "=========================================="
echo ""

# Kill any existing server
pkill -f "gunicorn main:app" 2>/dev/null
sleep 1

# Activate venv and start server
source venv/bin/activate

echo "Starting server..."
gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --log-level info > server.log 2>&1 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to be ready..."
sleep 3

echo ""
echo "Testing /sync-with-async endpoint..."
echo ""

curl "http://localhost:8000/sync-with-async?seconds=0.2" -s

echo ""
echo ""
echo "Checking logs for uvloop detection..."
echo ""
grep -A 2 "Event loop type" server.log | tail -3

echo ""
echo "Checking for RuntimeError from asyncio.get_running_loop()..."
echo ""
grep "ERROR.*asyncio.get_running_loop" server.log || echo "No RuntimeError found (expected)"

echo ""
echo "Full startup logs:"
echo ""
grep "STARTUP" server.log

echo ""
echo "To view full logs: tail -f server.log"

# Keep server running for manual testing
echo ""
echo "Server is running on http://localhost:8000"
echo "Test it with: curl 'http://localhost:8000/sync-with-async?seconds=0.3'"
echo "Stop it with: pkill -f 'gunicorn main:app'"

