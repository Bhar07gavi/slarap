"""
SLARAP Concurrent Process Manager.

This module demonstrates Operating Systems concepts:
- Process creation using fork()
- Process execution using exec()
- Process synchronization using waitpid()
- Inter-process communication using pipes
- Background process management
- Process hierarchy traversal
"""

import os
import select
import shlex
import signal
import subprocess
import threading
import time
from typing import Any

import psutil


# Lock to protect shared state (background processes)
_BG_LOCK = threading.RLock()

# Dictionary: pid -> process information
_BACKGROUND_PROCESSES: dict[int, dict[str, Any]] = {}


def _normalize_command(command: str | list[str]) -> list[str]:
    """
    Convert a command string to a list of arguments.
    If shell metacharacters are present, run through bash -lc.
    """

    if isinstance(command, list):
        return command

    if any(ch in command for ch in "|><&;$*?`"):
        return ["/bin/bash", "-lc", command]

    return shlex.split(command)


# ---------------------------------------------------------
# 1. fork() + exec() + pipe() + waitpid()  (full example)
# ---------------------------------------------------------
def run_with_pipe(command: str | list[str], timeout: float = 120) -> dict[str, Any]:
    """
    Fork a child process, exec the command, capture stdout/stderr
    through a pipe, and wait for the child with waitpid().
    """

    argv = _normalize_command(command)

    # Create an anonymous pipe (IPC)
    read_fd, write_fd = os.pipe()

    start_time = time.time()

    # --- PROCESS CREATION: fork() ---
    pid = os.fork()

    if pid == 0:  # CHILD PROCESS
        try:
            os.close(read_fd)
            os.setsid()  # create new process group
            os.dup2(write_fd, 1)  # stdout -> pipe
            os.dup2(write_fd, 2)  # stderr -> pipe
            os.close(write_fd)

            # --- PROCESS EXECUTION: exec() ---
            os.execvp(argv[0], argv)

        except Exception as error:
            try:
                os.write(2, f"[exec-error] {error}\n".encode())
            except Exception:
                pass
            os._exit(127)

    # --- PARENT PROCESS ---
    os.close(write_fd)

    chunks = []
    timed_out = False

    while True:
        remaining = timeout - (time.time() - start_time)
        if remaining <= 0:
            timed_out = True
            break

        ready, _, _ = select.select([read_fd], [], [], min(0.5, remaining))
        if ready:
            data = os.read(read_fd, 65536)
            if not data:
                break
            chunks.append(data)

    if timed_out:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            pass

    os.close(read_fd)

    # --- PROCESS SYNCHRONIZATION: waitpid() ---
    _, status = os.waitpid(pid, 0)

    if os.WIFEXITED(status):
        exit_code = os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        exit_code = -os.WTERMSIG(status)
    else:
        exit_code = -1

    output = b"".join(chunks).decode("utf-8", "replace")

    return {
        "pid": pid,
        "command": " ".join(argv),
        "exit_code": exit_code,
        "output": output,
        "duration": round(time.time() - start_time, 3),
        "timed_out": timed_out,
        "status": (
            "TIMEOUT" if timed_out
            else "SUCCESS" if exit_code == 0
            else "FAILED"
        ),
    }


# ---------------------------------------------------------
# 2. Background process (fork + exec, no wait)
# ---------------------------------------------------------
def run_background(command: str | list[str]) -> int:
    """
    Fork a child process and execute the command without waiting.
    Returns the child PID.
    """

    argv = _normalize_command(command)

    pid = os.fork()

    if pid == 0:  # CHILD
        try:
            os.setsid()
            devnull = os.open(os.devnull, os.O_RDWR)
            os.dup2(devnull, 0)  # stdin
            os.dup2(devnull, 1)  # stdout
            os.dup2(devnull, 2)  # stderr
            os.execvp(argv[0], argv)
        except Exception:
            os._exit(127)

    with _BG_LOCK:
        _BACKGROUND_PROCESSES[pid] = {
            "command": " ".join(argv),
            "started": time.time(),
        }

    return pid


def list_background_processes() -> dict[int, dict[str, Any]]:
    """Return information about tracked background processes."""

    with _BG_LOCK:
        return {
            pid: dict(
                info,
                elapsed=round(time.time() - info["started"], 1),
            )
            for pid, info in _BACKGROUND_PROCESSES.items()
        }


