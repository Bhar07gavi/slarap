#!/usr/bin/env python3

"""
Test for the Report Generator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config
from backend.reports import generator
from backend.monitor.resources import ResourceMonitor
from backend.storage import db


def main() -> None:
    db.initialize_database()

    monitor = ResourceMonitor(interval=1.0, persist=True)
    monitor.start()

    import time
    time.sleep(3)  # Collect some data

    print("=" * 60)
    print("SLARAP Report Generator Tests")
    print("=" * 60)

    # Generate TXT report
    print("\n--- TXT Report ---")
    txt_path = generator.save_txt_report(monitor)
    print(f"Saved: {txt_path}")
    print(f"Size: {Path(txt_path).stat().st_size} bytes")

    # CSV exports
    print("\n--- CSV Exports ---")
    metrics_path, metrics_count = generator.export_metrics_csv(24)
    print(f"Metrics: {metrics_path} ({metrics_count} rows)")

    tasks_path, tasks_count = generator.export_tasks_csv()
    print(f"Tasks:   {tasks_path} ({tasks_count} rows)")

    alerts_path, alerts_count = generator.export_alerts_csv()
    print(f"Alerts:  {alerts_path} ({alerts_count} rows)")

    # PDF
    print("\n--- PDF Report ---")
    pdf_path, error = generator.export_pdf_report(monitor)
    if pdf_path:
        print(f"Saved: {pdf_path}")
        print(f"Size: {Path(pdf_path).stat().st_size} bytes")
    else:
        print(f"Error: {error}")

    # Full report generation
    print("\n--- All Reports ---")
    all_reports = generator.generate_all_reports(monitor)
    for key, path in all_reports.items():
        print(f"  {key}: {path}")

    monitor.stop()
    monitor.join(timeout=3)

    print("\n" + "=" * 60)
    print("Report generator tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
