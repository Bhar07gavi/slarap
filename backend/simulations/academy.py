"""
SLARAP Educational OS Academy & Gamification Content.

Covers the complete 6-Unit Operating Systems Syllabus:
- Unit 1: Operating Systems Overview & Architectures
- Unit 2: Process Management & CPU Scheduling
- Unit 3: Synchronization & Deadlocks
- Unit 4: Memory Management & Virtual Memory
- Unit 5: File & I/O Management
- Unit 6: Linux Kernel Internals & Android OS

Also provides:
- Structured Mission & Challenge definitions with completion conditions and XP rewards.
- Knowledge Check Quizzes for each unit with explanations.
- Achievement Badge catalog.
"""

from typing import Any, Dict, List, Optional


SYLLABUS_UNITS = [
    {
        "id": "unit1",
        "number": 1,
        "title": "Operating Systems Overview & Shell Programming",
        "description": "Foundations of operating systems, kernel architectures (Monolithic, Microkernel, Hybrid, Modular), system calls, and Linux shell programming.",
        "topics": [
            {
                "id": "u1_intro",
                "title": "Introduction & OS Objectives",
                "content": (
                    "An Operating System (OS) is software that acts as an intermediary between the computer hardware and the computer user. "
                    "Its two primary objectives are: 1) Convenience (making computer system convenient and user-friendly to use), and 2) Efficiency (managing hardware resources efficiently).\n\n"
                    "Major OS Functions include: Process Management, Main-Memory Management, File-System Management, I/O System Management, Secondary-Storage Management, Protection & Security, and Command-Interpreter System."
                ),
                "key_takeaways": [
                    "OS acts as resource allocator and control program.",
                    "Dual-mode operation (User Mode vs Kernel Mode) protects hardware via privileged instructions.",
                    "System calls provide the programmatic interface to kernel services."
                ],
            },
            {
                "id": "u1_architectures",
                "title": "Kernel Architectures Comparison",
                "content": (
                    "Operating systems structure their kernels in fundamentally distinct ways:\n\n"
                    "1. Monolithic Kernel (e.g. Linux, Traditional Unix):\n"
                    "   - Entire OS (VFS, scheduler, IPC, drivers, network stack) executes in privileged kernel space in a single address space.\n"
                    "   - Advantage: Maximum execution speed due to direct in-memory function calls without IPC overhead.\n"
                    "   - Disadvantage: Lack of isolation; a crash in a device driver can panic the entire system.\n\n"
                    "2. Microkernel (e.g. Mach, QNX, L4):\n"
                    "   - Only absolute bare essentials stay in kernel space (minimal IPC, low-level memory, basic scheduling).\n"
                    "   - File systems, networking, and device drivers run in user space as servers.\n"
                    "   - Advantage: Extreme reliability, modularity, and security.\n"
                    "   - Disadvantage: Performance overhead from frequent message passing (IPC) across user-kernel boundaries.\n\n"
                    "3. Hybrid Kernel (e.g. Windows NT, macOS XNU):\n"
                    "   - Combines microkernel modularity with monolithic performance by running select performance-critical servers in kernel space.\n\n"
                    "4. Modular Kernel (e.g. Modern Linux with Loadable Kernel Modules - LKM):\n"
                    "   - Monolithic core with dynamic run-time module loading (`insmod`, `rmmod`, `lsmod`) without recompiling or rebooting."
                ),
                "key_takeaways": [
                    "Monolithic = Speed & Complexity.",
                    "Microkernel = Safety & Modularity via Message Passing.",
                    "Linux uses a Monolithic core enhanced with Loadable Kernel Modules (LKMs)."
                ],
            },
            {
                "id": "u1_shell",
                "title": "Linux Shell Commands & Scripting Lab",
                "content": (
                    "The Linux Shell is a command language interpreter that executes commands read from standard input devices or from scripts.\n\n"
                    "Core administration command categories:\n"
                    "- Process inspection: `ps aux`, `top`, `pstree`, `pgrep`\n"
                    "- Inter-Process Communication & pipes: `cmd1 | cmd2`\n"
                    "- Signal handling: `kill -TERM <pid>`, `kill -9 <pid>`\n"
                    "- Disk & memory stats: `free -m`, `df -h`, `lsblk`, `iostat`\n"
                    "- Shell scripting constructs: Variables (`VAR=value`), Conditionals (`if [ ... ]; then ... fi`), Loops (`for`, `while`), Functions."
                ),
                "key_takeaways": [
                    "Standard Streams: stdin (fd 0), stdout (fd 1), stderr (fd 2).",
                    "Pipes connect stdout of one process to stdin of another via kernel circular memory buffer.",
                    "Exit codes: 0 indicates success, non-zero indicates an error."
                ],
            },
        ],
    },
    {
        "id": "unit2",
        "number": 2,
        "title": "Process Management & CPU Scheduling",
        "description": "Process Control Block (PCB), 5-state process lifecycle, fork/exec/waitpid in Linux, and comprehensive CPU scheduling algorithms.",
        "topics": [
            {
                "id": "u2_lifecycle",
                "title": "Process Lifecycle & Process Control Block (PCB)",
                "content": (
                    "A process is a program in execution. It is represented in the operating system by a Process Control Block (PCB / `struct task_struct` in Linux).\n\n"
                    "PCB Components:\n"
                    "- Process Identification (PID, PPID, UID, GID)\n"
                    "- Process State (New, Ready, Running, Waiting/Blocked, Terminated)\n"
                    "- CPU Registers & Program Counter (PC)\n"
                    "- CPU-Scheduling Information (Priority, scheduling queues)\n"
                    "- Memory-Management Information (Page tables, base/limit registers)\n"
                    "- Accounting Information (CPU time consumed, time limits)\n"
                    "- I/O Status Information (List of open file descriptors `fd_array`).\n\n"
                    "State Transitions:\n"
                    "- New -> Ready: Process created and admitted to ready queue.\n"
                    "- Ready -> Running: Scheduler dispatches process to CPU.\n"
                    "- Running -> Ready: Time slice expires or preempted by higher priority process.\n"
                    "- Running -> Waiting: Process issues blocking I/O or waits for event/signal.\n"
                    "- Waiting -> Ready: I/O completes or event occurs.\n"
                    "- Running -> Terminated: Process exits or is killed."
                ),
                "key_takeaways": [
                    "Context switch saves state of old process into PCB and loads state of new process.",
                    "In Linux, every task is represented by `struct task_struct` defined in `<linux/sched.h>`.",
                    "Threads share the same address space and file descriptors, but each has its own thread ID (TID), registers, and stack."
                ],
            },
            {
                "id": "u2_scheduling_criteria",
                "title": "CPU Scheduling Criteria & Textbook vs Real Linux",
                "content": (
                    "Scheduling Criteria:\n"
                    "- CPU Utilization: Percentage of time CPU is executing user/system code.\n"
                    "- Throughput: Number of processes completed per unit time.\n"
                    "- Turnaround Time (TAT): Time from arrival to completion (TAT = Completion - Arrival).\n"
                    "- Waiting Time (WT): Total time spent waiting in ready queue (WT = TAT - Burst).\n"
                    "- Response Time (RT): Time from arrival to first execution start (RT = First Start - Arrival).\n\n"
                    "Algorithms compared in SLARAP:\n"
                    "1. FCFS: Simple, non-preemptive. Suffers from Convoy Effect (short jobs stuck behind long job).\n"
                    "2. SJF: Provably optimal minimum average waiting time, but requires predicting future bursts.\n"
                    "3. SRTF: Preemptive version of SJF.\n"
                    "4. Priority: Preemptive or non-preemptive. Suffers from starvation (mitigated by aging).\n"
                    "5. Round Robin (RR): Time quantum driven, highly responsive for time-sharing systems.\n"
                    "6. MLFQ: Multiple queues with dynamic priority adjustment based on CPU burst history.\n\n"
                    "Textbook vs Modern Linux:\n"
                    "While textbooks teach Round Robin and SJF, modern Linux (kernel 2.6.23+) uses the Completely Fair Scheduler (CFS) based on Red-Black Trees tracking `vruntime` (virtual runtime)."
                ),
                "key_takeaways": [
                    "Convoy Effect in FCFS causes high average waiting times.",
                    "Aging gradually increases priority of waiting tasks to prevent starvation.",
                    "Linux CFS schedules task with smallest `vruntime` using an O(log N) Red-Black Tree."
                ],
            },
        ],
    },
    {
        "id": "unit3",
        "number": 3,
        "title": "Process Synchronization & Deadlocks",
        "description": "Principles of concurrency, critical sections, Peterson's algorithm, semaphores, classical synchronization problems, and Banker's algorithm.",
        "topics": [
            {
                "id": "u3_sync",
                "title": "Critical Section Problem & Synchronization Primitives",
                "content": (
                    "A Critical Section (CS) is a code segment that accesses shared resources (memory, variables, files) that must not be concurrently accessed by more than one execution thread.\n\n"
                    "Three Essential Requirements for any valid solution:\n"
                    "1. Mutual Exclusion: If process Pi is executing in its CS, no other processes can execute in their CS.\n"
                    "2. Progress: If no process is executing in its CS and some processes wish to enter, only those not in their remainder section can participate in deciding who enters next.\n"
                    "3. Bounded Waiting: A bound must exist on the number of times other processes are allowed to enter their CS after a process has made a request to enter.\n\n"
                    "Primitives:\n"
                    "- Mutex: Binary lock with ownership (only owner can unlock).\n"
                    "- Semaphore: Integer variable accessed only via atomic operations `wait()` (P) and `signal()` (V).\n"
                    "- Spinlocks: Busy-waiting locks efficient for short durations in multiprocessor kernels."
                ),
                "key_takeaways": [
                    "Race conditions occur when outcome depends on non-deterministic thread execution order.",
                    "Semaphores can be Counting (arbitrary resource count) or Binary (0 or 1).",
                    "Disabling interrupts works only on uniprocessor architectures, not modern multicore SMP."
                ],
            },
            {
                "id": "u3_deadlocks",
                "title": "Deadlock Characterization & Banker's Algorithm",
                "content": (
                    "A deadlock occurs when a set of processes are blocked because each process is holding a resource and waiting for another resource held by another process in the same set.\n\n"
                    "The Four Necessary Coffman Conditions:\n"
                    "1. Mutual Exclusion: Non-shareable resource mode.\n"
                    "2. Hold and Wait: Process holds resources while waiting for more.\n"
                    "3. No Preemption: Resources cannot be forcibly taken.\n"
                    "4. Circular Wait: Closed loop of waiting dependencies (P0 -> P1 -> P2 -> P0).\n\n"
                    "Deadlock Strategies:\n"
                    "- Prevention: Invalidate at least one of the 4 Coffman conditions.\n"
                    "- Avoidance (Banker's Algorithm): Dynamically inspect resource allocation state to ensure system never enters an Unsafe state.\n"
                    "- Detection & Recovery: Allow deadlocks to occur, periodically detect cycles, and recover via process abort or resource preemption.\n"
                    "- Ignorance (Ostrich Algorithm): Assume deadlocks never occur (practically used by general-purpose OS like Linux and Windows due to performance trade-offs)."
                ),
                "key_takeaways": [
                    "Safe State: There exists a safe sequence of process execution where all processes can complete.",
                    "Unsafe State is NOT necessarily a deadlock, but deadlock can ONLY arise from an unsafe state.",
                    "Banker's Algorithm requires each process to declare its Maximum demand a priori."
                ],
            },
        ],
    },
    {
        "id": "unit4",
        "number": 4,
        "title": "Memory Management & Virtual Memory",
        "description": "Contiguous memory allocation, internal & external fragmentation, paging, segmentation, demand paging, and page replacement policies.",
        "topics": [
            {
                "id": "u4_allocation",
                "title": "Contiguous Allocation & Fragmentation",
                "content": (
                    "Techniques for assigning variable-sized memory blocks:\n"
                    "- First Fit: Allocates the first free hole large enough. Fast, minimal search overhead.\n"
                    "- Best Fit: Allocates the smallest free hole that is large enough. Leaves small leftover fragments.\n"
                    "- Worst Fit: Allocates the largest free hole. Leaves largest leftover hole, which may be more useful.\n\n"
                    "Fragmentation:\n"
                    "- Internal Fragmentation: Allocated block is larger than requested memory; unused portion within allocated block.\n"
                    "- External Fragmentation: Total free memory is sufficient to satisfy a request, but storage is fragmented into small non-contiguous chunks.\n"
                    "- Compaction: Relocates allocated memory blocks to coalesce free space into a single large hole (requires dynamic relocation at runtime)."
                ),
                "key_takeaways": [
                    "First Fit and Best Fit generally outperform Worst Fit in speed and storage utilization.",
                    "Compaction is expensive because it requires copying memory contents and updating registers.",
                    "Non-contiguous memory allocation (Paging) completely eliminates external fragmentation."
                ],
            },
            {
                "id": "u4_virtual_memory",
                "title": "Paging, Virtual Memory & Page Replacement",
                "content": (
                    "Virtual Memory decouples user logical memory from physical memory, allowing execution of processes that require more memory than is physically installed.\n\n"
                    "Paging Architecture:\n"
                    "- Physical memory divided into fixed-size blocks called Frames.\n"
                    "- Logical memory divided into same-sized blocks called Pages.\n"
                    "- Page Table maps logical Page Number (p) to physical Frame Number (f).\n"
                    "- Offset (d) remains identical in both logical and physical addresses.\n\n"
                    "Page Replacement Algorithms:\n"
                    "1. FIFO: Oldest page in memory is replaced. Can suffer from Belady's Anomaly (more frames -> more page faults!).\n"
                    "2. LRU: Replaces page that has not been referenced for the longest time. Requires hardware timestamp/stack support.\n"
                    "3. Optimal (Belady's MIN): Replaces page that will not be used for the longest period in the future. Theoretical upper bound benchmark."
                ),
                "key_takeaways": [
                    "Translation Lookaside Buffer (TLB) is high-speed associative hardware cache for page table lookups.",
                    "Page Fault causes OS trap: OS fetches page from disk swap space into free physical frame.",
                    "Belady's Anomaly shows FIFO page faults can paradoxically increase with more physical frames."
                ],
            },
        ],
    },
    {
        "id": "unit5",
        "number": 5,
        "title": "File Systems & Secondary Storage Management",
        "description": "File allocation methods, directory structures, free-space management, I/O organization, and disk scheduling algorithms.",
        "topics": [
            {
                "id": "u5_disk_scheduling",
                "title": "Disk Arm Scheduling Algorithms",
                "content": (
                    "Secondary storage disk seek time (time for read/write head to move to target cylinder) is the slowest mechanical latency.\n\n"
                    "Disk Scheduling Algorithms:\n"
                    "- FCFS: Fair, no starvation, but wildly oscillating head movement.\n"
                    "- SSTF (Shortest Seek Time First): Services closest pending request to current head position. Minimizes average seek time, but prone to starvation of distant requests.\n"
                    "- SCAN (Elevator): Sweeps to boundary cylinder in one direction, reverses, and sweeps back. Provides uniform wait times.\n"
                    "- C-SCAN (Circular SCAN): Sweeps in one direction to boundary, then returns directly to beginning without servicing on return trip. More uniform waiting time than SCAN.\n"
                    "- LOOK & C-LOOK: Optimization of SCAN/C-SCAN that reverses at furthest request without traveling all the way to cylinder 0 or max."
                ),
                "key_takeaways": [
                    "Seek time dominates disk I/O performance (much larger than rotational latency or transfer time).",
                    "SSTF is the disk equivalent of SJF and suffers from potential starvation.",
                    "LOOK and C-LOOK avoid wasted arm travel to extreme disk boundaries."
                ],
            },
            {
                "id": "u5_file_allocation",
                "title": "File Allocation Methods & Free Space Management",
                "content": (
                    "Three primary file allocation methods:\n"
                    "1. Contiguous Allocation:\n"
                    "   - File occupies consecutive disk blocks.\n"
                    "   - Directory stores: (Start Block, Length).\n"
                    "   - Excellent sequential and random direct access; suffers from external fragmentation and dynamic growth difficulties.\n\n"
                    "2. Linked Allocation:\n"
                    "   - Each block contains a pointer to the next block in chain.\n"
                    "   - Directory stores: (Start Block, End Block).\n"
                    "   - No external fragmentation; poor direct access (O(N) traversal), pointer storage overhead.\n\n"
                    "3. Indexed Allocation:\n"
                    "   - Each file has an Index Block containing array of pointers to data blocks.\n"
                    "   - Fast direct access, no external fragmentation, index block overhead for small files.\n\n"
                    "Free Space Management:\n"
                    "- Bit Vector (Bitmap): 1 bit per block (0=free, 1=allocated). Compact and efficient with CPU bitwise instructions.\n"
                    "- Linked Free List: Pointers chain free blocks together."
                ),
                "key_takeaways": [
                    "Linux Ext4 and modern file systems use Extents (contiguous ranges of blocks) and multi-level indexed tree structures.",
                    "FAT (File Allocation Table) is a cached variation of linked allocation.",
                    "Inodes in UNIX store file metadata and direct, single-indirect, double-indirect, and triple-indirect block pointers."
                ],
            },
        ],
    },
    {
        "id": "unit6",
        "number": 6,
        "title": "Linux Kernel Internals & Android OS Architecture",
        "description": "Linux boot process, system call dispatch, interrupt handling, and the complete 6-layer Android Open Source Project (AOSP) software stack.",
        "topics": [
            {
                "id": "u6_linux_internals",
                "title": "Linux Kernel Architecture & Boot Sequence",
                "content": (
                    "Linux Kernel Architecture:\n"
                    "- User Space: User applications, GNU C library (`glibc`), shell utilities.\n"
                    "- System Call Interface (SCI): Trap/software interrupt (`sysenter`/`syscall`) transitioning CPU from Ring 3 (user) to Ring 0 (kernel).\n"
                    "- Kernel Subsystems: Process Scheduler, Virtual File System (VFS), Memory Management Subsystem, Network Stack, Inter-Process Communication (IPC), Device Drivers.\n\n"
                    "Linux Boot Process Stages:\n"
                    "1. BIOS / UEFI: Performs Power-On Self-Test (POST), initializes base hardware, loads MBR/EFI bootloader.\n"
                    "2. Bootloader (GRUB2): Loads Linux kernel image (`vmlinuz`) and initial RAM disk (`initrd` / `initramfs`) into RAM.\n"
                    "3. Kernel Initialization: Decompresses kernel, sets up CPU page tables, mounts temporary rootfs, detects devices via drivers.\n"
                    "4. Systemd / Init (PID 1): The ancestor process of all user-space processes. Starts system targets, mounts real root filesystem, spawns daemons, and presents login prompt."
                ),
                "key_takeaways": [
                    "System calls switch CPU privilege level via CPU architecture-specific hardware instructions.",
                    "PID 1 (`systemd` or classical `init`) is the first user-space process and adopts orphaned processes.",
                    "Linux Virtual File System (VFS) provides a unified object-oriented interface for diverse filesystems (ext4, btrfs, NFS, procfs, sysfs)."
                ],
            },
            {
                "id": "u6_android_stack",
                "title": "Android OS Architecture (6 Layers) & Ecosystem",
                "content": (
                    "Android is an open-source, Linux-based software stack designed primarily for mobile devices.\n\n"
                    "The 6 Layers of Android Architecture (Top to Bottom):\n"
                    "1. System & User Applications: Launcher, Dial, Browser, Contacts, Third-party apps.\n"
                    "2. Application Framework: High-level Java/Kotlin APIs providing services (Activity Manager, Window Manager, Content Providers, View System, Notification Manager).\n"
                    "3. Android Runtime (ART) & Core Libraries: Ahead-of-Time (AOT) and Just-in-Time (JIT) compilation of DEX bytecode; replaces legacy Dalvik VM.\n"
                    "4. Native C/C++ Libraries: Surface Manager, Media Framework, SQLite, WebKit, OpenGL ES, Bionic libc.\n"
                    "5. Hardware Abstraction Layer (HAL): Standardized C/C++ interfaces (Camera, Audio, Bluetooth, Sensors, GPS) that bridge framework Java APIs to proprietary hardware drivers.\n"
                    "6. Linux Kernel Layer: Underlying modified Linux kernel managing low-level memory, power (Wakelocks), drivers, security (SELinux, app sandbox UID/GID), and low-memory killer (LMK)."
                ),
                "key_takeaways": [
                    "Android uses the Linux kernel for drivers, memory, and security, but does NOT use GNU C library (uses Bionic libc).",
                    "Each Android app runs in its own isolated process with its own unique Linux UID (sandboxing).",
                    "ART compiles DEX bytecode directly into native machine code for superior execution performance."
                ],
            },
        ],
    },
]


