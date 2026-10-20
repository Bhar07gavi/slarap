"""
SLARAP Automation Engine.

This module demonstrates:
- Thread-based concurrency (ThreadPoolExecutor)
- Sequential and parallel task execution
- Retry logic with delays
- A Scheduler thread for periodic tasks
- SQLite persistence of execution history
"""

import json
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable

from backend import config
from backend.procmgr import manager
from backend.storage import db


class Task:
    """Represents a single Linux command to execute."""

    def __init__(
        self,
        name: str,
        command: str,
        retries: int = 0,
        timeout: float = 120,
        retry_delay: float = 2.0,
        continue_on_error: bool = False,
    ) -> None:
        self.name = name
        self.command = command
        self.retries = retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.continue_on_error = continue_on_error

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Task":
        """Create a Task from a dictionary (JSON)."""

        return Task(
            name=data.get("name", "unnamed_task"),
            command=data.get("command", ""),
            retries=data.get("retries", 0),
            timeout=data.get("timeout", 120),
            retry_delay=data.get("retry_delay", 2),
            continue_on_error=data.get("continue_on_error", False),
        )


class Workflow:
    """Represents a collection of tasks to run."""

    def __init__(
        self,
        name: str,
        tasks: list[Task],
        mode: str = "sequential",
        max_workers: int = 4,
    ) -> None:
        self.name = name
        self.tasks = tasks
        self.mode = mode  # "sequential" or "parallel"
        self.max_workers = max_workers

    @staticmethod
    def from_file(path: str | Path) -> "Workflow":
        """Load a Workflow from a JSON file."""

        path = Path(path)
        with open(path, "r") as f:
            data = json.load(f)

        tasks = [Task.from_dict(task) for task in data.get("tasks", [])]

        return Workflow(
            name=data.get("name", path.stem),
            tasks=tasks,
            mode=data.get("mode", "sequential"),
            max_workers=data.get("max_workers", 4),
        )


