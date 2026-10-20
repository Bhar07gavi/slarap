"""
SLARAP Educational OS Simulation Engine - Deadlock Lab.

Provides:
1. Resource Allocation Graph (RAG) modeling and cycle detection.
2. The Four Necessary Coffman Deadlock Conditions Analyzer.
3. Banker's Algorithm:
   - Safety Algorithm (step-by-step state verification with work & finish vectors)
   - Resource-Request Algorithm
4. Deadlock Detection Algorithm (for systems with multiple instances of each resource type).
5. Deadlock Recovery strategies (Process termination, Resource preemption).
"""

from typing import Any, Dict, List, Optional, Tuple
import copy


def analyze_coffman_conditions(
    mutual_exclusion: bool = True,
    hold_and_wait: bool = True,
    no_preemption: bool = True,
    circular_wait: bool = True,
) -> Dict[str, Any]:
    """
    Evaluates whether a system can deadlock based on Coffman's 4 conditions.
    Deadlock can arise if and only if ALL four conditions hold simultaneously.
    """
    conditions = [
        {
            "name": "Mutual Exclusion",
            "present": mutual_exclusion,
            "description": "At least one resource must be held in a non-shareable mode.",
            "prevention_strategy": "Spooling or make resources shareable (e.g. read-only files).",
        },
        {
            "name": "Hold and Wait",
            "present": hold_and_wait,
            "description": "A process must be holding at least one resource and waiting to acquire additional resources.",
            "prevention_strategy": "Require processes to request all resources at once, or release held resources before requesting new ones.",
        },
        {
            "name": "No Preemption",
            "present": no_preemption,
            "description": "Resources cannot be preempted; they can only be released voluntarily by the process holding them.",
            "prevention_strategy": "If a process holding resources requests another that cannot be immediately allocated, preempt its held resources.",
        },
        {
            "name": "Circular Wait",
            "present": circular_wait,
            "description": "A closed chain of processes exists such that each process holds at least one resource needed by the next.",
            "prevention_strategy": "Impose a strict global ordering of all resource types; require processes to request resources in strictly increasing order.",
        },
    ]

    can_deadlock = all(c["present"] for c in conditions)

    return {
        "conditions": conditions,
        "deadlock_possible": can_deadlock,
        "explanation": (
            "All 4 Coffman conditions are PRESENT. Deadlock is POSSIBLE in this system!"
            if can_deadlock
            else "At least one Coffman condition is BROKEN. Deadlock is PREVENTED!"
        ),
    }


def analyze_rag(
    processes: List[str],
    resources: Dict[str, int],  # resource_name -> instance count
    allocations: List[Dict[str, Any]],  # [{process, resource, count}]
    requests: List[Dict[str, Any]],     # [{process, resource, count}]
) -> Dict[str, Any]:
    """
    Analyzes a Resource Allocation Graph (RAG) for cycles and deadlocks.
    For single-instance resources, a cycle implies a deadlock.
    For multi-instance resources, a cycle is a necessary but not sufficient condition.
    """
    # Build adjacency graph
    nodes = list(processes) + list(resources.keys())
    adj: Dict[str, List[str]] = {n: [] for n in nodes}

    # Allocation edges: Resource -> Process
    for alloc in allocations:
        p = alloc["process"]
        r = alloc["resource"]
        if r in adj and p in nodes:
            adj[r].append(p)

    # Request edges: Process -> Resource
    for req in requests:
        p = req["process"]
        r = req["resource"]
        if p in adj and r in nodes:
            adj[p].append(r)

    # Detect cycle using DFS
    visited: Dict[str, int] = {n: 0 for n in nodes}  # 0=unvisited, 1=visiting, 2=visited
    cycle_nodes: List[str] = []
    has_cycle = False

    def dfs(u: str, path: List[str]) -> bool:
        visited[u] = 1
        path.append(u)
        for v in adj.get(u, []):
            if visited[v] == 1:
                idx = path.index(v)
                cycle_nodes.extend(path[idx:] + [v])
                return True
            if visited[v] == 0:
                if dfs(v, path):
                    return True
        path.pop()
        visited[u] = 2
        return False

    for node in nodes:
        if visited[node] == 0:
            if dfs(node, []):
                has_cycle = True
                break

    all_single_instance = all(cnt == 1 for cnt in resources.values())
    deadlock_detected = False
    if has_cycle:
        if all_single_instance:
            deadlock_detected = True
            verdict = "Deadlock Detected! Since all resources have single instances, the cycle implies deadlock."
        else:
            verdict = "Cycle detected in multi-instance RAG. Run Banker's/Deadlock Detection algorithm to verify if deadlock exists."
    else:
        verdict = "No cycles detected in Resource Allocation Graph. The system is DEADLOCK-FREE."

    return {
        "nodes": nodes,
        "processes": processes,
        "resources": resources,
        "allocations": allocations,
        "requests": requests,
        "has_cycle": has_cycle,
        "cycle_path": cycle_nodes if has_cycle else [],
        "deadlock_detected": deadlock_detected,
        "verdict": verdict,
    }


