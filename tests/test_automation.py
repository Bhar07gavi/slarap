#!/usr/bin/env python3

"""
Test for the Automation Engine.

Demonstrates:
- Sequential vs Parallel execution (ThreadPoolExecutor)
- Retry logic
- Scheduler thread
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config
from backend.automation.engine import (
    AutomationEngine,
    Scheduler,
    Task,
    Workflow,
)
from backend.storage import db


def test_simple_task() -> None:
    print("\n=== TEST 1: Execute a Simple Task ===")
    engine = AutomationEngine()

    task = Task(name="echo_test", command="echo 'Automation works!'")
    result = engine.run_task(task)

    print(f"Task: {result['task_name']}")
    print(f"Status: {result['status']}")
    print(f"Output: {result['output'].strip()}")


def test_retry_logic() -> None:
    print("\n=== TEST 2: Retry Logic (Command Will Fail) ===")
    engine = AutomationEngine()

    # This command will fail (exit code 1)
    task = Task(
        name="fail_test",
        command="exit 1",
        retries=2,
        retry_delay=1,  # 1 second between retries
    )
    start = time.time()
    result = engine.run_task(task)
    elapsed = time.time() - start

    print(f"Status: {result['status']}")
    print(f"Attempts: {result['attempts']} (expected 3)")
    print(f"Time taken: {elapsed:.2f}s (expected ~2s delay)")
    assert result["attempts"] == 3, "Should have tried 3 times"
    print("PASSED: Retry logic works correctly.")


def test_parallel_vs_sequential() -> None:
    print("\n=== TEST 3: Parallel vs Sequential Speed Comparison ===")
    engine = AutomationEngine()

    # Create 3 tasks that sleep for 2 seconds each
    tasks = [
        Task(name=f"sleep_{i}", command="sleep 2") for i in range(3)
    ]

    # Sequential
    wf_seq = Workflow(name="sequential_test", tasks=tasks, mode="sequential")
    start = time.time()
    engine.run_workflow(wf_seq)
    seq_time = time.time() - start

    # Parallel
    wf_par = Workflow(name="parallel_test", tasks=tasks, mode="parallel", max_workers=3)
    start = time.time()
    engine.run_workflow(wf_par)
    par_time = time.time() - start

    print(f"Sequential time: {seq_time:.2f}s (expected ~6.0s)")
    print(f"Parallel time:   {par_time:.2f}s (expected ~2.0s)")
    print(f"Speedup:         {seq_time / par_time:.1f}x")
    assert par_time < seq_time, "Parallel should be faster"
    print("PASSED: ThreadPoolExecutor provides parallel speedup.")


def test_scheduler() -> None:
    print("\n=== TEST 4: Scheduler Thread ===")
    engine = AutomationEngine()
    scheduler = Scheduler(engine)

    job = scheduler.add_job(
        name="test_job",
        command="echo 'Scheduled task executed'",
        interval_seconds=2,
        retries=1,
    )

    scheduler.start()
    print(f"Scheduled job {job['id']} to run every 2 seconds")

    # Wait for the scheduled job to execute at least once
    time.sleep(2.5)

    scheduler.stop()
    scheduler.join(timeout=2)

    # Verify the job has run
    jobs = scheduler.list_jobs()
    for j in jobs:
        print(f"Job '{j['name']}' runs: {j['runs']}")

    assert len(list(jobs)) == 1, "Should have 1 job"
    assert list(jobs)[0]["runs"] >= 1, "Job should have executed"
    print("PASSED: Scheduler thread executed the job.")


def main() -> None:
    db.initialize_database()

    print("=" * 60)
    print("SLARAP Automation Engine Tests")
    print("=" * 60)

    test_simple_task()
    test_retry_logic()
    test_parallel_vs_sequential()
    test_scheduler()

    print("\n" + "=" * 60)
    print("All automation tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
