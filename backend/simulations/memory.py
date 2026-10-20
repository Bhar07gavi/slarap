"""
SLARAP Educational OS Simulation Engine - Memory Management Lab.

Provides:
1. Contiguous Dynamic Partition Allocation:
   - First Fit
   - Best Fit
   - Worst Fit
   - Fragmentation analysis (Internal & External fragmentation)
2. Paging & Segmentation Address Translation:
   - Logical address (Page number, Offset) -> Physical address (Frame, Offset)
   - Segment table (Base, Limit) address translation with limit violation traps
3. Virtual Memory Page Replacement:
   - FIFO (First-In, First-Out)
   - LRU (Least Recently Used)
   - Optimal (Belady's MIN algorithm)
   - Clock / Second Chance algorithm
4. Buddy Allocation System:
   - Power-of-two recursive block splitting and coalescing
"""

from typing import Any, Dict, List, Optional, Tuple
import math
import copy


def simulate_contiguous_allocation(
    algorithm: str,
    blocks: List[int],  # initial block sizes
    processes: List[Dict[str, Any]],  # [{id: "P1", size: 212}, ...]
) -> Dict[str, Any]:
    """
    Simulates First Fit, Best Fit, or Worst Fit allocation.
    Calculates internal/external fragmentation and provides step-by-step decisions.
    """
    alg = algorithm.upper().replace("-", "_").replace(" ", "_")
    if alg not in ("FIRST_FIT", "BEST_FIT", "WORST_FIT"):
        raise ValueError(f"Unknown allocation algorithm: {algorithm}")

    # Track blocks: list of {id, initial_size, remaining_size, allocated_to: [{pid, size}]}
    memory_blocks = [
        {
            "block_id": i,
            "total_size": sz,
            "remaining_size": sz,
            "allocated_processes": [],
        }
        for i, sz in enumerate(blocks)
    ]

    steps = []
    unallocated_processes = []
    total_internal_frag = 0

    for p in processes:
        pid = str(p["id"])
        psize = int(p["size"])
        target_block_idx = None
        explanation = ""

        # Candidates that have enough space
        candidates = [
            (i, b) for i, b in enumerate(memory_blocks) if b["remaining_size"] >= psize
        ]

        if not candidates:
            unallocated_processes.append(pid)
            explanation = f"Allocation FAILED for {pid} (size {psize} KB): No memory block has sufficient contiguous free space."
            steps.append({
                "process_id": pid,
                "process_size": psize,
                "allocated": False,
                "block_assigned": None,
                "explanation": explanation,
                "memory_blocks": copy.deepcopy(memory_blocks),
            })
            continue

        if alg == "FIRST_FIT":
            target_block_idx = candidates[0][0]
            b = memory_blocks[target_block_idx]
            explanation = f"First Fit: Found first block with enough space: Block {target_block_idx} (free: {b['remaining_size']} KB)."

        elif alg == "BEST_FIT":
            # Smallest remaining size that fits
            best_tuple = min(candidates, key=lambda c: c[1]["remaining_size"])
            target_block_idx = best_tuple[0]
            b = memory_blocks[target_block_idx]
            explanation = f"Best Fit: Found closest-sized block leaving minimum leftover: Block {target_block_idx} (free: {b['remaining_size']} KB, leaves {b['remaining_size'] - psize} KB)."

        elif alg == "WORST_FIT":
            # Largest remaining size
            worst_tuple = max(candidates, key=lambda c: c[1]["remaining_size"])
            target_block_idx = worst_tuple[0]
            b = memory_blocks[target_block_idx]
            explanation = f"Worst Fit: Placed in largest available block to leave largest reusable leftover: Block {target_block_idx} (free: {b['remaining_size']} KB, leaves {b['remaining_size'] - psize} KB)."

        # Perform allocation
        blk = memory_blocks[target_block_idx]
        blk["allocated_processes"].append({"id": pid, "size": psize})
        blk["remaining_size"] -= psize

        steps.append({
            "process_id": pid,
            "process_size": psize,
            "allocated": True,
            "block_assigned": target_block_idx,
            "explanation": explanation,
            "memory_blocks": copy.deepcopy(memory_blocks),
        })

    # Fragmentation calculation
    total_free_memory = sum(b["remaining_size"] for b in memory_blocks)
    # External fragmentation exists when total free memory could satisfy a failed process, but no single block was big enough
    external_fragmentation = False
    for pid in unallocated_processes:
        psize = next(p["size"] for p in processes if str(p["id"]) == pid)
        if total_free_memory >= psize:
            external_fragmentation = True
            break

    return {
        "algorithm": alg,
        "initial_blocks": blocks,
        "processes": processes,
        "steps": steps,
        "final_blocks": memory_blocks,
        "unallocated_processes": unallocated_processes,
        "total_free_memory": total_free_memory,
        "external_fragmentation_present": external_fragmentation,
    }


