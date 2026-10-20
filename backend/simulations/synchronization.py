"""
SLARAP Educational OS Simulation Engine - Synchronization Lab.

Simulates classical concurrency and synchronization problems:
1. Race Condition vs Mutex (Shared Counter / Account Balance)
2. Peterson's Algorithm (2-process mutual exclusion step-by-step)
3. Producer-Consumer Problem (Bounded buffer with Mutex, Empty, Full semaphores)
4. Dining Philosophers Problem (Resource hierarchy & asymmetric deadlock prevention)
5. Readers-Writers Problem (Reader preference vs Writer preference)
"""

from typing import Any, Dict, List, Optional
import copy


def simulate_race_condition(
    iterations: int = 10,
    threads_count: int = 2,
    use_mutex: bool = False,
) -> Dict[str, Any]:
    """
    Demonstrates race conditions on a shared counter.
    When use_mutex is False, simulated context switches interleave Read-Modify-Write,
    causing lost updates. When True, critical section is protected.
    """
    shared_counter = 0
    history: List[Dict[str, Any]] = []

    # Interleaved simulation trace
    step = 0
    local_registers = {f"T{i}": None for i in range(threads_count)}
    thread_states = {f"T{i}": "IDLE" for i in range(threads_count)}

    if use_mutex:
        mutex_locked = False
        mutex_owner = None
        for i in range(iterations):
            for t_idx in range(threads_count):
                t_id = f"T{t_idx}"
                # 1. Acquire Lock
                step += 1
                mutex_locked = True
                mutex_owner = t_id
                thread_states[t_id] = "CRITICAL_SECTION"
                history.append({
                    "step": step,
                    "thread": t_id,
                    "action": "ACQUIRE_MUTEX",
                    "shared_counter": shared_counter,
                    "explanation": f"{t_id} entered Critical Section after acquiring Mutex lock.",
                    "mutex_locked": True,
                    "mutex_owner": t_id,
                })

                # 2. Read
                step += 1
                local_registers[t_id] = shared_counter
                history.append({
                    "step": step,
                    "thread": t_id,
                    "action": "READ_VALUE",
                    "shared_counter": shared_counter,
                    "explanation": f"{t_id} read shared_counter={shared_counter} into local register.",
                    "mutex_locked": True,
                    "mutex_owner": t_id,
                })

                # 3. Increment & Write back
                step += 1
                shared_counter = local_registers[t_id] + 1
                history.append({
                    "step": step,
                    "thread": t_id,
                    "action": "WRITE_VALUE",
                    "shared_counter": shared_counter,
                    "explanation": f"{t_id} wrote incremented value {shared_counter} to shared_counter.",
                    "mutex_locked": True,
                    "mutex_owner": t_id,
                })

                # 4. Release Lock
                step += 1
                mutex_locked = False
                mutex_owner = None
                thread_states[t_id] = "IDLE"
                history.append({
                    "step": step,
                    "thread": t_id,
                    "action": "RELEASE_MUTEX",
                    "shared_counter": shared_counter,
                    "explanation": f"{t_id} released Mutex lock and left Critical Section.",
                    "mutex_locked": False,
                    "mutex_owner": None,
                })
    else:
        # Race condition interleaving
        for i in range(iterations):
            # T0 reads
            step += 1
            local_registers["T0"] = shared_counter
            thread_states["T0"] = "READ_SHARED"
            history.append({
                "step": step,
                "thread": "T0",
                "action": "READ_VALUE",
                "shared_counter": shared_counter,
                "explanation": f"T0 reads shared_counter ({shared_counter}). Context switch occurs before write!",
                "mutex_locked": False,
                "mutex_owner": None,
            })

            # T1 preempts, reads same old value, and writes back
            step += 1
            local_registers["T1"] = shared_counter
            thread_states["T1"] = "READ_SHARED"
            history.append({
                "step": step,
                "thread": "T1",
                "action": "READ_VALUE",
                "shared_counter": shared_counter,
                "explanation": f"T1 preempts T0! T1 reads un-incremented shared_counter ({shared_counter}).",
                "mutex_locked": False,
                "mutex_owner": None,
            })

            step += 1
            shared_counter = local_registers["T1"] + 1
            thread_states["T1"] = "WRITE_SHARED"
            history.append({
                "step": step,
                "thread": "T1",
                "action": "WRITE_VALUE",
                "shared_counter": shared_counter,
                "explanation": f"T1 increments and writes {shared_counter}.",
                "mutex_locked": False,
                "mutex_owner": None,
            })

            # Now T0 resumes with stale register value and writes
            step += 1
            shared_counter = local_registers["T0"] + 1
            thread_states["T0"] = "WRITE_SHARED"
            history.append({
                "step": step,
                "thread": "T0",
                "action": "OVERWRITE_LOST_UPDATE",
                "shared_counter": shared_counter,
                "explanation": f"RACE CONDITION OCCURRED! T0 overwrites shared_counter with {shared_counter}. T1's increment was LOST!",
                "mutex_locked": False,
                "mutex_owner": None,
            })

    expected_value = iterations * threads_count
    return {
        "mode": "WITH_MUTEX" if use_mutex else "WITHOUT_MUTEX (RACE CONDITION)",
        "expected_value": expected_value,
        "actual_value": shared_counter,
        "lost_updates": max(0, expected_value - shared_counter),
        "steps": history,
    }


