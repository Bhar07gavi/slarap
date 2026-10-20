"""
SLARAP Educational OS Simulation Engine - Disk Scheduling Lab.

Implements all 6 standard disk arm scheduling algorithms:
1. FCFS (First-Come, First-Served)
2. SSTF (Shortest Seek Time First)
3. SCAN (Elevator Algorithm to boundary)
4. C-SCAN (Circular SCAN to boundary)
5. LOOK (Elevator to furthest request)
6. C-LOOK (Circular LOOK to furthest request)

Calculates seek paths, step-by-step head movements, total head displacement,
and gives exact algorithmic rationales for every movement.
"""

from typing import Any, Dict, List, Optional
import copy


def simulate_disk_scheduling(
    algorithm: str,
    requests: List[int],
    initial_head: int = 53,
    disk_size: int = 200,  # Cylinders 0 to disk_size - 1
    direction: str = "UP",  # "UP" (towards higher cylinders) or "DOWN" (towards 0)
) -> Dict[str, Any]:
    """
    Main entry point for disk scheduling.
    """
    if not requests:
        return {
            "algorithm": algorithm,
            "initial_head": initial_head,
            "requests": [],
            "seek_sequence": [initial_head],
            "movements": [],
            "total_head_movement": 0,
            "steps": [],
        }

    alg_upper = algorithm.upper().replace("-", "_").replace(" ", "_")
    dir_upper = "UP" if direction.upper() in ("UP", "RIGHT", "HIGH", "HIGHER") else "DOWN"

    if alg_upper == "FCFS":
        return _simulate_fcfs(requests, initial_head)
    elif alg_upper == "SSTF":
        return _simulate_sstf(requests, initial_head)
    elif alg_upper == "SCAN":
        return _simulate_scan(requests, initial_head, disk_size, dir_upper)
    elif alg_upper == "C_SCAN":
        return _simulate_cscan(requests, initial_head, disk_size, dir_upper)
    elif alg_upper == "LOOK":
        return _simulate_look(requests, initial_head, dir_upper)
    elif alg_upper == "C_LOOK":
        return _simulate_clook(requests, initial_head, dir_upper)
    else:
        raise ValueError(f"Unsupported disk scheduling algorithm: {algorithm}")


def _build_result(
    algorithm: str,
    initial_head: int,
    seek_sequence: List[int],
    explanations: List[str],
) -> Dict[str, Any]:
    steps = []
    total_movement = 0
    movements = []

    for i in range(len(seek_sequence) - 1):
        from_cyl = seek_sequence[i]
        to_cyl = seek_sequence[i + 1]
        distance = abs(to_cyl - from_cyl)
        total_movement += distance
        movements.append(distance)

        steps.append({
            "step": i + 1,
            "from_cylinder": from_cyl,
            "to_cylinder": to_cyl,
            "distance": distance,
            "cumulative_movement": total_movement,
            "explanation": explanations[i] if i < len(explanations) else f"Move from {from_cyl} to {to_cyl} (Seek: {distance}).",
        })

    return {
        "algorithm": algorithm,
        "initial_head": initial_head,
        "seek_sequence": seek_sequence,
        "movements": movements,
        "total_head_movement": total_movement,
        "average_seek_length": round(total_movement / max(1, len(seek_sequence) - 1), 2),
        "steps": steps,
    }


def _simulate_fcfs(requests: List[int], initial_head: int) -> Dict[str, Any]:
    seek_sequence = [initial_head] + list(requests)
    explanations = [
        f"FCFS order: Servicing request at cylinder {cyl} as submitted in queue."
        for cyl in requests
    ]
    return _build_result("FCFS", initial_head, seek_sequence, explanations)


def _simulate_sstf(requests: List[int], initial_head: int) -> Dict[str, Any]:
    current = initial_head
    pending = list(requests)
    seek_sequence = [initial_head]
    explanations = []

    while pending:
        # Pick cylinder with minimal distance to current
        closest = min(pending, key=lambda c: (abs(c - current), c))
        dist = abs(closest - current)
        explanations.append(
            f"SSTF: Selected cylinder {closest} because it has shortest seek distance ({dist}) from current head ({current})."
        )
        seek_sequence.append(closest)
        pending.remove(closest)
        current = closest

    return _build_result("SSTF", initial_head, seek_sequence, explanations)


def _simulate_scan(
    requests: List[int], initial_head: int, disk_size: int, direction: str
) -> Dict[str, Any]:
    """Elevator algorithm: sweeps to disk boundary (0 or disk_size-1), then reverses."""
    below = sorted([c for c in requests if c < initial_head])
    above = sorted([c for c in requests if c >= initial_head])
    max_cyl = disk_size - 1

    seek_sequence = [initial_head]
    explanations = []

    if direction == "UP":
        # Service above, then go to max_cyl boundary, then reverse and service below descending
        for c in above:
            seek_sequence.append(c)
            explanations.append(f"SCAN (UP): Servicing cylinder {c} on upward sweep.")
        if below:  # Only touch boundary if we need to reverse to service requests below
            seek_sequence.append(max_cyl)
            explanations.append(f"SCAN (UP): Reached upper disk boundary {max_cyl}. Reversing direction to DOWN.")
            for c in reversed(below):
                seek_sequence.append(c)
                explanations.append(f"SCAN (DOWN): Servicing cylinder {c} on downward sweep.")
    else:
        # Service below descending, touch 0 boundary, reverse and service above ascending
        for c in reversed(below):
            seek_sequence.append(c)
            explanations.append(f"SCAN (DOWN): Servicing cylinder {c} on downward sweep.")
        if above:
            seek_sequence.append(0)
            explanations.append("SCAN (DOWN): Reached lower disk boundary 0. Reversing direction to UP.")
            for c in above:
                seek_sequence.append(c)
                explanations.append(f"SCAN (UP): Servicing cylinder {c} on upward sweep.")

    return _build_result("SCAN", initial_head, seek_sequence, explanations)


