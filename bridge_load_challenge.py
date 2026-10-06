import hashlib
import json
import math
import secrets
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


COLORS = {
    "bg": "#0A1118",
    "panel": "#101922",
    "panel2": "#0C151D",
    "line": "#223342",
    "text": "#EEF3F6",
    "muted": "#8395A5",
    "accent": "#F0A33D",
    "green": "#50D18B",
    "yellow": "#F2C94C",
    "red": "#EF6470",
    "blue": "#67A9FF",
    "sky1": "#9EC6D8",
    "sky2": "#D9E8EB",
    "water1": "#608AA0",
    "water2": "#375E74",
}

MATERIALS = {
    "Steel": {
        "key": "steel",
        "E": 200000.0,
        "allowable": 165.0,
        "density": 7850.0,
        "area_factor": 0.12,
        "inertia_factor": 0.42,
        "cost_per_kg": 85.0,
        "cost_per_m3": None,
    },
    "Timber": {
        "key": "timber",
        "E": 11000.0,
        "allowable": 12.0,
        "density": 520.0,
        "area_factor": 1.00,
        "inertia_factor": 1.00,
        "cost_per_kg": None,
        "cost_per_m3": 75000.0,
    },
    "Aluminum": {
        "key": "aluminum",
        "E": 69000.0,
        "allowable": 90.0,
        "density": 2700.0,
        "area_factor": 0.16,
        "inertia_factor": 0.55,
        "cost_per_kg": 320.0,
        "cost_per_m3": None,
    },
}

MISSIONS = [
    {
        "title": "Neighborhood Connector",
        "span": 10.0,
        "load": 420.0,
        "budget": 1550000.0,
        "difficulty": "ROOKIE",
        "brief": "Build a safe two-lane community bridge.",
        "suggested": ("Steel", 300, 700, 4),
    },
    {
        "title": "Industrial Access",
        "span": 12.0,
        "load": 650.0,
        "budget": 2150000.0,
        "difficulty": "ROOKIE",
        "brief": "Carry heavier service trucks into a logistics yard.",
        "suggested": ("Steel", 320, 800, 4),
    },
    {
        "title": "Mountain Supply Route",
        "span": 14.0,
        "load": 820.0,
        "budget": 2800000.0,
        "difficulty": "INTERMEDIATE",
        "brief": "Balance a longer span against a tighter budget.",
        "suggested": ("Steel", 340, 900, 5),
    },
    {
        "title": "Urban Flyover Link",
        "span": 16.0,
        "load": 1000.0,
        "budget": 3500000.0,
        "difficulty": "INTERMEDIATE",
        "brief": "Design an efficient bridge for dense urban traffic.",
        "suggested": ("Steel", 360, 980, 5),
    },
    {
        "title": "Emergency Relief Crossing",
        "span": 18.0,
        "load": 1250.0,
        "budget": 4900000.0,
        "difficulty": "ADVANCED",
        "brief": "Carry heavy relief vehicles with little room for error.",
        "suggested": ("Steel", 380, 1080, 6),
    },
    {
        "title": "Regional Freight Bridge",
        "span": 20.0,
        "load": 1500.0,
        "budget": 6000000.0,
        "difficulty": "EXPERT",
        "brief": "Complete the campaign with the heaviest freight load.",
        "suggested": ("Steel", 400, 1180, 6),
    },
]

PRESETS = {
    "Economy": (260, 600, 3),
    "Balanced": (300, 700, 4),
    "Heavy": (400, 950, 6),
}

SAVE_FILE = Path(__file__).with_name("buildsafe_save.json")
USERS_FILE = Path(__file__).with_name("buildsafe_users.json")


class BuildSafeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BuildSafe — Bridge Engineering Game")
        self.geometry("1280x780")
        self.minsize(1040, 680)
        self.configure(bg=COLORS["bg"])

        self.current_user = None
        self.users = self._load_users()
        self.state = self._default_state()
        self.testing = False
        self.last_result = None

        self.material_var = tk.StringVar(value="Steel")
        self.width_var = tk.IntVar(value=300)
        self.depth_var = tk.IntVar(value=700)
        self.girders_var = tk.IntVar(value=4)

        self._build_ui()
        self._bind_controls()
        self._apply_suggested(show_notice=False)
        self._render_all()

        self.after(180, self._show_login_screen)

    # ---------- persistence ----------

    def _default_state(self):
        return {
            "mission_index": 0,
            "unlocked": 0,
            "score": 0,
            "xp": 0,
            "attempts": 3,
            "completed": [False] * len(MISSIONS),
            "best_scores": [0] * len(MISSIONS),
        }

    def _normalize_state(self, raw=None):
        state = self._default_state()
        if isinstance(raw, dict):
            state.update(raw)

        state["mission_index"] = max(
            0, min(int(state.get("mission_index", 0)), len(MISSIONS) - 1)
        )
        state["unlocked"] = max(
            0, min(int(state.get("unlocked", 0)), len(MISSIONS) - 1)
        )
        state["score"] = max(0, int(state.get("score", 0)))
        state["xp"] = max(0, int(state.get("xp", 0)))
        state["attempts"] = max(0, min(int(state.get("attempts", 3)), 3))
        state["completed"] = (
            list(state.get("completed", [])) + [False] * len(MISSIONS)
        )[: len(MISSIONS)]
        state["best_scores"] = (
            list(state.get("best_scores", [])) + [0] * len(MISSIONS)
        )[: len(MISSIONS)]
        return state

    def _load_users(self):
        try:
            if USERS_FILE.exists():
                data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
                if isinstance(data, dict) and isinstance(data.get("users"), dict):
                    return data
        except Exception:
            pass
        return {"users": {}}

    def _save_users(self):
        try:
            USERS_FILE.write_text(
                json.dumps(self.users, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            messagebox.showerror(
                "Save Error",
                f"Could not save local profile data.\n\n{exc}",
                parent=self,
            )

    @staticmethod
    def _password_hash(password, salt_hex=None):
        salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            180000,
        )
        return salt.hex(), digest.hex()

    def _verify_password(self, password, account):
        try:
            _, digest = self._password_hash(password, account["salt"])
            return secrets.compare_digest(digest, account["password_hash"])
        except Exception:
            return False

    def _save_state(self):
        if not self.current_user:
            return
        account = self.users["users"].get(self.current_user)
        if not account:
            return
        account["progress"] = self._normalize_state(self.state)
        account["last_played"] = int(time.time())
        self._save_users()

    # ---------- UI ----------

    def _build_ui(self):
        self._build_header()
        self._build_mission_bar()

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=14, pady=(10, 8))
        body.columnconfigure(0, minsize=290)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self.controls = tk.Frame(
            body,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=14,
            pady=14,
        )
        self.controls.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.game_area = tk.Frame(
            body,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=10,
            pady=10,
        )
        self.game_area.grid(row=0, column=1, sticky="nsew")
        self.game_area.columnconfigure(0, weight=1)
        self.game_area.rowconfigure(1, weight=1)

        self._build_controls()
        self._build_simulation()
        self._build_footer()

    def _build_header(self):
        header = tk.Frame(self, bg="#0B131B", padx=16, pady=9)
        header.pack(fill="x")

        logo = tk.Label(
            header,
            text="BS",
            bg=COLORS["accent"],
            fg="#111820",
            font=("Segoe UI", 12, "bold"),
            width=3,
            height=2,
        )
        logo.pack(side="left")

        brand = tk.Frame(header, bg="#0B131B")
        brand.pack(side="left", padx=9)
        tk.Label(
            brand,
            text="BuildSafe",
            bg="#0B131B",
            fg=COLORS["text"],
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand,
            text="BRIDGE ENGINEERING",
            bg="#0B131B",
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w")

        right = tk.Frame(header, bg="#0B131B")
        right.pack(side="right")

        self.level_label = self._hud_box(right, "LVL", "1")
        self.score_label = self._hud_box(right, "SCORE", "0")

        self.menu_btn = tk.Button(
            right,
            text="MENU",
            command=self._show_main_menu,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            padx=9,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        )
        self.menu_btn.pack(side="left", padx=(6, 0), ipady=8)

        self.help_btn = tk.Button(
            right,
            text="?",
            command=self._show_help_modal,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            width=3,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        self.help_btn.pack(side="left", padx=(6, 0), ipady=7)

    def _hud_box(self, parent, label, value):
        frame = tk.Frame(
            parent,
            bg=COLORS["panel2"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=9,
            pady=5,
        )
        frame.pack(side="left", padx=3)
        tk.Label(
            frame,
            text=label,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w")
        value_label = tk.Label(
            frame,
            text=value,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        )
        value_label.pack(anchor="w")
        return value_label

    def _build_mission_bar(self):
        bar = tk.Frame(
            self,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=14,
            pady=9,
        )
        bar.pack(fill="x", padx=14, pady=(10, 0))

        left = tk.Frame(bar, bg=COLORS["panel"])
        left.pack(side="left", fill="x", expand=True)

        self.mission_no_label = tk.Label(
            left,
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 7, "bold"),
        )
        self.mission_no_label.pack(side="left", padx=(0, 10))

        self.mission_title_label = tk.Label(
            left,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        self.mission_title_label.pack(side="left")

        self.difficulty_label = tk.Label(
            left,
            bg=COLORS["panel2"],
            fg="#B8C4CD",
            font=("Segoe UI", 7, "bold"),
            padx=7,
            pady=3,
        )
        self.difficulty_label.pack(side="left", padx=9)

        self.mission_stats_frame = tk.Frame(bar, bg=COLORS["panel"])
        self.mission_stats_frame.pack(side="right")

        self.span_stat = self._mission_stat(self.mission_stats_frame, "SPAN")
        self.load_stat = self._mission_stat(self.mission_stats_frame, "LOAD")
        self.budget_stat = self._mission_stat(self.mission_stats_frame, "BUDGET")
        self.tries_stat = self._mission_stat(self.mission_stats_frame, "TRIES")

    def _mission_stat(self, parent, title):
        frame = tk.Frame(
            parent,
            bg=COLORS["panel2"],
            padx=9,
            pady=4,
            highlightbackground="#1C2B38",
            highlightthickness=1,
        )
        frame.pack(side="left", padx=3)
        tk.Label(
            frame,
            text=title,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            font=("Segoe UI", 6, "bold"),
        ).pack(anchor="w")
        value = tk.Label(
            frame,
            text="—",
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            font=("Segoe UI", 9, "bold"),
        )
        value.pack(anchor="w")
        return value

    def _build_controls(self):
        title_row = tk.Frame(self.controls, bg=COLORS["panel"])
        title_row.pack(fill="x")

        title_text = tk.Frame(title_row, bg=COLORS["panel"])
        title_text.pack(side="left")
        tk.Label(
            title_text,
            text="BUILD",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_text,
            text="Bridge Setup",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        tk.Button(
            title_row,
            text="AUTO",
            command=self._apply_suggested,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        ).pack(side="right")

        tk.Frame(self.controls, bg=COLORS["line"], height=1).pack(
            fill="x", pady=(12, 10)
        )

        tk.Label(
            self.controls,
            text="MATERIAL",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w")

        material_row = tk.Frame(self.controls, bg=COLORS["panel"])
        material_row.pack(fill="x", pady=(5, 10))
        self.material_buttons = {}
        for name in MATERIALS:
            button = tk.Radiobutton(
                material_row,
                text=name,
                value=name,
                variable=self.material_var,
                command=self._on_control_change,
                indicatoron=False,
                bg=COLORS["panel2"],
                fg="#9FB0BF",
                selectcolor=COLORS["panel2"],
                activebackground=COLORS["line"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                padx=5,
                pady=7,
                font=("Segoe UI", 7, "bold"),
                cursor="hand2",
            )
            button.pack(side="left", fill="x", expand=True, padx=2)
            self.material_buttons[name] = button

        preset_row = tk.Frame(self.controls, bg=COLORS["panel"])
        preset_row.pack(fill="x", pady=(0, 8))
        for name in PRESETS:
            tk.Button(
                preset_row,
                text=name,
                command=lambda n=name: self._apply_preset(n),
                bg="#0C151D",
                fg=COLORS["muted"],
                activebackground=COLORS["line"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                pady=5,
                font=("Segoe UI", 7),
                cursor="hand2",
            ).pack(side="left", fill="x", expand=True, padx=2)

        self.width_value = self._slider(
            self.controls, "Width", self.width_var, 220, 520, 10, " mm"
        )
        self.depth_value = self._slider(
            self.controls, "Depth", self.depth_var, 450, 1200, 10, " mm"
        )
        self.girder_value = self._slider(
            self.controls, "Girders", self.girders_var, 3, 7, 1, ""
        )

        stats = tk.Frame(
            self.controls,
            bg=COLORS["panel2"],
            highlightbackground="#1D2B37",
            highlightthickness=1,
            padx=8,
            pady=8,
        )
        stats.pack(fill="x", pady=(10, 8))
        stats.columnconfigure((0, 1), weight=1)

        self.mass_preview = self._mini_stat(stats, "MASS", 0, 0)
        self.dead_preview = self._mini_stat(stats, "DEAD LOAD", 0, 1)
        self.cost_preview = self._mini_stat(stats, "COST", 1, 0)
        self.budget_preview = self._mini_stat(stats, "BUDGET", 1, 1)

        self.tip_label = tk.Label(
            self.controls,
            text="Balanced is a good starting point.",
            wraplength=245,
            justify="left",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
        )
        self.tip_label.pack(fill="x", pady=(2, 8))

        self.test_button = tk.Button(
            self.controls,
            text="▶   LOAD TEST",
            command=self._run_load_test,
            bg=COLORS["accent"],
            fg="#101820",
            activebackground="#FFC46D",
            activeforeground="#101820",
            relief="flat",
            bd=0,
            pady=12,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.test_button.pack(fill="x")

        actions = tk.Frame(self.controls, bg=COLORS["panel"])
        actions.pack(fill="x", pady=(7, 0))

        tk.Button(
            actions,
            text="DETAILS",
            command=self._show_details_modal,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            pady=6,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        tk.Button(
            actions,
            text="PROJECTS",
            command=self._show_campaign_modal,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            pady=6,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

    def _slider(self, parent, title, variable, min_value, max_value, step, suffix):
        row = tk.Frame(parent, bg=COLORS["panel"])
        row.pack(fill="x", pady=6)

        label_row = tk.Frame(row, bg=COLORS["panel"])
        label_row.pack(fill="x")
        tk.Label(
            label_row,
            text=title,
            bg=COLORS["panel"],
            fg="#CBD5DC",
            font=("Segoe UI", 8),
        ).pack(side="left")

        value_label = tk.Label(
            label_row,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 8, "bold"),
        )
        value_label.pack(side="right")

        scale = tk.Scale(
            row,
            from_=min_value,
            to=max_value,
            resolution=step,
            orient="horizontal",
            variable=variable,
            command=lambda _=None: self._on_control_change(),
            showvalue=False,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            troughcolor="#233746",
            activebackground=COLORS["accent"],
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
        )
        scale.pack(fill="x")

        if suffix:
            variable.trace_add(
                "write",
                lambda *_args, lbl=value_label, var=variable, s=suffix: lbl.config(
                    text=f"{var.get()}{s}"
                ),
            )
            value_label.config(text=f"{variable.get()}{suffix}")
        else:
            variable.trace_add(
                "write",
                lambda *_args, lbl=value_label, var=variable: lbl.config(
                    text=str(var.get())
                ),
            )
            value_label.config(text=str(variable.get()))

        return value_label

    def _mini_stat(self, parent, title, row, column):
        frame = tk.Frame(parent, bg="#101C27", padx=7, pady=6)
        frame.grid(row=row, column=column, sticky="nsew", padx=2, pady=2)
        tk.Label(
            frame,
            text=title,
            bg="#101C27",
            fg="#728698",
            font=("Segoe UI", 6, "bold"),
        ).pack(anchor="w")
        value = tk.Label(
            frame,
            text="—",
            bg="#101C27",
            fg=COLORS["text"],
            font=("Segoe UI", 8, "bold"),
        )
        value.pack(anchor="w", pady=(2, 0))
        return value

    def _build_simulation(self):
        top = tk.Frame(self.game_area, bg=COLORS["panel"])
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        tk.Label(
            top,
            text="SIMULATION",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 7, "bold"),
        ).pack(side="left")

        self.stage_label = tk.Label(
            top,
            text="READY",
            bg=COLORS["panel2"],
            fg="#95A5B3",
            font=("Segoe UI", 7, "bold"),
            padx=8,
            pady=5,
        )
        self.stage_label.pack(side="right")

        self.canvas = tk.Canvas(
            self.game_area,
            bg=COLORS["sky2"],
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda _e: self._draw_scene())

        bottom = tk.Frame(self.game_area, bg=COLORS["panel"])
        bottom.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        bottom.columnconfigure((0, 1, 2), weight=1)

        self.result_cards = {}
        self.result_cards["strength"] = self._result_card(bottom, "STRENGTH", 0)
        self.result_cards["deflection"] = self._result_card(bottom, "DEFLECTION", 1)
        self.result_cards["cost"] = self._result_card(bottom, "COST", 2)

    def _result_card(self, parent, title, column):
        frame = tk.Frame(
            parent,
            bg=COLORS["panel2"],
            highlightbackground="#1D2B37",
            highlightthickness=1,
            padx=9,
            pady=7,
        )
        frame.grid(row=0, column=column, sticky="ew", padx=3)

        head = tk.Frame(frame, bg=COLORS["panel2"])
        head.pack(fill="x")
        tk.Label(
            head,
            text=title,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            font=("Segoe UI", 6, "bold"),
        ).pack(side="left")

        state_label = tk.Label(
            head,
            text="WAITING",
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            font=("Segoe UI", 6, "bold"),
        )
        state_label.pack(side="right")

        value_label = tk.Label(
            frame,
            text="—",
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            font=("Segoe UI", 11, "bold"),
        )
        value_label.pack(anchor="w", pady=(5, 0))

        limit_label = tk.Label(
            frame,
            text="",
            bg=COLORS["panel2"],
            fg="#6F8292",
            font=("Segoe UI", 7),
        )
        limit_label.pack(anchor="w")

        return {
            "frame": frame,
            "state": state_label,
            "value": value_label,
            "limit": limit_label,
        }

    def _build_footer(self):
        footer = tk.Frame(self, bg=COLORS["bg"], padx=14, pady=6)
        footer.pack(fill="x")

        self.rank_label = tk.Label(
            footer,
            text="C · Junior Designer",
            bg=COLORS["bg"],
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold"),
        )
        self.rank_label.pack(side="left")

        tk.Label(
            footer,
            text="Educational simulation only — not for real structural design.",
            bg=COLORS["bg"],
            fg="#566B7A",
            font=("Segoe UI", 7),
        ).pack(side="right")

    def _bind_controls(self):
        self.material_var.trace_add("write", lambda *_: self._on_control_change())


    # ---------- account + menu flow ----------

    def _overlay(self):
        frame = tk.Frame(self, bg="#081018")
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.lift()
        return frame

    def _show_login_screen(self):
        if hasattr(self, "active_overlay") and self.active_overlay.winfo_exists():
            self.active_overlay.destroy()

        self.active_overlay = self._overlay()

        card = tk.Frame(
            self.active_overlay,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=34,
            pady=30,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=500)

        tk.Label(
            card,
            text="BS",
            bg=COLORS["accent"],
            fg="#111820",
            font=("Segoe UI", 18, "bold"),
            width=3,
            height=2,
        ).pack()

        tk.Label(
            card,
            text="BuildSafe",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(12, 0))

        tk.Label(
            card,
            text="BRIDGE ENGINEERING GAME",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(pady=(2, 24))

        self.login_username = tk.StringVar()
        self.login_password = tk.StringVar()

        username_entry = self._auth_field(
            card,
            "USERNAME",
            self.login_username,
        )
        password_entry = self._auth_field(
            card,
            "PASSWORD",
            self.login_password,
            password=True,
        )

        self.auth_message = tk.Label(
            card,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["red"],
            font=("Segoe UI", 8),
        )
        self.auth_message.pack(fill="x", pady=(7, 0))

        tk.Button(
            card,
            text="LOGIN",
            command=self._login,
            bg=COLORS["accent"],
            fg="#101820",
            activebackground="#FFC46D",
            activeforeground="#101820",
            relief="flat",
            bd=0,
            pady=11,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(fill="x", pady=(14, 7))

        tk.Button(
            card,
            text="CREATE ACCOUNT",
            command=self._show_register_screen,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            pady=10,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(fill="x")

        tk.Label(
            card,
            text="Profiles are stored locally on this computer.",
            bg=COLORS["panel"],
            fg="#5E7180",
            font=("Segoe UI", 7),
        ).pack(side="bottom")

        username_entry.bind("<Return>", lambda _event: password_entry.focus_set())
        password_entry.bind("<Return>", lambda _event: self._login())
        self.after(100, username_entry.focus_set)

    def _focus_first_entry(self, container):
        for child in container.winfo_children():
            if isinstance(child, tk.Entry):
                child.focus_set()
                break

    def _auth_field(self, parent, label, variable, password=False):
        tk.Label(
            parent,
            text=label,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 7, "bold"),
        ).pack(anchor="w", pady=(4, 4))

        entry = tk.Entry(
            parent,
            textvariable=variable,
            show="•" if password else "",
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            bd=0,
            highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"],
            highlightthickness=1,
            font=("Segoe UI", 11),
        )
        entry.pack(fill="x", ipady=9, pady=(0, 9))
        return entry

    def _show_register_screen(self):
        modal = self._modal("Create Account", 450, 465)

        self._modal_heading(modal, "NEW PROFILE", "Create Account")

        username = tk.StringVar()
        password = tk.StringVar()
        confirm = tk.StringVar()

        form = tk.Frame(modal, bg=COLORS["panel"])
        form.pack(fill="both", expand=True, padx=28, pady=(12, 4))

        self._auth_field(form, "USERNAME", username)
        self._auth_field(form, "PASSWORD", password, password=True)
        self._auth_field(form, "CONFIRM PASSWORD", confirm, password=True)

        message = tk.Label(
            form,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["red"],
            font=("Segoe UI", 8),
        )
        message.pack(fill="x")

        def create():
            raw_name = username.get().strip()
            key = raw_name.lower()
            pw = password.get()

            if not (3 <= len(raw_name) <= 18):
                message.config(text="Username must be 3–18 characters.")
                return
            if not all(ch.isalnum() or ch == "_" for ch in raw_name):
                message.config(text="Use letters, numbers, or underscore only.")
                return
            if key in self.users["users"]:
                message.config(text="That username already exists.")
                return
            if len(pw) < 6:
                message.config(text="Password must be at least 6 characters.")
                return
            if pw != confirm.get():
                message.config(text="Passwords do not match.")
                return

            salt, digest = self._password_hash(pw)
            self.users["users"][key] = {
                "display_name": raw_name,
                "salt": salt,
                "password_hash": digest,
                "progress": self._default_state(),
                "created_at": int(time.time()),
                "last_played": None,
            }
            self._save_users()
            modal.destroy()
            self.login_username.set(raw_name)
            self.login_password.set("")
            self.auth_message.config(
                text="Account created. Enter your password to login.",
                fg=COLORS["green"],
            )

        tk.Button(
            form,
            text="CREATE ACCOUNT",
            command=create,
            bg=COLORS["accent"],
            fg="#101820",
            activebackground="#FFC46D",
            activeforeground="#101820",
            relief="flat",
            bd=0,
            pady=10,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(fill="x", pady=(13, 5))

        tk.Button(
            form,
            text="CANCEL",
            command=modal.destroy,
            bg=COLORS["panel2"],
            fg=COLORS["muted"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            pady=9,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(fill="x")

    def _login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get()
        key = username.lower()

        account = self.users["users"].get(key)
        if not account or not self._verify_password(password, account):
            self.auth_message.config(
                text="Incorrect username or password.",
                fg=COLORS["red"],
            )
            return

        self.current_user = key
        self.state = self._normalize_state(account.get("progress"))
        self.login_password.set("")

        if self.active_overlay.winfo_exists():
            self.active_overlay.destroy()

        self._apply_suggested(show_notice=False)
        self._render_all()
        self.after(120, self._show_main_menu)

    def _show_main_menu(self):
        if not self.current_user:
            self._show_login_screen()
            return

        if self.testing:
            return

        if hasattr(self, "active_overlay") and self.active_overlay.winfo_exists():
            self.active_overlay.destroy()

        self.active_overlay = self._overlay()
        account = self.users["users"][self.current_user]
        name = account.get("display_name", self.current_user)

        card = tk.Frame(
            self.active_overlay,
            bg=COLORS["panel"],
            highlightbackground=COLORS["line"],
            highlightthickness=1,
            padx=34,
            pady=28,
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=470, height=540)

        tk.Label(
            card,
            text="BUILDSAFE",
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 8, "bold"),
        ).pack()

        tk.Label(
            card,
            text=f"Welcome, {name}",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(4, 2))

        completed = sum(bool(v) for v in self.state["completed"])
        tk.Label(
            card,
            text=f'{completed}/{len(MISSIONS)} projects complete  ·  Score {self.state["score"]:,}',
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 8),
        ).pack(pady=(0, 24))

        primary_text = "CONTINUE" if completed or self.state["score"] else "START GAME"
        tk.Button(
            card,
            text=f"▶   {primary_text}",
            command=self._start_from_menu,
            bg=COLORS["accent"],
            fg="#101820",
            activebackground="#FFC46D",
            activeforeground="#101820",
            relief="flat",
            bd=0,
            pady=13,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(fill="x", pady=5)

        for text, command in [
            ("PROJECTS", self._show_campaign_modal),
            ("HOW TO PLAY", self._show_help_modal),
            ("ENGINEERING DETAILS", self._show_details_modal),
        ]:
            tk.Button(
                card,
                text=text,
                command=command,
                bg=COLORS["panel2"],
                fg=COLORS["text"],
                activebackground=COLORS["line"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                pady=10,
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
            ).pack(fill="x", pady=4)

        tk.Button(
            card,
            text="LOG OUT",
            command=self._logout,
            bg=COLORS["panel"],
            fg=COLORS["red"],
            activebackground=COLORS["panel2"],
            activeforeground=COLORS["red"],
            relief="flat",
            bd=0,
            pady=9,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(fill="x", pady=(12, 0))

        tk.Label(
            card,
            text="Local player profile",
            bg=COLORS["panel"],
            fg="#566B7A",
            font=("Segoe UI", 7),
        ).pack(side="bottom")

    def _start_from_menu(self):
        if hasattr(self, "active_overlay") and self.active_overlay.winfo_exists():
            self.active_overlay.destroy()
        self.after(120, self._show_mission_modal)

    def _logout(self):
        self._save_state()
        self.current_user = None
        self.state = self._default_state()
        self.last_result = None
        self._render_all()
        self._show_login_screen()


    # ---------- calculations ----------

    def _mission(self):
        return MISSIONS[self.state["mission_index"]]

    @staticmethod
    def _peso(value):
        return f"₱{value:,.0f}"

    @staticmethod
    def _clamp(value, minimum, maximum):
        return min(maximum, max(minimum, value))

    def _calculate(self):
        mission = self._mission()
        material = MATERIALS[self.material_var.get()]
        width = float(self.width_var.get())
        depth = float(self.depth_var.get())
        girders = float(self.girders_var.get())

        deck_width_m = 7.2
        deck_thickness_m = 0.20
        concrete_unit_weight = 24.0
        impact_factor = 1.15

        gross_area_mm2 = width * depth
        effective_area_m2 = (
            gross_area_mm2 * material["area_factor"] / 1_000_000.0
        )
        effective_i = (
            width
            * depth**3
            / 12.0
            * material["inertia_factor"]
        )

        girder_self_weight_kn_m = (
            effective_area_m2 * material["density"] * 9.81 / 1000.0
        )

        deck_dead_load_total_kn_m = (
            deck_width_m * deck_thickness_m * concrete_unit_weight
        )

        dead_load_per_girder_kn_m = (
            deck_dead_load_total_kn_m / girders
            + girder_self_weight_kn_m
        )

        dynamic_vehicle_total_kn = mission["load"] * impact_factor
        vehicle_per_girder_kn = dynamic_vehicle_total_kn / girders

        factored_moment_kn_m = (
            1.2
            * dead_load_per_girder_kn_m
            * mission["span"] ** 2
            / 8.0
            + 1.6
            * vehicle_per_girder_kn
            * mission["span"]
            / 4.0
        )

        stress_mpa = (
            factored_moment_kn_m
            * 1_000_000.0
            * (depth / 2.0)
            / effective_i
        )

        span_mm = mission["span"] * 1000.0

        dead_deflection_mm = (
            5.0
            * dead_load_per_girder_kn_m
            * span_mm**4
            / (384.0 * material["E"] * effective_i)
        )

        live_deflection_mm = (
            vehicle_per_girder_kn
            * 1000.0
            * span_mm**3
            / (48.0 * material["E"] * effective_i)
        )

        deflection_mm = dead_deflection_mm + live_deflection_mm
        deflection_limit_mm = span_mm / 800.0

        girder_volume_m3 = effective_area_m2 * mission["span"] * girders
        girder_mass_kg = girder_volume_m3 * material["density"]

        deck_volume_m3 = deck_width_m * deck_thickness_m * mission["span"]

        if material["cost_per_kg"] is not None:
            girder_cost = girder_mass_kg * material["cost_per_kg"]
        else:
            girder_cost = girder_volume_m3 * material["cost_per_m3"]

        deck_cost = deck_volume_m3 * 12000.0
        substructure_allowance = 320000.0 + mission["span"] * 18000.0
        connection_allowance = girders * 25000.0

        total_cost = (
            girder_cost
            + deck_cost
            + substructure_allowance
            + connection_allowance
        )

        strength_ratio = stress_mpa / material["allowable"]
        deflection_ratio = deflection_mm / deflection_limit_mm
        budget_ratio = total_cost / mission["budget"]
        governing_ratio = max(strength_ratio, deflection_ratio)

        return {
            "material": self.material_var.get(),
            "width": width,
            "depth": depth,
            "girders": int(girders),
            "dead_load_per_girder": dead_load_per_girder_kn_m,
            "vehicle_per_girder": vehicle_per_girder_kn,
            "moment": factored_moment_kn_m,
            "stress": stress_mpa,
            "stress_limit": material["allowable"],
            "deflection": deflection_mm,
            "deflection_limit": deflection_limit_mm,
            "cost": total_cost,
            "girder_mass": girder_mass_kg,
            "strength_ratio": strength_ratio,
            "deflection_ratio": deflection_ratio,
            "budget_ratio": budget_ratio,
            "governing_ratio": governing_ratio,
            "pass": (
                strength_ratio <= 1.0
                and deflection_ratio <= 1.0
                and budget_ratio <= 1.0
            ),
        }

    # ---------- render ----------

    def _render_all(self):
        mission = self._mission()
        index = self.state["mission_index"]

        self.mission_no_label.config(
            text=f"MISSION {index + 1:02d}"
        )
        self.mission_title_label.config(text=mission["title"])
        self.difficulty_label.config(text=mission["difficulty"])

        self.span_stat.config(text=f'{mission["span"]:.1f} m')
        self.load_stat.config(text=f'{mission["load"]:.0f} kN')
        self.budget_stat.config(text=self._peso(mission["budget"]))
        self.tries_stat.config(text=str(self.state["attempts"]))

        level = self.state["xp"] // 500 + 1
        self.level_label.config(text=str(level))
        self.score_label.config(text=f'{self.state["score"]:,}')

        completed = sum(bool(v) for v in self.state["completed"])
        if completed >= 6 and self.state["score"] >= 4000:
            rank = "S · Chief Bridge Engineer"
        elif completed >= 4 or self.state["score"] >= 2400:
            rank = "A · Senior Engineer"
        elif completed >= 2 or self.state["score"] >= 1000:
            rank = "B · Project Engineer"
        else:
            rank = "C · Junior Designer"
        self.rank_label.config(text=rank)

        self._update_preview()
        self._reset_result_cards()
        self._draw_scene()

    def _update_preview(self):
        if self.testing:
            return

        result = self._calculate()
        mission = self._mission()

        self.mass_preview.config(
            text=f'{result["girder_mass"] / 1000.0:.1f} t'
        )
        self.dead_preview.config(
            text=f'{result["dead_load_per_girder"]:.1f} kN/m'
        )
        self.cost_preview.config(text=self._peso(result["cost"]))
        self.budget_preview.config(
            text=f'{result["budget_ratio"] * 100:.0f}%'
        )

        if result["budget_ratio"] > 1.0:
            self.budget_preview.config(fg=COLORS["red"])
            self.tip_label.config(
                text="Over budget — reduce material or change the system."
            )
        elif result["material"] == "Timber" and mission["span"] >= 14:
            self.budget_preview.config(fg=COLORS["text"])
            self.tip_label.config(
                text="Long timber spans may be controlled by deflection."
            )
        elif result["material"] == "Aluminum":
            self.budget_preview.config(fg=COLORS["text"])
            self.tip_label.config(
                text="Aluminum is light, but its material cost is high."
            )
        else:
            self.budget_preview.config(fg=COLORS["text"])
            self.tip_label.config(
                text="Balanced is a good starting point."
            )

        self._draw_scene()

    def _reset_result_cards(self):
        self.last_result = None
        for card in self.result_cards.values():
            card["frame"].config(highlightbackground="#1D2B37")
            card["state"].config(text="WAITING", fg=COLORS["muted"])
            card["value"].config(text="—")
            card["limit"].config(text="")
        self.stage_label.config(text="READY", fg="#95A5B3")

    def _set_card(self, name, value, limit, ratio):
        card = self.result_cards[name]
        card["value"].config(text=value)
        card["limit"].config(text=limit)

        if ratio > 1.0:
            color = COLORS["red"]
            state = "FAIL"
        elif ratio > 0.90:
            color = COLORS["yellow"]
            state = "NEAR LIMIT"
        else:
            color = COLORS["green"]
            state = "PASS"

        card["state"].config(text=state, fg=color)
        card["frame"].config(highlightbackground=color)

    # ---------- controls ----------

    def _on_control_change(self):
        if self.testing:
            return
        self._update_preview()

    def _apply_preset(self, name):
        if self.testing:
            return
        width, depth, girders = PRESETS[name]
        self.width_var.set(width)
        self.depth_var.set(depth)
        self.girders_var.set(girders)
        self._update_preview()

    def _apply_suggested(self, show_notice=True):
        if self.testing:
            return

        material, width, depth, girders = self._mission()["suggested"]
        self.material_var.set(material)
        self.width_var.set(width)
        self.depth_var.set(depth)
        self.girders_var.set(girders)
        self._update_preview()

        if show_notice:
            self.tip_label.config(text="Suggested design loaded.")

    # ---------- canvas ----------

    def _draw_scene(
        self,
        truck_progress=0.0,
        sag_ratio=0.0,
        broken=False,
        collapse_progress=0.0,
        show_cracks=False,
        show_debris=False,
        show_splash=False,
        warning=False,
    ):
        canvas = self.canvas
        if not canvas.winfo_exists():
            return

        width = max(canvas.winfo_width(), 720)
        height = max(canvas.winfo_height(), 420)
        canvas.delete("all")

        # background
        canvas.create_rectangle(
            0, 0, width, height, fill=COLORS["sky2"], outline=""
        )
        canvas.create_oval(
            width - 120,
            45,
            width - 70,
            95,
            fill="#F6E8B0",
            outline="",
        )

        hill_y = height * 0.58
        canvas.create_polygon(
            0,
            hill_y,
            width * 0.12,
            hill_y - 60,
            width * 0.25,
            hill_y - 12,
            width * 0.40,
            hill_y - 70,
            width * 0.58,
            hill_y - 20,
            width * 0.73,
            hill_y - 55,
            width,
            hill_y - 20,
            width,
            height * 0.72,
            0,
            height * 0.72,
            fill="#849E8A",
            outline="",
        )
        canvas.create_polygon(
            0,
            hill_y + 30,
            width * 0.17,
            hill_y - 12,
            width * 0.33,
            hill_y + 26,
            width * 0.49,
            hill_y - 18,
            width * 0.70,
            hill_y + 22,
            width * 0.88,
            hill_y - 12,
            width,
            hill_y + 8,
            width,
            height * 0.75,
            0,
            height * 0.75,
            fill="#6B8776",
            outline="",
        )

        water_y = height * 0.72
        canvas.create_rectangle(
            0, water_y, width, height, fill=COLORS["water1"], outline=""
        )
        for i in range(7):
            y = water_y + 14 + i * 17
            canvas.create_line(
                0,
                y,
                width,
                y,
                fill="#6F9BAE" if i % 2 == 0 else "#527B90",
                width=1,
            )

        left_x = width * 0.12
        right_x = width * 0.88
        deck_y = height * 0.55
        mid_x = (left_x + right_x) / 2.0
        span_px = right_x - left_x

        # abutments
        canvas.create_polygon(
            left_x - 70,
            deck_y + 18,
            left_x + 14,
            deck_y + 18,
            left_x + 14,
            water_y + 55,
            left_x - 92,
            water_y + 55,
            left_x - 92,
            deck_y + 45,
            fill="#727A7D",
            outline="",
        )
        canvas.create_polygon(
            right_x - 14,
            deck_y + 18,
            right_x + 70,
            deck_y + 18,
            right_x + 92,
            deck_y + 45,
            right_x + 92,
            water_y + 55,
            right_x - 14,
            water_y + 55,
            fill="#727A7D",
            outline="",
        )

        sag_px = self._clamp(sag_ratio, 0.0, 1.5) * 34.0

        if broken:
            gap = 18 + 56 * collapse_progress
            drop = 18 + 92 * collapse_progress
            left_end = mid_x - gap / 2
            right_start = mid_x + gap / 2

            canvas.create_line(
                left_x,
                deck_y,
                left_end,
                deck_y + drop,
                fill="#A94C53",
                width=20,
                capstyle="round",
            )
            canvas.create_line(
                right_start,
                deck_y + drop * 0.9,
                right_x,
                deck_y,
                fill="#A94C53",
                width=20,
                capstyle="round",
            )
            canvas.create_line(
                left_x,
                deck_y + 19,
                left_end,
                deck_y + 20 + drop,
                fill="#9F3941",
                width=12,
                capstyle="round",
            )
            canvas.create_line(
                right_start,
                deck_y + 19 + drop * 0.95,
                right_x,
                deck_y + 19,
                fill="#9F3941",
                width=12,
                capstyle="round",
            )
        else:
            points = [
                left_x,
                deck_y,
                mid_x,
                deck_y + sag_px,
                right_x,
                deck_y,
            ]
            canvas.create_line(
                *points,
                fill="#BBBDB8",
                width=20,
                smooth=True,
                splinesteps=28,
                capstyle="round",
            )
            canvas.create_line(
                left_x,
                deck_y - 7,
                mid_x,
                deck_y - 7 + sag_px,
                right_x,
                deck_y - 7,
                fill="#333A3E",
                width=10,
                smooth=True,
                splinesteps=28,
                capstyle="round",
            )
            canvas.create_line(
                left_x,
                deck_y + 18,
                mid_x,
                deck_y + 18 + sag_px,
                right_x,
                deck_y + 18,
                fill="#53616A",
                width=12,
                smooth=True,
                splinesteps=28,
                capstyle="round",
            )

        # additional girders
        girder_count = max(3, int(self.girders_var.get()))
        for i in range(girder_count - 1):
            offset = 24 + i * 3
            if broken:
                gap = 18 + 56 * collapse_progress
                drop = 18 + 92 * collapse_progress
                canvas.create_line(
                    left_x,
                    deck_y + offset,
                    mid_x - gap / 2,
                    deck_y + offset + drop,
                    fill="#6E7D87",
                    width=2,
                )
                canvas.create_line(
                    mid_x + gap / 2,
                    deck_y + offset + drop * 0.9,
                    right_x,
                    deck_y + offset,
                    fill="#6E7D87",
                    width=2,
                )
            else:
                canvas.create_line(
                    left_x,
                    deck_y + offset,
                    mid_x,
                    deck_y + offset + sag_px,
                    right_x,
                    deck_y + offset,
                    fill="#6E7D87",
                    width=2,
                    smooth=True,
                )

        # lane marks
        for i in range(6):
            p1 = (i + 0.25) / 6.5
            p2 = (i + 0.72) / 6.5
            x1 = left_x + span_px * p1
            x2 = left_x + span_px * p2
            y1 = deck_y - 8 + sag_px * (4 * p1 * (1 - p1))
            y2 = deck_y - 8 + sag_px * (4 * p2 * (1 - p2))
            if not broken:
                canvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#F6D862",
                    width=2,
                )

        # cracks
        if show_cracks:
            crack_y = deck_y + 3 + (50 if broken else sag_px)
            canvas.create_line(
                mid_x - 18,
                crack_y - 12,
                mid_x - 6,
                crack_y + 1,
                mid_x - 14,
                crack_y + 14,
                mid_x + 2,
                crack_y + 28,
                fill="#D84049",
                width=4,
            )
            canvas.create_line(
                mid_x + 16,
                crack_y - 10,
                mid_x + 6,
                crack_y + 4,
                mid_x + 17,
                crack_y + 16,
                fill="#D84049",
                width=4,
            )

        # debris
        if show_debris:
            for dx, dy, size in [
                (-30, 40, 12),
                (-8, 55, 9),
                (18, 42, 14),
                (34, 65, 7),
            ]:
                fall = 52 * collapse_progress
                canvas.create_rectangle(
                    mid_x + dx,
                    deck_y + dy + fall,
                    mid_x + dx + size,
                    deck_y + dy + fall + 6,
                    fill="#606A6E",
                    outline="",
                )

        if show_splash:
            radius = 16 + 45 * collapse_progress
            canvas.create_oval(
                mid_x - radius,
                water_y + 24 - radius / 5,
                mid_x + radius,
                water_y + 24 + radius / 5,
                outline="#E2F4FA",
                width=3,
            )

        # truck
        if broken:
            truck_x = mid_x - 20
            truck_y = deck_y - 55 + 90 * collapse_progress
            angle_hint = int(15 * collapse_progress)
            self._draw_truck(
                canvas,
                truck_x,
                truck_y,
                angle_hint=angle_hint,
            )
        else:
            p = self._clamp(truck_progress, 0.0, 1.0)
            truck_x = left_x - 55 + p * (span_px + 40)
            local_sag = sag_px * (4 * p * (1 - p))
            truck_y = deck_y - 55 + local_sag
            self._draw_truck(canvas, truck_x, truck_y)

        # load arrow near midspan
        if 0.42 <= truck_progress <= 0.60 and not broken:
            canvas.create_line(
                mid_x,
                deck_y - 150,
                mid_x,
                deck_y - 65,
                arrow="last",
                fill="#B83C47",
                width=4,
            )
            canvas.create_text(
                mid_x,
                deck_y - 164,
                text=f'{self._mission()["load"]:.0f} kN',
                fill="#7D1E28",
                font=("Segoe UI", 9, "bold"),
            )

        # warning overlay
        if warning:
            canvas.create_rectangle(
                0,
                0,
                width,
                5,
                fill=COLORS["yellow"],
                outline="",
            )
            canvas.create_text(
                width / 2,
                22,
                text="STRUCTURAL LIMIT APPROACHING",
                fill="#6C5210",
                font=("Segoe UI", 9, "bold"),
            )

        # failure overlay
        if broken:
            canvas.create_rectangle(
                mid_x - 115,
                24,
                mid_x + 115,
                63,
                fill="#6B1E27",
                outline="#A83D48",
                width=1,
            )
            canvas.create_text(
                mid_x,
                43,
                text="STRUCTURAL FAILURE",
                fill="#FFD0D4",
                font=("Segoe UI", 10, "bold"),
            )

        # span dimension
        canvas.create_line(
            left_x,
            height - 28,
            right_x,
            height - 28,
            fill="#294959",
            width=1,
        )
        canvas.create_text(
            mid_x,
            height - 13,
            text=f'{self._mission()["span"]:.1f} m CLEAR SPAN',
            fill="#294959",
            font=("Segoe UI", 8, "bold"),
        )

    def _draw_truck(self, canvas, x, y, angle_hint=0):
        # Tkinter Canvas has no native group rotation; the falling angle is
        # suggested by vertically offset cab/body geometry.
        tilt = angle_hint * 0.6
        canvas.create_rectangle(
            x,
            y + 14 + tilt,
            x + 70,
            y + 39 + tilt,
            fill="#E48B2F",
            outline="",
        )
        canvas.create_rectangle(
            x + 61,
            y + 21,
            x + 96,
            y + 39,
            fill="#F2A94E",
            outline="",
        )
        canvas.create_polygon(
            x + 68,
            y + 21,
            x + 77,
            y + 9,
            x + 91,
            y + 9,
            x + 96,
            y + 21,
            fill="#F2A94E",
            outline="",
        )
        for wheel_x in (x + 18, x + 62, x + 84):
            canvas.create_oval(
                wheel_x - 8,
                y + 34 + tilt,
                wheel_x + 8,
                y + 50 + tilt,
                fill="#24292C",
                outline="#C5CDD1",
                width=2,
            )

    # ---------- animation ----------

    def _animate(self, duration_ms, update, done=None):
        start = time.perf_counter()

        def frame():
            elapsed = (time.perf_counter() - start) * 1000.0
            progress = self._clamp(elapsed / duration_ms, 0.0, 1.0)
            update(progress)
            if progress < 1.0:
                self.after(16, frame)
            elif done:
                done()

        frame()

    def _run_load_test(self):
        if self.testing:
            return

        self.testing = True
        self.test_button.config(state="disabled")
        self.last_result = self._calculate()
        self._reset_result_cards()

        result = self.last_result
        structural_fail = (
            result["strength_ratio"] > 1.0
            or result["deflection_ratio"] > 1.0
        )

        self.stage_label.config(
            text="DEAD LOAD",
            fg=COLORS["yellow"],
        )

        dead_ratio = min(result["deflection_ratio"] * 0.25, 0.55)

        self._animate(
            520,
            lambda p: self._draw_scene(
                truck_progress=0.0,
                sag_ratio=dead_ratio * p,
            ),
            done=lambda: self._animate_vehicle(result, structural_fail),
        )

    def _animate_vehicle(self, result, structural_fail):
        self.stage_label.config(
            text="TRUCK CROSSING",
            fg=COLORS["yellow"],
        )

        end_progress = 0.52 if structural_fail else 1.0
        near_limit = (
            result["governing_ratio"] > 0.90
            and result["governing_ratio"] <= 1.0
        )

        def update(p):
            truck_p = p * end_progress
            load_shape = math.sin(math.pi * truck_p)
            sag = (
                result["deflection_ratio"] * 0.25
                + result["governing_ratio"] * 0.75
            ) * load_shape

            self._draw_scene(
                truck_progress=truck_p,
                sag_ratio=sag,
                warning=near_limit and 0.36 < truck_p < 0.68,
            )

        self._animate(
            2200 if structural_fail else 2900,
            update,
            done=lambda: (
                self._animate_failure(result)
                if structural_fail
                else self._inspect_result(result)
            ),
        )

    def _animate_failure(self, result):
        self.stage_label.config(
            text="FAILURE",
            fg=COLORS["red"],
        )
        self.bell()

        catastrophic = (
            result["strength_ratio"] > 1.18
            or result["deflection_ratio"] > 1.30
            or result["governing_ratio"] > 1.32
        )

        # crack pause
        self._draw_scene(
            truck_progress=0.52,
            sag_ratio=min(result["governing_ratio"], 1.4),
            show_cracks=True,
            warning=True,
        )

        def start_collapse():
            duration = 1100 if catastrophic else 820

            def update(p):
                self._draw_scene(
                    truck_progress=0.52,
                    broken=True,
                    collapse_progress=p,
                    show_cracks=True,
                    show_debris=True,
                    show_splash=catastrophic and p > 0.68,
                )

            self._animate(
                duration,
                update,
                done=lambda: self._inspect_result(result, keep_broken=True),
            )

        self.after(430, start_collapse)

    def _inspect_result(self, result, keep_broken=False):
        self.stage_label.config(text="INSPECTION", fg=COLORS["muted"])

        self._set_card(
            "strength",
            f'{result["stress"]:.1f} MPa',
            f'limit {result["stress_limit"]:.0f} MPa',
            result["strength_ratio"],
        )
        self._set_card(
            "deflection",
            f'{result["deflection"]:.1f} mm',
            f'limit {result["deflection_limit"]:.1f} mm',
            result["deflection_ratio"],
        )
        self._set_card(
            "cost",
            self._peso(result["cost"]),
            f'budget {self._peso(self._mission()["budget"])}',
            result["budget_ratio"],
        )

        if keep_broken:
            self._draw_scene(
                truck_progress=0.52,
                broken=True,
                collapse_progress=1.0,
                show_cracks=True,
                show_debris=True,
                show_splash=(
                    result["governing_ratio"] > 1.32
                    or result["strength_ratio"] > 1.18
                    or result["deflection_ratio"] > 1.30
                ),
            )
        else:
            self._draw_scene(
                truck_progress=1.0,
                sag_ratio=min(result["deflection_ratio"], 1.0),
            )

        if result["pass"]:
            self._handle_pass(result)
        else:
            self._handle_fail(result)

        self.testing = False
        self.test_button.config(state="normal")

    # ---------- outcomes ----------

    def _handle_pass(self, result):
        self.stage_label.config(text="APPROVED", fg=COLORS["green"])

        structure_efficiency = round(
            self._clamp(
                100.0 - abs(result["governing_ratio"] - 0.82) * 145.0,
                35.0,
                100.0,
            )
        )
        budget_efficiency = round(
            self._clamp(
                115.0 - result["budget_ratio"] * 70.0,
                25.0,
                100.0,
            )
        )
        attempt_bonus = self.state["attempts"] * 30
        mission_score = round(
            180
            + structure_efficiency * 2.1
            + budget_efficiency * 1.7
            + attempt_bonus
        )
        xp_gain = round(110 + mission_score * 0.22)

        index = self.state["mission_index"]
        self.state["score"] += mission_score
        self.state["xp"] += xp_gain
        self.state["best_scores"][index] = max(
            self.state["best_scores"][index],
            mission_score,
        )
        self.state["completed"][index] = True

        if index < len(MISSIONS) - 1:
            self.state["unlocked"] = max(
                self.state["unlocked"],
                index + 1,
            )

        self._save_state()
        self._render_header_only()

        self.bell()
        self.after(
            150,
            lambda: self._show_result_modal(
                passed=True,
                title="Bridge Approved",
                message="Safe · serviceable · within budget",
                stats=[
                    ("SCORE", f"+{mission_score}"),
                    ("XP", f"+{xp_gain}"),
                    (
                        "USE",
                        f'{result["governing_ratio"] * 100:.0f}%',
                    ),
                ],
            ),
        )

    def _handle_fail(self, result):
        self.stage_label.config(text="REVISE", fg=COLORS["red"])
        self.state["attempts"] = max(
            0,
            self.state["attempts"] - 1,
        )
        self.tries_stat.config(text=str(self.state["attempts"]))
        self._save_state()

        reasons = []
        if result["strength_ratio"] > 1.0:
            reasons.append("Strength")
        if result["deflection_ratio"] > 1.0:
            reasons.append("Deflection")
        if result["budget_ratio"] > 1.0:
            reasons.append("Budget")

        message = " + ".join(reasons) + " failed"

        self.after(
            150,
            lambda: self._show_result_modal(
                passed=False,
                title="Bridge Failed",
                message=message,
                stats=[
                    (
                        "STRESS",
                        f'{result["strength_ratio"] * 100:.0f}%',
                    ),
                    (
                        "DEFLECT",
                        f'{result["deflection_ratio"] * 100:.0f}%',
                    ),
                    (
                        "BUDGET",
                        f'{result["budget_ratio"] * 100:.0f}%',
                    ),
                ],
            ),
        )

    def _render_header_only(self):
        level = self.state["xp"] // 500 + 1
        self.level_label.config(text=str(level))
        self.score_label.config(text=f'{self.state["score"]:,}')

        completed = sum(bool(v) for v in self.state["completed"])
        if completed >= 6 and self.state["score"] >= 4000:
            rank = "S · Chief Bridge Engineer"
        elif completed >= 4 or self.state["score"] >= 2400:
            rank = "A · Senior Engineer"
        elif completed >= 2 or self.state["score"] >= 1000:
            rank = "B · Project Engineer"
        else:
            rank = "C · Junior Designer"
        self.rank_label.config(text=rank)

    # ---------- modals ----------

    def _modal(self, title, width=430, height=310):
        modal = tk.Toplevel(self)
        modal.title(title)
        modal.configure(bg=COLORS["panel"])
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        self.update_idletasks()
        x = self.winfo_x() + max(20, (self.winfo_width() - width) // 2)
        y = self.winfo_y() + max(20, (self.winfo_height() - height) // 2)
        modal.geometry(f"{width}x{height}+{x}+{y}")

        return modal

    def _show_help_modal(self):
        modal = self._modal("How to Play", 430, 320)

        self._modal_heading(
            modal,
            "HOW TO PLAY",
            "Build. Test. Improve.",
        )

        steps = [
            ("1", "Choose material and girder size."),
            ("2", "Run the truck load test."),
            ("3", "Pass strength, deflection, and budget."),
        ]

        box = tk.Frame(modal, bg=COLORS["panel"])
        box.pack(fill="both", expand=True, padx=22, pady=10)

        for number, text in steps:
            row = tk.Frame(
                box,
                bg=COLORS["panel2"],
                padx=10,
                pady=9,
            )
            row.pack(fill="x", pady=3)
            tk.Label(
                row,
                text=number,
                bg="#223646",
                fg=COLORS["accent"],
                font=("Segoe UI", 9, "bold"),
                width=3,
            ).pack(side="left")
            tk.Label(
                row,
                text=text,
                bg=COLORS["panel2"],
                fg=COLORS["text"],
                font=("Segoe UI", 9),
            ).pack(side="left", padx=8)

        self._modal_button(modal, "GOT IT", modal.destroy)

    def _show_mission_modal(self):
        mission = self._mission()
        modal = self._modal("Mission Brief", 470, 330)

        self._modal_heading(
            modal,
            f'MISSION {self.state["mission_index"] + 1:02d}',
            mission["title"],
        )

        tk.Label(
            modal,
            text=mission["brief"],
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(pady=(2, 12))

        stats = tk.Frame(modal, bg=COLORS["panel"])
        stats.pack(fill="x", padx=22)

        for label, value in [
            ("SPAN", f'{mission["span"]:.1f} m'),
            ("LOAD", f'{mission["load"]:.0f} kN'),
            ("BUDGET", self._peso(mission["budget"])),
            ("TRIES", str(self.state["attempts"])),
        ]:
            row = tk.Frame(
                stats,
                bg=COLORS["panel2"],
                padx=10,
                pady=7,
            )
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text=label,
                bg=COLORS["panel2"],
                fg=COLORS["muted"],
                font=("Segoe UI", 7, "bold"),
            ).pack(side="left")
            tk.Label(
                row,
                text=value,
                bg=COLORS["panel2"],
                fg=COLORS["text"],
                font=("Segoe UI", 9, "bold"),
            ).pack(side="right")

        self._modal_button(modal, "START", modal.destroy)

    def _show_result_modal(self, passed, title, message, stats):
        modal = self._modal(title, 450, 330)

        color = COLORS["green"] if passed else COLORS["red"]
        mark = "✓" if passed else "!"

        tk.Label(
            modal,
            text=mark,
            bg=COLORS["panel2"],
            fg=color,
            font=("Segoe UI", 22, "bold"),
            width=3,
        ).pack(pady=(20, 6))

        tk.Label(
            modal,
            text=title,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 17, "bold"),
        ).pack()

        tk.Label(
            modal,
            text=message,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9),
        ).pack(pady=(4, 12))

        stat_row = tk.Frame(modal, bg=COLORS["panel"])
        stat_row.pack(fill="x", padx=22)

        for label, value in stats:
            cell = tk.Frame(
                stat_row,
                bg=COLORS["panel2"],
                padx=10,
                pady=8,
            )
            cell.pack(side="left", fill="x", expand=True, padx=3)
            tk.Label(
                cell,
                text=label,
                bg=COLORS["panel2"],
                fg=COLORS["muted"],
                font=("Segoe UI", 6, "bold"),
            ).pack()
            tk.Label(
                cell,
                text=value,
                bg=COLORS["panel2"],
                fg=COLORS["text"],
                font=("Segoe UI", 11, "bold"),
            ).pack(pady=(2, 0))

        actions = tk.Frame(modal, bg=COLORS["panel"])
        actions.pack(fill="x", padx=22, pady=(18, 0))

        tk.Button(
            actions,
            text="REVIEW",
            command=modal.destroy,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            activebackground=COLORS["line"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            pady=9,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        if passed:
            text = (
                "NEXT MISSION"
                if self.state["mission_index"] < len(MISSIONS) - 1
                else "REPLAY"
            )
            tk.Button(
                actions,
                text=text,
                command=lambda: self._next_mission_from_modal(modal),
                bg=COLORS["accent"],
                fg="#101820",
                activebackground="#FFC46D",
                activeforeground="#101820",
                relief="flat",
                bd=0,
                pady=9,
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))
        elif self.state["attempts"] == 0:
            tk.Button(
                actions,
                text="RESTART",
                command=lambda: self._restart_mission_from_modal(modal),
                bg=COLORS["accent"],
                fg="#101820",
                activebackground="#FFC46D",
                activeforeground="#101820",
                relief="flat",
                bd=0,
                pady=9,
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _show_details_modal(self):
        result = self.last_result or self._calculate()
        modal = self._modal("Engineering Details", 500, 390)

        self._modal_heading(
            modal,
            "ENGINEERING",
            "Calculation Details",
        )

        grid = tk.Frame(modal, bg=COLORS["panel"])
        grid.pack(fill="both", expand=True, padx=22, pady=10)
        grid.columnconfigure((0, 1), weight=1)

        items = [
            ("Material", result["material"]),
            ("Dead load / girder", f'{result["dead_load_per_girder"]:.1f} kN/m'),
            ("Vehicle / girder", f'{result["vehicle_per_girder"]:.1f} kN'),
            ("Factored moment", f'{result["moment"]:.0f} kN·m'),
            ("Bending stress", f'{result["stress"]:.1f} MPa'),
            ("Stress limit", f'{result["stress_limit"]:.1f} MPa'),
            ("Deflection", f'{result["deflection"]:.1f} mm'),
            ("L/800 limit", f'{result["deflection_limit"]:.1f} mm'),
            ("Project cost", self._peso(result["cost"])),
            ("Utilization", f'{result["governing_ratio"] * 100:.0f}%'),
        ]

        for i, (label, value) in enumerate(items):
            cell = tk.Frame(
                grid,
                bg=COLORS["panel2"],
                padx=9,
                pady=8,
            )
            cell.grid(
                row=i // 2,
                column=i % 2,
                sticky="nsew",
                padx=3,
                pady=3,
            )
            tk.Label(
                cell,
                text=label.upper(),
                bg=COLORS["panel2"],
                fg=COLORS["muted"],
                font=("Segoe UI", 6, "bold"),
            ).pack(anchor="w")
            tk.Label(
                cell,
                text=value,
                bg=COLORS["panel2"],
                fg=COLORS["text"],
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            modal,
            text="Simplified educational model only.",
            bg=COLORS["panel"],
            fg="#607585",
            font=("Segoe UI", 7),
        ).pack(pady=(0, 8))

        self._modal_button(modal, "CLOSE", modal.destroy)

    def _show_campaign_modal(self):
        modal = self._modal("Projects", 520, 430)

        self._modal_heading(
            modal,
            "CAMPAIGN",
            "Projects",
        )

        list_frame = tk.Frame(modal, bg=COLORS["panel"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=8)

        for i, mission in enumerate(MISSIONS):
            unlocked = i <= self.state["unlocked"]
            completed = self.state["completed"][i]
            current = i == self.state["mission_index"]

            row = tk.Frame(
                list_frame,
                bg=COLORS["panel2"],
                padx=9,
                pady=7,
                highlightbackground=(
                    COLORS["accent"] if current else "#1D2B37"
                ),
                highlightthickness=1,
            )
            row.pack(fill="x", pady=2)

            tk.Label(
                row,
                text=f"{i + 1:02d}",
                bg=COLORS["panel2"],
                fg=COLORS["accent"] if unlocked else "#516574",
                font=("Segoe UI", 8, "bold"),
                width=3,
            ).pack(side="left")

            tk.Label(
                row,
                text=mission["title"],
                bg=COLORS["panel2"],
                fg=COLORS["text"] if unlocked else "#657988",
                font=("Segoe UI", 8, "bold"),
            ).pack(side="left", padx=6)

            status = (
                f'✓ {self.state["best_scores"][i]}'
                if completed
                else ("OPEN" if unlocked else "LOCKED")
            )

            tk.Button(
                row,
                text=status,
                command=lambda idx=i, m=modal: self._select_mission(idx, m),
                state="normal" if unlocked else "disabled",
                bg=COLORS["panel2"],
                fg=COLORS["green"] if completed else COLORS["muted"],
                activebackground=COLORS["line"],
                activeforeground=COLORS["text"],
                disabledforeground="#445766",
                relief="flat",
                bd=0,
                font=("Segoe UI", 7, "bold"),
                cursor="hand2" if unlocked else "",
            ).pack(side="right")

        reset = tk.Button(
            modal,
            text="RESET PROGRESS",
            command=lambda: self._reset_progress(modal),
            bg=COLORS["panel"],
            fg=COLORS["red"],
            activebackground=COLORS["panel2"],
            activeforeground=COLORS["red"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 7, "bold"),
            cursor="hand2",
        )
        reset.pack(pady=(2, 10))

    def _modal_heading(self, modal, kicker, title):
        tk.Label(
            modal,
            text=kicker,
            bg=COLORS["panel"],
            fg=COLORS["accent"],
            font=("Segoe UI", 7, "bold"),
        ).pack(pady=(20, 2))
        tk.Label(
            modal,
            text=title,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        ).pack()

    def _modal_button(self, modal, text, command):
        tk.Button(
            modal,
            text=text,
            command=command,
            bg=COLORS["accent"],
            fg="#101820",
            activebackground="#FFC46D",
            activeforeground="#101820",
            relief="flat",
            bd=0,
            padx=18,
            pady=8,
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        ).pack(pady=(6, 16))

    def _next_mission_from_modal(self, modal):
        modal.destroy()

        if self.state["mission_index"] < len(MISSIONS) - 1:
            self.state["mission_index"] += 1

        self.state["attempts"] = 3
        self._save_state()
        self._apply_suggested(show_notice=False)
        self._render_all()
        self.after(180, self._show_mission_modal)

    def _restart_mission_from_modal(self, modal):
        modal.destroy()
        self.state["attempts"] = 3
        self._save_state()
        self._apply_suggested(show_notice=False)
        self._render_all()

    def _select_mission(self, index, modal):
        if index > self.state["unlocked"]:
            return

        modal.destroy()
        self.state["mission_index"] = index
        self.state["attempts"] = 3
        self._save_state()
        self._apply_suggested(show_notice=False)
        self._render_all()
        self.after(180, self._show_mission_modal)

    def _reset_progress(self, modal):
        if not messagebox.askyesno(
            "Reset Progress",
            "Reset score, XP, and all unlocked missions?",
            parent=modal,
        ):
            return

        modal.destroy()
        self.state = self._default_state()
        self._save_state()
        self._apply_suggested(show_notice=False)
        self._render_all()
        self.after(180, self._show_mission_modal)


if __name__ == "__main__":
    app = BuildSafeGame()
    app.mainloop()