MISSIONS_CATALOG = [
    {
        "id": "mission_fcfs_run",
        "title": "First Step into CPU Scheduling",
        "unit_id": "unit2",
        "category": "simulation",
        "difficulty": "Beginner",
        "xp_reward": 50,
        "description": "Execute a complete FCFS scheduling simulation with at least 3 processes and examine its Gantt chart.",
        "badge_unlock": "Process Explorer",
    },
    {
        "id": "mission_rr_quantum",
        "title": "Master of Time Slicing",
        "unit_id": "unit2",
        "category": "simulation",
        "difficulty": "Intermediate",
        "xp_reward": 75,
        "description": "Run a Round Robin simulation with a custom time quantum and observe how quantum size impacts context switches and waiting time.",
        "badge_unlock": "Scheduling Specialist",
    },
    {
        "id": "mission_race_condition",
        "title": "Concurrency Duel: Mutex vs Race Condition",
        "unit_id": "unit3",
        "category": "simulation",
        "difficulty": "Intermediate",
        "xp_reward": 75,
        "description": "Simulate a race condition on a shared counter without a mutex, observe lost updates, then re-run with Mutex protection.",
        "badge_unlock": "Synchronization Defender",
    },
    {
        "id": "mission_bankers_safety",
        "title": "The Safe Banker",
        "unit_id": "unit3",
        "category": "simulation",
        "difficulty": "Advanced",
        "xp_reward": 100,
        "description": "Perform Banker's algorithm safety verification on a multi-resource system and find the safe execution sequence.",
        "badge_unlock": "Deadlock Detective",
    },
    {
        "id": "mission_page_replacement_compare",
        "title": "Virtual Memory Benchmark",
        "unit_id": "unit4",
        "category": "simulation",
        "difficulty": "Intermediate",
        "xp_reward": 80,
        "description": "Compare FIFO and LRU page replacement on a reference string and calculate page fault reduction.",
        "badge_unlock": "Memory Master",
    },
    {
        "id": "mission_disk_scan",
        "title": "Elevator Optimization",
        "unit_id": "unit5",
        "category": "simulation",
        "difficulty": "Intermediate",
        "xp_reward": 80,
        "description": "Simulate SCAN or LOOK disk scheduling and observe how directional sweeping reduces total head movement compared to FCFS.",
        "badge_unlock": "Disk Scheduling Expert",
    },
    {
        "id": "mission_kernel_android_quiz",
        "title": "Kernel & Android Architecture Scholar",
        "unit_id": "unit6",
        "category": "quiz",
        "difficulty": "Advanced",
        "xp_reward": 100,
        "description": "Score 100% on the Unit 6 Linux Kernel Internals and Android OS Architecture knowledge check.",
        "badge_unlock": "Kernel Explorer",
    },
    {
        "id": "mission_grandmaster",
        "title": "Operating Systems Grandmaster",
        "unit_id": "system",
        "category": "challenge",
        "difficulty": "Master",
        "xp_reward": 250,
        "description": "Complete all 6 unit syllabus lessons, simulations, and achieve at least 500 total XP.",
        "badge_unlock": "OS Master",
    },
]


