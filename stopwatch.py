import math
import tkinter as tk
from time import perf_counter


class StopwatchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wristwatch Stopwatch")
        self.geometry("520x700")
        self.minsize(480, 650)
        self.configure(bg="#0f172a")

        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        self._timer_id = None
        self._laps = []

        self._build_ui()
        self.bind("<Configure>", self._on_resize)
        self._sync_state()
        self._update_display(self._elapsed)

    def _build_ui(self):
        shell = tk.Frame(self, bg="#0f172a", padx=22, pady=24)
        shell.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(shell, bg="#111827", padx=18, pady=14)
        top_bar.pack(fill=tk.X, pady=(0, 18))

        self.title_label = tk.Label(
            top_bar,
            text="Watch Stopwatch",
            font=("Segoe UI", 22, "bold"),
            bg="#111827",
            fg="#f8fafc",
        )
        self.title_label.pack(anchor="w")

        self.status_label = tk.Label(
            top_bar,
            text="READY",
            font=("Segoe UI", 10, "bold"),
            bg="#1e293b",
            fg="#cbd5e1",
            padx=10,
            pady=5,
        )
        self.status_label.pack(anchor="w", pady=(8, 0))

        watch_panel = tk.Frame(shell, bg="#111827", padx=18, pady=18)
        watch_panel.pack(fill=tk.X, pady=(0, 18))

        watch_canvas = tk.Canvas(
            watch_panel,
            width=260,
            height=260,
            bg="#111827",
            highlightthickness=0,
        )
        watch_canvas.pack(anchor="center")
        self.watch_canvas = watch_canvas

        self._draw_watch_face()

        self.time_label = tk.Label(
            watch_panel,
            text="00:00:00.00",
            font=("Segoe UI", 24, "bold"),
            bg="#111827",
            fg="#f8fafc",
        )
        self.time_label.pack(anchor="center", pady=(10, 0))

        controls = tk.Frame(shell, bg="#0f172a")
        controls.pack(fill=tk.X, pady=(0, 16))

        self.start_button = self._make_button(
            controls,
            "Start",
            "#22c55e",
            "#16a34a",
            self.start,
        )
        self.start_button.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.pause_button = self._make_button(
            controls,
            "Pause",
            "#f59e0b",
            "#d97706",
            self.pause,
        )
        self.pause_button.grid(row=0, column=1, padx=(8, 8), pady=8, sticky="ew")

        self.reset_button = self._make_button(
            controls,
            "Reset",
            "#ef4444",
            "#dc2626",
            self.reset,
        )
        self.reset_button.grid(row=1, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.lap_button = self._make_button(
            controls,
            "Lap",
            "#3b82f6",
            "#2563eb",
            self.record_lap,
        )
        self.lap_button.grid(row=1, column=1, padx=(8, 0), pady=8, sticky="ew")

        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)

        lap_frame = tk.Frame(
            shell,
            bg="#111827",
            highlightbackground="#334155",
            highlightthickness=1,
            padx=12,
            pady=12,
        )
        lap_frame.pack(fill=tk.BOTH, expand=True)

        self.lap_header = tk.Label(
            lap_frame,
            text="Recent laps",
            font=("Segoe UI", 13, "bold"),
            bg="#111827",
            fg="#e2e8f0",
            anchor="w",
        )
        self.lap_header.pack(fill=tk.X, pady=(0, 8))

        self.lap_list = tk.Listbox(
            lap_frame,
            height=7,
            font=("Segoe UI", 11),
            bg="#111827",
            fg="#f8fafc",
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
            relief=tk.FLAT,
        )
        self.lap_list.pack(fill=tk.BOTH, expand=True)

    def _draw_watch_face(self):
        canvas = self.watch_canvas
        canvas.delete("all")
        w = max(200, min(canvas.winfo_width(), canvas.winfo_height()))
        cx, cy, r = w / 2, w / 2, w * 0.42

        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#1e293b", outline="#94a3b8", width=3)
        canvas.create_oval(cx - r + 12, cy - r + 12, cx + r - 12, cy + r - 12, fill="#0f172a", outline="#334155", width=2)

        for tick in range(60):
            angle = math.radians(tick * 6)
            outer_x = cx + math.cos(angle) * (r - 12)
            outer_y = cy + math.sin(angle) * (r - 12)
            inner_x = cx + math.cos(angle) * (r - 24)
            inner_y = cy + math.sin(angle) * (r - 24)
            width = 3 if tick % 5 == 0 else 1
            canvas.create_line(outer_x, outer_y, inner_x, inner_y, fill="#e2e8f0", width=width)

        canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="#f8fafc")

        self.watch_hands = {
            "hour": canvas.create_line(cx, cy, cx, cy - r * 0.45, fill="#f8fafc", width=5, capstyle="round"),
            "minute": canvas.create_line(cx, cy, cx + r * 0.52, cy - r * 0.09, fill="#22d3ee", width=3, capstyle="round"),
            "second": canvas.create_line(cx, cy, cx + r * 0.62, cy + r * 0.05, fill="#f87171", width=2, capstyle="round"),
        }

    def _update_watch_hands(self, total_seconds: float):
        canvas = self.watch_canvas
        if not canvas.winfo_exists():
            return
        w = max(200, min(canvas.winfo_width(), canvas.winfo_height()))
        cx, cy = w / 2, w / 2
        r = w * 0.42

        minutes = (total_seconds % 3600) / 60
        hours = (total_seconds // 3600) % 12
        hour_angle = (hours + minutes / 60) * 30
        minute_angle = minutes * 6
        second_angle = (total_seconds % 60) * 6

        self._rotate_hand(canvas, self.watch_hands["hour"], cx, cy, r * 0.45, hour_angle)
        self._rotate_hand(canvas, self.watch_hands["minute"], cx, cy, r * 0.52, minute_angle)
        self._rotate_hand(canvas, self.watch_hands["second"], cx, cy, r * 0.62, second_angle)

    def _rotate_hand(self, canvas, item_id, cx, cy, length, angle_deg):
        angle = math.radians(angle_deg - 90)
        end_x = cx + math.cos(angle) * length
        end_y = cy + math.sin(angle) * length
        canvas.coords(item_id, cx, cy, end_x, end_y)

    def _on_resize(self, event):
        if event.widget is self:
            width = self.winfo_width()
            height = self.winfo_height()
            size = min(width, height - 260)
            target = max(220, min(320, size))
            self.watch_canvas.config(width=target, height=target)
            self._draw_watch_face()
            self._update_display(self._elapsed)

    def _make_button(self, parent, text, color, hover_color, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            bg=color,
            fg="white",
            activebackground=hover_color,
            activeforeground="white",
            bd=0,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            cursor="hand2",
            command=command,
        )
        btn.bind("<Enter>", lambda event, c=hover_color: btn.config(bg=c))
        btn.bind("<Leave>", lambda event, c=color: btn.config(bg=c))
        return btn

    def _format_time(self, total_seconds: float) -> str:
        total_seconds = max(0.0, total_seconds)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        hundredths = int((total_seconds % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"

    def _update_display(self, elapsed_time: float):
        self.time_label.config(text=self._format_time(elapsed_time))
        self._update_watch_hands(elapsed_time)

    def _sync_state(self):
        if self._running:
            self.status_label.config(text="RUNNING", bg="#14532d", fg="#dcfce7")
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.lap_button.config(state=tk.NORMAL)
        else:
            if self._elapsed > 0:
                self.status_label.config(text="PAUSED", bg="#78350f", fg="#fef3c7")
            else:
                self.status_label.config(text="READY", bg="#1e293b", fg="#cbd5e1")
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.lap_button.config(state=tk.DISABLED)

    def _tick(self):
        if not self._running:
            return
        elapsed = perf_counter() - self._start_time
        self._elapsed = elapsed
        self._update_display(elapsed)
        self._timer_id = self.after(10, self._tick)

    def start(self):
        if self._running:
            return
        self._running = True
        self._start_time = perf_counter() - self._elapsed
        self._sync_state()
        self._tick()

    def pause(self):
        if not self._running:
            return
        self._running = False
        self._elapsed = perf_counter() - self._start_time
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._update_display(self._elapsed)
        self._sync_state()

    def reset(self):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        self._laps.clear()
        self.lap_list.delete(0, tk.END)
        self._update_display(self._elapsed)
        self._sync_state()

    def record_lap(self):
        if not self._running:
            return
        lap_time = perf_counter() - self._start_time
        label = f"Lap {len(self._laps) + 1}: {self._format_time(lap_time)}"
        self._laps.insert(0, label)
        self.lap_list.delete(0, tk.END)
        for lap in self._laps:
            self.lap_list.insert(tk.END, lap)


if __name__ == "__main__":
    app = StopwatchApp()
    app.mainloop()
