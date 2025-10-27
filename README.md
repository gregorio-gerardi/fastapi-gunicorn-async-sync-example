# FastAPI Gunicorn Test Server

This is a simple FastAPI server to test how it works with Gunicorn and Uvicorn workers in conjunction with asyncio.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Option 1: Direct Uvicorn (for development)
```bash
python main.py
```

### Option 2: Gunicorn with Uvicorn workers (recommended for production)
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Option 3: Gunicorn with a custom configuration file
```bash
gunicorn -c gunicorn_config.py main:app
```

## Testing Endpoints

After starting the server, test these endpoints:

- `GET /` - Root endpoint with basic info
- `GET /health` - Health check endpoint
- `GET /async-task` - Simple async task
- `GET /async-delay/{seconds}` - Async delay (e.g., `/async-delay/1`)
- `GET /concurrent` - Demonstrates concurrent async operations (should be fast!)
- `GET /sync-task` - Synchronous task for comparison
- `GET /sync-with-async?seconds=0.2` - **Sync endpoint using async primitives**:
  - Uses `asyncio.get_running_loop()` to get event loop
  - Uses `asyncio.to_thread()` to run blocking sync method
  - Uses `asyncio.run_coroutine_threadsafe()` to schedule and wait

## Notes

- The `/concurrent` endpoint demonstrates the power of async: it should complete in ~0.3s (the longest task) rather than 0.6s (the sum)
- Gunicorn manages the process, Uvicorn workers handle the async event loop
- This combination provides both process-based concurrency (Gunicorn) and async I/O concurrency (Uvicorn)
- You can adjust the `-w` flag (number of workers) based on your CPU cores

## Logging

The server includes extensive verbose logging to track the async/sync flow:

- 🚀 **Startup logs**: Show when the event loop is stored
- 🟢 **Sync-with-async logs**: Track the entire flow in the sync endpoint:
  1. Event loop retrieval
  2. Coroutine creation with `asyncio.to_thread()`
  3. Scheduling with `asyncio.run_coroutine_threadsafe()`
  4. Waiting for future result
- 🔵 **Blocking operation logs**: Show when blocking work executes in thread pool

View logs in real-time:
```bash
# Terminal 1: Run the server
./start.sh

# Terminal 2: Make requests and watch logs
curl "http://localhost:8000/sync-with-async?seconds=0.5"
```

## Performance Testing

To test concurrency, you can use `curl` or a tool like `wrk` or `ab`:

```bash
# Sequential requests
for i in {1..10}; do curl http://localhost:8000/async-delay/0.5; done

# Concurrent requests (timing)
time curl http://localhost:8000/concurrent
```

