"""
AI Flood Guard - Real-Time Dashboard UI
A modern, dark-themed Tkinter desktop interface displaying live sensor metrics,
AI risk classification, scenario simulator controls, and event logging.
"""

from datetime import datetime
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, Optional


class FloodGuardUI:
    """
    Tkinter desktop dashboard for the AI Flood Guard system.
    """

    # Color Palette (Modern Dark Theme)
    COLOR_BG = "#0f172a"          # Slate 900
    COLOR_CARD = "#1e293b"        # Slate 800
    COLOR_CARD_BORDER = "#334155" # Slate 700
    COLOR_TEXT = "#f8fafc"        # Slate 50
    COLOR_MUTED = "#94a3b8"       # Slate 400
    
    LEVEL_COLORS = {
        "Green": "#10b981",       # Emerald 500
        "Yellow": "#f59e0b",      # Amber 500
        "Orange": "#f97316",      # Orange 500
        "Red": "#ef4444",         # Red 500
    }

    def __init__(
        self,
        root: tk.Tk,
        on_scenario_change: Optional[Callable[[str], None]] = None,
        on_sound_toggle: Optional[Callable[[bool], None]] = None,
        on_pause_toggle: Optional[Callable[[bool], None]] = None,
    ):
        self.root = root
        self.on_scenario_change = on_scenario_change
        self.on_sound_toggle = on_sound_toggle
        self.on_pause_toggle = on_pause_toggle

        self.is_paused = False
        self.sound_enabled = True

        self._setup_window()
        self._build_header()
        self._build_sensor_cards()
        self._build_risk_hero()
        self._build_control_panel()
        self._build_event_log()

    def _setup_window(self) -> None:
        self.root.title("AI Flood Guard - Autonomous Early Warning System")
        self.root.geometry("980x740")
        self.root.minsize(920, 680)
        self.root.configure(bg=self.COLOR_BG)

        # Configure custom TTK styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background=self.COLOR_BG, foreground=self.COLOR_TEXT)

    def _build_header(self) -> None:
        header_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=24, pady=16)
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg=self.COLOR_BG)
        title_box.pack(side=tk.LEFT)

        app_title = tk.Label(
            title_box,
            text="🌊 AI FLOOD GUARD",
            font=("Segoe UI", 20, "bold"),
            fg="#38bdf8",  # Sky blue
            bg=self.COLOR_BG,
        )
        app_title.pack(anchor="w")

        subtitle = tk.Label(
            title_box,
            text="Autonomous Real-Time Hydrological Monitoring & Flash Flood Risk Intelligence",
            font=("Segoe UI", 10),
            fg=self.COLOR_MUTED,
            bg=self.COLOR_BG,
        )
        subtitle.pack(anchor="w")

        # Right side status pill & clock
        info_box = tk.Frame(header_frame, bg=self.COLOR_BG)
        info_box.pack(side=tk.RIGHT)

        self.status_pill = tk.Label(
            info_box,
            text="● SYSTEM LIVE",
            font=("Segoe UI", 10, "bold"),
            fg="#10b981",
            bg="#064e3b",
            padx=12,
            pady=4,
            relief=tk.FLAT,
        )
        self.status_pill.pack(anchor="e", pady=(0, 4))

        self.time_label = tk.Label(
            info_box,
            text="--:--:--",
            font=("Consolas", 10),
            fg=self.COLOR_MUTED,
            bg=self.COLOR_BG,
        )
        self.time_label.pack(anchor="e")

    def _build_sensor_cards(self) -> None:
        cards_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=20, pady=4)
        cards_frame.pack(fill=tk.X)
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="sensors")

        # 1. Rainfall Card
        self.rain_card, self.rain_val_label, self.rain_bar = self._create_metric_card(
            cards_frame, 0, "🌧️ Rainfall Rate", "0.0 mm/h", "Max capacity: 150 mm/h"
        )

        # 2. Soil Moisture Card
        self.soil_card, self.soil_val_label, self.soil_bar = self._create_metric_card(
            cards_frame, 1, "🌱 Soil Saturation", "0.0 %", "Infiltration threshold: 85%"
        )

        # 3. Water Level Card
        self.water_card, self.water_val_label, self.water_bar = self._create_metric_card(
            cards_frame, 2, "📏 River Water Level", "0.00 m", "Danger overflow: 7.50 m"
        )

    def _create_metric_card(
        self, parent: tk.Widget, col: int, title: str, default_val: str, caption: str
    ):
        card = tk.Frame(
            parent,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=16,
            pady=12,
        )
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        title_lbl = tk.Label(
            card, text=title, font=("Segoe UI", 11, "bold"), fg=self.COLOR_MUTED, bg=self.COLOR_CARD
        )
        title_lbl.pack(anchor="w")

        val_lbl = tk.Label(
            card, text=default_val, font=("Segoe UI", 18, "bold"), fg=self.COLOR_TEXT, bg=self.COLOR_CARD
        )
        val_lbl.pack(anchor="w", pady=(4, 6))

        # Progress bar indicator
        canvas_bar = tk.Canvas(card, height=8, bg="#334155", highlightthickness=0)
        canvas_bar.pack(fill=tk.X, pady=(2, 6))
        # Initial fill
        canvas_bar.create_rectangle(0, 0, 0, 8, fill="#38bdf8", outline="", tags="fill")

        cap_lbl = tk.Label(
            card, text=caption, font=("Segoe UI", 9), fg=self.COLOR_MUTED, bg=self.COLOR_CARD
        )
        cap_lbl.pack(anchor="w")

        return card, val_lbl, canvas_bar

    def _build_risk_hero(self) -> None:
        hero_frame = tk.Frame(
            self.root,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        hero_frame.pack(fill=tk.X, padx=26, pady=12)

        # Top row: Risk Badge and Score
        top_row = tk.Frame(hero_frame, bg=self.COLOR_CARD)
        top_row.pack(fill=tk.X)

        self.risk_badge = tk.Label(
            top_row,
            text="LEVEL: GREEN - SAFE",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg=self.LEVEL_COLORS["Green"],
            padx=14,
            pady=6,
            relief=tk.FLAT,
        )
        self.risk_badge.pack(side=tk.LEFT)

        self.score_label = tk.Label(
            top_row,
            text="AI Risk Score: 12.0%",
            font=("Segoe UI", 15, "bold"),
            fg=self.LEVEL_COLORS["Green"],
            bg=self.COLOR_CARD,
        )
        self.score_label.pack(side=tk.RIGHT)

        # Visual Risk Scale bar
        self.risk_bar_canvas = tk.Canvas(hero_frame, height=14, bg="#334155", highlightthickness=0)
        self.risk_bar_canvas.pack(fill=tk.X, pady=(12, 10))
        self.risk_bar_canvas.create_rectangle(0, 0, 0, 14, fill="#10b981", outline="", tags="fill")

        # Factors & Action Advice
        self.factors_label = tk.Label(
            hero_frame,
            text="Key Drivers: Baseline hydrological conditions.",
            font=("Segoe UI", 10),
            fg=self.COLOR_MUTED,
            bg=self.COLOR_CARD,
            anchor="w",
            justify=tk.LEFT,
        )
        self.factors_label.pack(fill=tk.X)

        self.action_box = tk.Label(
            hero_frame,
            text="Action Required: Conditions normal. Continuous AI observation active.",
            font=("Segoe UI", 10, "italic"),
            fg="#38bdf8",
            bg="#0f172a",
            padx=10,
            pady=8,
            anchor="w",
            justify=tk.LEFT,
        )
        self.action_box.pack(fill=tk.X, pady=(8, 0))

    def _build_control_panel(self) -> None:
        control_frame = tk.Frame(self.root, bg=self.COLOR_BG, padx=26, pady=4)
        control_frame.pack(fill=tk.X)

        ctrl_title = tk.Label(
            control_frame,
            text="🎮 Hackathon Simulation Controls & Scenarios",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLOR_TEXT,
            bg=self.COLOR_BG,
        )
        ctrl_title.pack(anchor="w", pady=(0, 6))

        btn_row = tk.Frame(control_frame, bg=self.COLOR_BG)
        btn_row.pack(fill=tk.X)

        scenarios = [
            ("☀️ Normal / Dry", "NORMAL", "#10b981"),
            ("🌧️ Moderate Rain", "MODERATE_RAIN", "#f59e0b"),
            ("⛈️ Heavy Storm", "HEAVY_STORM", "#f97316"),
            ("🚨 Flash Flood Surge", "FLASH_FLOOD", "#ef4444"),
        ]

        for label, scen_id, col in scenarios:
            btn = tk.Button(
                btn_row,
                text=label,
                font=("Segoe UI", 9, "bold"),
                fg="#ffffff",
                bg=col,
                activebackground=col,
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=10,
                pady=6,
                cursor="hand2",
                command=lambda s=scen_id: self._trigger_scenario(s),
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))

        # Audio mute toggle
        self.sound_btn = tk.Button(
            btn_row,
            text="🔊 Sound: ON",
            font=("Segoe UI", 9),
            fg=self.COLOR_TEXT,
            bg="#334155",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._toggle_sound,
        )
        self.sound_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # Pause / Resume simulation
        self.pause_btn = tk.Button(
            btn_row,
            text="⏸ Pause",
            font=("Segoe UI", 9),
            fg=self.COLOR_TEXT,
            bg="#334155",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self._toggle_pause,
        )
        self.pause_btn.pack(side=tk.RIGHT)

    def _build_event_log(self) -> None:
        log_frame = tk.Frame(
            self.root,
            bg=self.COLOR_CARD,
            highlightbackground=self.COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=16,
            pady=10,
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=26, pady=(10, 16))

        log_hdr = tk.Label(
            log_frame,
            text="📋 Live Hydrological Event Log",
            font=("Segoe UI", 10, "bold"),
            fg=self.COLOR_MUTED,
            bg=self.COLOR_CARD,
        )
        log_hdr.pack(anchor="w", pady=(0, 4))

        # Text area with scrollbar
        self.log_text = tk.Text(
            log_frame,
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Consolas", 9),
            height=7,
            relief=tk.FLAT,
            wrap=tk.WORD,
        )
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure color tags
        self.log_text.tag_config("Green", foreground="#10b981")
        self.log_text.tag_config("Yellow", foreground="#f59e0b")
        self.log_text.tag_config("Orange", foreground="#f97316")
        self.log_text.tag_config("Red", foreground="#ef4444")
        self.log_text.tag_config("Muted", foreground="#94a3b8")

    def _trigger_scenario(self, scenario: str) -> None:
        if self.on_scenario_change:
            self.on_scenario_change(scenario)
        self.add_log_entry("SYSTEM", f"Manual scenario override triggered: {scenario}")

    def _toggle_sound(self) -> None:
        self.sound_enabled = not self.sound_enabled
        text = "🔊 Sound: ON" if self.sound_enabled else "🔇 Sound: MUTED"
        self.sound_btn.configure(text=text)
        if self.on_sound_toggle:
            self.on_sound_toggle(self.sound_enabled)

    def _toggle_pause(self) -> None:
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.configure(text="▶ Resume", bg="#0284c7")
            self.status_pill.configure(text="⏸ PAUSED", bg="#78350f", fg="#fde68a")
        else:
            self.pause_btn.configure(text="⏸ Pause", bg="#334155")
            self.status_pill.configure(text="● SYSTEM LIVE", bg="#064e3b", fg="#10b981")

        if self.on_pause_toggle:
            self.on_pause_toggle(self.is_paused)

    def add_log_entry(self, level: str, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] ", "Muted")
        self.log_text.insert(tk.END, f"[{level}] ", level if level in self.LEVEL_COLORS else "Muted")
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def show_alert_popup(self, risk_data: Dict[str, Any]) -> None:
        """Display an emergency notification popup for critical risk escalation."""
        level = risk_data.get("risk_level", "Red")
        score = risk_data.get("risk_score", 0.0)
        action = risk_data.get("action", "")

        def _popup():
            if level == "Red":
                messagebox.showerror(
                    "🚨 CRITICAL FLOOD WARNING 🚨",
                    f"FLASH FLOOD IMMINENT!\n\nRisk Score: {score}%\n\nAction Required:\n{action}\n\nPlease take immediate safety precautions!",
                )
            else:
                messagebox.showwarning(
                    "⚠️ ELEVATED FLOOD ADVISORY",
                    f"HIGH FLOOD RISK DETECTED!\n\nRisk Score: {score}%\n\nAction Required:\n{action}",
                )

        # Trigger on UI thread
        self.root.after(0, _popup)

    def update_metrics(self, risk_data: Dict[str, Any]) -> None:
        """Update live UI metrics, gauges, risk badges, and logs."""
        readings = risk_data.get("sensor_readings", {})
        rain = readings.get("rainfall", 0.0)
        soil = readings.get("soil_moisture", 0.0)
        water = readings.get("water_level", 0.0)

        level = risk_data.get("risk_level", "Green")
        score = risk_data.get("risk_score", 0.0)
        factors = risk_data.get("factors", [])
        action = risk_data.get("action", "")
        level_color = self.LEVEL_COLORS.get(level, "#10b981")

        # Update Clock
        self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Update Sensor Text
        self.rain_val_label.configure(text=f"{rain:.1f} mm/h")
        self.soil_val_label.configure(text=f"{soil:.1f} %")
        self.water_val_label.configure(text=f"{water:.2f} m")

        # Update Sensor Bar Widths
        self._update_bar(self.rain_bar, rain / 150.0, "#38bdf8")
        self._update_bar(self.soil_bar, soil / 100.0, "#a855f7")
        self._update_bar(self.water_bar, water / 10.0, "#06b6d4")

        # Update Risk Badge and Score
        self.risk_badge.configure(
            text=f"LEVEL: {level.upper()} - {risk_data.get('title', '')}",
            bg=level_color,
        )
        self.score_label.configure(
            text=f"AI Risk Score: {score:.1f}%",
            fg=level_color,
        )

        # Update Hero Risk Bar
        self._update_bar(self.risk_bar_canvas, score / 100.0, level_color)

        # Update Factors and Action
        factor_str = " | ".join(factors)
        self.factors_label.configure(text=f"Key Drivers: {factor_str}")
        self.action_box.configure(text=f"Action Required: {action}")

        # Add to event log
        log_msg = f"Rain: {rain:.1f}mm/h | Soil: {soil:.1f}% | Water: {water:.2f}m | Score: {score:.1f}%"
        self.add_log_entry(level, log_msg)

    def _update_bar(self, canvas: tk.Canvas, fraction: float, color: str) -> None:
        fraction = max(0.0, min(1.0, fraction))
        width = canvas.winfo_width()
        if width <= 1:
            width = 250  # Default fallback width before first render
        fill_width = int(width * fraction)
        height = canvas.winfo_height() or 10
        canvas.coords("fill", 0, 0, fill_width, height)
        canvas.itemconfig("fill", fill=color)
