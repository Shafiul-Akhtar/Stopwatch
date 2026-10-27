
import tkinter as tk
import math
from time import perf_counter


class StopwatchApp(tk.Tk):
    BG = "#000000"
    DIAL_BG = "#101114"
    BORDER = "#292a2d"
    WHITE = "#f5f5f7"
    GREEN = "#30d158"
    RED = "#ff453a"
    CYAN = "#64d2ff"

    def __init__(self):
        super().__init__()
        self.title("Stopwatch")
        self.geometry("430x640")
        self.minsize(300, 400)
        self.configure(bg=self.BG)

        self._running = False
        self._elapsed = 0.0
        self._start_time = 0.0
        self._timer_id = None
        self._laps = []
        self._lap_start = 0.0

        self.build_ui()
        self.update_display()
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def build_ui(self):
        # Layout: title, dial, buttons, lap list
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(3, weight=1)

        header = tk.Frame(self, bg=self.BG)
        header.grid(row=0, column=0, sticky="ew",
                    padx=24, pady=(12, 4))

        tk.Label(
            header, text="Stopwatch",
            font=("Segoe UI", 22, "bold"),
            fg=self.WHITE, bg=self.BG
        ).pack(anchor="w")

        self.watch_canvas = tk.Canvas(
            self, bg=self.BG,
            highlightthickness=0, bd=0
        )
        self.watch_canvas.grid(
            row=1, column=0, sticky="nsew",
            padx=8, pady=4
        )
        self.watch_canvas.bind("<Configure>", self._draw_watch)

        # Buttons below the dial
        controls = tk.Frame(self, bg=self.BG)
        controls.grid(row=2, column=0, sticky="ew",
                      padx=24, pady=12)
        controls.columnconfigure(0, weight=1, uniform="buttons")
        controls.columnconfigure(1, weight=1, uniform="buttons")

        self.lap_button = tk.Button(
            controls, text="Reset",
            command=self.left_button_action,
            font=("Segoe UI", 14),
            fg=self.WHITE, bg="#252527",
            activebackground="#3a3a3c",
            activeforeground=self.WHITE,
            relief="flat", bd=0, cursor="hand2"
        )
        self.lap_button.grid(
            row=0, column=0, sticky="ew",
            padx=(0, 8), ipady=12
        )

        self.start_button = tk.Button(
            controls, text="Start",
            command=self.toggle_timer,
            font=("Segoe UI", 14, "bold"),
            fg=self.GREEN, bg="#102719",
            activebackground="#193c26",
            activeforeground=self.GREEN,
            relief="flat", bd=0, cursor="hand2"
        )
        self.start_button.grid(
            row=0, column=1, sticky="ew",
            padx=(8, 0), ipady=12
        )

        # Lap list at the very bottom
        lap_container = tk.Frame(self, bg=self.BG)
        lap_container.grid(
            row=3, column=0, sticky="nsew",
            padx=24, pady=(0, 8)
        )

        tk.Frame(
            lap_container, bg=self.BORDER, height=1
        ).pack(fill="x")

        list_frame = tk.Frame(lap_container, bg=self.BG)
        list_frame.pack(fill="both", expand=True, pady=4)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.lap_list = tk.Listbox(
            list_frame, bg=self.BG, fg=self.WHITE,
            selectbackground="#252527",
            selectforeground=self.WHITE,
            activestyle="none",
            highlightthickness=0, bd=0,
            font=("Segoe UI", 13),
            yscrollcommand=scrollbar.set
        )
        self.lap_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lap_list.yview)

    def _draw_watch(self, event=None):
        c = self.watch_canvas
        c.delete("all")

        width = max(c.winfo_width(), 1)
        height = max(c.winfo_height(), 1)
        radius = max(35, min(width * 0.43, height * 0.47, 175))
        cx, cy = width / 2, height / 2

        self.cx, self.cy, self.radius = cx, cy, radius

        c.create_oval(
            cx-radius, cy-radius, cx+radius, cy+radius,
            fill=self.DIAL_BG, outline=self.BORDER, width=2
        )

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            outer = radius * 0.91
            inner = radius * (0.79 if i % 5 == 0 else 0.85)

            c.create_line(
                cx + math.cos(angle) * inner,
                cy + math.sin(angle) * inner,
                cx + math.cos(angle) * outer,
                cy + math.sin(angle) * outer,
                fill="#c5c5ca" if i % 5 == 0 else "#636369",
                width=2 if i % 5 == 0 else 1,
                capstyle=tk.ROUND
            )

        pad = radius * 0.045
        self.progress_arc = c.create_arc(
            cx-radius+pad, cy-radius+pad,
            cx+radius-pad, cy+radius-pad,
            start=90, extent=0, style="arc",
            outline=self.CYAN,
            width=max(2, int(radius * 0.035))
        )

        self.second_hand = c.create_line(
            cx, cy, cx, cy-radius*0.68,
            fill=self.CYAN,
            width=max(2, int(radius*0.018)),
            capstyle=tk.ROUND
        )

        c.create_oval(
            cx-radius*0.035, cy-radius*0.035,
            cx+radius*0.035, cy+radius*0.035,
            fill=self.CYAN, outline=""
        )

        self.time_text = c.create_text(
            cx, cy,
            text=self.format_time(self._elapsed),
            fill=self.WHITE,
            font=("Segoe UI", max(16, min(int(radius*0.23), 36)), "bold")
        )
        self._update_dial()

    @staticmethod
    def format_time(seconds):
        minutes = int(seconds // 60)
        sec = int(seconds % 60)
        hundredths = int((seconds % 1) * 100)
        return f"{minutes:02d}:{sec:02d}.{hundredths:02d}"

    def update_display(self):
        if hasattr(self, "time_text"):
            self.watch_canvas.itemconfig(
                self.time_text,
                text=self.format_time(self._elapsed)
            )
        self._update_dial()

    def _update_dial(self):
        if not hasattr(self, "second_hand"):
            return

        seconds = self._elapsed % 60
        angle = math.radians(seconds * 6 - 90)
        x = self.cx + math.cos(angle) * self.radius * 0.68
        y = self.cy + math.sin(angle) * self.radius * 0.68

        self.watch_canvas.coords(
            self.second_hand, self.cx, self.cy, x, y
        )
        self.watch_canvas.itemconfig(
            self.progress_arc, extent=-(seconds / 60) * 360
        )

    def tick(self):
        self._timer_id = None
        if not self._running:
            return
        self._elapsed = perf_counter() - self._start_time
        self.update_display()
        self._timer_id = self.after(10, self.tick)

    def start(self):
        if self._running:
            return
        self._running = True
        self._start_time = perf_counter() - self._elapsed
        self.tick()

    def pause(self):
        if not self._running:
            return
        self._elapsed = perf_counter() - self._start_time
        self._running = False
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self.update_display()

    def toggle_timer(self):
        if self._running:
            self.pause()
            self.start_button.config(
                text="Start", fg=self.GREEN,
                bg="#102719", activebackground="#193c26"
            )
            self.lap_button.config(text="Reset")
        else:
            self.start()
            self.start_button.config(
                text="Stop", fg=self.RED,
                bg="#351817", activebackground="#51201e"
            )
            self.lap_button.config(text="Lap")

    def left_button_action(self):
        if self._running:
            self.record_lap()
        else:
            self.reset()

    def record_lap(self):
        if not self._running:
            return
        lap_time = self._elapsed - self._lap_start
        self._lap_start = self._elapsed
        self._laps.insert(
            0, (len(self._laps) + 1, lap_time, self._elapsed)
        )
        self.refresh_laps()

    def refresh_laps(self):
        self.lap_list.delete(0, tk.END)
        for number, lap_time, total in self._laps:
            self.lap_list.insert(
                tk.END,
                f"Lap {number:<3}    "
                f"{self.format_time(lap_time)}    "
                f"{self.format_time(total)}"
            )

    def reset(self):
        self.pause()
        self._elapsed = 0.0
        self._start_time = 0.0
        self._lap_start = 0.0
        self._laps.clear()
        self.lap_list.delete(0, tk.END)
        self.update_display()

        self.lap_button.config(text="Reset")
        self.start_button.config(
            text="Start", fg=self.GREEN,
            bg="#102719", activebackground="#193c26"
        )

    def close_app(self):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
        self.destroy()


if __name__ == "__main__":
    app = StopwatchApp()
    app.mainloop()
