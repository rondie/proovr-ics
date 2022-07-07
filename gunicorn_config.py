import os

host = os.getenv("PROOVR_ICS_HOST", "0.0.0.0")
port = os.getenv("PROOVR_ICS_PORT", 5000)
workers = os.getenv("PROOVR_ICS_WORKERS", 4)
threads = os.getenv("PROOVR_ICS_THREADS", 4)
timeout = os.getenv("PROOVR_ICS_TIMEOUT", 120)

bind = f"{host}:{port}"
workers = f"{workers}"
threads = f"{threads}"
timeout = f"{timeout}"
