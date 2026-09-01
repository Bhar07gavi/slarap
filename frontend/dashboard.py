from backend.automation.engine import Task
"""
SLARAP GUI Dashboard (Tkinter + matplotlib).

Provides:
- Live CPU/Memory/Disk/Network graphs
- System cards (health score, uptime, load, etc.)
- Process table (killable)
- Recent alerts list
- Quick command execution
- Predictions + recommendations tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from backend.monitor.resources import (
    calculate_health_score,
    human_uptime,
)
from backend.procmgr import manager
from backend.analytics import predictor, recommender


class SLARAPDashboard(tk.Tk):
    """Main GUI window."""

    def __init__(self, monitor, alerts, engine, scheduler):
        super().__init__()

        self.monitor = monitor
        self.alerts = alerts
        self.engine = engine
        self.scheduler = scheduler

        self.title("SLARAP — Smart Linux Automation & Resource Analytics")
        self.geometry("1200x800")
        self.configure(bg="#0f172a")

        self._build_ui()
        self.after(1500, self._refresh_all)

    def _build_ui(self):
        """Build all UI components."""

        # ----- Top Bar -----
        top_bar = tk.Frame(self, bg="#0f172a", height=70)
        top_bar.pack(fill="x", padx=10, pady=8)

        self.health_label = tk.Label(
            top_bar,
            text="Health: --",
            font=("Helvetica", 18, "bold"),
            fg="#4ade80",
            bg="#0f172a",
        )
        self.health_label.pack(side="left", padx=10)

        self.info_label = tk.Label(
            top_bar,
            text="",
            font=("Helvetica", 11),
            fg="#94a3b8",
            bg="#0f172a",
        )
        self.info_label.pack(side="right", padx=10)

        # ----- System Cards -----
        cards_frame = tk.Frame(self, bg="#0f172a")
        cards_frame.pack(fill="x", padx=10, pady=8)

        self.cards = {}
        card_data = [
            ("cpu", "CPU"),
            ("memory", "MEMORY"),
            ("disk", "DISK"),
            ("swap", "SWAP"),
            ("network", "NETWORK"),
            ("processes", "PROCESSES"),
        ]

        for key, title in card_data:
            card = tk.Frame(
                cards_frame,
                bg="#1e293b",
                bd=0,
                relief="flat",
                padx=10,
                pady=8,
            )
            card.pack(side="left", expand=True, fill="both", padx=4)

            tk.Label(
                card,
                text=title,
                font=("Helvetica", 9, "bold"),
                fg="#38bdf8",
                bg="#1e293b",
            ).pack(pady=(0, 4))

            value_label = tk.Label(
                card,
                text="--",
                font=("Helvetica", 20, "bold"),
                fg="white",
                bg="#1e293b",
            )
            value_label.pack()

            detail_label = tk.Label(
                card,
                text="",
                font=("Helvetica", 8),
                fg="#94a3b8",
                bg="#1e293b",
            )
            detail_label.pack(pady=(2, 0))

            self.cards[key] = (value_label, detail_label)

        # ----- Notebook (Tabs) -----
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=8)

        # Tab 1: Live Graphs
        graphs_frame = tk.Frame(notebook, bg="#0f172a")
        notebook.add(graphs_frame, text="📈 Live Graphs")

        self.figure = Figure(figsize=(11, 5), dpi=100, facecolor="#0f172a")
        self.ax1 = self.figure.add_subplot(221)
        self.ax2 = self.figure.add_subplot(222)
        self.ax3 = self.figure.add_subplot(223)
        self.ax4 = self.figure.add_subplot(224)

        for ax in (self.ax1, self.ax2, self.ax3, self.ax4):
            ax.set_facecolor("#1e293b")
            ax.tick_params(colors="#94a3b8", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#334155")

        self.figure.tight_layout(pad=3)

        self.canvas = FigureCanvasTkAgg(self.figure, master=graphs_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Tab 2: Processes
        processes_frame = tk.Frame(notebook, bg="#0f172a")
        notebook.add(processes_frame, text="⚙️ Processes")

        columns = ("pid", "name", "user", "cpu", "memory", "status")
        self.process_tree = ttk.Treeview(
            processes_frame,
            columns=columns,
            show="headings",
            height=16,
        )

        for col, width in zip(columns, (80, 200, 120, 80, 80, 100)):
            self.process_tree.heading(col, text=col.upper())
            self.process_tree.column(col, width=width)

        self.process_tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(
            processes_frame,
            command=self.process_tree.yview,
        )
        scrollbar.pack(side="right", fill="y")
        self.process_tree.configure(yscrollcommand=scrollbar.set)

        proc_buttons = tk.Frame(processes_frame, bg="#0f172a")
        proc_buttons.pack(fill="x", pady=4)

        tk.Button(
            proc_buttons,
            text="Terminate Selected",
            command=self._kill_process,
            bg="#ef4444",
            fg="white",
        ).pack(side="left", padx=5)

        tk.Button(
            proc_buttons,
            text="Refresh",
            command=self._refresh_processes,
            bg="#3b82f6",
            fg="white",
        ).pack(side="left", padx=5)

        # Tab 3: Alerts
        alerts_frame = tk.Frame(notebook, bg="#0f172a")
        notebook.add(alerts_frame, text="🔔 Alerts")

        self.alerts_text = tk.Text(
            alerts_frame,
            bg="#0f172a",
            fg="#fca5a5",
            font=("Courier", 10),
        )
        self.alerts_text.pack(fill="both", expand=True)

        # Tab 4: Automation
        automation_frame = tk.Frame(notebook, bg="#0f172a")
        notebook.add(automation_frame, text="⚡ Automation")

        top = tk.Frame(automation_frame, bg="#0f172a")
        top.pack(fill="x", pady=4)

        tk.Label(
            top,
            text="Command:",
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(side="left")

        self.cmd_entry = tk.Entry(top, width=60)
        self.cmd_entry.pack(side="left", padx=5)

        tk.Button(
            top,
            text="Run (fork+exec)",
            command=self._run_command,
            bg="#22c55e",
            fg="black",
        ).pack(side="left")

        self.cmd_output = tk.Text(
            automation_frame,
            bg="#0f172a",
            fg="#86efac",
            font=("Courier", 10),
        )
        self.cmd_output.pack(fill="both", expand=True, pady=4)

        # Tab 5: Analytics
        analytics_frame = tk.Frame(notebook, bg="#0f172a")
        notebook.add(analytics_frame, text="🧠 Analytics")

        tk.Button(
            analytics_frame,
            text="Refresh Predictions + Recommendations",
            command=self._refresh_analytics,
            bg="#a855f7",
            fg="white",
        ).pack(pady=4)

        self.analytics_text = tk.Text(
            analytics_frame,
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Courier", 9),
        )
        self.analytics_text.pack(fill="both", expand=True)

    # ----- Actions -----
    def _kill_process(self):
        selected = self.process_tree.selection()
        if not selected:
            return

        pid = int(self.process_tree.item(selected[0])["values"][0])
        if messagebox.askyesno("Confirm", f"Terminate PID {pid}?"):
            success, message = manager.kill_process(pid)
            messagebox.showinfo("Result", message)

    def _run_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return

        task = Task(name="gui_command", command=cmd, retries=0, timeout=120)
        result = self.engine.run_task(task)

        self.cmd_output.insert(
            "1.0",
            f"$ {result['command']}\n"
            f"[{result['status']}] exit={result['exit_code']} "
            f"{result['duration']}s\n"
            f"{result['output']}\n"
            f"{'-' * 60}\n",
        )

    def _refresh_analytics(self):
        predictions = predictor.predict_all(self.monitor)
        recs = recommender.generate_recommendations(self.monitor, persist=False)

        text = predictor.format_predictions(predictions)
        text += "\n\n" + recommender.format_recommendations(recs)

        self.analytics_text.delete("1.0", "end")
        self.analytics_text.insert("1.0", text)

    # ----- Refresh Methods -----
    def _refresh_all(self):
        self._refresh_cards()
        self._refresh_graphs()
        self._refresh_processes()
        self._refresh_alerts()

        self.after(2000, self._refresh_all)

    def _refresh_cards(self):
        sample = self.monitor.get_snapshot()
        if not sample:
            return

        score, label = calculate_health_score(sample)
        self.health_label.config(
            text=f"Health {score}/100 ({label})",
            fg="#4ade80" if score >= 70 else "#facc15" if score >= 40 else "#f87171",
        )

        self.info_label.config(
            text=f"Uptime {human_uptime(sample['uptime'])} | "
                 f"Load {sample['load'][0]:.2f} | "
                 f"{sample['cpu_count']} cores"
        )

        self._set_card("cpu", f"{sample['cpu']:.1f}%", f"{sample['cpu_count']} cores")
        self._set_card(
            "memory",
            f"{sample['memory']:.1f}%",
            f"{sample['memory_used_gb']}/{sample['memory_total_gb']} GB",
        )
        self._set_card("disk", f"{sample['disk']:.1f}%", f"{sample['disk_free_gb']} GB free")
        self._set_card("swap", f"{sample['swap']:.1f}%", "")
        self._set_card(
            "network",
            f"{sample['network_download_kbps']:.0f}",
            f"KB/s down | {sample['network_upload_kbps']:.0f} up",
        )
        self._set_card("processes", str(sample["process_count"]), f"{len(self.engine.get_active_runs())} workflows")

    def _set_card(self, key, value, detail):
        if key in self.cards:
            self.cards[key][0].config(text=value)
            self.cards[key][1].config(text=detail)

    def _refresh_graphs(self):
        cpu = self.monitor.get_series("cpu")
        memory = self.monitor.get_series("memory")
        disk = self.monitor.get_series("disk")

        net_down = self.monitor.get_series("network_download")
        net_up = self.monitor.get_series("network_upload")

        self._plot_series(self.ax1, cpu, "CPU %", "#38bdf8")
        self._plot_series(self.ax2, memory, "Memory %", "#a78bfa")

        self.ax3.clear()
        self.ax3.set_facecolor("#1e293b")
        self.ax3.plot(net_down, color="#4ade80", lw=1.2, label="KB/s down")
        self.ax3.plot(net_up, color="#fb923c", lw=1.2, label="KB/s up")
        self.ax3.set_title("Network (KB/s)", color="#e2e8f0", fontsize=9)
        self.ax3.legend(fontsize=7, facecolor="#1e293b", labelcolor="#e2e8f0")
        self.ax3.tick_params(colors="#94a3b8", labelsize=7)

        # Forecast
        self.ax4.clear()
        self.ax4.set_facecolor("#1e293b")
        if len(cpu) >= 5:
            forecast_vals, _ = predictor.forecast(cpu, steps=10)
            self.ax4.plot(range(len(cpu)), cpu, color="#38bdf8", lw=1.2, label="actual")
            self.ax4.plot(
                range(len(cpu), len(cpu) + len(forecast_vals)),
                forecast_vals,
                "--",
                color="#f472b6",
                lw=1.4,
                label="forecast",
            )
            self.ax4.set_ylim(0, 100)
            self.ax4.set_title("CPU Forecast", color="#e2e8f0", fontsize=9)
            self.ax4.legend(fontsize=7, facecolor="#1e293b", labelcolor="#e2e8f0")
            self.ax4.tick_params(colors="#94a3b8", labelsize=7)

        self.canvas.draw_idle()

    def _plot_series(self, ax, data, title, color):
        ax.clear()
        ax.set_facecolor("#1e293b")
        ax.plot(data, color=color, lw=1.4)
        ax.fill_between(range(len(data)), data, color=color, alpha=0.2)
        ax.set_ylim(0, 100)
        ax.set_title(title, color="#e2e8f0", fontsize=9)
        ax.tick_params(colors="#94a3b8", labelsize=7)

    def _refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        for proc in manager.top_processes(30, "cpu"):
            self.process_tree.insert(
                "",
                "end",
                values=(
                    proc["pid"],
                    (proc["name"] or "")[:36],
                    (proc.get("username") or "")[:16],
                    f"{proc.get('cpu_percent') or 0:.1f}",
                    f"{proc.get('memory_percent') or 0:.1f}",
                    proc.get("status", ""),
                ),
            )

    def _refresh_alerts(self):
        for alert in self.alerts.get_recent_alerts(30):
            self.alerts_text.insert(
                "1.0",
                f"[{alert['time']}] {alert['level']:<8} "
                f"{alert['category']:<10} {alert['message']}\n",
            )


def launch(monitor, alerts, engine, scheduler):
    """Launch the GUI dashboard (must be called from main thread)."""
    app = SLARAPDashboard(monitor, alerts, engine, scheduler)
    app.mainloop()
