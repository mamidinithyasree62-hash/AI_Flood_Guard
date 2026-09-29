import argparse
import sys
import time
import tkinter as tk
from typing import Any, Dict, Optional

# Ensure safe console encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from alerts import AlertManager
from flood_model import FloodRiskClassifier, SensorSimulator
from ui import FloodGuardUI


class FloodGuardApp:
    """
    Main orchestrator for the AI Flood Guard platform.
    Coordinates simulation, prediction, alerting, and visualization.
    """

    def __init__(
        self,
        initial_scenario: str = "NORMAL",
        update_interval: float = 1.5,
        sound_enabled: bool = True,
        is_cli_mode: bool = False,
    ):
        self.update_interval = update_interval
        self.is_cli_mode = is_cli_mode
        self.is_paused = False

        # 1. Initialize Core Subsystems
        print("[Initializing] Hydrological Sensor Simulator...")
        self.simulator = SensorSimulator(initial_scenario=initial_scenario)

        print("[Initializing] AI Flood Risk Classifier (ML + Physics)...")
        self.classifier = FloodRiskClassifier()

        print("[Initializing] Multi-Channel Alert Manager...")
        self.alerts = AlertManager(sound_enabled=sound_enabled, popup_enabled=not is_cli_mode)

        # 2. UI Attributes
        self.root: Optional[tk.Tk] = None
        self.ui: Optional[FloodGuardUI] = None

    def evaluate_cycle(self) -> Dict[str, Any]:
        """
        Execute a single hydrological monitoring and decision cycle:
        1. Collect sensor readings (simulated or live)
        2. Pass readings into the AI risk classifier
        3. Trigger multi-channel alerts if thresholds met
        4. Return the risk assessment payload
        """
        # Step 1: Collect sensor telemetry
        readings = self.simulator.get_readings()

        # Step 2: Classify flood risk level
        risk_data = self.classifier.predict_risk(**readings)

        # Step 3: Trigger alerts (console colors, audio sirens, popups)
        self.alerts.process_alerts(risk_data)

        return risk_data

    def _on_scenario_selected(self, scenario: str) -> None:
        """Callback when user selects a different scenario in the UI."""
        self.simulator.set_scenario(scenario)
        print(f"\n[Scenario Change] Switched to: {scenario}")

    def _on_sound_toggled(self, enabled: bool) -> None:
        """Callback when user toggles sound alert in the UI."""
        self.alerts.set_sound_enabled(enabled)
        state = "Enabled" if enabled else "Muted"
        print(f"\n[Audio Alert] Sound {state}")

    def _on_pause_toggled(self, is_paused: bool) -> None:
        """Callback when user pauses or resumes simulation."""
        self.is_paused = is_paused

    def _gui_loop_step(self) -> None:
        """Single tick of the GUI update loop scheduled via Tkinter root.after."""
        if not self.is_paused and self.ui:
            try:
                risk_data = self.evaluate_cycle()
                self.ui.update_metrics(risk_data)
            except Exception as e:
                print(f"[Error in evaluation cycle]: {e}")

        # Schedule next tick
        if self.root:
            delay_ms = int(self.update_interval * 1000)
            self.root.after(delay_ms, self._gui_loop_step)

    def run_gui(self) -> None:
        """Launch the Tkinter desktop GUI and run continuous real-time monitoring."""
        print("[AI Flood Guard] Starting GUI Dashboard...")
        self.root = tk.Tk()

        # Instantiate UI and hook callbacks
        self.ui = FloodGuardUI(
            root=self.root,
            on_scenario_change=self._on_scenario_selected,
            on_sound_toggle=self._on_sound_toggled,
            on_pause_toggle=self._on_pause_toggled,
        )

        # Connect alert manager popup trigger to UI dialog
        self.alerts.set_popup_callback(self.ui.show_alert_popup)

        # Run first evaluation immediately
        initial_data = self.evaluate_cycle()
        self.ui.update_metrics(initial_data)

        # Schedule continuous loop
        delay_ms = int(self.update_interval * 1000)
        self.root.after(delay_ms, self._gui_loop_step)

        # Start Tkinter event loop
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n[AI Flood Guard] Shutdown signal received. Exiting GUI.")
        finally:
            print("[AI Flood Guard] System stopped.")

    def run_cli(self, max_cycles: Optional[int] = None) -> None:
        """Run headless CLI monitoring loop in terminal."""
        print("\n" + "=" * 70)
        print(">>> AI FLOOD GUARD - REAL-TIME TERMINAL MONITORING MODE <<<")
        print("=" * 70)
        print("Press Ctrl+C to terminate the monitoring loop.\n")

        cycle_count = 0
        try:
            while True:
                cycle_count += 1
                self.evaluate_cycle()

                if max_cycles and cycle_count >= max_cycles:
                    print(f"\n[Completed] Reached requested limit of {max_cycles} cycles.")
                    break

                time.sleep(self.update_interval)
        except KeyboardInterrupt:
            print("\n[AI Flood Guard] Monitoring loop interrupted by user. Exiting.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Flood Guard - Real-Time Hydrological Monitoring & Alerting"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in headless terminal CLI mode instead of launching the Tkinter GUI",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="NORMAL",
        choices=["NORMAL", "MODERATE_RAIN", "HEAVY_STORM", "FLASH_FLOOD"],
        help="Initial simulation scenario preset (default: NORMAL)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.5,
        help="Monitoring cycle interval in seconds (default: 1.5s)",
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        help="Mute audio alert beeps and sirens",
    )
    parser.add_argument(
        "-n",
        "--cycles",
        type=int,
        default=None,
        help="Number of monitoring cycles to run before exiting (CLI mode only)",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    app = FloodGuardApp(
        initial_scenario=args.scenario,
        update_interval=args.interval,
        sound_enabled=not args.mute,
        is_cli_mode=args.cli,
    )

    if args.cli:
        app.run_cli(max_cycles=args.cycles)
    else:
        app.run_gui()


if __name__ == "__main__":
    main()
