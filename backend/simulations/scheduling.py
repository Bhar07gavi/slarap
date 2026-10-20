"""
SLARAP Educational OS Simulation Engine - CPU Scheduling.

Provides deterministic step-by-step simulation for:
1. First-Come, First-Served (FCFS)
2. Shortest Job First (SJF Non-Preemptive)
3. Shortest Remaining Time First (SRTF Preemptive)
4. Priority (Non-Preemptive)
5. Priority (Preemptive)
6. Round Robin (RR)
7. Multilevel Feedback Queue (MLFQ)

Every algorithm produces:
- A timeline of discrete execution steps/events with real-time dynamic explanations.
- Step-by-step growing Gantt chart slices.
- Process Control Block (PCB) snapshots with state transitions.
- Accurate metrics (Completion, Turnaround, Waiting, Response times, CPU Utilization).
"""

from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional
import copy


@dataclass
class ProcessInput:
    id: str
    arrival_time: int
    burst_time: int
    priority: int = 0  # Lower number = higher priority (standard textbook convention)


def simulate_cpu_scheduling(
    algorithm: str,
    processes: List[Dict[str, Any]],
    time_quantum: int = 2,
    mlfq_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Main entry point for CPU scheduling simulations.
    processes: list of dicts with keys 'id', 'arrival_time', 'burst_time', and optional 'priority'.
    algorithm: 'FCFS', 'SJF', 'SRTF', 'PRIORITY', 'PRIORITY_PREEMPTIVE', 'ROUND_ROBIN', 'MLFQ'.
    """
    if not processes:
        return {
            "algorithm": algorithm,
            "events": [],
            "gantt": [],
            "metrics": {
                "process_metrics": {},
                "avg_waiting_time": 0,
                "avg_turnaround_time": 0,
                "avg_response_time": 0,
                "cpu_utilization": 0,
                "throughput": 0,
                "total_time": 0,
            },
        }

    # Normalize inputs
    procs = [
        ProcessInput(
            id=str(p["id"]),
            arrival_time=int(p["arrival_time"]),
            burst_time=int(p["burst_time"]),
            priority=int(p.get("priority", 0)),
        )
        for p in processes
    ]

    alg_upper = algorithm.upper().replace("-", "_").replace(" ", "_")

    if alg_upper == "FCFS":
        return _simulate_fcfs(procs)
    elif alg_upper in ("SJF", "SJF_NON_PREEMPTIVE"):
        return _simulate_sjf(procs)
    elif alg_upper in ("SRTF", "SJF_PREEMPTIVE"):
        return _simulate_srtf(procs)
    elif alg_upper in ("PRIORITY", "PRIORITY_NON_PREEMPTIVE"):
        return _simulate_priority(procs, preemptive=False)
    elif alg_upper in ("PRIORITY_PREEMPTIVE", "PREEMPTIVE_PRIORITY"):
        return _simulate_priority(procs, preemptive=True)
    elif alg_upper in ("ROUND_ROBIN", "RR"):
        return _simulate_round_robin(procs, time_quantum=max(1, time_quantum))
    elif alg_upper == "MLFQ":
        return _simulate_mlfq(procs, mlfq_config or {})
    else:
        raise ValueError(f"Unsupported scheduling algorithm: {algorithm}")


def _build_initial_pcbs(procs: List[ProcessInput]) -> Dict[str, Dict[str, Any]]:
    return {
        p.id: {
            "id": p.id,
            "state": "NEW",
            "arrival_time": p.arrival_time,
            "burst_time": p.burst_time,
            "remaining_burst": p.burst_time,
            "priority": p.priority,
            "start_time": None,
            "completion_time": None,
            "waiting_time": 0,
            "turnaround_time": 0,
            "response_time": None,
        }
        for p in procs
    }


def _calculate_final_metrics(
    pcbs: Dict[str, Dict[str, Any]], total_time: int, busy_time: int
) -> Dict[str, Any]:
    n = len(pcbs)
    if n == 0:
        return {
            "process_metrics": {},
            "avg_waiting_time": 0,
            "avg_turnaround_time": 0,
            "avg_response_time": 0,
            "cpu_utilization": 0,
            "throughput": 0,
            "total_time": total_time,
        }

    total_wt = 0
    total_tat = 0
    total_rt = 0

    for pid, p in pcbs.items():
        comp = p["completion_time"] if p["completion_time"] is not None else total_time
        p["turnaround_time"] = comp - p["arrival_time"]
        p["waiting_time"] = p["turnaround_time"] - p["burst_time"]
        if p["start_time"] is not None:
            p["response_time"] = p["start_time"] - p["arrival_time"]
        else:
            p["response_time"] = 0

        total_wt += p["waiting_time"]
        total_tat += p["turnaround_time"]
        total_rt += p["response_time"]

    cpu_util = round((busy_time / total_time * 100) if total_time > 0 else 0, 2)
    throughput = round((n / total_time) if total_time > 0 else 0, 4)

    return {
        "process_metrics": pcbs,
        "avg_waiting_time": round(total_wt / n, 2),
        "avg_turnaround_time": round(total_tat / n, 2),
        "avg_response_time": round(total_rt / n, 2),
        "cpu_utilization": cpu_util,
        "throughput": throughput,
        "total_time": total_time,
    }


def _record_event(
    events: List[Dict[str, Any]],
    current_time: int,
    event_type: str,
    running_id: Optional[str],
    ready_queue: List[str],
    waiting_queue: List[str],
    pcbs: Dict[str, Dict[str, Any]],
    explanation: str,
    gantt: List[Dict[str, Any]],
) -> None:
    events.append({
        "time": current_time,
        "event_type": event_type,
        "running": running_id,
        "ready_queue": list(ready_queue),
        "waiting_queue": list(waiting_queue),
        "process_states": copy.deepcopy(pcbs),
        "explanation": explanation,
        "gantt": copy.deepcopy(gantt),
    })


def _simulate_fcfs(procs: List[ProcessInput]) -> Dict[str, Any]:
    sorted_procs = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = list(sorted_procs)
    busy_time = 0

    while unentered or ready_queue:
        # Check newly arrived
        arrived = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            _record_event(
                events, current_time, "ARRIVAL", None, ready_queue, [], pcbs,
                f"Process {p.id} arrived at t={current_time} and entered Ready Queue.",
                gantt
            )

        if not ready_queue:
            # CPU is idle until next process arrives
            next_arrival = min(p.arrival_time for p in unentered)
            gantt.append({"id": "IDLE", "start": current_time, "end": next_arrival, "duration": next_arrival - current_time})
            _record_event(
                events, current_time, "IDLE", "IDLE", [], [], pcbs,
                f"CPU idle from t={current_time} until next process arrives at t={next_arrival}.",
                gantt
            )
            current_time = next_arrival
            continue

        # Pick first in FCFS
        pid = ready_queue.pop(0)
        p_obj = pcbs[pid]
        p_obj["state"] = "RUNNING"
        if p_obj["start_time"] is None:
            p_obj["start_time"] = current_time

        _record_event(
            events, current_time, "DISPATCH", pid, ready_queue, [], pcbs,
            f"At t={current_time}, {pid} is dispatched (FCFS order: earliest arrival {p_obj['arrival_time']}).",
            gantt
        )

        start = current_time
        duration = p_obj["burst_time"]
        busy_time += duration
        current_time += duration

        # Any processes arriving while pid was executing
        arrived_during = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived_during:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)

        p_obj["remaining_burst"] = 0
        p_obj["state"] = "TERMINATED"
        p_obj["completion_time"] = current_time
        gantt.append({"id": pid, "start": start, "end": current_time, "duration": duration})

        _record_event(
            events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
            f"{pid} completed execution at t={current_time} (Burst: {duration}).",
            gantt
        )

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "FCFS",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_sjf(procs: List[ProcessInput]) -> Dict[str, Any]:
    """Non-preemptive Shortest Job First."""
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    busy_time = 0

    while unentered or ready_queue:
        arrived = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            _record_event(
                events, current_time, "ARRIVAL", None, ready_queue, [], pcbs,
                f"Process {p.id} arrived at t={current_time} (burst={p.burst_time}).",
                gantt
            )

        if not ready_queue:
            next_arrival = min(p.arrival_time for p in unentered)
            gantt.append({"id": "IDLE", "start": current_time, "end": next_arrival, "duration": next_arrival - current_time})
            _record_event(
                events, current_time, "IDLE", "IDLE", [], [], pcbs,
                f"CPU idle from t={current_time} until t={next_arrival}.",
                gantt
            )
            current_time = next_arrival
            continue

        # SJF: Sort ready queue by burst_time, then arrival_time, then id
        ready_queue.sort(key=lambda pid: (pcbs[pid]["burst_time"], pcbs[pid]["arrival_time"], pid))
        pid = ready_queue.pop(0)
        p_obj = pcbs[pid]
        p_obj["state"] = "RUNNING"
        if p_obj["start_time"] is None:
            p_obj["start_time"] = current_time

        _record_event(
            events, current_time, "DISPATCH", pid, ready_queue, [], pcbs,
            f"At t={current_time}, {pid} is selected because it has the shortest burst ({p_obj['burst_time']}) among ready processes.",
            gantt
        )

        start = current_time
        duration = p_obj["burst_time"]
        busy_time += duration
        current_time += duration

        arrived_during = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived_during:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)

        p_obj["remaining_burst"] = 0
        p_obj["state"] = "TERMINATED"
        p_obj["completion_time"] = current_time
        gantt.append({"id": pid, "start": start, "end": current_time, "duration": duration})

        _record_event(
            events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
            f"{pid} finished at t={current_time}.",
            gantt
        )

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "SJF",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_srtf(procs: List[ProcessInput]) -> Dict[str, Any]:
    """Preemptive Shortest Remaining Time First (SRTF). Simulates tick by tick."""
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    total_burst = sum(p.burst_time for p in procs)
    completed_count = 0
    n = len(procs)
    busy_time = 0
    current_running: Optional[str] = None
    slice_start = 0

    while completed_count < n:
        # Check arrivals at current_time
        arrived = [p for p in unentered if p.arrival_time == current_time]
        new_arrival_occurred = False
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            new_arrival_occurred = True

        if new_arrival_occurred:
            _record_event(
                events, current_time, "ARRIVAL", current_running, ready_queue, [], pcbs,
                f"Process {[p.id for p in arrived]} arrived at t={current_time}.",
                gantt
            )

        # Build candidate pool (current running + ready queue)
        pool = list(ready_queue)
        if current_running and pcbs[current_running]["state"] == "RUNNING":
            pool.append(current_running)

        if not pool:
            # Idle tick
            if gantt and gantt[-1]["id"] == "IDLE":
                gantt[-1]["end"] += 1
                gantt[-1]["duration"] += 1
            else:
                gantt.append({"id": "IDLE", "start": current_time, "end": current_time + 1, "duration": 1})
            current_time += 1
            continue

        # Pick candidate with smallest remaining_burst, tie-break arrival_time, then id
        best_pid = min(pool, key=lambda pid: (pcbs[pid]["remaining_burst"], pcbs[pid]["arrival_time"], pid))

        if best_pid != current_running:
            # Context switch / dispatch
            if current_running:
                # Preempt current
                pcbs[current_running]["state"] = "READY"
                if current_running not in ready_queue:
                    ready_queue.append(current_running)
                _record_event(
                    events, current_time, "PREEMPT", best_pid, ready_queue, [], pcbs,
                    f"At t={current_time}, {current_running} (rem={pcbs[current_running]['remaining_burst']}) preempted by {best_pid} (rem={pcbs[best_pid]['remaining_burst']}).",
                    gantt
                )

            current_running = best_pid
            if current_running in ready_queue:
                ready_queue.remove(current_running)
            pcbs[current_running]["state"] = "RUNNING"
            if pcbs[current_running]["start_time"] is None:
                pcbs[current_running]["start_time"] = current_time

            _record_event(
                events, current_time, "DISPATCH", current_running, ready_queue, [], pcbs,
                f"At t={current_time}, {current_running} is selected (shortest remaining time: {pcbs[current_running]['remaining_burst']}).",
                gantt
            )

        # Execute 1 time unit
        if gantt and gantt[-1]["id"] == current_running:
            gantt[-1]["end"] += 1
            gantt[-1]["duration"] += 1
        else:
            gantt.append({"id": current_running, "start": current_time, "end": current_time + 1, "duration": 1})

        pcbs[current_running]["remaining_burst"] -= 1
        busy_time += 1
        current_time += 1

        # Check if finished
        if pcbs[current_running]["remaining_burst"] == 0:
            pcbs[current_running]["state"] = "TERMINATED"
            pcbs[current_running]["completion_time"] = current_time
            completed_count += 1
            _record_event(
                events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
                f"{current_running} finished execution at t={current_time}.",
                gantt
            )
            current_running = None

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "SRTF",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_priority(procs: List[ProcessInput], preemptive: bool = False) -> Dict[str, Any]:
    """Priority Scheduling (lower value = higher priority)."""
    if preemptive:
        return _simulate_priority_preemptive(procs)
    else:
        return _simulate_priority_non_preemptive(procs)


def _simulate_priority_non_preemptive(procs: List[ProcessInput]) -> Dict[str, Any]:
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    busy_time = 0

    while unentered or ready_queue:
        arrived = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            _record_event(
                events, current_time, "ARRIVAL", None, ready_queue, [], pcbs,
                f"Process {p.id} arrived at t={current_time} (priority={p.priority}).",
                gantt
            )

        if not ready_queue:
            next_arrival = min(p.arrival_time for p in unentered)
            gantt.append({"id": "IDLE", "start": current_time, "end": next_arrival, "duration": next_arrival - current_time})
            _record_event(
                events, current_time, "IDLE", "IDLE", [], [], pcbs,
                f"CPU idle from t={current_time} until t={next_arrival}.",
                gantt
            )
            current_time = next_arrival
            continue

        # Sort by priority ascending (0 is highest), then arrival_time, then id
        ready_queue.sort(key=lambda pid: (pcbs[pid]["priority"], pcbs[pid]["arrival_time"], pid))
        pid = ready_queue.pop(0)
        p_obj = pcbs[pid]
        p_obj["state"] = "RUNNING"
        if p_obj["start_time"] is None:
            p_obj["start_time"] = current_time

        _record_event(
            events, current_time, "DISPATCH", pid, ready_queue, [], pcbs,
            f"At t={current_time}, {pid} is selected (highest priority: {p_obj['priority']}).",
            gantt
        )

        start = current_time
        duration = p_obj["burst_time"]
        busy_time += duration
        current_time += duration

        arrived_during = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived_during:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)

        p_obj["remaining_burst"] = 0
        p_obj["state"] = "TERMINATED"
        p_obj["completion_time"] = current_time
        gantt.append({"id": pid, "start": start, "end": current_time, "duration": duration})

        _record_event(
            events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
            f"{pid} completed at t={current_time}.",
            gantt
        )

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "PRIORITY_NON_PREEMPTIVE",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_priority_preemptive(procs: List[ProcessInput]) -> Dict[str, Any]:
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    completed_count = 0
    n = len(procs)
    busy_time = 0
    current_running: Optional[str] = None

    while completed_count < n:
        arrived = [p for p in unentered if p.arrival_time == current_time]
        new_arrival = False
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            new_arrival = True

        if new_arrival:
            _record_event(
                events, current_time, "ARRIVAL", current_running, ready_queue, [], pcbs,
                f"Process {[p.id for p in arrived]} arrived at t={current_time}.",
                gantt
            )

        pool = list(ready_queue)
        if current_running and pcbs[current_running]["state"] == "RUNNING":
            pool.append(current_running)

        if not pool:
            if gantt and gantt[-1]["id"] == "IDLE":
                gantt[-1]["end"] += 1
                gantt[-1]["duration"] += 1
            else:
                gantt.append({"id": "IDLE", "start": current_time, "end": current_time + 1, "duration": 1})
            current_time += 1
            continue

        best_pid = min(pool, key=lambda pid: (pcbs[pid]["priority"], pcbs[pid]["arrival_time"], pid))

        if best_pid != current_running:
            if current_running:
                pcbs[current_running]["state"] = "READY"
                if current_running not in ready_queue:
                    ready_queue.append(current_running)
                _record_event(
                    events, current_time, "PREEMPT", best_pid, ready_queue, [], pcbs,
                    f"At t={current_time}, {current_running} (prio={pcbs[current_running]['priority']}) preempted by higher priority {best_pid} (prio={pcbs[best_pid]['priority']}).",
                    gantt
                )

            current_running = best_pid
            if current_running in ready_queue:
                ready_queue.remove(current_running)
            pcbs[current_running]["state"] = "RUNNING"
            if pcbs[current_running]["start_time"] is None:
                pcbs[current_running]["start_time"] = current_time

            _record_event(
                events, current_time, "DISPATCH", current_running, ready_queue, [], pcbs,
                f"At t={current_time}, {current_running} selected (highest priority: {pcbs[current_running]['priority']}).",
                gantt
            )

        if gantt and gantt[-1]["id"] == current_running:
            gantt[-1]["end"] += 1
            gantt[-1]["duration"] += 1
        else:
            gantt.append({"id": current_running, "start": current_time, "end": current_time + 1, "duration": 1})

        pcbs[current_running]["remaining_burst"] -= 1
        busy_time += 1
        current_time += 1

        if pcbs[current_running]["remaining_burst"] == 0:
            pcbs[current_running]["state"] = "TERMINATED"
            pcbs[current_running]["completion_time"] = current_time
            completed_count += 1
            _record_event(
                events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
                f"{current_running} finished at t={current_time}.",
                gantt
            )
            current_running = None

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "PRIORITY_PREEMPTIVE",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_round_robin(procs: List[ProcessInput], time_quantum: int = 2) -> Dict[str, Any]:
    """Round Robin scheduling with configurable time quantum."""
    pcbs = _build_initial_pcbs(procs)
    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    current_time = 0
    ready_queue: List[str] = []
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    completed_count = 0
    n = len(procs)
    busy_time = 0

    while completed_count < n:
        # Check arrivals up to current_time
        arrived = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)
            _record_event(
                events, current_time, "ARRIVAL", None, ready_queue, [], pcbs,
                f"Process {p.id} arrived at t={current_time} and joined Round Robin ready queue.",
                gantt
            )

        if not ready_queue:
            next_arrival = min(p.arrival_time for p in unentered)
            gantt.append({"id": "IDLE", "start": current_time, "end": next_arrival, "duration": next_arrival - current_time})
            _record_event(
                events, current_time, "IDLE", "IDLE", [], [], pcbs,
                f"CPU idle from t={current_time} to t={next_arrival}.",
                gantt
            )
            current_time = next_arrival
            continue

        pid = ready_queue.pop(0)
        p_obj = pcbs[pid]
        p_obj["state"] = "RUNNING"
        if p_obj["start_time"] is None:
            p_obj["start_time"] = current_time

        execute_time = min(time_quantum, p_obj["remaining_burst"])
        _record_event(
            events, current_time, "DISPATCH", pid, ready_queue, [], pcbs,
            f"At t={current_time}, {pid} dispatched for up to quantum={time_quantum} (rem={p_obj['remaining_burst']}).",
            gantt
        )

        start = current_time
        current_time += execute_time
        p_obj["remaining_burst"] -= execute_time
        busy_time += execute_time
        gantt.append({"id": pid, "start": start, "end": current_time, "duration": execute_time})

        # Arrived during this slice must join ready queue BEFORE preempted pid
        arrived_during = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived_during:
            pcbs[p.id]["state"] = "READY"
            ready_queue.append(p.id)
            unentered.remove(p)

        if p_obj["remaining_burst"] == 0:
            p_obj["state"] = "TERMINATED"
            p_obj["completion_time"] = current_time
            completed_count += 1
            _record_event(
                events, current_time, "COMPLETION", None, ready_queue, [], pcbs,
                f"{pid} finished execution at t={current_time}.",
                gantt
            )
        else:
            # Quantum expired, re-queue at tail
            p_obj["state"] = "READY"
            ready_queue.append(pid)
            _record_event(
                events, current_time, "TIME_QUANTUM_EXPIRED", None, ready_queue, [], pcbs,
                f"Time quantum expired for {pid}. Re-queued at tail of Ready Queue (rem={p_obj['remaining_burst']}).",
                gantt
            )

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "ROUND_ROBIN",
        "time_quantum": time_quantum,
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }


def _simulate_mlfq(procs: List[ProcessInput], config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Multilevel Feedback Queue (MLFQ):
    Queue 0: Round Robin with quantum Q0 (highest priority)
    Queue 1: Round Robin with quantum Q1
    Queue 2: FCFS (lowest priority)
    Processes start in Q0. If they consume their full quantum without finishing, they demote.
    """
    q0_quantum = config_dict.get("q0_quantum", 2)
    q1_quantum = config_dict.get("q1_quantum", 4)

    pcbs = _build_initial_pcbs(procs)
    for p in pcbs.values():
        p["mlfq_level"] = 0

    events: List[Dict[str, Any]] = []
    gantt: List[Dict[str, Any]] = []

    q0: List[str] = []
    q1: List[str] = []
    q2: List[str] = []

    current_time = 0
    unentered = sorted(procs, key=lambda p: (p.arrival_time, p.id))
    completed_count = 0
    n = len(procs)
    busy_time = 0

    def get_ready_snapshot():
        return [f"{pid}(Q{pcbs[pid]['mlfq_level']})" for pid in (q0 + q1 + q2)]

    while completed_count < n:
        # Check arrivals
        arrived = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived:
            pcbs[p.id]["state"] = "READY"
            pcbs[p.id]["mlfq_level"] = 0
            q0.append(p.id)
            unentered.remove(p)
            _record_event(
                events, current_time, "ARRIVAL", None, get_ready_snapshot(), [], pcbs,
                f"Process {p.id} arrived at t={current_time} and entered MLFQ Queue 0 (Quantum={q0_quantum}).",
                gantt
            )

        if not q0 and not q1 and not q2:
            next_arrival = min(p.arrival_time for p in unentered)
            gantt.append({"id": "IDLE", "start": current_time, "end": next_arrival, "duration": next_arrival - current_time})
            _record_event(
                events, current_time, "IDLE", "IDLE", [], [], pcbs,
                f"All MLFQ queues empty. CPU idle until t={next_arrival}.",
                gantt
            )
            current_time = next_arrival
            continue

        # Choose queue
        if q0:
            active_q = 0
            quantum = q0_quantum
            pid = q0.pop(0)
        elif q1:
            active_q = 1
            quantum = q1_quantum
            pid = q1.pop(0)
        else:
            active_q = 2
            quantum = pcbs[q2[0]]["remaining_burst"]  # FCFS run to completion unless preempted by higher arrival
            pid = q2.pop(0)

        p_obj = pcbs[pid]
        p_obj["state"] = "RUNNING"
        if p_obj["start_time"] is None:
            p_obj["start_time"] = current_time

        execute_time = min(quantum, p_obj["remaining_burst"])

        # Check if any new process arrives during execution that could preempt (if active_q > 0)
        if active_q > 0:
            earliest_new = [p.arrival_time for p in unentered if current_time < p.arrival_time < current_time + execute_time]
            if earliest_new:
                execute_time = min(earliest_new) - current_time

        _record_event(
            events, current_time, "DISPATCH", pid, get_ready_snapshot(), [], pcbs,
            f"At t={current_time}, {pid} dispatched from Queue {active_q} (quantum={quantum}, rem={p_obj['remaining_burst']}).",
            gantt
        )

        start = current_time
        current_time += execute_time
        p_obj["remaining_burst"] -= execute_time
        busy_time += execute_time
        gantt.append({"id": pid, "start": start, "end": current_time, "duration": execute_time})

        # Process arrivals during this slice
        arrived_during = [p for p in unentered if p.arrival_time <= current_time]
        for p in arrived_during:
            pcbs[p.id]["state"] = "READY"
            pcbs[p.id]["mlfq_level"] = 0
            q0.append(p.id)
            unentered.remove(p)

        if p_obj["remaining_burst"] == 0:
            p_obj["state"] = "TERMINATED"
            p_obj["completion_time"] = current_time
            completed_count += 1
            _record_event(
                events, current_time, "COMPLETION", None, get_ready_snapshot(), [], pcbs,
                f"{pid} finished at t={current_time}.",
                gantt
            )
        else:
            # Demote if full quantum used
            if execute_time == quantum and active_q < 2:
                p_obj["mlfq_level"] = active_q + 1
                if p_obj["mlfq_level"] == 1:
                    q1.append(pid)
                else:
                    q2.append(pid)
                p_obj["state"] = "READY"
                _record_event(
                    events, current_time, "DEMOTION", None, get_ready_snapshot(), [], pcbs,
                    f"{pid} consumed full Queue {active_q} quantum and is demoted to Queue {p_obj['mlfq_level']}.",
                    gantt
                )
            else:
                # Re-queue in current queue
                if active_q == 0:
                    q0.append(pid)
                elif active_q == 1:
                    q1.append(pid)
                else:
                    q2.append(pid)
                p_obj["state"] = "READY"

    metrics = _calculate_final_metrics(pcbs, current_time, busy_time)
    return {
        "algorithm": "MLFQ",
        "events": events,
        "gantt": gantt,
        "metrics": metrics,
    }
