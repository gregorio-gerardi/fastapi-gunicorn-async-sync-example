# --preload Flag with Gunicorn

## Summary

**YES**, `--preload` works with the shared app memory pattern and our sync-with-async endpoint!

## What --preload Does

The `--preload` flag loads the application **before** forking worker processes. This enables:

1. **Shared memory via copy-on-write**: Application code is loaded once in the master process
2. **Lower memory footprint**: Workers share code via copy-on-write semantics
3. **Faster worker startup**: Code is already loaded when workers fork

## How It Works with Our Setup

### Without --preload (Default)
```
Master Process
  ↓ Load app code
  ↓ Fork workers
  Worker 1: Has its own copy of app code
  Worker 2: Has its own copy of app code
```

### With --preload
```
Master Process
  ↓ Load app code ONCE
  ↓ Fork workers
  Worker 1: Shares code (copy-on-write) + its own event loop
  Worker 2: Shares code (copy-on-write) + its own event loop
```

## Key Point: Each Worker Has Its Own Event Loop

Even with `--preload`, **each worker gets its own event loop** when `@app.on_event("startup")` fires:

```
🚀 [STARTUP] Worker PID: 86723
🚀 [STARTUP] Event loop memory address: 5101355024

🚀 [STARTUP] Worker PID: 86724
🚀 [STARTUP] Event loop memory address: 4832002064  # Different!
```

This is **correct** because:
1. Code is shared via copy-on-write
2. Event loop is per-process/worker
3. The global `_event_loop` variable gets written to in each worker
4. Writes trigger copy-on-write, creating separate instances

## Architecture with --preload

```
┌────────────────────────────────────────────────────┐
│  Master Process (Gunicorn)                        │
│  ┌──────────────────────────────────────────────┐ │
│  │  Application Code (loaded once)             │ │
│  │  - main.py                                  │ │
│  │  - FastAPI app instance                     │ │
│  │  - Global variables initialized             │ │
│  └──────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────┤
│  Fork Worker 1                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Shares: Application code (read-only)       │ │
│  │  Owns: _event_loop (written in startup)     │ │
│  │  Owns: Event loop instance (unique)         │ │
│  └──────────────────────────────────────────────┘ │
├────────────────────────────────────────────────────┤
│  Fork Worker 2                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Shares: Application code (read-only)       │ │
│  │  Owns: _event_loop (written in startup)     │ │
│  │  Owns: Event loop instance (unique)         │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

## Benefits

1. **Memory Efficiency**: Application code is shared between workers
2. **Faster Startup**: Code is preloaded before forking
3. **Better for Large Applications**: Reduces memory footprint with many workers

## Testing

### Run without --preload:
```bash
source venv/bin/activate
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Run with --preload:
```bash
source venv/bin/activate
gunicorn main:app --preload -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

Or use the updated start.sh:
```bash
# Without preload
source venv/bin/activate
./start.sh

# With preload
source venv/bin/activate
PRELOAD=1 ./start.sh
```

### Use the test script:
```bash
./test_preload.sh
```

## Verification

Check that each worker has its own event loop:
```bash
grep "Event loop memory address" /tmp/gunicorn_preload_test.log
```

You'll see different memory addresses for each worker, confirming they have separate event loops.

## Important Notes

1. **Global Variables**: When using `--preload`, the global `_event_loop` is **None** in the master process
2. **Worker Initialization**: Each worker's `@app.on_event("startup")` hook runs and sets its own `_event_loop`
3. **Isolation**: Each worker's `_event_loop` is isolated from others
4. **Sync Endpoint**: Still works correctly - it gets the event loop from the worker that handles the request

## Compatibility

✅ Works with:
- uvloop
- Multiple workers
- Async endpoints
- Sync endpoints with asyncio primitives
- Gunicorn with UvicornWorker

✅ Verified:
- Each worker gets its own event loop
- Memory addresses are different per worker
- Sync-with-async endpoint works correctly
- RuntimeError from `asyncio.get_running_loop()` is properly caught

## Conclusion

The `--preload` flag is **safe to use** with this setup. It provides memory benefits while maintaining proper isolation of event loops per worker.

