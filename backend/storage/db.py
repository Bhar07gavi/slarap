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

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id TEXT UNIQUE NOT NULL,
    activity_type TEXT NOT NULL,
    unit_id TEXT NOT NULL,
    title TEXT NOT NULL,
    xp_awarded INTEGER NOT NULL,
    completed_at REAL NOT NULL,
    date_time TEXT NOT NULL,
    details TEXT
);

CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    badge_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT,
    earned_at REAL NOT NULL,
    date_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL DEFAULT 'SysAdmin Student',
    total_xp INTEGER NOT NULL DEFAULT 0,
    current_level INTEGER NOT NULL DEFAULT 1,
    streak_days INTEGER NOT NULL DEFAULT 1,
    last_active REAL NOT NULL
);
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


def insert_log_event(
    source: str,
    level: str,
    message: str,
    occurrences: int = 1,
) -> int:
    """Store a log analysis event."""
    timestamp, date_time = current_time()
    return execute(
        """
        INSERT INTO log_events (
            timestamp, date_time, source, level, message, occurrences
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (timestamp, date_time, source, level, message, occurrences),
    )


def recent_log_events(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent log events."""
    return query(
        """
        SELECT *
        FROM log_events
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )


def insert_recommendation(
    priority: str,
    title: str,
    detail: str,
) -> int:
    """Store an intelligent recommendation."""
    timestamp, date_time = current_time()
    return execute(
        """
        INSERT INTO recommendations (
            timestamp, date_time, priority, title, detail
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (timestamp, date_time, priority, title, detail),
    )


def recent_recommendations(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent recommendations."""
    return query(
        """
        SELECT *
        FROM recommendations
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )


# ---------------------------------------------------------
# Gamification & Learning Progress Persistence
# ---------------------------------------------------------

def get_or_create_profile() -> dict[str, Any]:
    """Return or initialize the persistent single-user learning profile."""
    rows = query("SELECT * FROM user_profile WHERE id = 1")
    if rows:
        return rows[0]

    now = time.time()
    execute(
        """
        INSERT OR IGNORE INTO user_profile (
            id, username, total_xp, current_level, streak_days, last_active
        )
        VALUES (1, 'SysAdmin Student', 0, 1, 1, ?)
        """,
        (now,),
    )
    rows = query("SELECT * FROM user_profile WHERE id = 1")
    return rows[0] if rows else {
        "id": 1,
        "username": "SysAdmin Student",
        "total_xp": 0,
        "current_level": 1,
        "streak_days": 1,
        "last_active": now,
    }


def award_xp(
    activity_id: str,
    activity_type: str,
    unit_id: str,
    title: str,
    xp: int,
    details: str = "",
) -> dict[str, Any]:
    """
    Award XP for completing a learning activity.
    Enforces idempotency: completing the same activity does not award duplicate XP.
    """
    timestamp, date_time = current_time()

    # Check if activity already completed
    existing = query(
        "SELECT * FROM user_progress WHERE activity_id = ?",
        (activity_id,),
    )
    if existing:
        profile = get_or_create_profile()
        return {
            "awarded": False,
            "already_completed": True,
            "xp_awarded": 0,
            "total_xp": profile["total_xp"],
            "current_level": profile["current_level"],
            "message": "Activity already completed. Knowledge reinforced!",
        }

    # Record progress
    execute(
        """
        INSERT INTO user_progress (
            activity_id, activity_type, unit_id, title, xp_awarded,
            completed_at, date_time, details
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            activity_id,
            activity_type,
            unit_id,
            title,
            xp,
            timestamp,
            date_time,
            details,
        ),
    )

    # Update profile XP and Level (100 XP per level)
    profile = get_or_create_profile()
    new_xp = profile["total_xp"] + xp
    new_level = max(1, (new_xp // 100) + 1)

    execute(
        """
        UPDATE user_profile
        SET total_xp = ?, current_level = ?, last_active = ?
        WHERE id = 1
        """,
        (new_xp, new_level, timestamp),
    )

    return {
        "awarded": True,
        "already_completed": False,
        "xp_awarded": xp,
        "total_xp": new_xp,
        "current_level": new_level,
        "message": f"+{xp} XP earned for {title}!",
    }


def get_user_progress() -> dict[str, Any]:
    """Return all completed activities and unit-level statistics."""
    profile = get_or_create_profile()
    activities = query(
        """
        SELECT * FROM user_progress
        ORDER BY completed_at DESC
        """
    )
    badges = query(
        """
        SELECT * FROM user_badges
        ORDER BY earned_at DESC
        """
    )

    unit_counts: dict[str, int] = {}
    for act in activities:
        uid = act["unit_id"]
        unit_counts[uid] = unit_counts.get(uid, 0) + 1

    return {
        "profile": profile,
        "activities": activities,
        "badges": badges,
        "unit_counts": unit_counts,
        "total_completed": len(activities),
    }


def award_badge(
    badge_id: str,
    title: str,
    description: str,
    icon: str = "Award",
) -> dict[str, Any]:
    """Award an achievement badge if not already earned."""
    timestamp, date_time = current_time()
    existing = query(
        "SELECT * FROM user_badges WHERE badge_id = ?",
        (badge_id,),
    )
    if existing:
        return {"awarded": False, "badge": existing[0]}

    execute(
        """
        INSERT INTO user_badges (
            badge_id, title, description, icon, earned_at, date_time
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (badge_id, title, description, icon, timestamp, date_time),
    )

    # Award bonus XP for badge
    award_xp(
        activity_id=f"badge_{badge_id}",
        activity_type="badge",
        unit_id="system",
        title=f"Earned Badge: {title}",
        xp=50,
        details=description,
    )

    return {
        "awarded": True,
        "badge": {
            "badge_id": badge_id,
            "title": title,
            "description": description,
            "icon": icon,
            "earned_at": timestamp,
            "date_time": date_time,
        },
    }


def get_user_badges() -> list[dict[str, Any]]:
    """Return all earned user badges."""
    return query("SELECT * FROM user_badges ORDER BY earned_at DESC")


def reset_gamification() -> None:
    """Reset gamification tables for a clean slate."""
    execute("DELETE FROM user_progress")
    execute("DELETE FROM user_badges")
    execute(
        """
        UPDATE user_profile
        SET total_xp = 0, current_level = 1, last_active = ?
        WHERE id = 1
        """,
        (time.time(),),
    )

