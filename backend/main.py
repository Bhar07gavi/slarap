#!/usr/bin/env python3

"""
SLARAP - Smart Linux Automation & Intelligent Resource Analytics Platform
Main CLI Dashboard
"""

import os
import time
import json
import signal
import sys
from pathlib import Path

# Add project root to path when running directly
if __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend import config
from backend.storage import db
from backend.monitor.resources import (
    ResourceMonitor,
    calculate_health_score,
    human_uptime,
)
from backend.procmgr import manager
from backend.automation.engine import (
    AutomationEngine,
    Scheduler,
    Task,
    Workflow,
)
from backend.analytics import logs, predictor, recommender
from backend.analytics.alerts import AlertEngine
from backend.reports import generator

BANNER = r"""
   ____  _        _    ____      _    ____
  / ___|| |      / \  |  _ \    / \  |  _ \    Smart Linux Automation &
  \___ \| |     / _ \ | |_) |  / _ \ | |_) |   Intelligent Resource
   ___) | |___ / ___ \|  _ <  / ___ \|  __/    Analytics Platform
  |____/|_____/_/   \_\_| \_\/_/   \_\_|       v1.0
"""

MENU = """
 ── MONITORING ──────────────────  ── AUTOMATION ────────────────────
  1  Live terminal dashboard      10  Run command (fork+exec+wait)
  2  System snapshot              11  Run command in BACKGROUND
  3  Top processes                12  Show background jobs
  4  Process tree (hierarchy)     13  Pipe IPC demo (cmd1 | cmd2)
                                  14  Run workflow from JSON
 ── ANALYTICS ──────────────────  15  Quick parallel workflow
  5  Log analysis                 16  Scheduler: add job
  6  Predictions / forecasting    17  Scheduler: list/remove jobs
  7  Recommendations              18  Automation history
  8  Historical reports
  9  Recent alerts                ── OUTPUT ─────────────────────────
                                  19  Generate full report (TXT)
 ── SYSTEM ─────────────────────  20  Export CSV (metrics/tasks/alerts)
 21  Launch GUI dashboard         22  Export PDF report
 23  Show thresholds              24  Kill a process
  0  Exit
"""


class SLARAPApp:
    """Main application class for SLARAP."""

    def __init__(self):
        """Initialize all SLARAP components."""
        db.initialize_database()

        # Resource monitoring thread
        self.monitor = ResourceMonitor()

        # Alert engine thread
        self.alerts = AlertEngine(self.monitor)

        # Automation engine with alert integration
        self.engine = AutomationEngine(alert_callback=self.alerts.fire)

        # Scheduler thread
        self.scheduler = Scheduler(self.engine)

    def start(self):
        """Start all background threads."""
        print("[*] Starting ResourceMonitor...")
        self.monitor.start()

        print("[*] Starting AlertEngine...")
        self.alerts.start()

        print("[*] Starting Scheduler...")
        self.scheduler.start()

        # Wait for first monitoring sample
        time.sleep(2.5)
        print("[*] All background services running.\n")

    def stop(self):
        """Stop all background threads."""
        print("\n[*] Stopping background services...")
        self.monitor.stop()
        self.alerts.stop()
        self.scheduler.stop()
        print("[*] Clean shutdown complete.\n")


# ───────────────────────── Helper Functions ─────────────────────────

def clear_screen():
    os.system("clear")


def progress_bar(percentage, width=34):
    """Return a colored progress bar."""
    filled = int(percentage / 100 * width)
    if percentage < 60:
        color = "\033[92m"  # green
    elif percentage < 85:
        color = "\033[93m"  # yellow
    else:
        color = "\033[91m"  # red
    return f"{color}{'█' * filled}{'░' * (width - filled)}\033[0m {percentage:5.1f}%"


