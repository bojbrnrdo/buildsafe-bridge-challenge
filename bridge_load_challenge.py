import random
import tkinter as tk
from tkinter import ttk, messagebox

MATERIALS = {
    "Structural Steel": {"E": 200000.0, "allowable": 165.0, "cost_factor": 190000.0},
    "Engineered Timber": {"E": 11000.0, "allowable": 12.0, "cost_factor": 75000.0},
    "Aluminum": {"E": 69000.0, "allowable": 95.0, "cost_factor": 240000.0},
}


class BuildSafeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BuildSafe: Bridge Load Challenge")
        self.geometry("1040x650")
        self.minsize(920, 600)
        self.configure(bg="#eef3f8")

        self.round_no = 1
        self.score = 0
        self.target_load = 120
        self.budget = 220000

        self._configure_styles()
        self._build_ui()
        self.new_challenge()

    def _configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Primary.TButton", background="#2d6ea3", foreground="white")
        style.map("Primary.TButton", background=[("active", "#245b86")])

    def _build_ui(self):
        header = tk.Frame(self, bg="#17324d", padx=28, pady=22)
        header.pack(fill="x")
        tk.Label(
            header,
            text="BuildSafe: Bridge Load Challenge",
            font=("Segoe UI", 25, "bold"),
            fg="white",
            bg="#17324d",
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Design a safe and cost-efficient simply supported beam.",
            font=("Segoe UI", 10),
            fg="#d8e7f4",
            bg="#17324d",
        ).pack(anchor="w", pady=(4, 0))

        status_bar = tk.Frame(self, bg="#dbe8f2", padx=28, pady=10)
        status_bar.pack(fill="x")
        self.round_label = tk.Label(
            status_bar, bg="#dbe8f2", fg="#17324d", font=("Segoe UI", 10, "bold")
        )
        self.round_label.pack(side="left")
        self.challenge_label = tk.Label(
            status_bar, bg="#dbe8f2", fg="#17324d", font=("Segoe UI", 10)
        )
        self.challenge_label.pack(side="left", padx=18)
        self.score_label = tk.Label(
            status_bar, bg="#dbe8f2", fg="#17324d", font=("Segoe UI", 10, "bold")
        )
        self.score_label.pack(side="right")

        content = tk.Frame(self, bg="#eef3f8", padx=24, pady=24)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left = tk.Frame(
            content,
            bg="white",
            padx=24,
            pady=22,
            highlightbackground="#d9e2ea",
            highlightthickness=1,
        )
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = tk.Frame(
            content,
            bg="white",
            padx=24,
            pady=22,
            highlightbackground="#d9e2ea",
            highlightthickness=1,
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            left,
            text="1. Beam Design Inputs",
            bg="white",
            fg="#17324d",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        self.material_var = tk.StringVar(value="Structural Steel")
        self.span_var = tk.StringVar(value="8")
        self.width_var = tk.StringVar(value="250")
        self.depth_var = tk.StringVar(value="500")
        self.load_var = tk.StringVar(value="120")

        self._field(
            left,
            "Material",
            ttk.Combobox(
                left,
                textvariable=self.material_var,
                values=list(MATERIALS.keys()),
                state="readonly",
            ),
        )
        self._field(left, "Span Length (m)", ttk.Entry(left, textvariable=self.span_var))
        self._field(left, "Beam Width b (mm)", ttk.Entry(left, textvariable=self.width_var))
        self._field(left, "Beam Depth h (mm)", ttk.Entry(left, textvariable=self.depth_var))
        self._field(
            left,
            "Applied Midspan Load (kN)",
            ttk.Entry(left, textvariable=self.load_var),
        )

        ttk.Button(
            left,
            text="TEST DESIGN",
            style="Primary.TButton",
            command=self.test_design,
        ).pack(fill="x", pady=(16, 6))

        ttk.Button(
            left,
            text="NEW CHALLENGE",
            command=self.new_challenge,
        ).pack(fill="x")

        tk.Label(
            left,
            text=(
                "Educational model only. Simplified rectangular-beam equations "
                "and game-only cost factors."
            ),
            wraplength=390,
            justify="left",
            bg="white",
            fg="#657382",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(14, 0))

        tk.Label(
            right,
            text="2. Structural Check & Game Result",
            bg="white",
            fg="#17324d",
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", pady=(0, 14))

        self.result_banner = tk.Label(
            right,
            text="READY",
            bg="#f3f6f9",
            fg="#17324d",
            font=("Segoe UI", 17, "bold"),
            pady=12,
        )
        self.result_banner.pack(fill="x", pady=(0, 12))

        self.results = tk.Text(
            right,
            wrap="word",
            height=19,
            font=("Consolas", 10),
            bg="#fbfcfd",
            fg="#263746",
            relief="solid",
            borderwidth=1,
            padx=12,
            pady=12,
        )
        self.results.pack(fill="both", expand=True)
        self.results.config(state="disabled")

    @staticmethod
    def _field(parent, label_text, widget):
        row = tk.Frame(parent, bg="white")
        row.pack(fill="x", pady=7)

        tk.Label(
            row,
            text=label_text,
            bg="white",
            fg="#263746",
            font=("Segoe UI", 10, "bold"),
            width=22,
            anchor="w",
        ).pack(side="left")

        widget.pack(side="right", fill="x", expand=True)

    @staticmethod
    def _peso(value):
        return f"₱{value:,.0f}"

    def _set_results(self, text):
        self.results.config(state="normal")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", text)
        self.results.config(state="disabled")

    def new_challenge(self):
        self.target_load = random.choice([60, 80, 100, 120, 150, 180, 220, 250])
        self.budget = random.choice([140000, 170000, 200000, 230000, 260000])
        self.load_var.set(str(self.target_load))

        self.round_label.config(text=f"Round {self.round_no}")
        self.challenge_label.config(
            text=(
                f"Target load: {self.target_load} kN   •   "
                f"Budget: {self._peso(self.budget)}"
            )
        )
        self.score_label.config(text=f"Score: {self.score}")
        self.result_banner.config(text="READY", bg="#f3f6f9", fg="#17324d")

        self._set_results(
            "Choose a material and beam size, then click TEST DESIGN.\n\n"
            "Pass conditions:\n"
            "• Bending stress ≤ allowable stress\n"
            "• Deflection ≤ L/360\n"
            "• Estimated cost ≤ challenge budget"
        )

    def test_design(self):
        try:
            span_m = float(self.span_var.get())
            width_mm = float(self.width_var.get())
            depth_mm = float(self.depth_var.get())
            load_kn = float(self.load_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter numeric values for span, width, depth, and load.",
            )
            return

        if not (1 <= span_m <= 30):
            messagebox.showerror("Invalid Span", "Span must be between 1 m and 30 m.")
            return

        if not (100 <= width_mm <= 1500):
            messagebox.showerror(
                "Invalid Width",
                "Beam width must be between 100 mm and 1500 mm.",
            )
            return

        if not (150 <= depth_mm <= 2500):
            messagebox.showerror(
                "Invalid Depth",
                "Beam depth must be between 150 mm and 2500 mm.",
            )
            return

        if not (1 <= load_kn <= 2000):
            messagebox.showerror(
                "Invalid Load",
                "Applied load must be between 1 kN and 2000 kN.",
            )
            return

        props = MATERIALS[self.material_var.get()]

        length_mm = span_m * 1000.0
        load_n = load_kn * 1000.0

        inertia = width_mm * depth_mm**3 / 12.0
        max_moment = load_n * length_mm / 4.0
        stress = max_moment * (depth_mm / 2.0) / inertia

        deflection = (
            load_n * length_mm**3 / (48.0 * props["E"] * inertia)
        )
        deflection_limit = length_mm / 360.0

        volume_m3 = (
            (width_mm / 1000.0)
            * (depth_mm / 1000.0)
            * span_m
        )
        estimated_cost = volume_m3 * props["cost_factor"]

        stress_ok = stress <= props["allowable"]
        deflection_ok = deflection <= deflection_limit
        budget_ok = estimated_cost <= self.budget

        passed = stress_ok and deflection_ok and budget_ok

        if passed:
            efficiency_bonus = max(
                0,
                min(
                    100,
                    int(
                        (1 - estimated_cost / max(self.budget, 1)) * 100
                        + 50
                    ),
                ),
            )
            points = 100 + efficiency_bonus
            self.score += points
            self.result_banner.config(
                text=f"PASS  +{points} pts",
                bg="#dff3e4",
                fg="#156b31",
            )
            verdict = "Your design passed all challenge requirements."
            self.round_no += 1
        else:
            self.result_banner.config(
                text="REVISE DESIGN",
                bg="#fde8e7",
                fg="#9d1c15",
            )
            verdict = "Your design did not pass all challenge requirements."

        self.score_label.config(text=f"Score: {self.score}")

        result_text = (
            f"{verdict}\n\n"
            f"Material: {self.material_var.get()}\n"
            f"Span: {span_m:.2f} m\n"
            f"Applied Load: {load_kn:.1f} kN\n\n"
            "BENDING CHECK\n"
            f"Stress = {stress:.2f} MPa\n"
            f"Allowable = {props['allowable']:.2f} MPa\n"
            f"Status = {'PASS' if stress_ok else 'FAIL'}\n\n"
            "DEFLECTION CHECK\n"
            f"Deflection = {deflection:.2f} mm\n"
            f"Limit (L/360) = {deflection_limit:.2f} mm\n"
            f"Status = {'PASS' if deflection_ok else 'FAIL'}\n\n"
            "COST CHECK\n"
            f"Estimated Cost = {self._peso(estimated_cost)}\n"
            f"Budget = {self._peso(self.budget)}\n"
            f"Status = {'PASS' if budget_ok else 'FAIL'}"
        )

        self._set_results(result_text)


if __name__ == "__main__":
    app = BuildSafeApp()
    app.mainloop()