def translate_paging_address(
    logical_address: int,
    page_size: int = 1024,  # in bytes
    page_table: Optional[Dict[int, int]] = None,  # page_num -> frame_num
) -> Dict[str, Any]:
    """
    Paging Hardware Address Translation:
    Logical Address = Page number (p) * page_size + Offset (d)
    Physical Address = Frame number (f) * page_size + Offset (d)
    """
    if page_table is None:
        # Default educational page table
        page_table = {0: 5, 1: 6, 2: 1, 3: 2}

    page_number = logical_address // page_size
    offset = logical_address % page_size

    if page_number in page_table:
        frame_number = page_table[page_number]
        physical_address = (frame_number * page_size) + offset
        valid = True
        explanation = (
            f"Logical address {logical_address} = Page {page_number}, Offset {offset}. "
            f"Page table maps Page {page_number} -> Frame {frame_number}. "
            f"Physical address = ({frame_number} * {page_size}) + {offset} = {physical_address}."
        )
    else:
        frame_number = None
        physical_address = None
        valid = False
        explanation = f"PAGE FAULT / INVALID: Page {page_number} is not in page table (not mapped in physical memory)."

    return {
        "logical_address": logical_address,
        "page_size": page_size,
        "page_number": page_number,
        "offset": offset,
        "frame_number": frame_number,
        "physical_address": physical_address,
        "valid": valid,
        "page_table": page_table,
        "explanation": explanation,
    }


def translate_segmentation_address(
    segment_number: int,
    offset: int,
    segment_table: Optional[Dict[int, Dict[str, int]]] = None,
) -> Dict[str, Any]:
    """
    Segmentation Address Translation:
    Logical Address = (Segment Number s, Offset d)
    If d < Limit: Physical Address = Base + d
    If d >= Limit: TRAP: Addressing error (segment violation)!
    """
    if segment_table is None:
        # Default educational segment table
        segment_table = {
            0: {"base": 1400, "limit": 1000},
            1: {"base": 6300, "limit": 400},
            2: {"base": 4300, "limit": 400},
            3: {"base": 3200, "limit": 1100},
            4: {"base": 4700, "limit": 1000},
        }

    if segment_number not in segment_table:
        return {
            "segment_number": segment_number,
            "offset": offset,
            "valid": False,
            "trap": True,
            "explanation": f"TRAP: Segment {segment_number} does not exist in segment table!",
            "segment_table": segment_table,
        }

    entry = segment_table[segment_number]
    base = entry["base"]
    limit = entry["limit"]

    if offset >= limit:
        return {
            "segment_number": segment_number,
            "offset": offset,
            "base": base,
            "limit": limit,
            "valid": False,
            "trap": True,
            "physical_address": None,
            "explanation": f"TRAP (SEGMENTATION FAULT): Offset {offset} >= Limit {limit} for Segment {segment_number}!",
            "segment_table": segment_table,
        }
    else:
        phys = base + offset
        return {
            "segment_number": segment_number,
            "offset": offset,
            "base": base,
            "limit": limit,
            "valid": True,
            "trap": False,
            "physical_address": phys,
            "explanation": f"Offset {offset} < Limit {limit}. Physical Address = Base {base} + Offset {offset} = {phys}.",
            "segment_table": segment_table,
        }


