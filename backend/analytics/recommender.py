"""
SLARAP Intelligent Recommendation Engine.

Rule-based system that suggests actions to improve system health:
- Kill high CPU/memory processes
- Clean temporary files
- Archive old logs
- Schedule backups at low load
- Detect memory leaks
- Warn about disk filling
"""

import os
import time
from pathlib import Path
from typing import Any

import psutil

from backend import config
from backend.procmgr import manager
from backend.storage import db


def _dir_size(path: str | Path, max_files: int = 20000) -> int:
    """
    Calculate total size of a directory in bytes.
    Limits to max_files to avoid hanging.
    """

    total = 0
    count = 0
    path = Path(path)

    if not path.exists():
        return 0

    try:
        for root, _, files in os.walk(path, onerror=lambda e: None):
            for file in files:
                try:
                    total += os.path.getsize(os.path.join(root, file))
                except OSError:
                    pass
                count += 1
                if count > max_files:
                    return total
    except Exception:
        pass

    return total


def generate_recommendations(monitor, persist: bool = True) -> list[dict[str, str]]:
    """
    Analyze current system state and return a list of recommendations.
    """

    sample = monitor.get_snapshot()
    recommendations = []

    def add(priority: str, title: str, detail: str) -> None:
        recommendations.append({
            "priority": priority,
            "title": title,
            "detail": detail,
        })

    if not sample:
        return recommendations

    # --- CPU hogs ---
    for process in manager.top_processes(5, "cpu"):
        if (process.get("cpu_percent") or 0) > 50:
            add(
                "HIGH",
                f"High CPU process: {process['name']} (PID {process['pid']})",
                f"Consuming {process['cpu_percent']:.1f}% CPU. "
                f"Review or terminate: kill {process['pid']}",
            )

    # --- Memory hogs ---
    for process in manager.top_processes(5, "memory"):
        if (process.get("memory_percent") or 0) > 15:
            add(
                "HIGH",
                f"High memory process: {process['name']} (PID {process['pid']})",
                f"Using {process['memory_percent']:.1f}% RAM. "
                f"Consider restarting the service.",
            )

    # --- Disk usage ---
    if sample.get("disk", 0) > 80:
        add(
            "HIGH",
            "Disk space running low",
            f"{sample['disk']:.1f}% used, {sample['disk_free_gb']} GB free. "
            f"Run: sudo apt clean && sudo journalctl --vacuum-time=7d",
        )

    # --- Temporary files ---
    tmp_size = _dir_size("/tmp") / (1024 ** 2)  # MB
    if tmp_size > 200:
        add(
            "MEDIUM",
            "Temporary files are large",
            f"/tmp holds ~{tmp_size:.0f} MB. "
            f"Clean with: sudo find /tmp -type f -atime +7 -delete",
        )

    # --- Log directory ---
    log_size = _dir_size("/var/log") / (1024 ** 2)
    if log_size > 500:
        add(
            "MEDIUM",
            "Log directory is large",
            f"/var/log ~{log_size:.0f} MB. "
            f"Archive/rotate: sudo logrotate -f /etc/logrotate.conf",
        )

    # --- Swap usage ---
    if sample.get("swap", 0) > 50:
        add(
            "HIGH",
            "Heavy swap usage",
            f"Swap at {sample['swap']:.1f}%. "
            f"Free cache: sudo sync && sudo sysctl -w vm.drop_caches=3",
        )

    # --- Memory pressure ---
    if sample.get("memory", 0) > 85:
        add(
            "HIGH",
            "Memory pressure",
            f"RAM {sample['memory']:.1f}% used. "
            f"Close idle apps or add swap.",
        )

    # --- Load average ---
    cores = sample.get("cpu_count") or 1
    if sample.get("load", (0,))[0] / cores > 1.5:
        add(
            "MEDIUM",
            "System load exceeds capacity",
            f"load1={sample['load'][0]:.2f} on {cores} cores. "
            f"Defer heavy jobs.",
        )

    # --- Zombie processes ---
    zombies = [
        process.pid
        for process in psutil.process_iter(["status"])
        if process.info.get("status") == psutil.STATUS_ZOMBIE
    ]
    if zombies:
        add(
            "MEDIUM",
            f"{len(zombies)} zombie process(es) found",
            f"PIDs: {zombies[:10]}. "
            f"Restart the parent process to reap them.",
        )

    # --- Idle processes ---
    idle = [
        process.info
        for process in psutil.process_iter(
            ["pid", "name", "cpu_percent", "create_time"]
        )
        if (process.info.get("cpu_percent") or 0) == 0
        and time.time() - (process.info.get("create_time") or time.time()) > 86400
    ]
    if len(idle) > 25:
        add(
            "LOW",
            f"{len(idle)} long-idle processes",
            "Many processes idle >24h with 0% CPU - "
            "review for unused services.",
        )

    # --- Predictive-based recommendations ---
    from backend.analytics import predictor

    predictions = predictor.predict_all(monitor)

    if predictions["cpu"]["trend"] == "RISING" and predictions["cpu"]["horizon"] > 80:
        add(
            "HIGH",
            "CPU trending toward saturation",
            f"Forecast {predictions['cpu']['horizon']}%. "
            f"Scale workload or reschedule jobs.",
        )

    if predictions["memory"]["trend"] == "RISING" and predictions["memory"]["horizon"] > 85:
        add(
            "HIGH",
            "Memory trending toward exhaustion",
            f"Forecast {predictions['memory']['horizon']}%. "
            f"Possible memory leak - inspect top consumers.",
        )

    disk_info = predictions["disk"]
    days_until_full = disk_info.get("days_until_full")
    if days_until_full and days_until_full < 30:
        add(
            "HIGH",
            "Disk projected to fill soon",
            f"At current growth the disk fills in ~{days_until_full} days. "
            f"Plan cleanup/expansion.",
        )

    # --- Backup window suggestion (from database) ---
    rows = db.metrics_since(7 * 24 * 3600)
    if len(rows) > 60:
        hourly = {}
        for row in rows:
            hour = row["date_time"][11:13]
            hourly.setdefault(hour, []).append(row["cpu"])

        best_hour = min(
            hourly.items(),
            key=lambda kv: sum(kv[1]) / len(kv[1]),
        )
        add(
            "LOW",
            "Optimal backup window identified",
            f"Lowest average CPU at {best_hour[0]}:00 "
            f"({sum(best_hour[1]) / len(best_hour[1]):.1f}%). "
            f"Schedule backups then.",
        )

    # --- Automation failures ---
    failures = db.query(
        "SELECT task_name, COUNT(*) c FROM task_runs "
        "WHERE status != 'SUCCESS' AND timestamp >= ? "
        "GROUP BY task_name ORDER BY c DESC LIMIT 3",
        (time.time() - 86400,),
    )
    for failure in failures:
        add(
            "MEDIUM",
            f"Automation task failing: {failure['task_name']}",
            f"Failed {failure['c']} time(s) in last 24h. "
            f"Check the command and retry policy.",
        )

    # --- No issues ---
    if not recommendations:
        add(
            "INFO",
            "System is healthy",
            "No optimization actions required right now.",
        )

    # Sort by priority (HIGH > MEDIUM > LOW > INFO)
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    recommendations.sort(
        key=lambda rec: priority_order.get(rec["priority"], 4)
    )

    # Persist to database
    if persist:
        for rec in recommendations:
            db.insert_recommendation(
                rec["priority"], rec["title"], rec["detail"]
            )

    return recommendations


def format_recommendations(recommendations: list[dict[str, str]]) -> str:
    """Return a formatted string of recommendations."""

    lines = [
        "=" * 70,
        "INTELLIGENT RECOMMENDATIONS",
        "=" * 70,
    ]

    for i, rec in enumerate(recommendations, 1):
        lines.append(f"\n{i}. [{rec['priority']}] {rec['title']}")
        lines.append(f"   -> {rec['detail']}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)
