# FastAPI Gunicorn Async/Sync Example

## GitHub Repository

🔗 **https://github.com/gregorio-gerardi/fastapi-gunicorn-async-sync-example**

## What This Project Demonstrates

This is a comprehensive example of a FastAPI server running with:
- **Gunicorn** as the WSGI HTTP server
- **Uvicorn workers** for async support
- **uvloop** for high-performance event loops
- **Async/sync interop** patterns with asyncio primitives

## Key Features

### 1. Async/Sync Pattern Example
Demonstrates how to call async primitives from synchronous endpoints:
- `asyncio.get_running_loop()` - Getting event loop from sync context
- `asyncio.to_thread()` - Running blocking operations in thread pools
- `asyncio.run_coroutine_threadsafe()` - Scheduling coroutines from sync context

### 2. Verbose Logging
Extensive logging throughout the flow to understand:
- Thread information
- Event loop lifecycle
- Async/sync boundaries
- Worker processes

### 3. uvloop Integration
- Automatic uvloop detection and usage
- Performance logging
- Event loop type identification

### 4. --preload Support
- Shared memory via copy-on-write
- Worker isolation verification
- Memory efficiency testing

## Files Included

- `main.py` - FastAPI server with all endpoints and patterns
- `requirements.txt` - All dependencies including uvloop
- `gunicorn_config.py` - Gunicorn configuration
- `start.sh` - Startup script with optional --preload support
- `test_*.sh` - Various test scripts
- Documentation:
  - `README.md` - Getting started guide
  - `LOG_FLOW.md` - Detailed logging flow explanation
  - `EVENT_LOOP_EXPLAINED.md` - Event loop architecture
  - `UVLOOP_SUMMARY.md` - uvloop integration details
  - `PRELOAD_EXPLAINED.md` - --preload flag explanation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/gregorio-gerardi/fastapi-gunicorn-async-sync-example.git
cd fastapi-gunicorn-async-sync-example

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the server
./start.sh

# Or with --preload
PRELOAD=1 ./start.sh

# Test the sync-with-async endpoint
curl "http://localhost:8000/sync-with-async?seconds=0.5"
```

## Key Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /async-task` - Simple async task
- `GET /concurrent` - Concurrent async operations
- `GET /sync-task` - Simple synchronous task
- `GET /sync-with-async` - **Sync endpoint using async primitives**
  - Uses `asyncio.get_running_loop()` (with error handling)
  - Uses `asyncio.to_thread()` for blocking operations
  - Uses `asyncio.run_coroutine_threadsafe()` for scheduling

## Architecture

```
┌────────────────────────────────────────────┐
│  Gunicorn Master                           │
├────────────────────────────────────────────┤
│  Worker 1 (uvloop event loop)              │
│    - MainThread: Event loop                │
│    - AnyIO: Sync endpoints          │
│    - Uses: asyncio.run_coroutine_threadsafe │
└────────────────────────────────────────────┘
```

## Use Cases

This example is useful for:
1. Understanding async/await in FastAPI
2. Learning how to bridge sync and async code
3. Testing uvloop performance improvements
4. Deploying FastAPI with Gunicorn in production
5. Understanding Python's asyncio primitives

## Requirements

- Python 3.9+
- pip
- git

## License

MIT (or your preferred license)

## Author

Created as a comprehensive example demonstrating FastAPI + Gunicorn + Uvicorn + uvloop patterns.