def reap_background_processes() -> list[tuple[int, dict[str, Any], int | None]]:
    """
    Non-blocking waitpid() for finished background children.
    Returns list of (pid, info, exit_code) tuples.
    """

    finished = []

    with _BG_LOCK:
        for pid in list(_BACKGROUND_PROCESSES):
            try:
                done_pid, status = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                info = _BACKGROUND_PROCESSES.pop(pid)
                finished.append((pid, info, None))
                continue

            if done_pid == pid:
                info = _BACKGROUND_PROCESSES.pop(pid)
                if os.WIFEXITED(status):
                    exit_code = os.WEXITSTATUS(status)
                elif os.WIFSIGNALED(status):
                    exit_code = -os.WTERMSIG(status)
                else:
                    exit_code = None
                finished.append((pid, info, exit_code))

    return finished


# ---------------------------------------------------------
# 3. Pipe IPC demo: command1 | command2
# ---------------------------------------------------------
def pipeline(command_a: str | list[str], command_b: str | list[str],
             timeout: float = 60) -> dict[str, Any]:
    """
    Execute two commands connected by a pipe (communicating processes).
    This uses two forks and one pipe.
    """

    argv_a = _normalize_command(command_a)
    argv_b = _normalize_command(command_b)

    # Create pipe: A writes, B reads
    pipe_read, pipe_write = os.pipe()

    # Another pipe to capture B's output
    out_read, out_write = os.pipe()

    start_time = time.time()

    # --- First fork: process A ---
    pid_a = os.fork()
    if pid_a == 0:  # Child A
        try:
            os.close(pipe_read)
            os.close(out_read)
            os.close(out_write)
            os.dup2(pipe_write, 1)  # stdout -> pipe
            os.close(pipe_write)
            os.execvp(argv_a[0], argv_a)
        except Exception:
            os._exit(127)

    # --- Second fork: process B ---
    pid_b = os.fork()
    if pid_b == 0:  # Child B
        try:
            os.close(pipe_write)
            os.close(out_read)
            os.dup2(pipe_read, 0)   # stdin <- pipe
            os.close(pipe_read)
            os.dup2(out_write, 1)   # stdout -> output pipe
            os.dup2(out_write, 2)   # stderr -> output pipe
            os.close(out_write)
            os.execvp(argv_b[0], argv_b)
        except Exception:
            os._exit(127)

    # --- Parent ---
    os.close(pipe_read)
    os.close(pipe_write)
    os.close(out_write)

    output_chunks = []
    while time.time() - start_time < timeout:
        ready, _, _ = select.select([out_read], [], [], 0.5)
        if ready:
            data = os.read(out_read, 65536)
            if not data:
                break
            output_chunks.append(data)

    os.close(out_read)

    os.waitpid(pid_a, 0)
    _, status_b = os.waitpid(pid_b, 0)

    if os.WIFEXITED(status_b):
        exit_code = os.WEXITSTATUS(status_b)
    else:
        exit_code = -1

    output = b"".join(output_chunks).decode("utf-8", "replace")

    return {
        "command": f"{' '.join(argv_a)} | {' '.join(argv_b)}",
        "output": output,
        "exit_code": exit_code,
        "duration": round(time.time() - start_time, 3),
    }


# ---------------------------------------------------------
# 4. Process hierarchy tree
# ---------------------------------------------------------
def process_tree(root_pid: int | None = None, max_depth: int = 3) -> list[str]:
    """Return a visual representation of the process tree."""

    root = psutil.Process(root_pid or os.getpid())
    lines = []

    def walk(process: psutil.Process, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            indent = "    " * depth
            lines.append(
                f"{indent}|-- [PID {process.pid}] {process.name()} "
                f"(CPU {process.cpu_percent(interval=0):.1f}%, "
                f"Mem {process.memory_percent():.1f}%)"
            )
            for child in process.children():
                walk(child, depth + 1)
        except psutil.Error:
            pass

    walk(root, 0)
    return lines


# ---------------------------------------------------------
# 5. Process listing and management
# ---------------------------------------------------------
def top_processes(count: int = 10, sort_by: str = "cpu") -> list[dict[str, Any]]:
    """Return top processes sorted by CPU or memory."""

    processes = []
    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_percent", "status"]
    ):
        try:
            processes.append(proc.info)
        except psutil.Error:
            pass

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    processes.sort(key=lambda x: x.get(key) or 0, reverse=True)
    return processes[:count]


def kill_process(pid: int, force: bool = False) -> tuple[bool, str]:
    """Terminate a process by PID."""

    try:
        process = psutil.Process(pid)
        if force:
            process.kill()
        else:
            process.terminate()
        process.wait(timeout=5)
        return True, f"Process {pid} terminated."
    except Exception as error:
        return False, str(error)


def command_exists(command: str) -> bool:
    """Check if a command is available in PATH."""

    try:
        subprocess.run(
            ["which", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False
