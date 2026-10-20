"""
Global configuration for SLARAP.
"""

from pathlib import Path


# backend/config.py -> backend -> slarap
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
WORKFLOW_DIR = BASE_DIR / "workflows"

for directory in (DATA_DIR, EXPORT_DIR, WORKFLOW_DIR):
    directory.mkdir(parents=True, exist_ok=True)


DB_PATH = DATA_DIR / "slarap.db"
APP_LOG_PATH = DATA_DIR / "slarap.log"
SCHEDULE_PATH = DATA_DIR / "schedules.json"


MONITOR_INTERVAL = 2.0
HISTORY_POINTS = 300
DISK_MOUNT = "/"


THRESHOLDS = {
    "cpu": 85.0,
    "memory": 90.0,
    "disk": 90.0,
    "swap": 60.0,
    "load_per_core": 2.0,
    "process_count": 600,
    "failed_logins": 5,
    "task_runtime": 300.0,
}

ALERT_COOLDOWN = 60


LOG_FILES = {
    "syslog": "/var/log/syslog",
    "auth": "/var/log/auth.log",
    "kernel": "/var/log/kern.log",
    "dpkg": "/var/log/dpkg.log",
}

LOG_TAIL_LINES = 4000


PREDICTION_WINDOW = 30
PREDICTION_STEPS = 10