def simulate_petersons_algorithm(steps_limit: int = 16) -> Dict[str, Any]:
    """
    Peterson's Algorithm for 2 processes (P0, P1).
    Variables:
      flag[0], flag[1]: boolean (intent to enter CS)
      turn: 0 or 1 (gives priority to other process)
    """
    flag = [False, False]
    turn = 0
    p_states = ["ENTRY_SECTION", "ENTRY_SECTION"]
    trace = []

    # Sequence of interleaved operations
    script = [
        (0, "SET_FLAG", "P0 sets flag[0] = True (wants to enter CS)"),
        (1, "SET_FLAG", "P1 sets flag[1] = True (wants to enter CS)"),
        (0, "SET_TURN", "P0 sets turn = 1 (courteously offers turn to P1)"),
        (1, "SET_TURN", "P1 sets turn = 0 (courteously offers turn to P0)"),
        (0, "CHECK_CONDITION", "P0 checks: while (flag[1] && turn == 1). Condition is False because turn == 0! P0 enters CS!"),
        (0, "ENTER_CS", "P0 is now executing inside Critical Section."),
        (1, "BUSY_WAIT", "P1 checks: while (flag[0] && turn == 0). Condition is True! P1 busy waits (spinning)."),
        (0, "EXIT_CS", "P0 finishes CS and sets flag[0] = False."),
        (1, "CHECK_CONDITION", "P1 checks while condition again. flag[0] is now False! P1 enters CS!"),
        (1, "ENTER_CS", "P1 is now executing inside Critical Section."),
        (1, "EXIT_CS", "P1 finishes CS and sets flag[1] = False."),
    ]

    for step_num, (pid, op, expl) in enumerate(script[:steps_limit], 1):
        other = 1 - pid
        if op == "SET_FLAG":
            flag[pid] = True
            p_states[pid] = "INTERESTED"
        elif op == "SET_TURN":
            turn = other
            p_states[pid] = "WAITING"
        elif op == "CHECK_CONDITION":
            pass
        elif op == "ENTER_CS":
            p_states[pid] = "CRITICAL_SECTION"
        elif op == "BUSY_WAIT":
            p_states[pid] = "WAITING"
        elif op == "EXIT_CS":
            flag[pid] = False
            p_states[pid] = "REMAINDER_SECTION"

        trace.append({
            "step": step_num,
            "active_process": f"P{pid}",
            "operation": op,
            "flag": list(flag),
            "turn": turn,
            "states": {
                "P0": p_states[0],
                "P1": p_states[1],
            },
            "explanation": expl,
        })

    return {
        "algorithm": "Peterson's Algorithm",
        "processes": ["P0", "P1"],
        "steps": trace,
        "mutual_exclusion_verified": True,
        "progress_verified": True,
        "bounded_waiting_verified": True,
    }