BADGES_CATALOG = [
    {
        "id": "badge_process_explorer",
        "title": "Process Explorer",
        "description": "Created and visualized process states, PCB fields, and FCFS execution progression.",
        "icon": "Cpu",
    },
    {
        "id": "badge_scheduling_specialist",
        "title": "Scheduling Specialist",
        "description": "Mastered preemption, Round Robin time slicing, and Multilevel Feedback Queues.",
        "icon": "Gauge",
    },
    {
        "id": "badge_synchronization_defender",
        "title": "Synchronization Defender",
        "description": "Prevented race conditions, eliminated deadlocks, and enforced mutual exclusion.",
        "icon": "ShieldCheck",
    },
    {
        "id": "badge_deadlock_detective",
        "title": "Deadlock Detective",
        "description": "Solved Banker's algorithm safe sequences and detected RAG circular wait dependencies.",
        "icon": "KeyRound",
    },
    {
        "id": "badge_memory_master",
        "title": "Memory Master",
        "description": "Conquered contiguous fit algorithms, paging address translation, and LRU replacement.",
        "icon": "Layers",
    },
    {
        "id": "badge_disk_expert",
        "title": "Disk Scheduling Expert",
        "description": "Minimized cylinder traversal and optimized seek times with SCAN, C-SCAN, and LOOK.",
        "icon": "Disc",
    },
    {
        "id": "badge_kernel_explorer",
        "title": "Kernel Explorer",
        "description": "Unveiled the Linux boot process, system call dispatch, and Android's 6-layer architecture.",
        "icon": "Terminal",
    },
    {
        "id": "badge_os_master",
        "title": "OS Master",
        "description": "Achieved mastery across all six Operating Systems syllabus domains in SLARAP.",
        "icon": "Trophy",
    },
]


