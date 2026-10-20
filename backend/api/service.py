"""
SLARAP Centralized Backend Service Manager.

Ensures singleton instances of:
- ResourceMonitor
- AlertEngine
- AutomationEngine
- Scheduler

Prevents duplicate thread creation and ensures clean startup/shutdown.
"""

import threading
from typing import Optional
from backend.storage import db
from backend.monitor.resources import ResourceMonitor
from backend.analytics.alerts import AlertEngine
from backend.automation.engine import AutomationEngine, Scheduler


class ServiceManager:
    """Singleton service manager to coordinate backend threads."""
    _instance: Optional["ServiceManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        db.initialize_database()
        self.monitor = ResourceMonitor(persist=True)
        self.alerts = AlertEngine(self.monitor)
        self.engine = AutomationEngine(alert_callback=self.alerts.fire)
        self.scheduler = Scheduler(self.engine)
        self._is_running = False

    @classmethod
    def get_instance(cls) -> "ServiceManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = ServiceManager()
            return cls._instance

    def start(self) -> None:
        """Start background services if not already running."""
        with self._lock:
            if not self._is_running:
                print("[API Service] Starting ResourceMonitor, AlertEngine, Scheduler...")
                self.monitor.start()
                self.alerts.start()
                self.scheduler.start()
                self._is_running = True

    def stop(self) -> None:
        """Gracefully stop background services."""
        with self._lock:
            if self._is_running:
                print("[API Service] Stopping background services...")
                self.monitor.stop()
                self.alerts.stop()
                self.scheduler.stop()
                self._is_running = False