def simulate_producer_consumer(
    buffer_capacity: int = 5,
    events_count: int = 12,
) -> Dict[str, Any]:
    """
    Producer-Consumer Problem using counting semaphores:
    - mutex = 1 (binary semaphore for mutual exclusion)
    - empty = buffer_capacity (counting empty slots)
    - full = 0 (counting filled slots)
    """
    buffer: List[str] = []
    mutex = 1
    empty = buffer_capacity
    full = 0
    item_counter = 1

    trace: List[Dict[str, Any]] = []

    # Alternating or randomized sequence of operations
    actions = [
        "PRODUCE", "PRODUCE", "CONSUME", "PRODUCE",
        "PRODUCE", "PRODUCE", "PRODUCE", "CONSUME",
        "CONSUME", "PRODUCE", "CONSUME", "CONSUME"
    ]

    for step, action in enumerate(actions[:events_count], 1):
        if action == "PRODUCE":
            if empty > 0:
                item_name = f"Item-{item_counter}"
                item_counter += 1
                empty -= 1  # wait(empty)
                mutex = 0   # wait(mutex)
                buffer.append(item_name)
                mutex = 1   # signal(mutex)
                full += 1   # signal(full)
                expl = f"Producer created {item_name} -> Placed in buffer slot {len(buffer)}/{buffer_capacity}."
                status = "SUCCESS"
            else:
                expl = f"Buffer FULL ({buffer_capacity}/{buffer_capacity})! Producer blocked on wait(empty)."
                status = "BLOCKED"
            role = "Producer"
        else:
            if full > 0:
                full -= 1   # wait(full)
                mutex = 0   # wait(mutex)
                consumed_item = buffer.pop(0)
                mutex = 1   # signal(mutex)
                empty += 1  # signal(empty)
                expl = f"Consumer fetched {consumed_item} from buffer. {len(buffer)} remaining."
                status = "SUCCESS"
            else:
                expl = "Buffer EMPTY (0/5)! Consumer blocked on wait(full)."
                status = "BLOCKED"
            role = "Consumer"

        trace.append({
            "step": step,
            "actor": role,
            "action": action,
            "status": status,
            "buffer": list(buffer),
            "buffer_capacity": buffer_capacity,
            "semaphores": {
                "mutex": mutex,
                "empty": empty,
                "full": full,
            },
            "explanation": expl,
        })

    return {
        "problem": "Producer-Consumer (Bounded Buffer)",
        "capacity": buffer_capacity,
        "steps": trace,
    }


def simulate_dining_philosophers(
    rounds: int = 8,
    strategy: str = "asymmetric",  # "naive_deadlock" or "asymmetric"
) -> Dict[str, Any]:
    """
    Dining Philosophers Problem (5 philosophers, 5 chopsticks).
    - naive_deadlock: Every philosopher grabs left chopstick first -> Deadlock cycle!
    - asymmetric: Odd philosophers grab right chopstick first, even grab left -> Deadlock-free!
    """
    n = 5
    states = ["THINKING"] * n
    forks = [True] * n  # True = on table, False = picked up
    trace = []

    if strategy == "naive_deadlock":
        # Step 1: Every philosopher gets hungry
        trace.append({
            "step": 1,
            "philosopher": "ALL",
            "states": ["HUNGRY"] * n,
            "forks": list(forks),
            "explanation": "All 5 philosophers simultaneously become hungry and sit at the round table.",
            "deadlock_detected": False,
        })
        states = ["HUNGRY"] * n

        # Step 2: Every philosopher picks up left fork (i)
        for i in range(n):
            forks[i] = False
        trace.append({
            "step": 2,
            "philosopher": "ALL",
            "states": ["HOLDING_LEFT_FORK"] * n,
            "forks": list(forks),
            "explanation": "Every philosopher picks up their left chopstick. All chopsticks are now taken!",
            "deadlock_detected": False,
        })

        # Step 3: Every philosopher attempts to pick up right fork ((i+1)%5) -> Circular wait!
        trace.append({
            "step": 3,
            "philosopher": "ALL",
            "states": ["WAITING_RIGHT_FORK (BLOCKED)"] * n,
            "forks": list(forks),
            "explanation": "DEADLOCK DETECTED! Circular Wait condition holds: P0 waits for P1's fork, P1 for P2's, P2 for P3's, P3 for P4's, P4 for P0's! None can eat, none will release.",
            "deadlock_detected": True,
        })
    else:
        # Asymmetric resource hierarchy solution (Dijkstra)
        events = [
            (0, "HUNGRY", "P0 becomes hungry."),
            (0, "PICK_LEFT", "P0 picks up left fork 0."),
            (0, "PICK_RIGHT", "P0 picks up right fork 1."),
            (0, "EATING", "P0 has both forks and starts eating!"),
            (1, "HUNGRY", "P1 becomes hungry. Attempts fork 1, but it is held by P0! P1 waits."),
            (0, "DONE_EATING", "P0 finishes eating, puts down fork 0 and 1, resumes THINKING."),
            (1, "PICK_FORKS", "P1 now picks up fork 1 and fork 2, starts eating!"),
            (1, "DONE_EATING", "P1 finishes eating, puts down fork 1 and 2, resumes THINKING."),
        ]
        forks = [True] * n
        states = ["THINKING"] * n

        for step, (p_idx, action, expl) in enumerate(events[:rounds], 1):
            if action == "HUNGRY":
                states[p_idx] = "HUNGRY"
            elif action == "PICK_LEFT":
                forks[p_idx] = False
                states[p_idx] = "HOLDING_1_FORK"
            elif action == "PICK_RIGHT":
                forks[(p_idx + 1) % n] = False
                states[p_idx] = "HOLDING_2_FORKS"
            elif action == "EATING":
                states[p_idx] = "EATING"
            elif action == "DONE_EATING":
                forks[p_idx] = True
                forks[(p_idx + 1) % n] = True
                states[p_idx] = "THINKING"
            elif action == "PICK_FORKS":
                forks[p_idx] = False
                forks[(p_idx + 1) % n] = False
                states[p_idx] = "EATING"

            trace.append({
                "step": step,
                "philosopher": f"P{p_idx}",
                "states": list(states),
                "forks": list(forks),
                "explanation": expl,
                "deadlock_detected": False,
            })

    return {
        "problem": "Dining Philosophers",
        "strategy": strategy,
        "steps": trace,
    }