def bankers_safety_algorithm(
    available: List[int],
    allocation: List[List[int]],
    max_matrix: List[List[int]],
    process_names: Optional[List[str]] = None,
    resource_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Dijkstra's Banker's Algorithm for Deadlock Avoidance.
    Returns:
    - Need matrix
    - Step-by-step trace of the Safety Algorithm
    - Safe sequence (if one exists) or reason why system is unsafe
    """
    n = len(allocation)  # Number of processes
    m = len(available)   # Number of resource types

    p_names = process_names or [f"P{i}" for i in range(n)]
    r_names = resource_names or [f"R{j}" for j in range(m)]

    # 1. Compute Need Matrix = Max - Allocation
    need: List[List[int]] = []
    for i in range(n):
        row = []
        for j in range(m):
            val = max_matrix[i][j] - allocation[i][j]
            if val < 0:
                raise ValueError(f"Max matrix cannot be smaller than Allocation matrix for process {p_names[i]}")
            row.append(val)
        need.append(row)

    # 2. Safety Algorithm
    work = list(available)
    finish = [False] * n
    safe_sequence: List[str] = []
    steps: List[Dict[str, Any]] = []

    step_num = 0
    while len(safe_sequence) < n:
        found = False
        for i in range(n):
            if not finish[i]:
                # Check if Need[i] <= Work
                can_allocate = all(need[i][j] <= work[j] for j in range(m))
                if can_allocate:
                    step_num += 1
                    old_work = list(work)
                    # Work = Work + Allocation[i]
                    for j in range(m):
                        work[j] += allocation[i][j]
                    finish[i] = True
                    safe_sequence.append(p_names[i])
                    found = True

                    steps.append({
                        "step": step_num,
                        "process": p_names[i],
                        "need": list(need[i]),
                        "work_before": old_work,
                        "allocation": list(allocation[i]),
                        "work_after": list(work),
                        "explanation": (
                            f"{p_names[i]} can satisfy its needs (Need={need[i]} <= Work={old_work}). "
                            f"{p_names[i]} finishes and releases Allocation={allocation[i]}, giving new Work={work}."
                        ),
                        "safe_sequence_so_far": list(safe_sequence),
                    })
                    break

        if not found:
            # Cannot find any process that can finish
            break

    is_safe = (len(safe_sequence) == n)
    deadlocked_processes = [p_names[i] for i in range(n) if not finish[i]]

    return {
        "is_safe": is_safe,
        "safe_sequence": safe_sequence if is_safe else [],
        "need_matrix": need,
        "allocation_matrix": allocation,
        "max_matrix": max_matrix,
        "available": available,
        "process_names": p_names,
        "resource_names": r_names,
        "steps": steps,
        "deadlocked_processes": deadlocked_processes,
        "verdict": (
            f"SAFE STATE: System is in a safe state with safe sequence: <{' -> '.join(safe_sequence)}>"
            if is_safe
            else f"UNSAFE STATE: Deadlock or potential deadlock detected! Processes {deadlocked_processes} cannot finish."
        ),
    }


def bankers_resource_request(
    available: List[int],
    allocation: List[List[int]],
    max_matrix: List[List[int]],
    process_index: int,
    request: List[int],
    process_names: Optional[List[str]] = None,
    resource_names: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Banker's Resource Request Algorithm.
    Evaluates if granting a request keeps the system in a safe state.
    """
    n = len(allocation)
    m = len(available)
    p_names = process_names or [f"P{i}" for i in range(n)]
    r_names = resource_names or [f"R{j}" for j in range(m)]

    # Compute need
    need = [
        [max_matrix[i][j] - allocation[i][j] for j in range(m)]
        for i in range(n)
    ]

    p_name = p_names[process_index]

    # Condition 1: Request <= Need
    for j in range(m):
        if request[j] > need[process_index][j]:
            return {
                "granted": False,
                "error": f"Error: Process {p_name} exceeded its maximum claim! Request {request[j]} > Need {need[process_index][j]} for {r_names[j]}.",
            }

    # Condition 2: Request <= Available
    for j in range(m):
        if request[j] > available[j]:
            return {
                "granted": False,
                "error": f"Process {p_name} must wait: Request {request[j]} > Available {available[j]} for {r_names[j]}.",
            }

    # Hypothetical Allocation
    hypo_avail = list(available)
    hypo_alloc = copy.deepcopy(allocation)
    hypo_max = copy.deepcopy(max_matrix)

    for j in range(m):
        hypo_avail[j] -= request[j]
        hypo_alloc[process_index][j] += request[j]

    # Test safety
    safety_result = bankers_safety_algorithm(
        available=hypo_avail,
        allocation=hypo_alloc,
        max_matrix=hypo_max,
        process_names=p_names,
        resource_names=r_names,
    )

    if safety_result["is_safe"]:
        return {
            "granted": True,
            "message": f"Request GRANTED! System remains in a safe state with sequence <{' -> '.join(safety_result['safe_sequence'])}>.",
            "new_available": hypo_avail,
            "new_allocation": hypo_alloc,
            "safety_result": safety_result,
        }
    else:
        return {
            "granted": False,
            "message": f"Request DENIED! Granting this request would transition the system into an UNSAFE state.",
            "safety_result": safety_result,
        }
