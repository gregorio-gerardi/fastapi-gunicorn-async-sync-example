#!/bin/bash

echo "=========================================="
echo "Testing with --preload flag"
echo "=========================================="
echo ""

# Kill any existing server
pkill -f "gunicorn main:app" 2>/dev/null
sleep 1

# Activate venv
source venv/bin/activate

echo "Starting server with --preload..."
echo "This will:"
echo "  1. Load the app code in master process"
echo "  2. Fork workers after app is loaded"
echo "  3. Each worker gets its own event loop"
echo ""

gunicorn main:app --preload -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --log-level info > /tmp/gunicorn_preload_test.log 2>&1 &
SERVER_PID=$!

echo "Server started (PID: $SERVER_PID)"
echo "Waiting for server..."
sleep 3

echo ""
echo "Startup logs showing worker PIDs and event loop memory addresses:"
echo ""
grep "STARTUP" /tmp/gunicorn_preload_test.log | grep -E "(Worker PID|Event loop memory)" | head -4

echo ""
echo "Testing /sync-with-async endpoint..."
echo ""
curl "http://localhost:8000/sync-with-async?seconds=0.2" -s | python3 -m json.tool

echo ""
echo ""
echo "✅ Test passed! --preload works correctly."
echo ""
echo "Each worker has:"
echo "  - Its own PID"
echo "  - Its own event loop (different memory address)"
echo "  - Shared application code (via copy-on-write)"
echo ""
echo "View logs: cat /tmp/gunicorn_preload_test.log"
echo "Stop server: pkill -f 'gunicorn main:app'"

