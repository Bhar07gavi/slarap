#!/usr/bin/env python3

"""
Test for the Alert Engine.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analytics.alerts import AlertEngine
from backend.monitor.resources import ResourceMonitor
from backend.storage import db


def main() -> None:
    db.initialize_database()

    monitor = ResourceMonitor(interval=1.0, persist=True)
    monitor.start()

    alerts = AlertEngine(monitor, interval=2.0)
    alerts.start()

    print("Alert Engine started. Waiting for checks...")

    # Wait a few seconds
    time.sleep(8)

    print("\nRecent Alerts:")
    for alert in alerts.get_recent_alerts(10):
        print(f"  [{alert['time']}] {alert['level']:<8} "
              f"{alert['category']:<10} {alert['message'][:60]}")

    alerts.stop()
    alerts.join(timeout=3)
    monitor.stop()
    monitor.join(timeout=3)


if __name__ == "__main__":
    main()
