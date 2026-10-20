"""
SLARAP Educational OS Simulation Engine - File System & I/O Lab.

Simulates:
1. File Allocation Methods (Contiguous, Linked, Indexed)
2. Free Space Management (Bit Vector / Bitmap, Linked Free List)
3. Directory Structure Models (Single-Level, Two-Level, Tree-Structured)
4. I/O Buffering Models (Single Buffer, Double Buffer, Circular Buffer)
"""

from typing import Any, Dict, List, Optional
import copy


def simulate_file_allocation(
    method: str,
    total_blocks: int = 32,
    files_to_allocate: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Demonstrates Contiguous, Linked, and Indexed file allocation strategies
    on a simulated disk consisting of block 0 to total_blocks - 1.
    """
    if files_to_allocate is None:
        files_to_allocate = [
            {"name": "kernel.bin", "blocks": 4},
            {"name": "report.pdf", "blocks": 3},
            {"name": "data.csv", "blocks": 5},
            {"name": "photo.jpg", "blocks": 2},
        ]

    m_upper = method.upper()
    disk_blocks: List[Optional[str]] = [None] * total_blocks
    directory: List[Dict[str, Any]] = []
    steps = []

    if m_upper == "CONTIGUOUS":
        # Needs contiguous sequence of free blocks
        for f in files_to_allocate:
            fname = f["name"]
            needed = f["blocks"]
            allocated = False

            # Search for contiguous free chunk
            free_start = -1
            free_len = 0
            for i in range(total_blocks):
                if disk_blocks[i] is None:
                    if free_len == 0:
                        free_start = i
                    free_len += 1
                    if free_len == needed:
                        # Found contiguous chunk!
                        for b in range(free_start, free_start + needed):
                            disk_blocks[b] = fname
                        directory.append({
                            "name": fname,
                            "start_block": free_start,
                            "length": needed,
                            "blocks": list(range(free_start, free_start + needed)),
                        })
                        allocated = True
                        steps.append({
                            "file": fname,
                            "blocks_needed": needed,
                            "allocated": True,
                            "start_block": free_start,
                            "allocated_blocks": list(range(free_start, free_start + needed)),
                            "explanation": f"Contiguous: Allocated {needed} consecutive blocks from block {free_start} to {free_start + needed - 1}.",
                            "disk_map": list(disk_blocks),
                        })
                        break
                else:
                    free_len = 0

            if not allocated:
                steps.append({
                    "file": fname,
                    "blocks_needed": needed,
                    "allocated": False,
                    "explanation": f"Contiguous allocation FAILED: No {needed} consecutive free blocks available (External fragmentation).",
                    "disk_map": list(disk_blocks),
                })

    elif m_upper == "LINKED":
        # Dispersed blocks linked by pointers
        for f in files_to_allocate:
            fname = f["name"]
            needed = f["blocks"]
            free_indices = [i for i, b in enumerate(disk_blocks) if b is None]

            if len(free_indices) >= needed:
                chosen_blocks = free_indices[:needed]
                for b in chosen_blocks:
                    disk_blocks[b] = fname

                # Build linked chain
                chain = []
                for idx, b in enumerate(chosen_blocks):
                    nxt = chosen_blocks[idx + 1] if idx + 1 < needed else -1  # -1 is EOF
                    chain.append({"block": b, "next_pointer": nxt})

                directory.append({
                    "name": fname,
                    "start_block": chosen_blocks[0],
                    "end_block": chosen_blocks[-1],
                    "length": needed,
                    "chain": chain,
                })
                steps.append({
                    "file": fname,
                    "blocks_needed": needed,
                    "allocated": True,
                    "start_block": chosen_blocks[0],
                    "end_block": chosen_blocks[-1],
                    "chain": chain,
                    "explanation": f"Linked: Allocated {needed} blocks dispersed across disk linked by pointers: {' -> '.join(str(b) for b in chosen_blocks)}.",
                    "disk_map": list(disk_blocks),
                })
            else:
                steps.append({
                    "file": fname,
                    "blocks_needed": needed,
                    "allocated": False,
                    "explanation": f"Allocation FAILED: Not enough total free disk blocks ({len(free_indices)} free < {needed} needed).",
                    "disk_map": list(disk_blocks),
                })

    elif m_upper == "INDEXED":
        # 1 Index block + data blocks
        for f in files_to_allocate:
            fname = f["name"]
            needed = f["blocks"]
            total_needed = needed + 1  # 1 block for index table
            free_indices = [i for i, b in enumerate(disk_blocks) if b is None]

            if len(free_indices) >= total_needed:
                index_block = free_indices[0]
                data_blocks = free_indices[1:total_needed]

                disk_blocks[index_block] = f"{fname}[IDX]"
                for b in data_blocks:
                    disk_blocks[b] = fname

                directory.append({
                    "name": fname,
                    "index_block": index_block,
                    "data_blocks": data_blocks,
                    "length": needed,
                })
                steps.append({
                    "file": fname,
                    "blocks_needed": needed,
                    "index_block": index_block,
                    "data_blocks": data_blocks,
                    "allocated": True,
                    "explanation": f"Indexed: Assigned Block {index_block} as Index Block pointing to data blocks {data_blocks}. Direct random access enabled!",
                    "disk_map": list(disk_blocks),
                })
            else:
                steps.append({
                    "file": fname,
                    "blocks_needed": needed,
                    "allocated": False,
                    "explanation": f"Indexed allocation FAILED: Need {total_needed} blocks (including 1 index block), but only {len(free_indices)} free.",
                    "disk_map": list(disk_blocks),
                })

    free_count = disk_blocks.count(None)
    used_count = total_blocks - free_count

    return {
        "method": m_upper,
        "total_blocks": total_blocks,
        "used_blocks": used_count,
        "free_blocks": free_count,
        "directory": directory,
        "steps": steps,
        "final_disk_map": disk_blocks,
    }


def simulate_free_space_management(
    total_blocks: int = 16,
    allocated_indices: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """
    Demonstrates Free-Space Management:
    - Bit Vector / Bitmap (0 = free, 1 = allocated)
    - Linked Free List
    """
    if allocated_indices is None:
        allocated_indices = [1, 2, 5, 6, 7, 10, 11]

    bitmap = [1 if i in allocated_indices else 0 for i in range(total_blocks)]
    free_blocks = [i for i, bit in enumerate(bitmap) if bit == 0]

    # Linked free list representation
    free_list = []
    for idx, b in enumerate(free_blocks):
        nxt = free_blocks[idx + 1] if idx + 1 < len(free_blocks) else None
        free_list.append({"block": b, "next_free": nxt})

    return {
        "total_blocks": total_blocks,
        "bitmap": bitmap,
        "bitmap_string": "".join(str(b) for b in bitmap),
        "free_blocks": free_blocks,
        "free_list": free_list,
        "explanation": (
            f"Bit Vector: {len(free_blocks)} free blocks found. "
            f"First free block at index {free_blocks[0] if free_blocks else 'None'}. "
            "Bitmap allows fast bitwise calculation of contiguous blocks."
        ),
    }


def simulate_io_buffering(model: str = "DOUBLE") -> Dict[str, Any]:
    """
    Compares Single Buffering, Double Buffering, and Circular Buffering for I/O operations.
    Shows producer/consumer timeline and time savings.
    """
    m = model.upper()
    # Typical cycle: Device input time T = 10ms, Transfer to user buffer C = 2ms, CPU computation M = 8ms
    T = 10
    C = 2
    M = 8

    if m == "SINGLE":
        time_per_block = max(T, C) + M
        desc = "Single Buffer: While I/O fills the system buffer, CPU cannot read it until completion. Sequential blocking."
    elif m == "DOUBLE":
        time_per_block = max(T, C + M)
        desc = "Double Buffer: CPU processes one buffer while I/O transfers into the alternate buffer. Overlapped execution!"
    else:  # CIRCULAR
        time_per_block = max(T, M)
        desc = "Circular Buffer: Queue of multiple buffers smooths out bursts when CPU or I/O speeds vary dynamically."

    return {
        "model": m,
        "device_transfer_time_T_ms": T,
        "system_to_user_copy_C_ms": C,
        "cpu_computation_time_M_ms": M,
        "time_per_block_ms": time_per_block,
        "explanation": desc,
    }
