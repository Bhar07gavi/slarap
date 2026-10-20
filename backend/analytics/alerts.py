"""
SLARAP Smart Alert System.

Continuously monitors system thresholds and fires alerts when:
- CPU exceeds threshold
- Memory exceeds threshold
- Disk usage exceeds threshold
- Swap usage exceeds threshold
- Load average is too high
- Too many processes running
- Failed login attempts detected
- Automation tasks fail

Implements cooldown de-duplication to avoid alert storms.
"""

import threading
import time
from typing import Any, Callable

from backend import config
from backend.procmgr import manager
from backend.storage import db


class AlertEngine(threading.Thread):
    """
    Background thread that checks alert conditions.
    """

    def __init__(self, monitor, interval: float = 5.0):
        super().__init__(name="AlertEngine", daemon=True)
        self.monitor = monitor
        self.interval = interval
        self.lock = threading.RLock()
        self.recent_alerts: list[dict[str, Any]] = []
        self._last_fire: dict[str, float] = {}
        self._stop_event = threading.Event()
        self.subscribers: list[Callable[[dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback to receive alerts."""

        self.subscribers.append(callback)

    def get_recent_alerts(self, limit: int = 25) -> list[dict[str, Any]]:
        """Return a copy of recent alerts."""

        with self.lock:
            return self.recent_alerts[:limit]

    def fire(
        self,
        level: str,
        category: str,
        message: str,
        current_value: float | None = None,
        threshold: float | None = None,
    ) -> None:
        """
        Fire an alert if not recently fired the same one.
        """

        key = f"{category}:{message[:40]}"
        now = time.time()

        with self.lock:
            # Cooldown de-duplication
            if now - self._last_fire.get(key, 0) < config.ALERT_COOLDOWN:
                return

            self._last_fire[key] = now

            alert = {
                "timestamp": now,
                "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "level": level,
                "category": category,
                "message": message,
                "value": current_value,
                "threshold": threshold,
            }
            self.recent_alerts.insert(0, alert)
            self.recent_alerts = self.recent_alerts[:200]

        # Store in database
        db.insert_alert(level, category, message, current_value, threshold)

        # Notify subscribers
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception:
                pass

        print(f"\n[ALERT] {level} - {category}: {message}")

    def check_resource_thresholds(self, sample: dict[str, Any]) -> None:
        """Check resource thresholds against a monitoring sample."""

        if not sample:
            return

        thresholds = config.THRESHOLDS

        if sample["cpu"] > thresholds["cpu"]:
            top = manager.top_processes(1, "cpu")
            process_info = (
                f" (top: {top[0]['name']} PID {top[0]['pid']})" if top else ""
            )
            self.fire(
                "CRITICAL",
                "cpu",
                f"CPU usage {sample['cpu']:.1f}%{process_info}",
                sample["cpu"],
                thresholds["cpu"],
            )

        if sample["memory"] > thresholds["memory"]:
            self.fire(
                "CRITICAL",
                "memory",
                f"Memory {sample['memory']:.1f}% "
                f"({sample['memory_used_gb']}/{sample['memory_total_gb']} GB)",
                sample["memory"],
                thresholds["memory"],
            )

        if sample["disk"] > thresholds["disk"]:
            self.fire(
                "CRITICAL",
                "disk",
                f"Disk {sample['disk']:.1f}% used, "
                f"only {sample['disk_free_gb']} GB free",
                sample["disk"],
                thresholds["disk"],
            )

        if sample["swap"] > thresholds["swap"]:
            self.fire(
                "WARNING",
                "memory",
                f"Swap usage {sample['swap']:.1f}%",
                sample["swap"],
                thresholds["swap"],
            )

        cores = sample.get("cpu_count") or 1
        load_per_core = sample["load"][0] / cores
        if load_per_core > thresholds["load_per_core"]:
            self.fire(
                "WARNING",
                "load",
                f"Load average {sample['load'][0]:.2f} "
                f"({load_per_core:.2f} per core)",
                load_per_core,
                thresholds["load_per_core"],
            )

        if sample["process_count"] > thresholds["process_count"]:
            self.fire(
                "WARNING",
                "process",
                f"High process count: {sample['process_count']}",
                sample["process_count"],
                thresholds["process_count"],
            )

    def check_security(self) -> None:
        """Analyze authentication logs for security events."""

        # Track which events we've already alerted about
        if not hasattr(self, "_seen_security_events"):
            self._seen_security_events = set()

        try:
            from backend.analytics import logs

            report = logs.analyze(sources=["auth"], persist=False)
        except Exception:
            return

        failed_logins = report.get("total_failed_logins", 0)
        if failed_logins >= config.THRESHOLDS["failed_logins"]:
            top_failed = sorted(
                report["failed_logins"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]

            self.fire(
                "CRITICAL",
                "security",
                f"{failed_logins} failed login attempts. "
                f"Top: {', '.join(f'{k}({v})' for k, v in top_failed)}",
                failed_logins,
                config.THRESHOLDS["failed_logins"],
            )

        # Only alert on NEW security events (not historical repeats)
        for event in report.get("security_events", []):
            if event not in self._seen_security_events:
                self._seen_security_events.add(event)
                self.fire("WARNING", "security", event)

    def run(self) -> None:
        """Main loop that periodically checks thresholds."""

        tick = 0
        while not self._stop_event.is_set():
            try:
                sample = self.monitor.get_snapshot()
                self.check_resource_thresholds(sample)

                # Check security every ~2 minutes (24 ticks at 5s)
                if tick % 24 == 0:
                    self.check_security()

                # Reap background processes and alert if any failed
                for pid, info, exit_code in manager.reap_background_processes():
                    if exit_code not in (0, None):
                        self.fire(
                            "WARNING",
                            "automation",
                            f"Background job PID {pid} exited with "
                            f"{exit_code}: {info['command']}",
                            exit_code,
                            0,
                        )

            except Exception as error:
                print(f"[AlertEngine] Error: {error}")

            tick += 1
            self._stop_event.wait(self.interval)

    def stop(self) -> None:
        """Stop the alert engine thread."""

        self._stop_event.set()
    # Add this method to AlertEngine class
    def _check_new_security_events(self) -> None:
        """Only alert on NEW security events (avoid repeats)."""
        
        # Maintain a set of seen events
        if not hasattr(self, "_seen_security_events"):
            self._seen_security_events = set()
        
        try:
            from backend.analytics import logs
            report = logs.analyze(sources=["auth"], persist=False)
        except Exception:
            return
        
        # Check failed logins (already handled by threshold)
        # Check security events like "New user created"
        for event in report.get("security_events", []):
            if event not in self._seen_security_events:
                self._seen_security_events.add(event)
                self.fire("WARNING", "security", event)
