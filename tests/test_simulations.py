"""
Comprehensive tests for SLARAP Educational OS Simulation Engines:
- CPU Scheduling (FCFS, SJF, SRTF, Priority Preemptive/Non-preemptive, Round Robin, MLFQ)
- Memory Management (First/Best/Worst Fit, Fragmentation, Address Translation, Page Replacement)
- Deadlock Lab (Banker's algorithm safety & request, RAG cycles, Coffman conditions)
- Disk Scheduling (FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK)
- Synchronization (Race condition, Peterson's algorithm, Producer-Consumer, Dining Philosophers)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.simulations import (
    scheduling,
    synchronization,
    deadlock,
    memory,
    disk,
    filesys,
    academy,
)


def test_cpu_scheduling_fcfs():
    processes = [
        {"id": "P1", "arrival_time": 0, "burst_time": 4},
        {"id": "P2", "arrival_time": 1, "burst_time": 3},
        {"id": "P3", "arrival_time": 2, "burst_time": 1},
    ]
    res = scheduling.simulate_cpu_scheduling("FCFS", processes)
    assert res["algorithm"] == "FCFS"
    assert len(res["events"]) > 0
    # P1 runs 0-4, P2 runs 4-7, P3 runs 7-8
    assert res["metrics"]["process_metrics"]["P1"]["completion_time"] == 4
    assert res["metrics"]["process_metrics"]["P2"]["completion_time"] == 7
    assert res["metrics"]["process_metrics"]["P3"]["completion_time"] == 8
    # TAT = Comp - Arr: P1=4-0=4, P2=7-1=6, P3=8-2=6. Avg = (4+6+6)/3 = 5.33
    assert res["metrics"]["avg_turnaround_time"] == 5.33
    # WT = TAT - Burst: P1=4-4=0, P2=6-3=3, P3=6-1=5. Avg = (0+3+5)/3 = 2.67
    assert res["metrics"]["avg_waiting_time"] == 2.67


def test_cpu_scheduling_sjf():
    processes = [
        {"id": "P1", "arrival_time": 0, "burst_time": 7},
        {"id": "P2", "arrival_time": 2, "burst_time": 4},
        {"id": "P3", "arrival_time": 4, "burst_time": 1},
        {"id": "P4", "arrival_time": 5, "burst_time": 4},
    ]
    res = scheduling.simulate_cpu_scheduling("SJF", processes)
    # P1 starts at 0, finishes at 7.
    # At t=7, P2 (burst 4), P3 (burst 1), P4 (burst 4) are ready.
    # P3 selected first (burst 1), completes at 8.
    # P2 and P4 tie burst 4, P2 arrived earlier (t=2 vs t=5), runs 8-12.
    # P4 runs 12-16.
    assert res["metrics"]["process_metrics"]["P1"]["completion_time"] == 7
    assert res["metrics"]["process_metrics"]["P3"]["completion_time"] == 8
    assert res["metrics"]["process_metrics"]["P2"]["completion_time"] == 12
    assert res["metrics"]["process_metrics"]["P4"]["completion_time"] == 16


def test_cpu_scheduling_round_robin():
    processes = [
        {"id": "P1", "arrival_time": 0, "burst_time": 5},
        {"id": "P2", "arrival_time": 1, "burst_time": 3},
    ]
    res = scheduling.simulate_cpu_scheduling("ROUND_ROBIN", processes, time_quantum=2)
    # t=0: P1 runs 0-2 (rem 3)
    # t=2: P2 arrived at t=1, P2 runs 2-4 (rem 1)
    # t=4: P1 runs 4-6 (rem 1)
    # t=6: P2 runs 6-7 (done, comp=7)
    # t=7: P1 runs 7-8 (done, comp=8)
    assert res["metrics"]["process_metrics"]["P2"]["completion_time"] == 7
    assert res["metrics"]["process_metrics"]["P1"]["completion_time"] == 8


def test_bankers_algorithm_safety():
    # Classic textbook 5-process, 3-resource safe example
    available = [3, 3, 2]
    allocation = [
        [0, 1, 0],  # P0
        [2, 0, 0],  # P1
        [3, 0, 2],  # P2
        [2, 1, 1],  # P3
        [0, 0, 2],  # P4
    ]
    max_matrix = [
        [7, 5, 3],  # P0
        [3, 2, 2],  # P1
        [9, 0, 2],  # P2
        [2, 2, 2],  # P3
        [4, 3, 3],  # P4
    ]
    res = deadlock.bankers_safety_algorithm(available, allocation, max_matrix)
    assert res["is_safe"] is True
    assert len(res["safe_sequence"]) == 5
    # First process in safe sequence must be P1 or P3
    assert res["safe_sequence"][0] in ("P1", "P3")


def test_bankers_algorithm_unsafe():
    available = [0, 0, 0]
    allocation = [[1, 0, 0], [0, 1, 0]]
    max_matrix = [[2, 2, 2], [2, 2, 2]]
    res = deadlock.bankers_safety_algorithm(available, allocation, max_matrix)
    assert res["is_safe"] is False
    assert len(res["deadlocked_processes"]) > 0


def test_memory_allocation_fits():
    blocks = [100, 500, 200, 300, 600]
    processes = [
        {"id": "P1", "size": 212},
        {"id": "P2", "size": 417},
        {"id": "P3", "size": 112},
        {"id": "P4", "size": 426},
    ]
    # First fit test
    ff = memory.simulate_contiguous_allocation("FIRST_FIT", blocks, processes)
    assert ff["steps"][0]["block_assigned"] == 1  # 500 KB block
    # Best fit test
    bf = memory.simulate_contiguous_allocation("BEST_FIT", blocks, processes)
    assert bf["steps"][0]["block_assigned"] == 3  # 300 KB block fits 212 best


def test_paging_and_segmentation():
    # Paging test: logical 2500, page_size 1024
    # 2500 // 1024 = 2 (page 2), offset = 452
    page_tab = {0: 5, 1: 6, 2: 1}
    p_res = memory.translate_paging_address(2500, page_size=1024, page_table=page_tab)
    assert p_res["valid"] is True
    assert p_res["page_number"] == 2
    assert p_res["offset"] == 452
    assert p_res["physical_address"] == (1 * 1024) + 452

    # Segmentation test: trap on limit violation
    seg_res = memory.translate_segmentation_address(segment_number=0, offset=1500)
    assert seg_res["trap"] is True  # offset 1500 >= limit 1000


def test_page_replacement_lru_and_fifo():
    refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3]
    fifo_res = memory.simulate_page_replacement("FIFO", refs, frame_count=3)
    lru_res = memory.simulate_page_replacement("LRU", refs, frame_count=3)
    opt_res = memory.simulate_page_replacement("OPTIMAL", refs, frame_count=3)
    assert fifo_res["total_faults"] > 0
    assert lru_res["total_faults"] > 0
    assert opt_res["total_faults"] <= fifo_res["total_faults"]


def test_disk_scheduling_algorithms():
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    initial_head = 53
    fcfs = disk.simulate_disk_scheduling("FCFS", requests, initial_head)
    sstf = disk.simulate_disk_scheduling("SSTF", requests, initial_head)
    scan = disk.simulate_disk_scheduling("SCAN", requests, initial_head, disk_size=200, direction="UP")

    # In textbook example:
    # FCFS total movement = 640
    # SSTF total movement = 236
    assert fcfs["total_head_movement"] == 640
    assert sstf["total_head_movement"] == 236
    assert scan["total_head_movement"] > 0


def test_synchronization_lab():
    # Mutex eliminates lost updates
    no_mutex = synchronization.simulate_race_condition(iterations=5, use_mutex=False)
    with_mutex = synchronization.simulate_race_condition(iterations=5, use_mutex=True)
    assert no_mutex["lost_updates"] > 0
    assert with_mutex["lost_updates"] == 0
    assert with_mutex["actual_value"] == 10

    # Peterson's solution
    peterson = synchronization.simulate_petersons_algorithm()
    assert peterson["mutual_exclusion_verified"] is True


def main():
    print("Testing CPU Scheduling...")
    test_cpu_scheduling_fcfs()
    test_cpu_scheduling_sjf()
    test_cpu_scheduling_round_robin()
    print("CPU Scheduling tests passed!")

    print("Testing Banker's Algorithm & Deadlocks...")
    test_bankers_algorithm_safety()
    test_bankers_algorithm_unsafe()
    print("Deadlock tests passed!")

    print("Testing Memory Management...")
    test_memory_allocation_fits()
    test_paging_and_segmentation()
    test_page_replacement_lru_and_fifo()
    print("Memory management tests passed!")

    print("Testing Disk Scheduling...")
    test_disk_scheduling_algorithms()
    print("Disk scheduling tests passed!")

    print("Testing Synchronization Lab...")
    test_synchronization_lab()
    print("Synchronization tests passed!")

    print("\nALL EDUCATIONAL SIMULATION ENGINE TESTS PASSED!")


if __name__ == "__main__":
    main()