class AutomationEngine:
    """Executes tasks and workflows with retry, logging, and parallel options."""

    def __init__(self, alert_callback: Callable[[str, str, str], None] | None = None):
        self.alert_callback = alert_callback
        self.lock = threading.RLock()  # Protects the running_workflows dict
        self.running_workflows: dict[str, dict[str, Any]] = {}

    def _fire_alert(self, level: str, category: str, message: str) -> None:
        """Fire an alert through the callback if a callback exists."""

        if self.alert_callback:
            self.alert_callback(level, category, message)
        else:
            print(f"[ALERT] {level} - {category}: {message}")

    def run_task(
        self,
        task: Task,
        workflow_name: str = "adhoc",
        mode: str = "sequential",
    ) -> dict[str, Any]:
        """
        Execute a Task with retry logic and log the result to the database.
        """

        attempt = 0
        result: dict[str, Any] = {}

        while attempt <= task.retries:
            attempt += 1
            # Use the Process Manager's fork/exec/wait/pipe functionality
            result = manager.run_with_pipe(task.command, timeout=task.timeout)

            if result["exit_code"] == 0:
                break

            if attempt <= task.retries:
                time.sleep(task.retry_delay)  # Backoff before retry

        task_log = {
            "workflow": workflow_name,
            "task_name": task.name,
            "command": result["command"],
            "execution_mode": mode,
            "status": result["status"],
            "exit_code": result["exit_code"],
            "attempts": attempt,
            "duration": result["duration"],
            "process_id": result["pid"],
            "output": result["output"],
        }

        # Store in SQLite
        db.insert_task_run(task_log)

        if result["status"] != "SUCCESS":
            self._fire_alert(
                "WARNING",
                "automation",
                f"Task '{task.name}' {result['status']} "
                f"(exit {result['exit_code']}, {attempt} attempt(s))",
            )

        if result["duration"] > config.THRESHOLDS["task_runtime"]:
            self._fire_alert(
                "INFO",
                "automation",
                f"Long-running task '{task.name}': {result['duration']}s",
            )

        return task_log

    def run_workflow(
        self,
        workflow: Workflow,
        on_progress: Callable[[dict[str, Any]], None] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a workflow sequentially or in parallel."""

        run_id = str(uuid.uuid4())[:8]

        with self.lock:
            self.running_workflows[run_id] = {
                "workflow": workflow.name,
                "started": time.time(),
                "total": len(workflow.tasks),
                "done": 0,
            }

        results: list[dict[str, Any]] = []

        try:
            if workflow.mode == "parallel":
                # --- THREAD CONCURRENCY: Run tasks simultaneously ---
                with ThreadPoolExecutor(max_workers=workflow.max_workers) as executor:
                    future_to_task = {
                        executor.submit(
                            self.run_task, task, workflow.name, "parallel"
                        ): task
                        for task in workflow.tasks
                    }

                    for future in as_completed(future_to_task):
                        result = future.result()
                        results.append(result)
                        self._update_progress(run_id, on_progress, result)
            else:
                # --- SEQUENTIAL EXECUTION ---
                for task in workflow.tasks:
                    result = self.run_task(task, workflow.name, "sequential")
                    results.append(result)
                    self._update_progress(run_id, on_progress, result)

                    if result["status"] != "SUCCESS" and not task.continue_on_error:
                        break
        finally:
            with self.lock:
                self.running_workflows.pop(run_id, None)

        return results

    def run_workflow_async(
        self,
        workflow: Workflow,
        on_complete: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> threading.Thread:
        """Run a workflow in a separate thread so the main program can continue."""

        def target() -> None:
            results = self.run_workflow(workflow)
            if on_complete:
                on_complete(results)

        thread = threading.Thread(
            target=target,
            name=f"Workflow-{workflow.name}",
            daemon=True,
        )
        thread.start()
        return thread

    def _update_progress(
        self,
        run_id: str,
        callback: Callable[[dict[str, Any]], None] | None,
        result: dict[str, Any],
    ) -> None:
        """Update running workflow progress and call the optional callback."""

        with self.lock:
            if run_id in self.running_workflows:
                self.running_workflows[run_id]["done"] += 1

        if callback:
            callback(result)

    def get_active_runs(self) -> dict[str, dict[str, Any]]:
        """Return a copy of the currently running workflows."""

        with self.lock:
            return dict(self.running_workflows)


class Scheduler(threading.Thread):
    """
    A background thread that executes commands at fixed intervals.
    Persists jobs to a JSON file.
    """

    def __init__(self, engine: AutomationEngine):
        super().__init__(name="Scheduler", daemon=True)
        self.engine = engine
        self.lock = threading.RLock()
        self.jobs: list[dict[str, Any]] = []
        self._stop_event = threading.Event()
        self.load_jobs()

    def add_job(
        self,
        name: str,
        command: str,
        interval_seconds: int,
        retries: int = 1,
    ) -> dict[str, Any]:
        """Add a new scheduled job."""

        job = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "command": command,
            "interval": interval_seconds,
            "retries": retries,
            "next_run": time.time() + interval_seconds,
            "enabled": True,
            "runs": 0,
        }

        with self.lock:
            self.jobs.append(job)
        self.save_jobs()
        return job

    def remove_job(self, job_id: str) -> None:
        """Remove a scheduled job by ID."""

        with self.lock:
            self.jobs = [job for job in self.jobs if job["id"] != job_id]
        self.save_jobs()

    def toggle_job(self, job_id: str) -> None:
        """Enable or disable a job."""

        with self.lock:
            for job in self.jobs:
                if job["id"] == job_id:
                    job["enabled"] = not job["enabled"]
        self.save_jobs()

    def list_jobs(self) -> list[dict[str, Any]]:
        """Return a copy of all jobs."""

        with self.lock:
            return dict([(job["id"], dict(job)) for job in self.jobs]).values()

    def save_jobs(self) -> None:
        """Persist jobs to JSON file."""

        with self.lock:
            with open(config.SCHEDULE_PATH, "w") as f:
                json.dump(self.jobs, f, indent=2)

    def load_jobs(self) -> None:
        """Load jobs from JSON file."""

        if Path(config.SCHEDULE_PATH).exists():
            try:
                with open(config.SCHEDULE_PATH, "r") as f:
                    self.jobs = json.load(f)
                for job in self.jobs:
                    job["next_run"] = time.time() + job["interval"]
            except Exception:
                self.jobs = []

    def run(self) -> None:
        """Main scheduler loop."""

        while not self._stop_event.is_set():
            now = time.time()
            due_jobs: list[dict[str, Any]] = []

            with self.lock:
                for job in self.jobs:
                    if job["enabled"] and now >= job["next_run"]:
                        due_jobs.append(dict(job))
                        job["next_run"] = now + job["interval"]
                        job["runs"] += 1

            for job in due_jobs:
                task = Task(
                    name=job["name"],
                    command=job["command"],
                    retries=job.get("retries", 1),
                )

                # Execute the scheduled task in a separate thread
                threading.Thread(
                    target=self.engine.run_task,
                    args=(task, "scheduled", "scheduled"),
                    daemon=True,
                ).start()

            self._stop_event.wait(1.0)

    def stop(self) -> None:
        """Stop the scheduler thread."""

        self._stop_event.set()