KNOWLEDGE_CHECKS = {
    "unit1": [
        {
            "id": "q1_1",
            "question": "Which kernel architecture runs device drivers, file systems, and network stacks as user-space servers?",
            "options": [
                "Monolithic Kernel",
                "Microkernel",
                "Modular Monolithic Kernel",
                "Exokernel without abstraction"
            ],
            "correct_index": 1,
            "explanation": "Microkernels (e.g. Mach, QNX) minimize kernel space to bare essentials and execute drivers and file systems as user-space processes communicating via IPC."
        },
        {
            "id": "q1_2",
            "question": "What is the primary mechanism by which a user-mode application requests a service from the operating system kernel?",
            "options": [
                "Direct memory jump to kernel address",
                "System Call via software interrupt / hardware trap",
                "Modifying the CPU control register CR0 directly",
                "Reading the /dev/null device file"
            ],
            "correct_index": 1,
            "explanation": "System calls safely transition the processor from user mode (Ring 3) to kernel mode (Ring 0) using privileged software traps or instructions like `syscall` / `sysenter`."
        },
    ],
    "unit2": [
        {
            "id": "q2_1",
            "question": "Which CPU scheduling algorithm guarantees the minimum average waiting time for a set of stationary processes?",
            "options": [
                "First-Come, First-Served (FCFS)",
                "Round Robin (RR)",
                "Shortest Job First (SJF / SRTF)",
                "Static Priority Scheduling"
            ],
            "correct_index": 2,
            "explanation": "SJF (and its preemptive version SRTF) is mathematically provable to provide the minimum average waiting time by always executing the shortest job first."
        },
        {
            "id": "q2_2",
            "question": "In Round Robin scheduling, what happens if the time quantum is set arbitrarily large (larger than the longest burst)?",
            "options": [
                "It causes CPU starvation",
                "It degenerates into First-Come, First-Served (FCFS)",
                "Context switches increase exponentially",
                "Throughput drops to zero"
            ],
            "correct_index": 1,
            "explanation": "If the time quantum exceeds the burst time of every process, every process runs to completion on its first dispatch, exactly mimicking FCFS."
        },
    ],
    "unit3": [
        {
            "id": "q3_1",
            "question": "Which of the following is NOT one of Coffman's four necessary conditions for a deadlock?",
            "options": [
                "Mutual Exclusion",
                "Hold and Wait",
                "Preemption Allowed",
                "Circular Wait"
            ],
            "correct_index": 2,
            "explanation": "The condition is 'No Preemption' (resources CANNOT be preempted). If preemption is allowed, deadlocks cannot persist."
        },
        {
            "id": "q3_2",
            "question": "In Banker's Algorithm, what defines a 'Safe State'?",
            "options": [
                "A state where all resources are immediately available",
                "A state for which there exists at least one order (safe sequence) in which all processes can finish",
                "A state where no process has requested more than 1 resource",
                "A state where CPU utilization is 100%"
            ],
            "correct_index": 1,
            "explanation": "A state is safe if there exists a safe sequence of processes <P1, P2, ..., Pn> such that for each Pi, its maximum need can be satisfied by current available resources plus resources held by all prior processes."
        },
    ],
    "unit4": [
        {
            "id": "q4_1",
            "question": "What is Belady's Anomaly in virtual memory page replacement?",
            "options": [
                "Page faults decrease as physical frames decrease",
                "Page faults increase as physical frames increase for certain algorithms like FIFO",
                "LRU performance approaches Optimal on small reference strings",
                "Thrashing occurs when page size is too large"
            ],
            "correct_index": 1,
            "explanation": "Belady's Anomaly describes the unexpected phenomenon where increasing the number of allocated physical frames leads to MORE page faults under FIFO replacement."
        },
        {
            "id": "q4_2",
            "question": "How does non-contiguous Paging eliminate external fragmentation?",
            "options": [
                "By compressing memory periodically",
                "By dividing physical memory into fixed-size frames, allowing any free frame to be assigned to any page",
                "By restricting process sizes to powers of two",
                "By moving all free blocks to disk swap"
            ],
            "correct_index": 1,
            "explanation": "Because physical memory is allocated in uniform, fixed-size frames, any free frame can satisfy any page request, completely avoiding external fragmentation holes."
        },
    ],
    "unit5": [
        {
            "id": "q5_1",
            "question": "Which disk arm scheduling algorithm services requests on an upward sweep, reverses at the boundary, and services requests on the downward sweep?",
            "options": [
                "FCFS",
                "SSTF",
                "SCAN (Elevator Algorithm)",
                "C-SCAN"
            ],
            "correct_index": 2,
            "explanation": "SCAN behaves like an elevator: it moves across cylinders in one direction until reaching the disk boundary, reverses, and services requests in the opposite direction."
        },
        {
            "id": "q5_2",
            "question": "What is the primary advantage of Indexed File Allocation over Linked File Allocation?",
            "options": [
                "No need for directory tables",
                "Supports direct / random access to any block without traversing the entire chain",
                "Zero storage overhead for index blocks",
                "Files cannot be fragmented"
            ],
            "correct_index": 1,
            "explanation": "Indexed allocation keeps an array of block pointers in an index block, allowing O(1) direct address calculation to any logical block offset without walking pointer chains."
        },
    ],
    "unit6": [
        {
            "id": "q6_1",
            "question": "In the 6-layer Android architecture, what is the role of the Hardware Abstraction Layer (HAL)?",
            "options": [
                "Runs Java bytecode ahead of time",
                "Provides standard C/C++ interfaces that expose device hardware capabilities to the higher-level Java framework",
                "Manages the Linux kernel scheduler",
                "Renders HTML views"
            ],
            "correct_index": 1,
            "explanation": "HAL defines standard interfaces (audio, camera, sensors, bluetooth) that enable hardware vendors to implement drivers without modifying the Android application framework layer."
        },
        {
            "id": "q6_2",
            "question": "During the Linux boot sequence, which process is executed as PID 1 to spawn all user-space services and daemons?",
            "options": [
                "systemd (or classic init)",
                "vmlinuz",
                "GRUB2",
                "swapper"
            ],
            "correct_index": 0,
            "explanation": "PID 1 is the first user-space process mounted by the kernel (historically `/sbin/init`, now `systemd` in modern distributions), which initializes all subsequent services and targets."
        },
    ],
}
