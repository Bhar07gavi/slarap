#!/usr/bin/env python3

"""
Test for the Concurrent Process Manager.

Demonstrates:
- fork() + exec() + waitpid() with pipe
- Background processes
- Pipe IPC (command1 | command2)
- Process tree
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time

from backend.procmgr import manager


def test_run_with_pipe() -> None:
    print("\n=== TEST 1: fork() + exec() + pipe() + waitpid() ===")
    result = manager.run_with_pipe("echo 'Hello from child process'; sleep 1; echo 'Process complete'")
    print(f"Command : {result['command']}")
    print(f"PID     : {result['pid']}")
    print(f"Status  : {result['status']}")
    print(f"Exit    : {result['exit_code']}")
    print(f"Time    : {result['duration']}s")
    print(f"Output  :\n{result['output']}")


def test_background() -> None:
    print("\n=== TEST 2: Background Process (fork + exec without wait) ===")
    pid = manager.run_background("sleep 5")
    print(f"Started background process with PID {pid}")

    time.sleep(0.5)
    jobs = manager.list_background_processes()
    print(f"Background jobs running: {list(jobs.keys())}")

    # Wait a bit and reap
    time.sleep(5.5)
    finished = manager.reap_background_processes()
    for pid, info, code in finished:
        print(f"  Reaped PID {pid}: exit={code}, command={info['command']}")


def test_pipeline() -> None:
    print("\n=== TEST 3: Pipe IPC (cmd1 | cmd2) ===")
    result = manager.pipeline("ls -la", "head -5")
    print(f"Command : {result['command']}")
    print(f"Exit    : {result['exit_code']}")
    print(f"Output  :\n{result['output']}")


def test_process_tree() -> None:
    print("\n=== TEST 4: Process Hierarchy ===")
    lines = manager.process_tree(max_depth=3)
    for line in lines:
        print(line)


def test_top_processes() -> None:
    print("\n=== TEST 5: Top Processes (by CPU) ===")
    for proc in manager.top_processes(10, "cpu"):
        print(
            f"PID {proc['pid']:>7}  {proc['name'][:24]:<24}  "
            f"CPU {proc.get('cpu_percent') or 0:>6.1f}%  "
            f"Mem {proc.get('memory_percent') or 0:>5.1f}%"
        )


def main() -> None:
    print("=" * 60)
    print("SLARAP Concurrent Process Manager Tests")
    print("=" * 60)

    test_run_with_pipe()
    test_background()
    test_pipeline()
    test_process_tree()
    test_top_processes()

    print("\n" + "=" * 60)
    print("All process manager tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
