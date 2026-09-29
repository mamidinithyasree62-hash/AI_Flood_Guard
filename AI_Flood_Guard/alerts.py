"""
AI Flood Guard - Alert Management System
Handles multi-channel alerting:
- Colored console logging (via colorama)
- Asynchronous sound alarms (via Windows winsound)
- Popup / notification banners with debounce and rate-limiting
"""

from datetime import datetime
import sys
import threading
import time
from typing import Any, Callable, Dict, Optional

# Ensure standard output can handle utf-8 safely on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI color output without requiring the optional colorama dependency.
BRIGHT = "\033[1m"
RESET = "\033[0m"
COLOR_MAP = {
    "Green": "\033[32m" + BRIGHT,
    "Yellow": "\033[33m" + BRIGHT,
    "Orange": "\033[91m" + BRIGHT,
    "Red": "\033[31m\033[40m" + BRIGHT,
}

# Windows native sound support
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class AlertManager:
    """
    Coordinates console, audio, and visual notifications.
    Ensures non-blocking execution and debounce rate-limiting.
    """

    def __init__(self, sound_enabled: bool = True, popup_enabled: bool = True):
        self.sound_enabled = sound_enabled
        self.popup_enabled = popup_enabled
        self.last_sound_time: float = 0.0
        self.sound_cooldown: float = 4.0  # Min seconds between audio alerts
        self.last_risk_level: Optional[str] = None
        self.last_popup_level: Optional[str] = None
        self.popup_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self._sound_thread: Optional[threading.Thread] = None
        self._is_beeping = False

    def set_popup_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for UI popups/toasts."""
        self.popup_callback = callback

    def set_sound_enabled(self, enabled: bool) -> None:
        """Toggle audio alerts on or off."""
        self.sound_enabled = enabled

    def _play_audio_alert(self, risk_level: str) -> None:
        """Play sound in background thread without blocking UI or loop."""
        if not HAS_WINSOUND or not self.sound_enabled:
            return

        if self._is_beeping:
            return

        def _sound_worker():
            self._is_beeping = True
            try:
                if risk_level == "Red":
                    # Urgent two-tone siren
                    for _ in range(2):
                        winsound.Beep(1600, 220)
                        time.sleep(0.05)
                        winsound.Beep(1100, 220)
                        time.sleep(0.05)
                elif risk_level == "Orange":
                    # Warning alert tone
                    winsound.Beep(1000, 350)
            except Exception:
                pass
            finally:
                self._is_beeping = False

        self._sound_thread = threading.Thread(target=_sound_worker, daemon=True)
        self._sound_thread.start()

    def log_console(self, risk_data: Dict[str, Any]) -> None:
        """
        Output structured, color-coded alert telemetry to the terminal.
        """
        level = risk_data.get("risk_level", "Green")
        score = risk_data.get("risk_score", 0.0)
        readings = risk_data.get("sensor_readings", {})
        rain = readings.get("rainfall", 0.0)
        soil = readings.get("soil_moisture", 0.0)
        water = readings.get("water_level", 0.0)
        action = risk_data.get("action", "")
        factors = risk_data.get("factors", [])
        
        color = COLOR_MAP.get(level, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sep = "=" * 70
        print(sep)
        print(f"[{timestamp}]  {color}RISK STATUS: [{level.upper()}] - {score}% ({risk_data.get('title', '')}){RESET}")
        print(f" Sensors     : Rain: {rain:>5.1f} mm/h  |  Soil Moisture: {soil:>5.1f}%  |  Water Level: {water:>4.2f}m")
        if factors:
            factor_str = " | ".join(factors[:2])
            print(f" Key Factors : {factor_str}")
        print(f" Action Req  : {action}")
        
        if level in ["Orange", "Red"]:
            print(f"{color}>>> [ALERT DISPATCHED] Sound: {'Active' if self.sound_enabled else 'Muted'} | Emergency Notification Sent <<<{RESET}")
        print(sep)

    def process_alerts(self, risk_data: Dict[str, Any]) -> None:
        """
        Evaluate risk data and trigger relevant multi-channel alerts.
        """
        risk_level = risk_data.get("risk_level", "Green")
        now = time.time()

        # 1. Console color logging
        self.log_console(risk_data)

        # 2. Audio alerting (Orange & Red)
        if risk_level in ["Orange", "Red"]:
            level_changed = (risk_level != self.last_risk_level)
            cooldown_passed = (now - self.last_sound_time >= self.sound_cooldown)
            
            if level_changed or cooldown_passed:
                self._play_audio_alert(risk_level)
                self.last_sound_time = now

        # 3. Popup notification (Orange & Red)
        escalated_to_orange = (risk_level == "Orange" and self.last_popup_level not in ["Orange", "Red"])
        escalated_to_red = (risk_level == "Red" and self.last_popup_level != "Red")

        if (escalated_to_orange or escalated_to_red) and self.popup_enabled and self.popup_callback:
            try:
                self.popup_callback(risk_data)
                self.last_popup_level = risk_level
            except Exception as e:
                print(f"[Warning] Failed to trigger popup callback: {e}")
        elif risk_level in ["Green", "Yellow"]:
            self.last_popup_level = risk_level

        self.last_risk_level = risk_level
