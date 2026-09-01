"""
SLARAP Intelligent Log Analyzer.

Analyzes Linux system log files:
- /var/log/syslog      (system messages)
- /var/log/auth.log    (authentication events)
- /var/log/kern.log    (kernel messages)
- /var/log/dpkg.log    (package manager events)

Generates:
- Error summary
- Warning summary
- Login activity (successful/failed)
- Security events
- Frequently occurring issues
"""

import collections
import os
import re
from pathlib import Path
from typing import Any

from backend import config
from backend.storage import db


# Regular expressions for log patterns
ERROR_PATTERN = re.compile(
    r"\b(error|failed|failure|critical|fatal|panic|denied|refused)\b",
    re.IGNORECASE,
)

WARNING_PATTERN = re.compile(
    r"\b(warn|warning|deprecated|timeout|retry)\b",
    re.IGNORECASE,
)

FAILED_LOGIN_PATTERN = re.compile(
    r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)",
    re.IGNORECASE,
)

SUCCESS_LOGIN_PATTERN = re.compile(
    r"Accepted (?:password|publickey) for (\S+) from (\d+\.\d+\.\d+\.\d+)",
    re.IGNORECASE,
)

SUDO_PATTERN = re.compile(
    r"sudo:\s+(\S+)\s*:.*COMMAND=(.*)",
    re.IGNORECASE,
)

NEW_USER_PATTERN = re.compile(
    r"new user: name=(\S+?),",
    re.IGNORECASE,
)

OOM_PATTERN = re.compile(
    r"Out of memory|oom-killer",
    re.IGNORECASE,
)

SERVICE_PATTERN = re.compile(
    r"^\w{3}\s+\d+\s[\d:]+\s+\S+\s+([\w\-\.]+)(\[\d+\])?:",
)


def _normalize_line(line: str) -> str:
    """
    Remove timestamps, PIDs, and numbers to group similar messages.
    This helps identify frequently recurring issues.
    """

    # Remove timestamp prefix: "Oct 12 15:30:45 hostname"
    line = re.sub(
        r"^\w{3}\s+\d+\s[\d:]+\s+\S+\s+",
        "",
        line.strip(),
    )

    # Remove PIDs like [1234]
    line = re.sub(r"\[\d+\]", "[]", line)

    # Replace small numbers with "N"
    line = re.sub(r"\b\d+\b", "N", line)

    # Replace hex addresses
    line = re.sub(r"0x[0-9a-f]+", "0xX", line, flags=re.IGNORECASE)

    return line[:200]


def _tail_file(path: str | Path, max_lines: int) -> tuple[list[str], str | None]:
    """
    Read the last N lines of a file.
    Returns a tuple: (lines, error_message)
    """

    path = Path(path)

    if not path.exists():
        return [], f"File not found: {path}"

    if not path.is_file():
        return [], f"Not a regular file: {path}"

    if not os.access(path, os.R_OK):
        return [], f"Permission denied: {path} (run with sudo)"

    try:
        # Read last max_lines using a deque with maxlen
        with open(path, "r", errors="replace") as f:
            lines = collections.deque(f, maxlen=max_lines)

        return list(lines), None

    except Exception as error:
        return [], str(error)


