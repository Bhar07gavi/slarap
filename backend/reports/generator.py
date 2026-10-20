"""
SLARAP Report Generator.

Exports system reports in:
- TXT (plain text)
- CSV (metrics, tasks, alerts)
- PDF (using reportlab)
"""

import csv
import os
import datetime
from pathlib import Path
from typing import Any

from backend import config
from backend.procmgr import manager
from backend.storage import db
from backend.monitor.resources import calculate_health_score, human_uptime
from backend.analytics import predictor, recommender, logs

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as rl_canvas
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def _timestamp() -> str:
    """Return a filename-safe timestamp."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


# ---------------------------------------------------------
# 1. TXT Report
# ---------------------------------------------------------
def generate_system_report_txt(monitor, hours: int = 24) -> str:
    """Generate a complete system report as a string."""

    sample = monitor.get_snapshot()
    score, label = calculate_health_score(sample)

    lines = []
    lines.append("=" * 72)
    lines.append("   SLARAP — SYSTEM PERFORMANCE REPORT")
    lines.append(
        f"   Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    lines.append("=" * 72)

    # Current state
    lines.append("\n[ CURRENT SYSTEM STATE ]")
    if sample:
        lines.append(f"  Health Score : {score}/100 ({label})")
        lines.append(f"  CPU          : {sample['cpu']:.1f}%  ({sample['cpu_count']} cores)")
        lines.append(f"  Memory       : {sample['memory']:.1f}%  "
                     f"({sample['memory_used_gb']}/{sample['memory_total_gb']} GB)")
        lines.append(f"  Swap         : {sample['swap']:.1f}%")
        lines.append(f"  Disk ({config.DISK_MOUNT})    : {sample['disk']:.1f}%  "
                     f"({sample['disk_free_gb']} GB free of {sample['disk_total_gb']} GB)")
        lines.append(f"  Load Average : {sample['load']}")
        lines.append(f"  Processes    : {sample['process_count']}")
        lines.append(f"  Network      : up {sample['network_upload_kbps']} KB/s / "
                     f"down {sample['network_download_kbps']} KB/s")
        lines.append(f"  Uptime       : {human_uptime(sample['uptime'])}")
    else:
        lines.append("  Monitoring data not yet available.")

    # Historical summary
    lines.append(f"\n[ HISTORICAL SUMMARY — last {hours}h ]")
    rows = db.metrics_since(hours * 3600)
    if rows:
        cpu_values = [row["cpu"] for row in rows]
        mem_values = [row["memory"] for row in rows]
        lines.append(f"  Samples: {len(rows)}")
        lines.append(f"  CPU  avg {sum(cpu_values)/len(cpu_values):.1f}%  "
                     f"min {min(cpu_values):.1f}%  max {max(cpu_values):.1f}%")
        lines.append(f"  MEM  avg {sum(mem_values)/len(mem_values):.1f}%  "
                     f"min {min(mem_values):.1f}%  max {max(mem_values):.1f}%")
    else:
        lines.append("  No historical data yet.")

    # Hourly breakdown
    lines.append("\n[ HOURLY BREAKDOWN ]")
    hourly = db.aggregate(hours * 3600, "hour")
    for entry in hourly[-12:]:
        lines.append(
            f"  {entry['bucket']}  CPU avg {entry['avg_cpu']:>5}% "
            f"max {entry['max_cpu']:>5}% | MEM avg {entry['avg_mem']:>5}% "
            f"| samples {entry['samples']}"
        )

    # Top processes
    lines.append("\n[ TOP PROCESSES BY CPU ]")
    for proc in manager.top_processes(10, "cpu"):
        lines.append(
            f"  {proc['pid']:>7}  {(proc['name'] or '')[:24]:<24} "
            f"CPU {(proc.get('cpu_percent') or 0):>5.1f}%  "
            f"MEM {(proc.get('memory_percent') or 0):>5.1f}%"
        )

    # Recent alerts
    lines.append("\n[ RECENT ALERTS ]")
    alerts = db.recent_alerts(10)
    if alerts:
        for alert in alerts:
            lines.append(
                f"  {alert['date_time']}  [{alert['level']:<8}] "
                f"{alert['category']:<12} {alert['message'][:60]}"
            )
    else:
        lines.append("  None.")

    # Automation history
    lines.append("\n[ AUTOMATION LOG ]")
    task_runs = db.recent_task_runs(10)
    if task_runs:
        for task in task_runs:
            lines.append(
                f"  {task['date_time']}  {task['status']:<8} "
                f"{task['task_name'][:24]:<24} "
                f"exit={task['exit_code']:<4} {task['duration']}s"
            )
    else:
        lines.append("  No tasks executed.")

    # Predictions
    lines.append("\n")
    predictions = predictor.predict_all(monitor)
    lines.append(predictor.format_predictions(predictions))

    # Recommendations
    lines.append("\n")
    recommendations = recommender.generate_recommendations(monitor, persist=False)
    lines.append(recommender.format_recommendations(recommendations))

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def save_txt_report(monitor) -> str:
    """Generate and save a TXT report file."""

    content = generate_system_report_txt(monitor)
    filename = f"system_report_{_timestamp()}.txt"
    path = Path(config.EXPORT_DIR) / filename

    with open(path, "w") as f:
        f.write(content)

    return str(path)


# ---------------------------------------------------------
# 2. Log Analysis Report (TXT)
# ---------------------------------------------------------
def save_log_report_txt() -> str:
    """Generate and save a log analysis TXT report."""

    report = logs.analyze(persist=False)
    content = logs.format_report(report)
    filename = f"log_report_{_timestamp()}.txt"
    path = Path(config.EXPORT_DIR) / filename

    with open(path, "w") as f:
        f.write(content)

    return str(path)


# ---------------------------------------------------------
# 3. CSV Exports
# ---------------------------------------------------------
def export_metrics_csv(hours: int = 24) -> tuple[str, int]:
    """Export metrics to CSV. Returns (path, row_count)."""

    rows = db.metrics_since(hours * 3600)
    filename = f"metrics_{_timestamp()}.csv"
    path = Path(config.EXPORT_DIR) / filename

    if not rows:
        columns = [
            "timestamp", "date_time", "cpu", "memory", "swap", "disk",
            "network_sent", "network_received", "load1", "load5", "load15",
            "process_count", "uptime",
        ]
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
        return str(path), 0

    columns = [
        "timestamp", "date_time", "cpu", "memory", "swap", "disk",
        "network_sent", "network_received", "load1", "load5", "load15",
        "process_count", "uptime",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return str(path), len(rows)


def export_tasks_csv() -> tuple[str, int]:
    """Export task executions to CSV. Returns (path, row_count)."""

    rows = db.recent_task_runs(1000)
    filename = f"automation_{_timestamp()}.csv"
    path = Path(config.EXPORT_DIR) / filename

    columns = [
        "timestamp", "date_time", "workflow", "task_name", "command",
        "execution_mode", "status", "exit_code", "attempts", "duration",
        "process_id", "output",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return str(path), len(rows)


def export_alerts_csv() -> tuple[str, int]:
    """Export alerts to CSV. Returns (path, row_count)."""

    rows = db.recent_alerts(1000)
    filename = f"alerts_{_timestamp()}.csv"
    path = Path(config.EXPORT_DIR) / filename

    columns = [
        "timestamp", "date_time", "level", "category", "message",
        "current_value", "threshold_value",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    return str(path), len(rows)


# ---------------------------------------------------------
# 4. PDF Report
# ---------------------------------------------------------
def export_pdf_report(monitor) -> tuple[str | None, str | None]:
    """
    Generate a PDF report using reportlab.
    Returns (path, error_message).
    """

    if not PDF_SUPPORT:
        return None, "reportlab not installed. Run: pip install reportlab"

    text = generate_system_report_txt(monitor)
    filename = f"slarap_report_{_timestamp()}.pdf"
    path = Path(config.EXPORT_DIR) / filename

    canvas = rl_canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 20 * mm
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(18 * mm, y, "SLARAP System Report")
    y -= 8 * mm
    canvas.setFont("Courier", 7.2)

    for line in text.splitlines():
        if y < 15 * mm:
            canvas.showPage()
            canvas.setFont("Courier", 7.2)
            y = height - 18 * mm
        canvas.drawString(14 * mm, y, line[:118])
        y -= 3.4 * mm

    canvas.save()
    return str(path), None


# ---------------------------------------------------------
# 5. Generate All Reports at Once
# ---------------------------------------------------------
def generate_all_reports(monitor) -> dict[str, str]:
    """Generate TXT, CSV, and PDF reports. Returns dictionary of paths."""

    paths = {}

    # TXT
    paths["txt_system"] = save_txt_report(monitor)
    paths["txt_logs"] = save_log_report_txt()

    # CSV
    paths["csv_metrics"], _ = export_metrics_csv(24)
    paths["csv_tasks"], _ = export_tasks_csv()
    paths["csv_alerts"], _ = export_alerts_csv()

    # PDF
    pdf_path, error = export_pdf_report(monitor)
    if pdf_path:
        paths["pdf"] = pdf_path
    else:
        paths["pdf_error"] = error or "PDF generation failed"

    return paths