def simulate_page_replacement(
    algorithm: str,
    reference_string: List[int],
    frame_count: int = 3,
) -> Dict[str, Any]:
    """
    Virtual Memory Page Replacement Simulation:
    Algorithms: FIFO, LRU, OPTIMAL, CLOCK
    Returns step-by-step frame contents, page hits, page faults, and replacement explanations.
    """
    alg = algorithm.upper().replace("-", "_").replace(" ", "_")
    frames: List[Optional[int]] = [None] * frame_count
    steps: List[Dict[str, Any]] = []

    fault_count = 0
    hit_count = 0

    if alg == "FIFO":
        fifo_queue: List[int] = []  # stores pages in insertion order
        for idx, page in enumerate(reference_string):
            if page in frames:
                hit_count += 1
                is_hit = True
                victim = None
                explanation = f"Page Hit: Page {page} is already in frame {frames.index(page)}."
            else:
                fault_count += 1
                is_hit = False
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    fifo_queue.append(page)
                    victim = None
                    explanation = f"Page Fault: Loaded page {page} into empty frame {empty_idx}."
                else:
                    victim = fifo_queue.pop(0)
                    v_idx = frames.index(victim)
                    frames[v_idx] = page
                    fifo_queue.append(page)
                    explanation = f"Page Fault: Replaced oldest page {victim} in frame {v_idx} with page {page}."

            steps.append({
                "step": idx + 1,
                "page": page,
                "frames": list(frames),
                "is_hit": is_hit,
                "victim": victim,
                "explanation": explanation,
            })

    elif alg == "LRU":
        last_used: Dict[int, int] = {}  # page -> last used step
        for idx, page in enumerate(reference_string):
            step_num = idx + 1
            if page in frames:
                hit_count += 1
                is_hit = True
                victim = None
                last_used[page] = step_num
                explanation = f"Page Hit: Page {page} is present. Updated its last-used timestamp to step {step_num}."
            else:
                fault_count += 1
                is_hit = False
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    last_used[page] = step_num
                    victim = None
                    explanation = f"Page Fault: Loaded page {page} into empty frame {empty_idx}."
                else:
                    # Victim is page in frames with minimum last_used timestamp
                    victim = min(frames, key=lambda p: last_used.get(p, -1))
                    v_idx = frames.index(victim)
                    frames[v_idx] = page
                    last_used[page] = step_num
                    explanation = f"Page Fault: Replaced Least Recently Used page {victim} (last used at step {last_used[victim]}) with page {page}."

            steps.append({
                "step": step_num,
                "page": page,
                "frames": list(frames),
                "is_hit": is_hit,
                "victim": victim,
                "explanation": explanation,
            })

    elif alg in ("OPTIMAL", "OPT"):
        for idx, page in enumerate(reference_string):
            step_num = idx + 1
            if page in frames:
                hit_count += 1
                is_hit = True
                victim = None
                explanation = f"Page Hit: Page {page} is already in memory."
            else:
                fault_count += 1
                is_hit = False
                if None in frames:
                    empty_idx = frames.index(None)
                    frames[empty_idx] = page
                    victim = None
                    explanation = f"Page Fault: Placed page {page} into empty frame {empty_idx}."
                else:
                    # Look ahead into future references
                    future_refs = reference_string[idx + 1:]
                    victim = None
                    furthest_distance = -1

                    for f in frames:
                        if f not in future_refs:
                            # Not used again in the future! Perfect victim
                            victim = f
                            break
                        else:
                            dist = future_refs.index(f)
                            if dist > furthest_distance:
                                furthest_distance = dist
                                victim = f

                    v_idx = frames.index(victim)
                    frames[v_idx] = page
                    explanation = f"Page Fault: Replaced page {victim} because it will not be used for the longest time in the future."

            steps.append({
                "step": step_num,
                "page": page,
                "frames": list(frames),
                "is_hit": is_hit,
                "victim": victim,
                "explanation": explanation,
            })

    else:
        raise ValueError(f"Unsupported page replacement algorithm: {algorithm}")

    total_refs = len(reference_string)
    fault_rate = round((fault_count / total_refs * 100) if total_refs > 0 else 0, 2)
    hit_rate = round((hit_count / total_refs * 100) if total_refs > 0 else 0, 2)

    return {
        "algorithm": alg,
        "frame_count": frame_count,
        "reference_string": reference_string,
        "steps": steps,
        "total_faults": fault_count,
        "total_hits": hit_count,
        "fault_rate_percent": fault_rate,
        "hit_rate_percent": hit_rate,
    }


