import tkinter as tk
from tkinter import ttk
from time import perf_counter


class StopwatchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stopwatch")
        self.geometry("420x520")
        self.minsize(360, 480)
        self.configure(bg="#f3f4f6")

        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        self._timer_id = None
        self._laps = []

        self._build_ui()
        self._update_display(self._elapsed)

    def _build_ui(self):
        title = tk.Label(
            self,
            text="Stopwatch",
            font=("Segoe UI", 24, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        title.pack(pady=(20, 5))

        self.time_label = tk.Label(
            self,
            text="00:00:00.00",
            font=("Segoe UI", 40, "bold"),
            bg="#f3f4f6",
            fg="#0f172a",
        )
        self.time_label.pack(pady=10)

        button_frame = tk.Frame(self, bg="#f3f4f6")
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="Start",
            width=10,
            height=2,
            font=("Segoe UI", 12, "bold"),
            bg="#22c55e",
            fg="white",
            command=self.start,
        )
        self.start_button.grid(row=0, column=0, padx=8, pady=8)

        self.pause_button = tk.Button(
            button_frame,
            text="Pause",
            width=10,
            height=2,
            font=("Segoe UI", 12, "bold"),
            bg="#f59e0b",
            fg="white",
            command=self.pause,
        )
        self.pause_button.grid(row=0, column=1, padx=8, pady=8)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            width=10,
            height=2,
            font=("Segoe UI", 12, "bold"),
            bg="#ef4444",
            fg="white",
            command=self.reset,
        )
        self.reset_button.grid(row=1, column=0, padx=8, pady=8)

        self.lap_button = tk.Button(
            button_frame,
            text="Lap",
            width=10,
            height=2,
            font=("Segoe UI", 12, "bold"),
            bg="#3b82f6",
            fg="white",
            command=self.record_lap,
        )
        self.lap_button.grid(row=1, column=1, padx=8, pady=8)

        lap_title = tk.Label(
            self,
            text="Laps",
            font=("Segoe UI", 16, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        lap_title.pack(pady=(10, 5))

        self.lap_list = tk.Listbox(
            self,
            width=28,
            height=10,
            font=("Segoe UI", 11),
            bg="white",
            fg="#111827",
            activestyle="none",
        )
        self.lap_list.pack(padx=15, pady=(0, 15), fill=tk.BOTH, expand=True)

    def _format_time(self, total_seconds: float) -> str:
        total_seconds = max(0.0, total_seconds)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        hundredths = int((total_seconds % 1) * 100)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"

    def _update_display(self, elapsed_time: float):
        self.time_label.config(text=self._format_time(elapsed_time))

    def _tick(self):
        if not self._running:
            return
        elapsed = perf_counter() - self._start_time
        self._update_display(elapsed)
        self._timer_id = self.after(10, self._tick)

    def start(self):
        if self._running:
            return
        self._running = True
        self._start_time = perf_counter() - self._elapsed
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

    def record_lap(self):
        if not self._running:
            return
        lap_time = perf_counter() - self._start_time
        self._laps.insert(0, f"Lap {len(self._laps) + 1}: {self._format_time(lap_time)}")
        self.lap_list.delete(0, tk.END)
        for lap in self._laps:
            self.lap_list.insert(tk.END, lap)


if __name__ == "__main__":
    app = StopwatchApp()
    app.mainloop()
