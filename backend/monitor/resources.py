"""
SLARAP Resource Monitoring Engine.

This module monitors:
- CPU
- Memory
- Swap
- Disk
- Network
- Load average
- Process count
- System uptime

It runs in a separate thread and protects shared data using a mutex.
"""

import threading
import time
from collections import deque
from typing import Any

import psutil

from backend import config
from backend.storage import db


class ResourceMonitor(threading.Thread):
    """Continuously collect Linux resource information."""

    def __init__(
        self,
        interval: float = config.MONITOR_INTERVAL,
        persist: bool = True,
    ) -> None:
        super().__init__(name="ResourceMonitor", daemon=True)

        self.interval = interval
        self.persist = persist

        # Mutex used to protect shared monitoring information.
        self.data_lock = threading.RLock()

        # Event used to safely stop the monitoring thread.
        self.stop_event = threading.Event()

        self.latest: dict[str, Any] = {}

        self.history = {
            "timestamp": deque(maxlen=config.HISTORY_POINTS),
            "cpu": deque(maxlen=config.HISTORY_POINTS),
            "memory": deque(maxlen=config.HISTORY_POINTS),
            "swap": deque(maxlen=config.HISTORY_POINTS),
            "disk": deque(maxlen=config.HISTORY_POINTS),
            "network_upload": deque(maxlen=config.HISTORY_POINTS),
            "network_download": deque(maxlen=config.HISTORY_POINTS),
        }

        self.previous_network = psutil.net_io_counters()
        self.previous_network_time = time.time()

        # Prime psutil's CPU measurement.
        psutil.cpu_percent(interval=None)

    def collect_sample(self) -> dict[str, Any]:
        """Collect one complete resource sample."""

        now = time.time()

        cpu = psutil.cpu_percent(interval=None)
        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)

        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage(config.DISK_MOUNT)
        network = psutil.net_io_counters()

        elapsed = max(now - self.previous_network_time, 0.000001)

        upload_kbps = (
            network.bytes_sent - self.previous_network.bytes_sent
        ) / elapsed / 1024

        download_kbps = (
            network.bytes_recv - self.previous_network.bytes_recv
        ) / elapsed / 1024

        self.previous_network = network
        self.previous_network_time = now

        try:
            load_average = psutil.getloadavg()
        except (AttributeError, OSError):
            load_average = (0.0, 0.0, 0.0)

        return {
            "timestamp": now,
            "cpu": cpu,
            "cpu_per_core": cpu_per_core,
            "memory": memory.percent,
            "memory_used_gb": round(memory.used / (1024 ** 3), 2),
            "memory_total_gb": round(memory.total / (1024 ** 3), 2),
            "swap": swap.percent,
            "disk": disk.percent,
            "disk_free_gb": round(disk.free / (1024 ** 3), 2),
            "disk_total_gb": round(disk.total / (1024 ** 3), 2),
            "network_sent": network.bytes_sent,
            "network_received": network.bytes_recv,
            "network_upload_kbps": round(upload_kbps, 2),
            "network_download_kbps": round(download_kbps, 2),
            "load": load_average,
            "process_count": len(psutil.pids()),
            "uptime": now - psutil.boot_time(),
            "cpu_count": psutil.cpu_count() or 1,
        }

    def run(self) -> None:
        """Main thread loop."""

        while not self.stop_event.is_set():
            try:
                sample = self.collect_sample()

                # Critical section: modify shared state under a lock.
                with self.data_lock:
                    self.latest = sample
                    self.history["timestamp"].append(sample["timestamp"])
                    self.history["cpu"].append(sample["cpu"])
                    self.history["memory"].append(sample["memory"])
                    self.history["swap"].append(sample["swap"])
                    self.history["disk"].append(sample["disk"])
                    self.history["network_upload"].append(
                        sample["network_upload_kbps"]
                    )
                    self.history["network_download"].append(
                        sample["network_download_kbps"]
                    )

                if self.persist:
                    db.insert_metric(sample)

            except Exception as error:
                print(f"[ResourceMonitor] Error: {error}")

            self.stop_event.wait(self.interval)

    def get_snapshot(self) -> dict[str, Any]:
        """Return a thread-safe copy of the latest sample."""

        with self.data_lock:
            return dict(self.latest)

    def get_series(self, name: str) -> list[Any]:
        """Return a thread-safe copy of one history series."""

        with self.data_lock:
            if name not in self.history:
                raise KeyError(f"Unknown monitoring series: {name}")

            return list(self.history[name])

    def stop(self) -> None:
        """Request that the monitor thread stop."""

        self.stop_event.set()


def human_uptime(seconds: float) -> str:
    """Convert uptime seconds to days, hours, and minutes."""

    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    return f"{days}d {hours}h {minutes}m"


def calculate_health_score(
    sample: dict[str, Any],
) -> tuple[int, str]:
    """Calculate a simple system-health score from 0 to 100."""

    if not sample:
        return 0, "UNKNOWN"

    cpu_penalty = max(0.0, sample["cpu"] - 60.0) * 0.6
    memory_penalty = max(0.0, sample["memory"] - 65.0) * 0.7
    disk_penalty = max(0.0, sample["disk"] - 75.0) * 0.8

    load_per_core = (
        sample["load"][0] / max(sample["cpu_count"], 1)
    )
    load_penalty = max(0.0, load_per_core - 1.0) * 15.0

    score = round(
        100
        - cpu_penalty
        - memory_penalty
        - disk_penalty
        - load_penalty
    )

    score = max(0, min(100, score))

    if score >= 85:
        label = "EXCELLENT"
    elif score >= 70:
        label = "GOOD"
    elif score >= 50:
        label = "FAIR"
    elif score >= 30:
        label = "POOR"
    else:
        label = "CRITICAL"

    return score, label