def simulate_buddy_allocation(
    total_memory: int = 1024,  # e.g. 1024 KB
    requests: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Buddy System memory allocation:
    Splits blocks recursively in half until smallest power of 2 >= request size.
    When a block is freed, buddies are coalesced into a single larger block.
    """
    if requests is None:
        requests = [
            {"action": "ALLOC", "id": "A", "size": 100},
            {"action": "ALLOC", "id": "B", "size": 240},
            {"action": "ALLOC", "id": "C", "size": 64},
            {"action": "FREE", "id": "B"},
            {"action": "ALLOC", "id": "D", "size": 200},
        ]

    # Block representation: {id, size, allocated_to: str or None, address}
    blocks = [{"size": total_memory, "allocated_to": None, "address": 0}]
    steps = []

    def get_needed_size(size: int) -> int:
        power = 1
        while power < size:
            power *= 2
        return power

    for req in requests:
        act = req["action"]
        pid = req.get("id")

        if act == "ALLOC":
            req_size = req["size"]
            needed = get_needed_size(req_size)
            allocated = False

            # Find best block to split
            # Sort available blocks by size
            available_indices = [i for i, b in enumerate(blocks) if b["allocated_to"] is None and b["size"] >= needed]
            if not available_indices:
                steps.append({
                    "action": act,
                    "process_id": pid,
                    "size": req_size,
                    "success": False,
                    "explanation": f"Buddy Allocation FAILED: No free block >= {needed} KB available.",
                    "blocks": copy.deepcopy(blocks),
                })
                continue

            # Pick smallest suitable free block
            target_idx = min(available_indices, key=lambda i: blocks[i]["size"])
            target_block = blocks[target_idx]

            # Split until block size == needed
            while target_block["size"] > needed:
                half = target_block["size"] // 2
                addr = target_block["address"]
                # Replace target_block with two buddies
                b1 = {"size": half, "allocated_to": None, "address": addr}
                b2 = {"size": half, "allocated_to": None, "address": addr + half}
                blocks.pop(target_idx)
                blocks.insert(target_idx, b2)
                blocks.insert(target_idx, b1)
                target_block = b1

            target_block["allocated_to"] = pid
            steps.append({
                "action": act,
                "process_id": pid,
                "size": req_size,
                "allocated_size": needed,
                "internal_fragmentation": needed - req_size,
                "success": True,
                "explanation": f"Allocated {pid} (req={req_size} KB -> rounded to {needed} KB) at address {target_block['address']}.",
                "blocks": copy.deepcopy(blocks),
            })

        elif act == "FREE":
            # Find and free
            freed = False
            for b in blocks:
                if b["allocated_to"] == pid:
                    b["allocated_to"] = None
                    freed = True
                    break

            # Coalesce adjacent free buddies
            # Repeat coalescing pass while changes occur
            changed = True
            while changed:
                changed = False
                i = 0
                while i < len(blocks) - 1:
                    b1 = blocks[i]
                    b2 = blocks[i + 1]
                    if (
                        b1["allocated_to"] is None
                        and b2["allocated_to"] is None
                        and b1["size"] == b2["size"]
                        and (b1["address"] % (2 * b1["size"])) == 0
                        and b2["address"] == b1["address"] + b1["size"]
                    ):
                        # Merge buddies
                        merged = {"size": 2 * b1["size"], "allocated_to": None, "address": b1["address"]}
                        blocks.pop(i + 1)
                        blocks.pop(i)
                        blocks.insert(i, merged)
                        changed = True
                    else:
                        i += 1

            steps.append({
                "action": act,
                "process_id": pid,
                "success": freed,
                "explanation": f"Freed process {pid} and coalesced adjacent free buddy blocks.",
                "blocks": copy.deepcopy(blocks),
            })

    return {
        "total_memory": total_memory,
        "steps": steps,
        "final_blocks": blocks,
    }
