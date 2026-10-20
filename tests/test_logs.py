#!/usr/bin/env python3

"""
Test for the Intelligent Log Analyzer.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.analytics import logs
from backend.storage import db


def test_analyze_no_sudo() -> None:
    print("\n=== TEST 1: Analyze logs (without sudo) ===")
    report = logs.analyze(persist=False)

    print(f"Problems: {len(report['problems'])}")
    for problem in report["problems"]:
        print(f"  [!] {problem}")

    print(f"Total errors:   {report['total_errors']}")
    print(f"Total warnings: {report['total_warnings']}")
    print(f"Failed logins:  {report['total_failed_logins']}")


def test_format_report() -> None:
    print("\n=== TEST 2: Format the report ===")
    report = logs.analyze(persist=False)
    formatted = logs.format_report(report)

    print(formatted[:1000])
    print("...")
    print(f"(Report length: {len(formatted)} characters)")


def main() -> None:
    db.initialize_database()

    print("=" * 60)
    print("SLARAP Log Analyzer Tests")
    print("=" * 60)

    test_analyze_no_sudo()
    test_format_report()

    print("\n" + "=" * 60)
    print("Log analyzer tests completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