def live_dashboard(app):
    """Interactive live dashboard display."""
    print("\n[ Live Dashboard — press Ctrl+C to return to menu ]\n")
    try:
        while True:
            sample = app.monitor.get_snapshot()
            if not sample:
                time.sleep(1)
                continue

            score, label = calculate_health_score(sample)

            clear_screen()
            print("\033[96m" + "=" * 80 + "\033[0m")
            print(f"  SLARAP LIVE DASHBOARD         {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("\033[96m" + "=" * 80 + "\033[0m")
            print(f"  HEALTH  {score}/100  [{label}]   "
                  f"Uptime {human_uptime(sample['uptime'])}")
            print()
            print(f"  CPU    {progress_bar(sample['cpu'])}  ({sample['cpu_count']} cores)")
            print(f"  MEM    {progress_bar(sample['memory'])}  "
                  f"{sample['memory_used_gb']}/{sample['memory_total_gb']} GB")
            print(f"  SWAP   {progress_bar(sample['swap'])}")
            print(f"  DISK   {progress_bar(sample['disk'])}  "
                  f"{sample['disk_free_gb']} GB free")
            print()
            print(f"  Load   {sample['load'][0]:.2f} {sample['load'][1]:.2f} "
                  f"{sample['load'][2]:.2f}   Procs {sample['process_count']}")
            print(f"  Net    ↓{sample['network_download_kbps']:.0f} "
                  f"↑{sample['network_upload_kbps']:.0f} KB/s")

            # Active workflows
            active = app.engine.get_active_runs()
            print(f"  Workflows: {len(active)}   Background: "
                  f"{len(manager.list_background_processes())}   "
                  f"Scheduled: {len(app.scheduler.list_jobs())}")

            # Top processes
            print("\n  TOP PROCESSES")
            print(f"  {'PID':>7} {'NAME':<24} {'CPU%':>7} {'MEM%':>7}")
            for proc in manager.top_processes(7, "cpu"):
                print(f"  {proc['pid']:>7} {(proc['name'] or '')[:24]:<24} "
                      f"{(proc.get('cpu_percent') or 0):>7.1f} "
                      f"{(proc.get('memory_percent') or 0):>7.1f}")

            # Recent alerts
            recent = app.alerts.get_recent_alerts(4)
            print("\n  RECENT ALERTS")
            if recent:
                for alert in recent:
                    print(f"   [{alert['time']}] {alert['level']:<8} "
                          f"{alert['message'][:56]}")
            else:
                print("   none")

            print("\033[96m" + "=" * 80 + "\033[0m")
            print("  Ctrl+C to exit")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n[*] Returning to menu...")


def system_snapshot(app):
    """Display current system state."""
    sample = app.monitor.get_snapshot()
    score, label = calculate_health_score(sample)

    print(f"\nHealth        : {score}/100 ({label})")
    print(f"CPU           : {sample['cpu']:.1f}% ({sample['cpu_count']} cores)")
    print(f"Per-core CPU  : {[f'{c:.1f}%' for c in sample['cpu_per_core']]}")
    print(f"Memory        : {sample['memory']:.1f}% "
          f"({sample['memory_used_gb']}/{sample['memory_total_gb']} GB)")
    print(f"Swap          : {sample['swap']:.1f}%")
    print(f"Disk ({config.DISK_MOUNT})     : {sample['disk']:.1f}% "
          f"({sample['disk_free_gb']} GB free)")
    print(f"Load average  : {sample['load']}")
    print(f"Processes     : {sample['process_count']}")
    print(f"Network       : ↓{sample['network_download_kbps']:.0f} "
          f"↑{sample['network_upload_kbps']:.0f} KB/s")
    print(f"Uptime        : {human_uptime(sample['uptime'])}")


def show_top_processes():
    """Display top processes by CPU or memory."""
    sort_by = input("Sort by (cpu/mem) [cpu]: ").strip() or "cpu"
    if sort_by not in ("cpu", "mem"):
        sort_by = "cpu"

    print(f"\n{'PID':>7} {'NAME':<26} {'USER':<14} "
          f"{'CPU%':>7} {'MEM%':>7}  STATUS")
    print("-" * 70)

    for proc in manager.top_processes(20, sort_by):
        print(f"{proc['pid']:>7} {(proc['name'] or '')[:26]:<26} "
              f"{(proc.get('username') or '')[:14]:<14} "
              f"{(proc.get('cpu_percent') or 0):>7.1f} "
              f"{(proc.get('memory_percent') or 0):>7.1f}  {proc.get('status')}")


def show_process_tree(app):
    """Display process hierarchy."""
    root_pid = input("Root PID [this process]: ").strip()
    pid = int(root_pid) if root_pid else None

    print("\nProcess hierarchy:")
    for line in manager.process_tree(pid, max_depth=3):
        print(line)


def run_single_command(app):
    """Run a command with fork+exec+pipe+wait."""
    cmd = input("Command: ").strip()
    if not cmd:
        return

    print(f"\nExecuting: {cmd}")
    print("-" * 60)

    task = Task(name="manual_command", command=cmd, retries=0, timeout=120)
    result = app.engine.run_task(task)

    print(f"\nStatus: {result['status']}")
    print(f"Exit code: {result['exit_code']}")
    print(f"Duration: {result['duration']}s")
    print(f"Output:\n{result['output']}")


def run_background_command():
    """Run command in background."""
    cmd = input("Background command: ").strip()
    if not cmd:
        return

    pid = manager.run_background(cmd)
    print(f"Started background process with PID {pid}")


def show_background_jobs():
    """List background jobs."""
    jobs = manager.list_background_processes()
    if not jobs:
        print("No background jobs running.")
        return

    print("\nBackground jobs:")
    for pid, info in jobs.items():
        print(f"  PID {pid}  elapsed {info['elapsed']}s  {info['cmd']}")


def run_pipeline_demo():
    """Demonstrate pipe IPC (cmd1 | cmd2)."""
    cmd1 = input("First command [ps aux]: ").strip() or "ps aux"
    cmd2 = input("Second command [head -10]: ").strip() or "head -10"

    result = manager.pipeline(cmd1, cmd2)

    print(f"\n$ {result['command']} (exit {result['exit_code']})")
    print("-" * 60)
    print(result["output"])


def run_workflow_from_file(app):
    """Run a workflow defined in a JSON file."""
    workflow_dir = Path(config.WORKFLOW_DIR)
    workflows = list(workflow_dir.glob("*.json"))

    if not workflows:
        print(f"\nNo workflows found in {workflow_dir}")
        print("Create one or add a JSON file.")
        return

    print("\nAvailable workflows:")
    for i, wf_path in enumerate(workflows, 1):
        print(f"  {i}. {wf_path.stem}")

    choice = input("\nSelect number: ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(workflows):
        print("Invalid selection.")
        return

    selected = workflows[int(choice) - 1]
    workflow = Workflow.from_file(selected)

    print(f"\nRunning '{workflow.name}' [{workflow.mode}] "
          f"with {len(workflow.tasks)} tasks...")
    start = time.time()

    results = app.engine.run_workflow(
        workflow,
        on_progress=lambda r: print(
            f"  ✓ {r['task_name']:<20} {r['status']:<10} "
            f"{r['duration']}s"
        ),
    )

    success = sum(1 for r in results if r["status"] == "SUCCESS")
    total_time = time.time() - start

    print(f"\nDone: {success}/{len(results)} succeeded in {total_time:.2f}s")

    if input("Show output? (y/N): ").lower() == "y":
        for result in results:
            print(f"\n--- {result['task_name']} ---")
            print(result["output"][:1500])


def run_parallel_workflow(app):
    """Run multiple commands in parallel."""
    cmd_input = input("Commands separated by ';;': ").strip()
    commands = [cmd.strip() for cmd in cmd_input.split(";;") if cmd.strip()]

    if not commands:
        print("No commands provided.")
        return

    tasks = [Task(f"task_{i+1}", cmd) for i, cmd in enumerate(commands)]
    workflow = Workflow("adhoc_parallel", tasks, mode="parallel", max_workers=4)

    print(f"\nRunning {len(tasks)} tasks in parallel...")
    start = time.time()
    results = app.engine.run_workflow(workflow)
    elapsed = time.time() - start

    print(f"\nCompleted {len(results)} tasks in {elapsed:.2f}s")
    for r in results:
        print(f"  {r['task_name']:<10} {r['status']:<8} {r['duration']}s")


def scheduler_add_job(app):
    """Add a scheduled job to the scheduler."""
    name = input("Job name: ").strip()
    cmd = input("Command: ").strip()
    interval = input("Interval (seconds): ").strip()

    if not name or not cmd or not interval.isdigit():
        print("Invalid input. Name, command, and numeric interval required.")
        return

    job = app.scheduler.add_job(name, cmd, int(interval))
    print(f"Scheduled job {job['id']} every {interval}s: {cmd}")


def scheduler_list_jobs(app):
    """List and manage scheduled jobs."""
    jobs = list(app.scheduler.list_jobs())

    if not jobs:
        print("No scheduled jobs.")
        return

    print("\nScheduled jobs:")
    for job in jobs:
        status = "ON" if job["enabled"] else "OFF"
        print(f"  {job['id']}  {job['name']:<20} "
              f"every {job['interval']}s  runs={job['runs']}  "
              f"{status}  :: {job['command']}")

    job_id = input("\nRemove job ID (or blank to skip): ").strip()
    if job_id:
        app.scheduler.remove_job(job_id)
        print("Job removed.")


def show_automation_history():
    """Display recent task executions."""
    runs = db.recent_task_runs(25)

    if not runs:
        print("No task executions recorded.")
        return

    print("\nRecent task executions:")
    print(f"{'DateTime':<20} {'Status':<8} {'Workflow':<16} "
          f"{'Task':<20} {'Exit':<5} {'Duration'}")
    print("-" * 80)

    for run in runs:
        print(f"{run['date_time']:<20} {run['status']:<8} "
              f"{(run['workflow'] or '')[:16]:<16} "
              f"{(run['task_name'] or '')[:20]:<20} "
              f"{run['exit_code']:<5} {run['duration']}s")


def show_recent_alerts(app):
    """Display recent alerts."""
    alerts = app.alerts.get_recent_alerts(25)

    if not alerts:
        print("No recent alerts.")
        return

    print("\nRecent alerts:")
    for alert in alerts:
        print(f"[{alert['time']}] {alert['level']:<8} "
              f"{alert['category']:<12} {alert['message']}")


def kill_process_interactive():
    """Interactive process killer."""
    pid = input("PID to terminate: ").strip()
    if not pid.isdigit():
        print("Invalid PID.")
        return

    force = input("Force kill? (y/N): ").lower() == "y"
    success, message = manager.kill_process(int(pid), force)
    print(message)


# ───────────────────────── Main Menu ─────────────────────────

def main_menu(app):
    """Display main menu and handle user input."""
    while True:
        clear_screen()
        print(BANNER)
        print(MENU)

        choice = input("slarap> ").strip()

        if choice == "0":
            app.stop()
            print("Goodbye!")
            break

        elif choice == "1":
            live_dashboard(app)

        elif choice == "2":
            system_snapshot(app)

        elif choice == "3":
            show_top_processes()

        elif choice == "4":
            show_process_tree(app)

        elif choice == "5":
            report = logs.analyze()
            print(logs.format_report(report))

        elif choice == "6":
            predictions = predictor.predict_all(app.monitor)
            print(predictor.format_predictions(predictions))

        elif choice == "7":
            recs = recommender.generate_recommendations(app.monitor)
            print(recommender.format_recommendations(recs))

        elif choice == "8":
            bucket = input("Bucket (hour/day/week) [hour]: ").strip() or "hour"
            hours_map = {"hour": 24, "day": 24 * 7, "week": 24 * 30}
            hours = hours_map.get(bucket, 24)
            rows = db.aggregate(hours * 3600, bucket)
            if not rows:
                print("No data yet. Let the monitor run.")
            else:
                print(f"\n{bucket.capitalize()} aggregation:")
                for row in rows:
                    print(f"  {row['bucket']:<16} CPU avg {row['avg_cpu']:>6}% "
                          f"max {row['max_cpu']:>6}% | "
                          f"Mem avg {row['avg_mem']:>6}% | "
                          f"Disk {row['avg_disk']:>6}% | n={row['samples']}")

        elif choice == "9":
            show_recent_alerts(app)

        elif choice == "10":
            run_single_command(app)

        elif choice == "11":
            run_background_command()

        elif choice == "12":
            show_background_jobs()

        elif choice == "13":
            run_pipeline_demo()

        elif choice == "14":
            run_workflow_from_file(app)

        elif choice == "15":
            run_parallel_workflow(app)

        elif choice == "16":
            scheduler_add_job(app)

        elif choice == "17":
            scheduler_list_jobs(app)

        elif choice == "18":
            show_automation_history()

        elif choice == "19":
            path = generator.save_txt_report(app.monitor)
            print(f"Saved: {path}")

        elif choice == "20":
            metrics_path, m_count = generator.export_metrics_csv(24)
            tasks_path, t_count = generator.export_tasks_csv()
            alerts_path, a_count = generator.export_alerts_csv()
            print(f"Metrics -> {metrics_path} ({m_count} rows)")
            print(f"Tasks   -> {tasks_path} ({t_count} rows)")
            print(f"Alerts  -> {alerts_path} ({a_count} rows)")

        elif choice == "21":
            try:
                from frontend import dashboard
                print("Launching GUI dashboard...")
                import threading
                gui_thread = threading.Thread(
                    target=dashboard.launch,
                    args=(app.monitor, app.alerts, app.engine, app.scheduler),
                    daemon=True,
                )
                gui_thread.start()
                print("GUI launched. You can continue using CLI.")
            except Exception as e:
                print(f"GUI launch failed: {e}")

        elif choice == "22":
            pdf_path, error = generator.export_pdf_report(app.monitor)
            if pdf_path:
                print(f"Saved: {pdf_path}")
            else:
                print(f"Error: {error}")

        elif choice == "23":
            print("\nAlert thresholds:")
            for key, value in config.THRESHOLDS.items():
                print(f"  {key:<20} {value}")

        elif choice == "24":
            kill_process_interactive()

        else:
            print("Invalid option. Try again.")

        input("\nPress Enter to continue...")


# ───────────────────────── Entry Point ─────────────────────────

def main():
    """Main entry point for SLARAP."""
    clear_screen()
    print(BANNER)

    app = SLARAPApp()
    app.start()

    # Create sample workflow if none exists
    sample_wf = Path(config.WORKFLOW_DIR) / "sample_health_check.json"
    if not sample_wf.exists():
        workflow_data = {
            "name": "system_health_check",
            "mode": "parallel",
            "max_workers": 3,
            "tasks": [
                {"name": "disk_usage", "command": "df -h"},
                {"name": "memory_info", "command": "free -h"},
                {"name": "uptime_load", "command": "uptime"},
                {"name": "top_cpu", "command": "ps -eo pid,comm,%cpu --sort=-%cpu | head -8"},
            ],
        }
        with open(sample_wf, "w") as f:
            json.dump(workflow_data, f, indent=2)
        print(f"[*] Created sample workflow: {sample_wf.name}")

    try:
        main_menu(app)
    except KeyboardInterrupt:
        app.stop()
        print("\nInterrupted. Goodbye!")


if __name__ == "__main__":
    main()
