"""
Gunicorn configuration file with uvloop support
"""

# Bind address
bind = "0.0.0.0:8000"

# Number of worker processes
workers = 4

# Worker class (Uvicorn worker for async support)
worker_class = "uvicorn.workers.UvicornWorker"

# Each worker process spawns 1 thread
threads = 1

# Maximum simultaneous requests per worker
worker_connections = 1000

# Timeout for graceful workers restart
timeout = 120

# Keepalive for 2 seconds
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr
loglevel = "info"

# Process naming
proc_name = "fastapi_gunicorn_test"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Worker class arguments for uvloop
worker_tmp_dir = "/dev/shm"  # Optional: use shared memory for better performance

