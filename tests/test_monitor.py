#!/usr/bin/env python3

import time

from backend.monitor.resources import (
    ResourceMonitor,
    calculate_health_score,
    human_uptime,
)
from backend.storage import db


def main() -> None:
    db.initialize_database()

    monitor = ResourceMonitor(interval=1.0, persist=True)

    print("Starting ResourceMonitor thread...")
    monitor.start()

    try:
        for sample_number in range(1, 6):
            time.sleep(1.2)

            sample = monitor.get_snapshot()
            score, label = calculate_health_score(sample)

            print(f"\nSample {sample_number}")
            print("-" * 50)
            print(f"CPU:       {sample['cpu']:.1f}%")
            print(f"Memory:    {sample['memory']:.1f}%")
            print(f"Swap:      {sample['swap']:.1f}%")
            print(f"Disk:      {sample['disk']:.1f}%")
            print(f"Processes: {sample['process_count']}")
            print(f"Load:      {sample['load']}")
            print(f"Uptime:    {human_uptime(sample['uptime'])}")
            print(
                "Network:   "
                f"down={sample['network_download_kbps']:.2f} KB/s, "
                f"up={sample['network_upload_kbps']:.2f} KB/s"
            )
            print(f"Health:    {score}/100 ({label})")

    finally:
        print("\nStopping ResourceMonitor...")
        monitor.stop()
        monitor.join(timeout=5)

    print("Monitor test completed.")


if __name__ == "__main__":
    main()