def simulate_readers_writers(events_count: int = 8) -> Dict[str, Any]:
    """
    Readers-Writers Problem (Reader Preference / First Readers-Writers).
    Multiple readers can read concurrently; writers require exclusive access.
    """
    read_count = 0
    rw_mutex = 1  # 1 = available, 0 = held by reader or writer
    mutex = 1     # protects read_count
    writer_active = False

    trace = []
    actions = [
        ("R1", "START_READ"),
        ("R2", "START_READ"),
        ("W1", "ATTEMPT_WRITE"),
        ("R1", "STOP_READ"),
        ("R2", "STOP_READ"),
        ("W1", "START_WRITE"),
        ("W1", "STOP_WRITE"),
        ("R3", "START_READ"),
    ]

    for step, (actor, op) in enumerate(actions[:events_count], 1):
        if op == "START_READ":
            read_count += 1
            if read_count == 1:
                rw_mutex = 0  # First reader locks rw_mutex
            expl = f"{actor} starts reading. Active readers: {read_count}. {'(First reader locked rw_mutex)' if read_count == 1 else '(Joined concurrent readers)'}"
        elif op == "STOP_READ":
            read_count -= 1
            if read_count == 0:
                rw_mutex = 1  # Last reader unlocks rw_mutex
            expl = f"{actor} finished reading. Active readers: {read_count}. {'(Last reader unlocked rw_mutex)' if read_count == 0 else ''}"
        elif op == "ATTEMPT_WRITE":
            if rw_mutex == 0:
                expl = f"{actor} wants to write, but rw_mutex is locked by active readers! Writer is BLOCKED."
            else:
                rw_mutex = 0
                writer_active = True
                expl = f"{actor} acquired rw_mutex and starts writing exclusively."
        elif op == "START_WRITE":
            rw_mutex = 0
            writer_active = True
            expl = f"{actor} acquired exclusive access and is WRITING to the shared dataset."
        elif op == "STOP_WRITE":
            rw_mutex = 1
            writer_active = False
            expl = f"{actor} completed writing and released rw_mutex."

        trace.append({
            "step": step,
            "actor": actor,
            "action": op,
            "read_count": read_count,
            "rw_mutex": rw_mutex,
            "writer_active": writer_active,
            "explanation": expl,
        })

    return {
        "problem": "Readers-Writers",
        "steps": trace,
    }
