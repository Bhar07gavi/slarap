import React, { useState, useEffect } from 'react';
import { 
  Smartphone, 
  Terminal, 
  CheckCircle2, 
  ShieldCheck, 
  Zap, 
  ChevronRight,
  Activity,
  Code2,
  BookOpen,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { UnitKnowledgeCheck } from '../components/UnitKnowledgeCheck';

interface BootStep {
  id: number;
  name: string;
  sub: string;
  desc: string;
  details: string[];
  icon: string;
}

const BOOT_STEPS: BootStep[] = [
  {
    id: 1,
    name: "1. BIOS / UEFI",
    sub: "Firmware Stage",
    desc: "Power-On Self-Test (POST), hardware checks, memory interrogation, and locates the primary boot device.",
    details: [
      "POST diagnostics verify CMOS RAM, CPU registers, and DMA controllers",
      "UEFI reads GPT partition table and executes EFI Boot Manager in NVRAM",
      "Loads the first 512-byte Master Boot Record (MBR) or EFI system partition (.efi binary)"
    ],
    icon: "HardDrive"
  },
  {
    id: 2,
    name: "2. Bootloader (GRUB2)",
    sub: "Grand Unified Bootloader",
    desc: "Provides the OS boot selection menu, loads the Linux kernel binary (vmlinuz) and the initial RAM disk (initrd/initramfs) into memory.",
    details: [
      "Stage 1: boot.img in MBR jumps to Stage 1.5 core.img",
      "Stage 2: Loads filesystem drivers (ext4, btrfs, xfs) to read /boot/grub/grub.cfg",
      "Transfers control to the decompression routine of the compressed vmlinuz image in protected/long mode"
    ],
    icon: "Server"
  },
  {
    id: 3,
    name: "3. Kernel Initialization",
    sub: "Ring 0 Startup",
    desc: "Unpacks vmlinuz, mounts initramfs as temporary root, detects architecture hardware, and initializes page tables, interrupt vectors, and core subsystems.",
    details: [
      "Initializes CPU control registers (CR0-CR4), sets up IDT (Interrupt Descriptor Table)",
      "Starts memory management (Buddy allocator, SLUB slab cache)",
      "Unpacks initramfs containing crucial storage/RAID drivers",
      "Mounts the genuine root filesystem read-only (/) and executes /sbin/init"
    ],
    icon: "Cpu"
  },
  {
    id: 4,
    name: "4. Systemd (PID 1)",
    sub: "Userspace Orchestrator",
    desc: "The mother of all userspace processes (PID 1). Replaces legacy SysV init with parallel socket/D-Bus activation of system units.",
    details: [
      "Reads default.target (graphical.target or multi-user.target)",
      "Spawns daemon processes via parallel dependency graph resolution",
      "Mounts filesystems listed in /etc/fstab read-write",
      "Initializes network interfaces, syslog, display manager (GDM/LightDM), and user login shells"
    ],
    icon: "Zap"
  }
];

const SYSCALL_STAGES = [
  {
    stage: 1,
    space: "User Space (Ring 3)",
    title: "Application Library Call",
    code: 'ssize_t bytes = write(fd, "Hello", 5);',
    explanation: "User application invokes glibc wrapper function 'write()'. The application cannot directly access hardware registers due to CPU Ring 3 hardware protection."
  },
  {
    stage: 2,
    space: "Hardware Transition",
    title: "Syscall Instruction Trap",
    code: 'mov $1, %rax        # __NR_write syscall number\nmov $1, %rdi        # fd 1 (stdout)\nsyscall             # CPU ring switch (Ring 3 -> Ring 0)',
    explanation: "Glibc places the syscall ID into %rax and arguments into %rdi, %rsi, %rdx, %r10, %r8, %r9. The 'syscall' x86_64 instruction triggers CPU privilege elevation to Ring 0."
  },
  {
    stage: 3,
    space: "Kernel Space (Ring 0)",
    title: "Kernel Dispatcher & sys_call_table",
    code: 'ENTRY(entry_SYSCALL_64)\ncall *sys_call_table(, %rax, 8)  # jumps to sys_write',
    explanation: "The CPU looks up entry_SYSCALL_64 in the MSR (Model-Specific Register). The kernel saves user registers on the per-thread kernel stack, validates pointers, and indexes sys_call_table[__NR_write]."
  },
  {
    stage: 4,
    space: "Kernel Space (Ring 0)",
    title: "VFS & Device Driver Execution",
    code: 'ksys_write(fd, buf, count) -> vfs_write() -> tty_write()',
    explanation: "Virtual File System (VFS) resolves the file descriptor to a struct file*. The character device driver for stdout/tty receives the buffer and sends it to the terminal screen buffer."
  },
  {
    stage: 5,
    space: "Hardware Transition",
    title: "Return to User Space",
    code: 'sysretq             # CPU ring drop (Ring 0 -> Ring 3)\n# %rax contains return code (5 bytes written)',
    explanation: "Kernel restores user registers from kernel stack. The 'sysretq' instruction resets CPU CPL (Current Privilege Level) to Ring 3 and execution resumes in user code."
  }
];

const ANDROID_LAYERS = [
  {
    layer: 1,
    name: "System Apps",
    color: "from-blue-600 to-cyan-600",
    components: ["Phone", "Contacts", "Browser", "Camera", "Third-Party Apps (Flutter, React Native, Java/Kotlin)"],
    notes: "Run as distinct Linux UIDs (e.g., u0_a124) inside the Android Application Sandbox. No app can access another app's data without explicit IPC permissions."
  },
  {
    layer: 2,
    name: "Java API Framework",
    color: "from-indigo-600 to-blue-600",
    components: ["Activity Manager", "Window Manager", "Content Providers", "Package Manager", "Notification Manager", "Resource Manager"],
    notes: "Exposes the complete Android feature set to apps via high-level Java/Kotlin APIs. Translates requests into Binder IPC calls to system daemons."
  },
  {
    layer: 3,
    name: "Android Runtime (ART) & Native C/C++ Libraries",
    color: "from-purple-600 to-indigo-600",
    components: ["ART (AOT + JIT Compiler)", "Zygote Process", "Bionic Libc", "WebKit / Chromium", "OpenGL ES / Vulkan", "SQLite", "OpenSSL / BoringSSL"],
    notes: "ART compiles DEX bytecode to native machine code. Zygote pre-loads common classes at boot and forks every new app with Copy-On-Write memory sharing."
  },
  {
    layer: 4,
    name: "Hardware Abstraction Layer (HAL)",
    color: "from-amber-600 to-purple-600",
    components: ["Camera HAL (HIDL/AIDL)", "Audio HAL", "Bluetooth HAL", "Sensors HAL", "Gralloc (Graphics Allocator)", "Biometrics HAL"],
    notes: "Standardized C++ interfaces allowing Android Framework to communicate with vendor-proprietary hardware drivers without exposing proprietary silicon IP."
  },
  {
    layer: 5,
    name: "Linux Kernel (Customized)",
    color: "from-emerald-600 to-teal-600",
    components: ["Binder IPC Driver (/dev/binder)", "Low Memory Killer (LMK/PSI)", "Ashmem (Anonymous Shared Memory)", "WakeLocks & Power Management", "SELinux Mandatory Access Control"],
    notes: "Core Linux OS provides hardware abstraction, device drivers, virtual memory, and process isolation. Enhanced with Android-specific IPC (Binder) and aggressive memory reclamation (LMK)."
  }
];

export const Unit6KernelAndroidPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'boot' | 'syscall' | 'android' | 'monolithic'>('boot');
  const [currentBootStep, setCurrentBootStep] = useState<number>(1);
  const [currentSyscallStep, setCurrentSyscallStep] = useState<number>(1);
  const [selectedAndroidLayer, setSelectedAndroidLayer] = useState<number>(1);
  const [showTheory, setShowTheory] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  useEffect(() => {
    try {
      if (localStorage.getItem('slarap_completed_unit6') === 'true') {
        setIsCompleted(true);
      }
    } catch {
      // ignore
    }
  }, []);

  const toggleCompleted = () => {
    const next = !isCompleted;
    setIsCompleted(next);
    try {
      localStorage.setItem('slarap_completed_unit6', String(next));
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-6">
      {/* Unit Header */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
              Unit 6
            </span>
            <h2 className="text-lg font-bold text-white">Linux Kernel & Android OS</h2>
          </div>
          <p className="text-xs text-slate-400">
            Monolithic kernel internals, 4-stage boot sequence, syscall dispatch, and Android 5-layer stack.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Topic Completion Indicator */}
          <button
            onClick={toggleCompleted}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
              isCompleted
                ? 'bg-emerald-950/70 text-emerald-400 border-emerald-800'
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <CheckCircle2 size={14} className={isCompleted ? 'text-emerald-400' : 'text-slate-500'} />
            <span>{isCompleted ? 'Topic Completed' : 'Mark Completed'}</span>
          </button>

          {/* Learn More Accordion Toggle */}
          <button
            onClick={() => setShowTheory((prev) => !prev)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition"
          >
            <BookOpen size={14} />
            <span>{showTheory ? 'Hide Theory' : 'Learn More'}</span>
            {showTheory ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>
      </div>

      {/* Expandable Theory Section */}
      {showTheory && (
        <div className="p-5 rounded-xl bg-slate-950 border border-slate-800 space-y-4 text-xs text-slate-300">
          <h4 className="font-bold text-white text-sm">Kernel Internals & Android OS Architecture</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-cyan-400 block">Linux Boot Sequence</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                <strong>1. BIOS/UEFI:</strong> POST hardware diagnostics.<br />
                <strong>2. GRUB2:</strong> Loads compressed kernel image (vmlinuz) & initramfs into RAM.<br />
                <strong>3. Kernel:</strong> Initializes memory & devices, mounts root filesystem.<br />
                <strong>4. systemd (PID 1):</strong> Starts user space daemons in parallel.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-indigo-400 block">System Call Dispatch Cycle</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Application calls glibc wrapper &rarr; places syscall ID in `%rax` register &rarr; triggers `syscall` instruction &rarr; hardware elevates to Ring 0 &rarr; looks up `sys_call_table` &rarr; executes handler &rarr; drops back to Ring 3 via `sysretq`.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 space-y-1">
              <span className="font-semibold text-emerald-400 block">Android OS Enhancements</span>
              <p className="text-slate-400 leading-relaxed text-[11px]">
                Runs on a modified Linux kernel. Key custom components include <strong>Binder IPC</strong> for high-speed inter-process communication, <strong>Zygote</strong> process for fast app forking, and <strong>Low Memory Killer (LMK)</strong> for aggressive mobile memory reclamation.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lab Challenge Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <span className="font-bold text-indigo-400 uppercase tracking-wider text-[10px]">
            Lab Challenge:
          </span>
          <span className="text-slate-300">
            Step through the 5 stages of the Linux System Call Dispatch Cycle to observe user space %rax register elevation to Ring 0!
          </span>
        </div>
      </div>

      {/* Tab Selectors */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-900 border border-slate-800 rounded-xl">
        <button
          onClick={() => setActiveTab('boot')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'boot' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Boot Sequence
        </button>
        <button
          onClick={() => setActiveTab('syscall')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'syscall' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Syscall Dispatch
        </button>
        <button
          onClick={() => setActiveTab('android')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'android' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Android Stack
        </button>
        <button
          onClick={() => setActiveTab('monolithic')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
            activeTab === 'monolithic' ? 'bg-cyan-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Kernel Architectures
        </button>
      </div>

      {/* TAB 1: BOOT SEQUENCE */}
      {activeTab === 'boot' && (
        <div className="space-y-6">
          {/* Stepper overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {BOOT_STEPS.map((step) => {
              const isSelected = currentBootStep === step.id;
              const isCompleted = currentBootStep > step.id;
              return (
                <button
                  key={step.id}
                  onClick={() => setCurrentBootStep(step.id)}
                  className={`p-4 rounded-xl text-left border transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/80 shadow-lg shadow-cyan-950/40'
                      : isCompleted
                      ? 'bg-slate-900/40 border-slate-700/60 hover:border-slate-600 text-slate-300'
                      : 'bg-slate-900/20 border-slate-800 text-slate-500 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono font-bold text-cyan-400">STAGE 0{step.id}</span>
                    {isCompleted ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <div className={`w-2.5 h-2.5 rounded-full ${isSelected ? 'bg-cyan-400 animate-pulse' : 'bg-slate-700'}`} />
                    )}
                  </div>
                  <div className="font-semibold text-slate-200 text-sm">{step.name.split('. ')[1]}</div>
                  <div className="text-xs text-slate-400 mt-1 truncate">{step.sub}</div>
                </button>
              );
            })}
          </div>

          {/* Active Boot Step Detailed View */}
          {(() => {
            const step = BOOT_STEPS.find(s => s.id === currentBootStep)!;
            return (
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl -z-10" />
                <div className="flex flex-col lg:flex-row gap-6">
                  <div className="flex-1 space-y-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-xs font-semibold">
                      Phase {step.id} of 4: {step.sub}
                    </div>
                    <h2 className="text-2xl font-bold text-white">{step.name}</h2>
                    <p className="text-slate-300 text-sm leading-relaxed">{step.desc}</p>

                    <div className="space-y-2 pt-2">
                      <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Low-Level Operations</h4>
                      <div className="space-y-2">
                        {step.details.map((detail, idx) => (
                          <div key={idx} className="flex items-start gap-3 bg-slate-950/40 p-3 rounded-lg border border-slate-800/80">
                            <span className="font-mono text-cyan-400 text-xs mt-0.5">#{idx + 1}</span>
                            <span className="text-xs text-slate-300 leading-normal">{detail}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 pt-4">
                      <button
                        disabled={currentBootStep <= 1}
                        onClick={() => setCurrentBootStep(c => Math.max(1, c - 1))}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium rounded-lg text-slate-200 transition-colors"
                      >
                        Previous Stage
                      </button>
                      <button
                        disabled={currentBootStep >= 4}
                        onClick={() => setCurrentBootStep(c => Math.min(4, c + 1))}
                        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-medium rounded-lg text-white transition-colors flex items-center gap-1.5"
                      >
                        Next Boot Stage
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Architecture Diagram / Terminal Mockup */}
                  <div className="w-full lg:w-96 bg-slate-950 rounded-xl border border-slate-800 p-4 font-mono text-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3 text-slate-400 text-[11px]">
                        <span className="flex items-center gap-1.5">
                          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                          dmesg | boot log preview
                        </span>
                        <span className="text-emerald-400">ACTIVE</span>
                      </div>
                      <div className="space-y-1.5 text-slate-400 leading-relaxed overflow-x-auto text-[11px]">
                        {currentBootStep === 1 && (
                          <>
                            <p className="text-cyan-400">[    0.000000] UEFI v2.70 (EDK II, 0x00010000)</p>
                            <p>[    0.000000] ACPI: RSDP 0x000000007FFE0014 000024</p>
                            <p>[    0.000000] e820: BIOS-provided physical RAM map:</p>
                            <p className="text-slate-500">[    0.000000]  BIOS-e820: [mem 0x0000000000000000-0x000000000009fbff] usable</p>
                            <p className="text-emerald-400">[    0.000000] Secure Boot disabled, booting primary EFI</p>
                          </>
                        )}
                        {currentBootStep === 2 && (
                          <>
                            <p className="text-cyan-400">[ GRUB 2.06 ] Loading Linux 6.8.0-generic ...</p>
                            <p>[ GRUB ] Loading initial ramdisk ...</p>
                            <p className="text-slate-500">vmlinuz decompressed: 14.8 MB @ 0x1000000</p>
                            <p className="text-slate-500">initrd unpacked: 48.2 MB @ 0x3400000</p>
                            <p className="text-emerald-400">Jumping to kernel start_kernel() entry point</p>
                          </>
                        )}
                        {currentBootStep === 3 && (
                          <>
                            <p className="text-cyan-400">[    0.000000] Linux version 6.8.0-generic (gcc version 13.2.0)</p>
                            <p>[    0.004210] Memory: 16182448K/16777216K available</p>
                            <p>[    0.012540] SLUB: Genslabs=28, HWalign=64, Order=0-3</p>
                            <p>[    0.158420] smpboot: CPU0: Intel(R) Core(TM) @ 3.40GHz</p>
                            <p className="text-emerald-400">[    0.842100] EXT4-fs (nvme0n1p2): mounted filesystem with ordered data mode</p>
                          </>
                        )}
                        {currentBootStep === 4 && (
                          <>
                            <p className="text-cyan-400">[    1.020110] systemd[1]: Inserted module 'autofs4'</p>
                            <p>[    1.082000] systemd[1]: systemd 255.4-1ubuntu8 running in system mode</p>
                            <p>[    1.240100] systemd[1]: Reached target Basic System.</p>
                            <p>[    1.512000] systemd[1]: Started Network Manager.</p>
                            <p className="text-emerald-400">[    1.980000] systemd[1]: Reached target Graphical Interface.</p>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="pt-3 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between">
                      <span>Privilege: {currentBootStep >= 3 ? "Ring 0 / Long Mode" : "Firmware Mode"}</span>
                      <span>Execution: x86_64</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* TAB 2: SYSCALL DISPATCH */}
      {activeTab === 'syscall' && (
        <div className="space-y-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
            <div className="max-w-2xl">
              <h2 className="text-lg font-bold text-white mb-2">Linux System Call (syscall) Dispatch Cycle</h2>
              <p className="text-sm text-slate-400">
                User processes cannot touch disk or network hardware directly. Step through the five-phase transition from User Mode (Ring 3) to Kernel Mode (Ring 0) and back.
              </p>
            </div>

            {/* Stage Selector */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-2 mt-6">
              {SYSCALL_STAGES.map((s) => (
                <button
                  key={s.stage}
                  onClick={() => setCurrentSyscallStep(s.stage)}
                  className={`p-3 rounded-xl text-left border transition-all ${
                    currentSyscallStep === s.stage
                      ? 'bg-cyan-950/60 border-cyan-500 text-cyan-200'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="text-[10px] font-mono text-cyan-400">STEP 0{s.stage}</div>
                  <div className="font-semibold text-xs truncate mt-0.5">{s.title}</div>
                  <div className="text-[10px] text-slate-500 truncate mt-1">{s.space.split(' ')[0]}</div>
                </button>
              ))}
            </div>

            {/* Active Stage Detail */}
            {(() => {
              const stage = SYSCALL_STAGES.find(s => s.stage === currentSyscallStep)!;
              const isKernel = stage.space.includes("Ring 0");
              return (
                <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        isKernel ? 'bg-amber-950/60 text-amber-300 border border-amber-800/60' : 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60'
                      }`}>
                        {stage.space}
                      </span>
                      <span className="text-xs text-slate-400">Step {stage.stage} of 5</span>
                    </div>

                    <h3 className="text-xl font-bold text-white">{stage.title}</h3>
                    <p className="text-sm text-slate-300 leading-relaxed">{stage.explanation}</p>

                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80">
                      <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Register State Transition</div>
                      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                        <div className="p-2 bg-slate-900 rounded border border-slate-800">
                          <span className="text-slate-500">%rax:</span> <span className="text-cyan-400">1 (__NR_write)</span>
                        </div>
                        <div className="p-2 bg-slate-900 rounded border border-slate-800">
                          <span className="text-slate-500">%rdi:</span> <span className="text-cyan-400">1 (STDOUT_FILENO)</span>
                        </div>
                        <div className="p-2 bg-slate-900 rounded border border-slate-800">
                          <span className="text-slate-500">%rsi:</span> <span className="text-cyan-400">0x7ffd9a... (&quot;Hello&quot;)</span>
                        </div>
                        <div className="p-2 bg-slate-900 rounded border border-slate-800">
                          <span className="text-slate-500">%rdx:</span> <span className="text-cyan-400">5 (byte count)</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Code Block */}
                  <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 font-mono text-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800 mb-3 text-slate-400 text-[11px]">
                        <span className="flex items-center gap-1.5">
                          <Code2 className="w-3.5 h-3.5 text-cyan-400" />
                          Kernel / User Interface Assembly
                        </span>
                        <span className={isKernel ? "text-amber-400 font-semibold" : "text-cyan-400 font-semibold"}>
                          {isKernel ? "SUPERVISOR MODE" : "USER MODE"}
                        </span>
                      </div>
                      <pre className="text-slate-300 whitespace-pre-wrap leading-relaxed text-[11px] bg-slate-900/60 p-3 rounded-lg border border-slate-800/50">
                        {stage.code}
                      </pre>
                    </div>

                    <div className="flex items-center justify-between pt-4 border-t border-slate-800/60">
                      <button
                        disabled={currentSyscallStep <= 1}
                        onClick={() => setCurrentSyscallStep(s => Math.max(1, s - 1))}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-xs rounded text-slate-300 transition-colors"
                      >
                        Previous
                      </button>
                      <button
                        disabled={currentSyscallStep >= 5}
                        onClick={() => setCurrentSyscallStep(s => Math.min(5, s + 1))}
                        className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 text-xs rounded text-white transition-colors"
                      >
                        Next Step
                      </button>
                    </div>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* TAB 3: ANDROID ARCHITECTURE */}
      {activeTab === 'android' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 5 Layer Interactive Stack */}
            <div className="lg:col-span-2 space-y-3">
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Smartphone className="w-4 h-4 text-emerald-400" />
                  Android 5-Layer Stack
                </h3>
                <span className="text-xs text-slate-400">Click a layer to inspect internals</span>
              </div>

              {ANDROID_LAYERS.map((layer) => {
                const isSelected = selectedAndroidLayer === layer.layer;
                return (
                  <div
                    key={layer.layer}
                    onClick={() => setSelectedAndroidLayer(layer.layer)}
                    className={`cursor-pointer rounded-xl p-4 border transition-all ${
                      isSelected
                        ? 'bg-slate-800/90 border-cyan-500 shadow-lg shadow-cyan-950/30'
                        : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className={`w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold text-white bg-gradient-to-r ${layer.color}`}>
                          L{layer.layer}
                        </span>
                        <h4 className="font-bold text-sm text-slate-100">{layer.name}</h4>
                      </div>
                      <ChevronRight className={`w-4 h-4 text-slate-500 transition-transform ${isSelected ? 'rotate-90 text-cyan-400' : ''}`} />
                    </div>

                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {layer.components.map((comp, i) => (
                        <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-slate-950/60 text-slate-300 border border-slate-800">
                          {comp}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Deep Dive Panel */}
            <div className="space-y-4">
              {(() => {
                const layer = ANDROID_LAYERS.find(l => l.layer === selectedAndroidLayer)!;
                return (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${layer.color}`} />
                      <h4 className="font-bold text-white text-sm">Layer {layer.layer}: {layer.name}</h4>
                    </div>

                    <div className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                      {layer.notes}
                    </div>

                    {/* Android Specific Mechanisms Card */}
                    <div className="space-y-3 pt-2">
                      <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">Android OS Unique Systems</div>

                      <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-cyan-400">
                          <Zap className="w-3.5 h-3.5" />
                          Binder IPC System
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">
                          Android avoids slow traditional Linux UNIX sockets or pipes. The in-kernel Binder driver (/dev/binder) implements single-copy shared memory IPC with built-in transaction tokens and UID validation.
                        </p>
                      </div>

                      <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          Application Sandbox
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">
                          Every Android app is assigned a unique Linux UID (e.g., 10124). Standard Linux discretionary access controls prevent app A from viewing app B&apos;s private storage or SQLite files.
                        </p>
                      </div>

                      <div className="p-3 bg-slate-950/40 rounded-xl border border-slate-800 space-y-1">
                        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400">
                          <Activity className="w-3.5 h-3.5" />
                          Low Memory Killer (LMK)
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">
                          Replaces standard Linux OOM (Out Of Memory) killer. Prioritizes killing inactive background cached apps first, keeping foreground UI activities and pinned services alive.
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: MONOLITHIC VS MICROKERNEL */}
      {activeTab === 'monolithic' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Monolithic */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-cyan-400">Monolithic Kernel (Linux)</h3>
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">High Performance</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              All core OS services—VFS, process scheduler, memory manager, network stack, and hardware device drivers—run in a single unified address space inside Ring 0.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div className="font-semibold text-slate-200">Key Advantages:</div>
              <ul className="list-disc list-inside text-slate-400 space-y-1">
                <li>Zero IPC overhead between subsystems (direct function calls in kernel memory)</li>
                <li>Maximum execution throughput for high-frequency I/O and packet filtering</li>
                <li>Dynamic Loadable Kernel Modules (LKMs via insmod/modprobe) for modularity without reboot</li>
              </ul>
              <div className="font-semibold text-slate-200 pt-2">Trade-offs:</div>
              <ul className="list-disc list-inside text-slate-400 space-y-1">
                <li>A single bug or null-pointer dereference in any device driver triggers a Kernel Panic</li>
                <li>Massive codebase footprint (30M+ lines of C in modern Linux)</li>
              </ul>
            </div>
          </div>

          {/* Microkernel */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-purple-400">Microkernel (Mach / seL4 / QNX)</h3>
              <span className="text-xs px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">Fault Isolation</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Keeps only the absolute bare minimum in Ring 0 (IPC, low-level memory mapping, basic thread scheduling). Drivers, filesystems, and network stacks run as isolated user-space daemons.
            </p>

            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div className="font-semibold text-slate-200">Key Advantages:</div>
              <ul className="list-disc list-inside text-slate-400 space-y-1">
                <li>Fault isolation: A crashed graphics driver simply restarts without crashing the OS</li>
                <li>Mathematically verifiable formal security (e.g., seL4 proof of correctness)</li>
                <li>High suitability for mission-critical automotive, medical, and aerospace systems</li>
              </ul>
              <div className="font-semibold text-slate-200 pt-2">Trade-offs:</div>
              <ul className="list-disc list-inside text-slate-400 space-y-1">
                <li>Message-passing IPC overhead and frequent Ring 3 &lt;-&gt; Ring 0 context switches</li>
                <li>Lower peak I/O throughput compared to monolithic architecture</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Embedded Unit Knowledge Check (Optional) */}
      <UnitKnowledgeCheck
        unitId="unit6"
        unitTitle="Unit 6: Kernel Internals & Android OS"
        onComplete={() => setIsCompleted(true)}
      />
    </div>
  );
};
