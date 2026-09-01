"""
Thread-safe SQLite database module for SLARAP.

Uses a reentrant lock to protect the shared connection.
"""

import datetime
import sqlite3
import threading
import time
from typing import Any

from backend import config


_DB_LOCK = threading.RLock()
_CONNECTION: sqlite3.Connection | None = None


SCHEMA = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    date_time TEXT NOT NULL,
    cpu REAL NOT NULL,
    memory REAL NOT NULL,
    swap REAL NOT NULL,
    disk REAL NOT NULL,
    network_sent INTEGER NOT NULL,
    network_received INTEGER NOT NULL,
    load1 REAL NOT NULL,
    load5 REAL NOT NULL,
    load15 REAL NOT NULL,
    process_count INTEGER NOT NULL,
    uptime REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS task_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    date_time TEXT NOT NULL,
    workflow TEXT,
    task_name TEXT,
    command TEXT NOT NULL,
    execution_mode TEXT,
    status TEXT NOT NULL,
    exit_code INTEGER,
    attempts INTEGER DEFAULT 1,
    duration REAL,
    process_id INTEGER,
    output TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    date_time TEXT NOT NULL,
    level TEXT NOT NULL,
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    current_value REAL,
    threshold_value REAL
);

CREATE TABLE IF NOT EXISTS log_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    date_time TEXT NOT NULL,
    source TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    occurrences INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    date_time TEXT NOT NULL,
    priority TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS index_metrics_timestamp
ON metrics(timestamp);

CREATE INDEX IF NOT EXISTS index_alerts_timestamp
ON alerts(timestamp);

CREATE INDEX IF NOT EXISTS index_task_runs_timestamp
ON task_runs(timestamp);
"""


def current_time() -> tuple[float, str]:
    """Return Unix timestamp and a human-readable date/time."""
    timestamp = time.time()
    date_time = datetime.datetime.fromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return timestamp, date_time


def initialize_database() -> sqlite3.Connection:
    """Create the shared SQLite connection and required tables."""
    global _CONNECTION

    with _DB_LOCK:
        if _CONNECTION is None:
            _CONNECTION = sqlite3.connect(
                str(config.DB_PATH),
                check_same_thread=False,
            )
            _CONNECTION.row_factory = sqlite3.Row
            _CONNECTION.executescript(SCHEMA)
            _CONNECTION.commit()
        return _CONNECTION


def execute(sql: str, parameters: tuple[Any, ...] = ()) -> int:
    """Execute a write query and return the inserted row ID."""
    with _DB_LOCK:
        connection = initialize_database()
        cursor = connection.execute(sql, parameters)
        connection.commit()
        return cursor.lastrowid


def query(
    sql: str,
    parameters: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    """Execute a read query and return rows as dictionaries."""
    with _DB_LOCK:
        connection = initialize_database()
        cursor = connection.execute(sql, parameters)
        return [dict(row) for row in cursor.fetchall()]


def insert_metric(metric: dict[str, Any]) -> int:
    """Store one resource-monitoring sample."""
    timestamp, date_time = current_time()

    return execute(
        """
        INSERT INTO metrics (
            timestamp, date_time, cpu, memory, swap, disk,
            network_sent, network_received, load1, load5, load15,
            process_count, uptime
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            date_time,
            metric["cpu"],
            metric["memory"],
            metric["swap"],
            metric["disk"],
            metric["network_sent"],
            metric["network_received"],
            metric["load"][0],
            metric["load"][1],
            metric["load"][2],
            metric["process_count"],
            metric["uptime"],
        ),
    )


def insert_task_run(task_run: dict[str, Any]) -> int:
    """Store the result of one automated task."""
    timestamp, date_time = current_time()

    return execute(
        """
        INSERT INTO task_runs (
            timestamp, date_time, workflow, task_name, command,
            execution_mode, status, exit_code, attempts, duration,
            process_id, output
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            date_time,
            task_run.get("workflow"),
            task_run.get("task_name"),
            task_run.get("command"),
            task_run.get("execution_mode"),
            task_run.get("status"),
            task_run.get("exit_code"),
            task_run.get("attempts", 1),
            task_run.get("duration"),
            task_run.get("process_id"),
            (task_run.get("output") or "")[:10000],
        ),
    )


def insert_alert(
    level: str,
    category: str,
    message: str,
    current_value: float | None = None,
    threshold_value: float | None = None,
) -> int:
    """Store an alert."""
    timestamp, date_time = current_time()

    return execute(
        """
        INSERT INTO alerts (
            timestamp, date_time, level, category, message,
            current_value, threshold_value
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            date_time,
            level,
            category,
            message,
            current_value,
            threshold_value,
        ),
    )


def recent_metrics(limit: int = 300) -> list[dict[str, Any]]:
    """Return recent metrics in chronological order."""
    rows = query(
        """
        SELECT *
        FROM metrics
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )
    return list(reversed(rows))


def metrics_since(seconds: int | float) -> list[dict[str, Any]]:
    """Return metrics collected during the specified period."""
    minimum_timestamp = time.time() - seconds
    return query(
        """
        SELECT *
        FROM metrics
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
        """,
        (minimum_timestamp,),
    )


def recent_alerts(limit: int = 50) -> list[dict[str, Any]]:
    """Return recently generated alerts."""
    return query(
        """
        SELECT *
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )


def recent_task_runs(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent automation executions."""
    return query(
        """
        SELECT *
        FROM task_runs
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )


def close_database() -> None:
    """Close the shared database connection."""
    global _CONNECTION

    with _DB_LOCK:
        if _CONNECTION is not None:
            _CONNECTION.close()
            _CONNECTION = None


def aggregate(seconds: float, bucket: str = "hour") -> list[dict]:
    """
    Aggregate metrics into buckets (hour/day/week).
    Returns a list of dicts with bucket label, avg and max values.
    """

    fmt_map = {
        "hour": "%Y-%m-%d %H",
        "day": "%Y-%m-%d",
        "week": "%Y-%W",
    }
    fmt = fmt_map.get(bucket, "%Y-%m-%d %H")

    rows = query(
        f"""
        SELECT strftime('{fmt}', date_time) AS bucket,
               ROUND(AVG(cpu), 2) AS avg_cpu,
               ROUND(MAX(cpu), 2) AS max_cpu,
               ROUND(AVG(memory), 2) AS avg_mem,
               ROUND(MAX(memory), 2) AS max_mem,
               ROUND(AVG(disk), 2) AS avg_disk,
               COUNT(*) AS samples
        FROM metrics
        WHERE timestamp >= ?
        GROUP BY bucket
        ORDER BY bucket
        """,
        (time.time() - seconds,),
    )
    return rows
