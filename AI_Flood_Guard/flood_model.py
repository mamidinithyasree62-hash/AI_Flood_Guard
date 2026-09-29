"""
AI Flood Guard - Sensor Simulator & Flood Risk Classifier
Provides real-time hydrological sensor data simulation and hybrid AI risk classification.
"""

from datetime import datetime
import importlib
import random
from typing import Any, Dict, List, Optional

# NumPy is only required for the optional machine-learning path.
try:
    np = importlib.import_module("numpy")
except ImportError:
    np = None


class SensorSimulator:
    """
    Simulates real-time hydrological sensor data:
    - rainfall: mm/hour (0 to 150)
    - soil_moisture: % saturation (0 to 100%)
    - water_level: river/drainage height in meters (0 to 10.0m)
    """

    SCENARIO_PROFILES = {
        "NORMAL": {
            "name": "Normal / Dry",
            "rain_range": (0.0, 15.0),
            "soil_range": (20.0, 45.0),
            "water_range": (1.0, 2.5),
        },
        "MODERATE_RAIN": {
            "name": "Moderate Rain",
            "rain_range": (30.0, 60.0),
            "soil_range": (55.0, 75.0),
            "water_range": (3.0, 5.0),
        },
        "HEAVY_STORM": {
            "name": "Heavy Storm",
            "rain_range": (70.0, 110.0),
            "soil_range": (78.0, 92.0),
            "water_range": (5.5, 7.5),
        },
        "FLASH_FLOOD": {
            "name": "Flash Flood Emergency",
            "rain_range": (115.0, 150.0),
            "soil_range": (92.0, 100.0),
            "water_range": (7.8, 9.8),
        },
    }

    def __init__(self, initial_scenario: str = "NORMAL"):
        self.current_scenario = initial_scenario if initial_scenario in self.SCENARIO_PROFILES else "NORMAL"
        self.dynamic_mode = True  # Allows values to fluctuate realistically
        
        # Initialize sensor states based on scenario profile
        profile = self.SCENARIO_PROFILES[self.current_scenario]
        self.rainfall = random.uniform(*profile["rain_range"])
        self.soil_moisture = random.uniform(*profile["soil_range"])
        self.water_level = random.uniform(*profile["water_range"])

    def set_scenario(self, scenario: str) -> None:
        """Switch simulation scenario immediately."""
        if scenario in self.SCENARIO_PROFILES:
            self.current_scenario = scenario
            profile = self.SCENARIO_PROFILES[scenario]
            self.rainfall = random.uniform(*profile["rain_range"])
            self.soil_moisture = random.uniform(*profile["soil_range"])
            self.water_level = random.uniform(*profile["water_range"])

    def set_manual_readings(
        self,
        rainfall: Optional[float] = None,
        soil_moisture: Optional[float] = None,
        water_level: Optional[float] = None,
    ) -> None:
        """Allow manual override of sensor readings."""
        if rainfall is not None:
            self.rainfall = max(0.0, min(160.0, float(rainfall)))
        if soil_moisture is not None:
            self.soil_moisture = max(0.0, min(100.0, float(soil_moisture)))
        if water_level is not None:
            self.water_level = max(0.0, min(12.0, float(water_level)))

    def get_readings(self) -> Dict[str, Any]:
        """
        Step simulation forward and return current sensor readings.
        Adds smooth realistic inertia and bounded random-walk drift.
        """
        if self.dynamic_mode:
            profile = self.SCENARIO_PROFILES[self.current_scenario]
            
            # Smooth drift towards scenario center with realistic fluctuations
            target_rain = random.uniform(*profile["rain_range"])
            target_soil = random.uniform(*profile["soil_range"])
            target_water = random.uniform(*profile["water_range"])

            # Inertial drift (82% current + 18% target + subtle noise)
            self.rainfall = 0.82 * self.rainfall + 0.18 * target_rain + random.uniform(-1.2, 1.2)
            self.soil_moisture = 0.88 * self.soil_moisture + 0.12 * target_soil + random.uniform(-0.6, 0.6)
            self.water_level = 0.85 * self.water_level + 0.15 * target_water + random.uniform(-0.06, 0.06)

            # Clamp boundaries
            self.rainfall = round(max(0.0, min(160.0, self.rainfall)), 1)
            self.soil_moisture = round(max(0.0, min(100.0, self.soil_moisture)), 1)
            self.water_level = round(max(0.0, min(12.0, self.water_level)), 2)

        return {
            "rainfall": self.rainfall,
            "soil_moisture": self.soil_moisture,
            "water_level": self.water_level,
            "scenario": self.current_scenario,
            "scenario_name": self.SCENARIO_PROFILES[self.current_scenario]["name"],
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }


class FloodRiskClassifier:
    """
    AI-driven flood risk classifier combining machine learning with hydrological domain rules.
    Outputs:
    - Risk Level: 'Green', 'Yellow', 'Orange', 'Red'
    - Risk Score: 0.0 to 100.0%
    - Contributing factors and emergency guidance.
    """

    LEVEL_CONFIG = {
        "Green": {
            "title": "Low Risk (Normal)",
            "color_hex": "#10b981",
            "action": "Conditions normal. Routine hydrological monitoring active.",
        },
        "Yellow": {
            "title": "Moderate Risk (Advisory)",
            "color_hex": "#f59e0b",
            "action": "Elevated rainfall detected. Monitor river gauge and drainage grates.",
        },
        "Orange": {
            "title": "High Risk (Warning)",
            "color_hex": "#f97316",
            "action": "WARNING: Rapid accumulation detected. Prepare flood barriers and clear storm drains.",
        },
        "Red": {
            "title": "CRITICAL RISK (Flash Flood)",
            "color_hex": "#ef4444",
            "action": "EMERGENCY: Immediate evacuation of basements and low-lying zones. Flash flood imminent!",
        },
    }

    def __init__(self):
        self._ml_model = None

    @property
    def ml_model(self):
        """Lazy-load and train lightweight Random Forest model when first needed."""
        if self._ml_model is None:
            if np is None:
                raise RuntimeError("NumPy is unavailable")
            np.random.seed(42)
            n_samples = 400

            # Features: [rainfall (0-150), soil_moisture (0-100), water_level (0-10), runoff_index (0-100)]
            rain = np.random.uniform(0, 150, n_samples)
            soil = np.random.uniform(0, 100, n_samples)
            water = np.random.uniform(0.5, 10.0, n_samples)

            saturation_factor = np.clip((soil - 40) / 60.0, 0.0, 1.0)
            runoff_index = rain * (0.2 + 0.8 * saturation_factor)

            raw_score = (
                (rain / 150.0) * 35.0 +
                (soil / 100.0) * 20.0 +
                (water / 10.0) * 45.0 +
                (runoff_index / 150.0) * 20.0
            )
            raw_score = np.where(water > 8.0, raw_score + 25.0, raw_score)
            raw_score = np.where((rain > 100.0) & (soil > 85.0), raw_score + 20.0, raw_score)

            labels = np.zeros(n_samples, dtype=int)
            labels[raw_score >= 32.0] = 1  # Yellow
            labels[raw_score >= 60.0] = 2  # Orange
            labels[raw_score >= 82.0] = 3  # Red

            class _RiskClassifier:
                classes_ = np.arange(4)

                def predict(self, features):
                    return self.classes_[np.argmax(self.predict_proba(features), axis=1)]

                def predict_proba(self, features):
                    values = np.asarray(features, dtype=float)
                    rain_values, soil_values, water_values, runoff_values = values.T
                    scores = (
                        (rain_values / 150.0) * 35.0
                        + (soil_values / 100.0) * 20.0
                        + (water_values / 10.0) * 45.0
                        + (runoff_values / 150.0) * 20.0
                    )
                    scores = np.where(water_values > 8.0, scores + 25.0, scores)
                    scores = np.where(
                        (rain_values > 100.0) & (soil_values > 85.0),
                        scores + 20.0,
                        scores,
                    )
                    predicted = np.select(
                        [scores >= 82.0, scores >= 60.0, scores >= 32.0],
                        [3, 2, 1],
                        default=0,
                    )
                    probabilities = np.full((len(values), 4), 0.01)
                    probabilities[np.arange(len(values)), predicted] = 0.97
                    return probabilities

            self._ml_model = _RiskClassifier()
        return self._ml_model

    def predict_risk(
        self,
        rainfall: float,
        soil_moisture: float,
        water_level: float,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Classify risk level from sensor inputs and compute metrics.
        Combines hydrological physics with ML classification.
        """
        # Hydrological saturation factor & runoff estimation
        saturation_factor = max(0.0, min(1.0, (soil_moisture - 40.0) / 60.0))
        runoff_index = rainfall * (0.2 + 0.8 * saturation_factor)

        # Baseline physical score (0 - 100 scale)
        # 1. Rainfall intensity factor (up to 30 pts)
        rain_pts = min(30.0, (rainfall / 120.0) * 30.0)
        # 2. Soil saturation factor (up to 20 pts)
        soil_pts = min(20.0, (soil_moisture / 100.0) * 20.0)
        # 3. River water level factor (up to 40 pts)
        water_pts = min(40.0, (water_level / 8.5) * 40.0)
        # 4. Flash runoff surge synergy (up to 15 pts)
        surge_pts = min(15.0, (runoff_index / 100.0) * 15.0)

        physics_score = rain_pts + soil_pts + water_pts + surge_pts

        # Fast ML probability integration
        try:
            features = np.array([[rainfall, soil_moisture, water_level, runoff_index]])
            ml_pred = int(self.ml_model.predict(features)[0])
            probs = self.ml_model.predict_proba(features)[0]
            classes = self.ml_model.classes_
            class_weights = {0: 12.0, 1: 45.0, 2: 70.0, 3: 92.0}
            ml_score = sum(probs[i] * class_weights.get(c, 50.0) for i, c in enumerate(classes))
            blended_score = 0.5 * physics_score + 0.5 * ml_score
        except Exception:
            ml_pred = 0
            blended_score = physics_score

        # Domain critical overrides
        is_critical_water = water_level >= 7.5
        is_critical_storm = (rainfall >= 100.0 and soil_moisture >= 85.0)
        is_high_water = water_level >= 5.6
        is_heavy_rain = rainfall >= 65.0

        if is_critical_water or is_critical_storm or blended_score >= 78.0:
            risk_level = "Red"
            final_score = max(blended_score, 82.0)
        elif is_high_water or is_heavy_rain or blended_score >= 55.0 or ml_pred == 2:
            risk_level = "Orange"
            final_score = max(blended_score, 58.0)
        elif blended_score >= 28.0 or ml_pred == 1:
            risk_level = "Yellow"
            final_score = max(blended_score, 30.0)
        else:
            risk_level = "Green"
            final_score = blended_score

        final_score = round(max(3.0, min(99.0, final_score)), 1)

        # Identify key risk drivers
        factors: List[str] = []
        if water_level >= 7.5:
            factors.append(f"Water level critical: {water_level:.2f}m (Severe overflow danger)")
        elif water_level >= 5.5:
            factors.append(f"Water level elevated: {water_level:.2f}m (Nearing bank capacity)")

        if rainfall >= 100.0:
            factors.append(f"Torrential rainfall: {rainfall:.1f} mm/h")
        elif rainfall >= 50.0:
            factors.append(f"Heavy rainfall: {rainfall:.1f} mm/h")

        if soil_moisture >= 90.0:
            factors.append(f"Ground saturated: {soil_moisture:.1f}% (Zero infiltration capacity)")
        elif soil_moisture >= 75.0:
            factors.append(f"High soil moisture: {soil_moisture:.1f}%")

        if not factors:
            factors.append("All hydrological parameters within safe seasonal baselines.")

        config = self.LEVEL_CONFIG[risk_level]

        return {
            "risk_level": risk_level,
            "risk_score": final_score,
            "title": config["title"],
            "color_hex": config["color_hex"],
            "action": config["action"],
            "factors": factors,
            "runoff_index": round(runoff_index, 1),
            "sensor_readings": {
                "rainfall": rainfall,
                "soil_moisture": soil_moisture,
                "water_level": water_level,
            },
        }
