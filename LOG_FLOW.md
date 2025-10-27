# Logging Flow Explanation

This document explains the detailed logging flow for the `/sync-with-async` endpoint.

## Request Flow

When you call `/sync-with-async?seconds=0.5`, you'll see logs in this order:

### 1. Startup Phase (When Server Starts)
```
🚀 [STARTUP] Application startup event triggered
🚀 [STARTUP] Storing event loop reference
🚀 [STARTUP] Event loop type: _UnixSelectorEventLoop
🚀 [STARTUP] Event loop is running: False
🚀 [STARTUP] Event loop thread: MainThread
```

### 2. Sync Endpoint Entry (Green Logs)
```
================================================================================
🟢 [SYNC_WITH_ASYNC] Starting sync endpoint with async primitives
================================================================================
🟢 [SYNC_WITH_ASYNC] Endpoint called with seconds=0.5
🟢 [SYNC_WITH_ASYNC] Endpoint executing in thread: ThreadPoolExecutor-0_0 (ID: 12345)
🟢 [SYNC_WITH_ASYNC] This is a SYNCHRONOUS endpoint (def, not async)
```

### 3. Step 1: Get Event Loop Reference
```
🟢 [SYNC_WITH_ASYNC] Step 1: Get event loop reference
🟢 [SYNC_WITH_ASYNC] Retrieved stored event loop: True
🟢 [SYNC_WITH_ASYNC] Event loop type: _UnixSelectorEventLoop
🟢 [SYNC_WITH_ASYNC] Event loop is running: True
🟢 [SYNC_WITH_ASYNC] Event loop is closed: False
```

### 4. Step 2: Create Coroutine with asyncio.to_thread()
```
🟢 [SYNC_WITH_ASYNC] Step 2: Create coroutine using asyncio.to_thread()
🟢 [SYNC_WITH_ASYNC] Calling: asyncio.to_thread(blocking_operation, 0.5)
🟢 [SYNC_WITH_ASYNC] Coroutine created: <coroutine object>
🟢 [SYNC_WITH_ASYNC] Coroutine type: coroutine
🟢 [SYNC_WITH_ASYNC] This coroutine will run blocking_operation() in a thread pool
```

### 5. Step 3: Schedule Coroutine with run_coroutine_threadsafe()
```
🟢 [SYNC_WITH_ASYNC] Step 3: Schedule coroutine using run_coroutine_threadsafe()
🟢 [SYNC_WITH_ASYNC] Calling: asyncio.run_coroutine_threadsafe(blocking_coro, loop)
🟢 [SYNC_WITH_ASYNC] This schedules the coroutine on the event loop running in another thread
🟢 [SYNC_WITH_ASYNC] Future created: <Future pending>
🟢 [SYNC_WITH_ASYNC] Future type: Future
🟢 [SYNC_WITH_ASYNC] Future done: False
🟢 [SYNC_WITH_ASYNC] Coroutine has been scheduled on event loop
🟢 [SYNC_WITH_ASYNC] The event loop is now managing the async execution
```

### 6. Blocking Operation Starts (Blue Logs - In Thread Pool)
```
🔵 [BLOCKING_OPERATION] Starting blocking operation in thread ThreadPoolExecutor-1_0 (ID: 67890)
🔵 [BLOCKING_OPERATION] Requested sleep time: 0.5 seconds
🔵 [BLOCKING_OPERATION] Calling time.sleep(0.5) - blocking I/O operation
[... waiting 0.5 seconds ...]
🔵 [BLOCKING_OPERATION] Sleep completed, actual elapsed time: 0.501 seconds
🔵 [BLOCKING_OPERATION] Returning result: {'blocking_time': 0.5, ...}
```

### 7. Step 4: Wait for Result
```
🟢 [SYNC_WITH_ASYNC] Step 4: Wait for result using future.result()
🟢 [SYNC_WITH_ASYNC] Calling: future.result(timeout=2.5)
🟢 [SYNC_WITH_ASYNC] This BLOCKS the endpoint thread but NOT the event loop
🟢 [SYNC_WITH_ASYNC] The event loop continues processing other requests concurrently
```

### 8. Result Received
```
🟢 [SYNC_WITH_ASYNC] Future completed!
🟢 [SYNC_WITH_ASYNC] Result received: {'blocking_time': 0.5, ...}
🟢 [SYNC_WITH_ASYNC] Future done: True
🟢 [SYNC_WITH_ASYNC] Total elapsed time in endpoint: 0.505 seconds
```

### 9. Endpoint Complete
```
🟢 [SYNC_WITH_ASYNC] Preparing response
🟢 [SYNC_WITH_ASYNC] Response: {...}
================================================================================
🟢 [SYNC_WITH_ASYNC] Endpoint completed successfully
================================================================================
```

## Key Insights from the Logs

1. **Thread Information**: Shows that the sync endpoint runs in a thread pool, separate from the event loop thread
2. **Event Loop Access**: The loop is retrieved from the startup event
3. **asyncio.to_thread()**: Creates a coroutine that will run in a thread pool
4. **run_coroutine_threadsafe()**: Schedules the coroutine on the event loop from the sync context
5. **Non-blocking Event Loop**: The event loop continues processing other requests while waiting

## Testing

Run the server and watch the logs:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
./start.sh

# In another terminal, make a request
curl "http://localhost:8000/sync-with-async?seconds=1"
```

You'll see all the detailed logs showing the complete flow of execution!

