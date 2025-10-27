# How to Get the Running Event Loop from a Sync Method

## The Problem

When you have a **synchronous endpoint** (`def sync_with_async_pattern`) that runs in a **thread pool** (like "AnyIO worker thread"), you **cannot** get a running event loop using `asyncio.get_running_loop()` because:

1. **Sync endpoints run in thread pools** - These are separate threads without event loops
2. **Event loops run in the main worker thread** - The async event loop runs in "MainThread" 
3. **Each thread has its own context** - You can't access another thread's event loop directly

## What Happens

From the logs you'll see:

```
🟢 [SYNC_WITH_ASYNC] Step 1: Attempt to get running event loop using asyncio.get_running_loop()
🟢 [SYNC_WITH_ASYNC] ERROR: RuntimeError when calling asyncio.get_running_loop(): no running event loop
🟢 [SYNC_WITH_ASYNC] This is expected in a sync endpoint - falling back to stored loop reference
🟢 [SYNC_WITH_ASYNC] Using stored event loop reference
🟢 [SYNC_WITH_ASYNC] Event loop type: _UnixSelectorEventLoop
🟢 [SYNC_WITH_ASYNC] Event loop is running: True  # Note: It's running in MainThread, not this thread!
```

## The Solution

The code handles this by:

1. **Storing the event loop at startup** in a global variable `_event_loop`
2. **Trying to get the running loop** with `asyncio.get_running_loop()` (which fails in sync context)
3. **Catching the RuntimeError** and using the stored reference instead
4. **Scheduling work on the other thread's event loop** using `asyncio.run_coroutine_threadsafe()`

## Code Flow

```python
def sync_with_async_pattern(seconds: float = 0.2):
    # Step 1: Try to get running loop (WILL FAIL in sync context)
    try:
        loop = asyncio.get_running_loop()  # ❌ RuntimeError!
    except RuntimeError as e:
        # This is EXPECTED - sync endpoints don't have running loops
        # Fall back to stored event loop from startup
        global _event_loop
        loop = _event_loop  # ✅ This is the loop from MainThread
    
    # Step 2: Create coroutine that will run in thread pool
    blocking_coro = asyncio.to_thread(blocking_operation, seconds)
    
    # Step 3: Schedule coroutine on the OTHER thread's event loop
    future = asyncio.run_coroutine_threadsafe(blocking_coro, loop)
    #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #         This is the KEY - run_coroutine_threadsafe allows
    #         scheduling work on an event loop running in ANOTHER thread
    
    # Step 4: Wait for result (blocks THIS thread, not the event loop)
    blocking_result = future.result()
    
    return blocking_result
```

## Thread Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MainThread                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Event Loop Running Here                          │ │
│  │  - Handles all async operations                   │ │
│  │  - Processes async endpoints                      │ │
│  │  - Started at app startup                        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              AnyIO worker thread                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Sync Endpoint Running Here                       │ │
│  │  - NO event loop here!                            │ │
│  │  - Uses asyncio.run_coroutine_threadsafe()       │ │
│  │  - Schedules work on MainThread's event loop      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Why `asyncio.run_coroutine_threadsafe()`?

This is the bridge between sync and async contexts:

- **From**: A sync function in a thread without an event loop
- **To**: An event loop running in another thread (MainThread)
- **How**: Thread-safe scheduling that doesn't block the event loop

## Key Takeaways

1. ❌ **Cannot** call `asyncio.get_running_loop()` from a sync endpoint
2. ✅ **Must** store the event loop reference at startup
3. ✅ **Must** use `asyncio.run_coroutine_threadsafe()` to schedule work
4. ✅ This allows blocking operations without blocking the event loop