def _simulate_cscan(
    requests: List[int], initial_head: int, disk_size: int, direction: str
) -> Dict[str, Any]:
    """Circular SCAN: sweeps in one direction to boundary, resets to opposite boundary without servicing, then continues."""
    below = sorted([c for c in requests if c < initial_head])
    above = sorted([c for c in requests if c >= initial_head])
    max_cyl = disk_size - 1

    seek_sequence = [initial_head]
    explanations = []

    if direction == "UP":
        for c in above:
            seek_sequence.append(c)
            explanations.append(f"C-SCAN (UP): Servicing cylinder {c} on forward sweep.")
        if below:
            seek_sequence.append(max_cyl)
            explanations.append(f"C-SCAN (UP): Reached upper boundary {max_cyl}.")
            seek_sequence.append(0)
            explanations.append("C-SCAN: Jumped straight back to beginning (cylinder 0) without servicing.")
            for c in below:
                seek_sequence.append(c)
                explanations.append(f"C-SCAN (UP): Servicing cylinder {c} after circular wrap-around.")
    else:
        for c in reversed(below):
            seek_sequence.append(c)
            explanations.append(f"C-SCAN (DOWN): Servicing cylinder {c} on downward sweep.")
        if above:
            seek_sequence.append(0)
            explanations.append("C-SCAN (DOWN): Reached lower boundary 0.")
            seek_sequence.append(max_cyl)
            explanations.append(f"C-SCAN: Jumped straight back to cylinder {max_cyl} without servicing.")
            for c in reversed(above):
                seek_sequence.append(c)
                explanations.append(f"C-SCAN (DOWN): Servicing cylinder {c} after circular wrap-around.")

    return _build_result("C-SCAN", initial_head, seek_sequence, explanations)


def _simulate_look(
    requests: List[int], initial_head: int, direction: str
) -> Dict[str, Any]:
    """LOOK: Elevator algorithm, but reverses at furthest request without touching cylinder 0 or max_cyl."""
    below = sorted([c for c in requests if c < initial_head])
    above = sorted([c for c in requests if c >= initial_head])

    seek_sequence = [initial_head]
    explanations = []

    if direction == "UP":
        for c in above:
            seek_sequence.append(c)
            explanations.append(f"LOOK (UP): Servicing cylinder {c}.")
        for c in reversed(below):
            seek_sequence.append(c)
            explanations.append(f"LOOK: Reached furthest upward request; reversed to DOWN to service {c}.")
    else:
        for c in reversed(below):
            seek_sequence.append(c)
            explanations.append(f"LOOK (DOWN): Servicing cylinder {c}.")
        for c in above:
            seek_sequence.append(c)
            explanations.append(f"LOOK: Reached furthest downward request; reversed to UP to service {c}.")

    return _build_result("LOOK", initial_head, seek_sequence, explanations)


def _simulate_clook(
    requests: List[int], initial_head: int, direction: str
) -> Dict[str, Any]:
    """C-LOOK: Circular LOOK, jumps from furthest request in sweep directly to lowest/highest request without touching boundary."""
    below = sorted([c for c in requests if c < initial_head])
    above = sorted([c for c in requests if c >= initial_head])

    seek_sequence = [initial_head]
    explanations = []

    if direction == "UP":
        for c in above:
            seek_sequence.append(c)
            explanations.append(f"C-LOOK (UP): Servicing cylinder {c}.")
        if below:
            # Jump to lowest request
            seek_sequence.append(below[0])
            explanations.append(f"C-LOOK: Reached furthest upward request. Jumped directly to lowest pending request {below[0]} without servicing.")
            for c in below[1:]:
                seek_sequence.append(c)
                explanations.append(f"C-LOOK (UP): Servicing cylinder {c}.")
    else:
        for c in reversed(below):
            seek_sequence.append(c)
            explanations.append(f"C-LOOK (DOWN): Servicing cylinder {c}.")
        if above:
            seek_sequence.append(above[-1])
            explanations.append(f"C-LOOK: Reached lowest downward request. Jumped directly to highest pending request {above[-1]} without servicing.")
            for c in reversed(above[:-1]):
                seek_sequence.append(c)
                explanations.append(f"C-LOOK (DOWN): Servicing cylinder {c}.")

    return _build_result("C-LOOK", initial_head, seek_sequence, explanations)


def compare_all_disk_algorithms(
    requests: List[int],
    initial_head: int = 53,
    disk_size: int = 200,
    direction: str = "UP",
) -> List[Dict[str, Any]]:
    """Compares all 6 disk scheduling algorithms on the exact same input."""
    algorithms = ["FCFS", "SSTF", "SCAN", "C_SCAN", "LOOK", "C_LOOK"]
    results = []
    for alg in algorithms:
        res = simulate_disk_scheduling(alg, requests, initial_head, disk_size, direction)
        results.append({
            "algorithm": res["algorithm"],
            "total_head_movement": res["total_head_movement"],
            "average_seek_length": res["average_seek_length"],
            "seek_sequence": res["seek_sequence"],
        })
    results.sort(key=lambda r: r["total_head_movement"])
    return results
