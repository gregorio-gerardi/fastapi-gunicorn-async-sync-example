"""
FastAPI server to test with gunicorn and uvicorn workers
Demonstrates asyncio compatibility with uvloop
"""

import asyncio
from fastapi import FastAPI, HTTPException
from datetime import datetime
import time
import logging
import threading

# Try to use uvloop for better performance
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("✅ Using uvloop event loop")
except ImportError:
    print("⚠️  uvloop not available, using default event loop")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - [%(threadName)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI Gunicorn Test Server")


# Store the event loop reference
_event_loop = None


@app.on_event("startup")
async def store_event_loop():
    """Store reference to the event loop on startup"""
    import os
    global _event_loop
    _event_loop = asyncio.get_running_loop()
    thread_name = threading.current_thread().name
    thread_id = threading.current_thread().ident
    
    # Determine event loop type
    loop_type = type(_event_loop).__name__
    is_uvloop = "Loop" in loop_type or "uvloop" in str(asyncio.get_event_loop_policy()).lower()
    
    logger.info(f"🚀 [STARTUP] Application startup event triggered")
    logger.info(f"🚀 [STARTUP] Worker PID: {os.getpid()}")
    logger.info(f"🚀 [STARTUP] Storing event loop reference")
    logger.info(f"🚀 [STARTUP] Event loop type: {loop_type}")
    logger.info(f"🚀 [STARTUP] Using uvloop: {is_uvloop}")
    logger.info(f"🚀 [STARTUP] Event loop is running: {_event_loop.is_running()}")
    logger.info(f"🚀 [STARTUP] Event loop thread: {thread_name} (ID: {thread_id})")
    logger.info(f"🚀 [STARTUP] Event loop memory address: {id(_event_loop)}")


@app.get("/")
async def root():
    """Simple root endpoint"""
    return {
        "message": "FastAPI server running with Gunicorn + Uvicorn workers",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/async-task")
async def async_task():
    """
    Simulates an async task with await
    """
    await asyncio.sleep(0.1)
    return {
        "message": "Async task completed",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/async-delay/{seconds}")
async def async_delay(seconds: float):
    """
    Demonstrates async I/O wait
    """
    start_time = time.time()
    await asyncio.sleep(seconds)
    elapsed = time.time() - start_time
    return {
        "message": f"Waited for {seconds} seconds",
        "actual_wait": round(elapsed, 3),
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/concurrent")
async def concurrent():
    """
    Demonstrates concurrent async operations
    """
    start_time = time.time()
    
    # Simulate multiple concurrent tasks
    results = await asyncio.gather(
        asyncio.sleep(0.1),
        asyncio.sleep(0.2),
        asyncio.sleep(0.3),
    )
    
    elapsed = time.time() - start_time
    
    return {
        "message": "Concurrent tasks completed",
        "elapsed_time": round(elapsed, 3),
        "expected_time": 0.3,  # Should take ~0.3s, not 0.6s
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/sync-task")
def sync_task():
    """
    Synchronous endpoint for comparison
    """
    time.sleep(0.1)
    return {
        "message": "Synchronous task completed",
        "timestamp": datetime.now().isoformat(),
    }


def blocking_operation(seconds: float) -> dict:
    """
    A blocking synchronous function that simulates work
    This will be run in a thread via asyncio.to_thread()
    """
    thread_name = threading.current_thread().name
    thread_id = threading.current_thread().ident
    
    logger.info(f"🔵 [BLOCKING_OPERATION] Starting blocking operation in thread {thread_name} (ID: {thread_id})")
    logger.info(f"🔵 [BLOCKING_OPERATION] Requested sleep time: {seconds} seconds")
    
    start_time = time.time()
    
    logger.info(f"🔵 [BLOCKING_OPERATION] Calling time.sleep({seconds}) - blocking I/O operation")
    time.sleep(seconds)
    
    elapsed = time.time() - start_time
    logger.info(f"🔵 [BLOCKING_OPERATION] Sleep completed, actual elapsed time: {round(elapsed, 3)} seconds")
    
    result = {
        "blocking_time": seconds,
        "actual_time": round(elapsed, 3),
        "executed_in_thread": thread_name,
    }
    
    logger.info(f"🔵 [BLOCKING_OPERATION] Returning result: {result}")
    return result


@app.get("/sync-with-async")
def sync_with_async_pattern(seconds: float = 0.2):
    """
    Synchronous endpoint that internally uses async primitives:
    - asyncio.get_running_loop() to get the event loop (from stored reference)
    - asyncio.to_thread() to run blocking sync method in thread pool
    - asyncio.run_coroutine_threadsafe() to schedule and wait for coroutine
    
    This demonstrates running blocking code in a sync endpoint
    without blocking the event loop.
    """
    logger.info("=" * 80)
    logger.info("🟢 [SYNC_WITH_ASYNC] Starting sync endpoint with async primitives")
    logger.info("=" * 80)
    
    # Get the current thread info
    endpoint_thread_id = threading.current_thread().ident
    endpoint_thread_name = threading.current_thread().name
    start_time = time.time()
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Endpoint called with seconds={seconds}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Endpoint executing in thread: {endpoint_thread_name} (ID: {endpoint_thread_id})")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] This is a SYNCHRONOUS endpoint (def, not async)")
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Step 1: Attempt to get running event loop using asyncio.get_running_loop()")
    
    # Try to get the running event loop using asyncio.get_running_loop()
    # This will likely fail in a sync endpoint (def) because there's no running loop
    try:
        loop = asyncio.get_running_loop()
        logger.info(f"🟢 [SYNC_WITH_ASYNC] SUCCESS: Got running loop using asyncio.get_running_loop()")
        logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop type: {type(loop).__name__}")
        logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop is running: {loop.is_running()}")
        logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop is closed: {loop.is_closed()}")
    except RuntimeError as e:
        logger.info(f"🟢 [SYNC_WITH_ASYNC] ERROR: RuntimeError when calling asyncio.get_running_loop(): {e}")
        logger.info(f"🟢 [SYNC_WITH_ASYNC] This is expected in a sync endpoint - falling back to stored loop reference")
        
        # Fallback to stored loop from startup
        global _event_loop
        loop = _event_loop
        
        if loop is None:
            logger.warning(f"🟢 [SYNC_WITH_ASYNC] WARNING: Stored event loop is also None, creating new loop")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            logger.info(f"🟢 [SYNC_WITH_ASYNC] Using stored event loop reference")
            logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop type: {type(loop).__name__}")
            logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop is running: {loop.is_running()}")
            logger.info(f"🟢 [SYNC_WITH_ASYNC] Event loop is closed: {loop.is_closed()}")
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Step 2: Create coroutine using asyncio.to_thread()")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Calling: asyncio.to_thread(blocking_operation, {seconds})")
    
    # Use asyncio.to_thread to create a coroutine that runs blocking operation
    # This creates a coroutine that will run the blocking function in a thread
    blocking_coro = asyncio.to_thread(blocking_operation, seconds)
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Coroutine created: {blocking_coro}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Coroutine type: {type(blocking_coro).__name__}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] This coroutine will run blocking_operation() in a thread pool")
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Step 3: Schedule coroutine using run_coroutine_threadsafe()")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Calling: asyncio.run_coroutine_threadsafe(blocking_coro, loop)")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] This schedules the coroutine on the event loop running in another thread")
    
    # Schedule the coroutine thread-safely and wait for result
    # run_coroutine_threadsafe is used when calling from a sync context
    # to schedule work on an event loop running in a different thread
    future = asyncio.run_coroutine_threadsafe(blocking_coro, loop)
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Future created: {future}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Future type: {type(future).__name__}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Future done: {future.done()}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Coroutine has been scheduled on event loop")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] The event loop is now managing the async execution")
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Step 4: Wait for result using future.result()")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Calling: future.result(timeout={seconds + 2})")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] This BLOCKS the endpoint thread but NOT the event loop")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] The event loop continues processing other requests concurrently")
    
    # Wait for the result (this blocks the sync endpoint thread, but not the event loop)
    blocking_result = future.result(timeout=seconds + 2)
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Future completed!")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Result received: {blocking_result}")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Future done: {future.done()}")
    
    elapsed = time.time() - start_time
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Total elapsed time in endpoint: {round(elapsed, 3)} seconds")
    
    response = {
        "message": "Sync endpoint using async primitives internally",
        "blocking_operation_result": blocking_result,
        "endpoint_thread_name": endpoint_thread_name,
        "event_loop_running_in_thread": loop.get_task_factory(),
        "total_elapsed_time": round(elapsed, 3),
        "event_loop_used": True,
        "asyncio_to_thread_used": True,
        "run_coroutine_threadsafe_used": True,
        "timestamp": datetime.now().isoformat(),
    }
    
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Preparing response")
    logger.info(f"🟢 [SYNC_WITH_ASYNC] Response: {response}")
    logger.info("=" * 80)
    logger.info("🟢 [SYNC_WITH_ASYNC] Endpoint completed successfully")
    logger.info("=" * 80)
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