def analyze(
    sources: list[str] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    """
    Analyze the selected log files and generate a comprehensive report.
    """

    sources = sources or list(config.LOG_FILES.keys())

    report: dict[str, Any] = {
        "sources": {},
        "errors": [],
        "warnings": [],
        "failed_logins": {},
        "successful_logins": [],
        "sudo_commands": [],
        "security_events": [],
        "top_issues": [],
        "top_warnings": [],
        "services": {},
        "problems": [],
        "oom_events": 0,
        "total_errors": 0,
        "total_warnings": 0,
        "total_failed_logins": 0,
    }

    # Counters for aggregating recurring issues
    error_counter = collections.Counter()
    warning_counter = collections.Counter()
    service_counter = collections.Counter()

    for source_name in sources:
        log_path = config.LOG_FILES.get(source_name)
        if not log_path:
            continue

        # Tail the log file (last N lines)
        lines, error_message = _tail_file(log_path, config.LOG_TAIL_LINES)

        if error_message:
            report["problems"].append(error_message)
            continue

        source_stat = {
            "lines": len(lines),
            "errors": 0,
            "warnings": 0,
        }

        for line in lines:
            # Check for errors
            if ERROR_PATTERN.search(line):
                source_stat["errors"] += 1
                normalized = _normalize_line(line)
                error_counter[normalized] += 1

                if len(report["errors"]) < 200:
                    report["errors"].append((source_name, line.strip()))

            # Check for warnings
            elif WARNING_PATTERN.search(line):
                source_stat["warnings"] += 1
                normalized = _normalize_line(line)
                warning_counter[normalized] += 1

                if len(report["warnings"]) < 200:
                    report["warnings"].append((source_name, line.strip()))

            # Failed login attempts
            match = FAILED_LOGIN_PATTERN.search(line)
            if match:
                key = f"{match.group(1)}@{match.group(2)}"
                report["failed_logins"][key] = (
                    report["failed_logins"].get(key, 0) + 1
                )

            # Successful logins
            match = SUCCESS_LOGIN_PATTERN.search(line)
            if match:
                report["successful_logins"].append(
                    f"{match.group(1)} from {match.group(2)}"
                )

            # Sudo commands
            match = SUDO_PATTERN.search(line)
            if match:
                report["sudo_commands"].append(
                    f"{match.group(1)} -> {match.group(2).strip()}"
                )

            # New user creation (security event)
            match = NEW_USER_PATTERN.search(line)
            if match:
                report["security_events"].append(
                    f"New user created: {match.group(1)}"
                )

            # OOM events
            if OOM_PATTERN.search(line):
                report["oom_events"] += 1
                report["security_events"].append(
                    "Kernel OOM-killer event detected"
                )

            # Service identification
            match = SERVICE_PATTERN.match(line)
            if match:
                service_counter[match.group(1)] += 1

        report["sources"][source_name] = source_stat

    # Aggregate results
    report["top_issues"] = error_counter.most_common(15)
    report["top_warnings"] = warning_counter.most_common(10)
    report["services"] = dict(service_counter.most_common(15))
    report["total_errors"] = sum(
        s["errors"] for s in report["sources"].values()
    )
    report["total_warnings"] = sum(
        s["warnings"] for s in report["sources"].values()
    )
    report["total_failed_logins"] = sum(
        report["failed_logins"].values()
    )

    # Persist top issues to database
    if persist:
        for message, count in report["top_issues"][:10]:
            db.insert_log_event("aggregate", "ERROR", message, count)

        for message, count in report["top_warnings"][:5]:
            db.insert_log_event("aggregate", "WARNING", message, count)

    return report


def format_report(report: dict[str, Any]) -> str:
    """Return a human-readable string of the log analysis report."""

    lines = [
        "=" * 70,
        "LOG ANALYSIS REPORT",
        "=" * 70,
    ]

    # Source statistics
    lines.append("")
    lines.append("-- SOURCE STATISTICS -" + "-" * 48)
    for name, stat in report["sources"].items():
        lines.append(
            f"  {name:<10} lines={stat['lines']:<6} "
            f"errors={stat['errors']:<5} warnings={stat['warnings']}"
        )

    # Problems reading files
    if report["problems"]:
        lines.append("")
        lines.append("-- PROBLEMS -" + "-" * 53)
        for problem in report["problems"]:
            lines.append(f"  [!] {problem}")

    # Totals
    lines += [
        "",
        f"Total errors    : {report['total_errors']}",
        f"Total warnings  : {report['total_warnings']}",
        f"Failed logins   : {report['total_failed_logins']}",
        f"OOM events      : {report['oom_events']}",
    ]

    # Top issues
    if report["top_issues"]:
        lines += [
            "",
            "-- TOP 10 RECURRING ISSUES -" + "-" * 40,
        ]
        for message, count in report["top_issues"][:10]:
            lines.append(f"  [{count:>4}x] {message[:100]}")

    # Failed logins
    if report["failed_logins"]:
        lines += [
            "",
            "-- FAILED LOGIN ATTEMPTS (top 10) -" + "-" * 37,
        ]
        sorted_failed = sorted(
            report["failed_logins"].items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for username_ip, count in sorted_failed[:10]:
            lines.append(f"  {count:>4}x  {username_ip}")

    # Successful logins
    if report["successful_logins"]:
        lines += [
            "",
            "-- RECENT SUCCESSFUL LOGINS -" + "-" * 42,
        ]
        for login in report["successful_logins"][-8:]:
            lines.append(f"  {login}")

    # Sudo commands
    if report["sudo_commands"]:
        lines += [
            "",
            "-- SUDO COMMANDS (last 10) -" + "-" * 43,
        ]
        for cmd in report["sudo_commands"][-10:]:
            lines.append(f"  {cmd}")

    # Security events
    if report["security_events"]:
        lines += [
            "",
            "-- SECURITY EVENTS -" + "-" * 50,
        ]
        for event in report["security_events"]:
            lines.append(f"  {event}")

    lines.append("=" * 70)

    return "\n".join(lines)
