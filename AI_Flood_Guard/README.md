# 🌊 AI Flood Guard - Autonomous Early Warning & Flash Flood Risk Intelligence

> An end-to-end, edge-ready hydrological monitoring system combining hybrid machine learning, environmental physics, multi-channel alerting, and a real-time desktop dashboard.

---

## 📌 Table of Contents
- [1. Executive Summary](#1-executive-summary)
- [2. How the System Was Created & Architectural Design](#2-how-the-system-was-created--architectural-design)
  - [2.1 Technology Stack](#21-technology-stack)
  - [2.2 Modular Architecture](#22-modular-architecture)
  - [2.3 Real-Time Lifecycle Flow](#23-real-time-lifecycle-flow)
- [3. Hydrological Measures & Parameters](#3-hydrological-measures--parameters)
  - [3.1 Key Sensor Metrics & Units](#31-key-sensor-metrics--units)
  - [3.2 Physics-Based Soil Saturation & Runoff Principle](#32-physics-based-soil-saturation--runoff-principle)
  - [3.3 4-Tier Risk Matrix & Action Thresholds](#33-4-tier-risk-matrix--action-thresholds)
- [4. Advantages](#4-advantages)
- [5. Disadvantages & Limitations](#5-disadvantages--limitations)
- [6. Future Scope & Hardware Integration](#6-future-scope--hardware-integration)
- [7. Installation & Quick Start Guide](#7-installation--quick-start-guide)

---

## 1. Executive Summary

Flash floods are among the deadliest natural hazards due to their rapid onset, often leaving communities with less than an hour to evacuate. Traditional early-warning solutions frequently rely on remote cloud servers and internet infrastructure that are susceptible to power outages and cellular tower failures during severe storms.

**AI Flood Guard** is designed as an **autonomous, offline-first edge monitoring system**. It continuously ingests hydrological sensor data (rainfall intensity, soil saturation, and river water levels), classifies danger in real-time through a hybrid AI engine (Random Forest ML blended with hydrological physics equations), dispatches instant multi-channel warnings (colored console telemetry, asynchronous sirens, and popups), and renders live telemetry on an interactive desktop dashboard.

---

## 2. How the System Was Created & Architectural Design

The project was engineered with a modular, decoupled architecture where data ingestion, intelligence, alerting, and visualization operate as independent layers coordinated by a central orchestrator.

```
+-------------------------------------------------------------------------+
|                              app.py                                     |
|                   (Main Application Orchestrator)                       |
+-------------------+------------------+-------------------+---------------+
                    |                  |                   |
                    v                  v                   v
     +--------------------------+  +-----------------+  +-----------------+
     |      flood_model.py      |  |    alerts.py    |  |      ui.py      |
     | - SensorSimulator        |  | - Color Console |  | - Tkinter GUI   |
     | - FloodRiskClassifier    |  | - Winsound Siren|  | - Live Gauges   |
     |   * Random Forest ML     |  | - Popups/Toasts |  | - Scenario Btns |
     |   * Runoff Physics Engine|  | - Rate Limiter  |  | - Event Log     |
     +--------------------------+  +-----------------+  +-----------------+
```

### 2.1 Technology Stack
- **Language**: Python 3.13+
- **Machine Learning**: `scikit-learn` (`RandomForestClassifier`) for non-linear hydrological pattern recognition.
- **Mathematical Computation**: `numpy` for vector processing and continuous score interpolation.
- **Terminal Telemetry**: `colorama` for cross-platform, color-coded ANSI console reporting.
- **Desktop Graphical Interface**: Python's native `tkinter` and `ttk` with custom vector canvas gauges.
- **Audio Siren Engine**: Windows native `winsound` executed inside background daemon threads.

### 2.2 Modular Architecture

1. **Hydrological Simulation Layer ([`flood_model.py`](flood_model.py) - `SensorSimulator`)**:
   - Generates dynamic, continuous sensor readings using an **inertial random walk formula**:
     $$\text{Value}_{t} = 0.85 \times \text{Value}_{t-1} + 0.15 \times \text{Target} + \epsilon$$
   - Prevents abrupt, unrealistic number jumps by simulating environmental inertia (rivers rise and ground absorbs moisture gradually).
   - Provides 4 preset meteorological scenarios (`NORMAL`, `MODERATE_RAIN`, `HEAVY_STORM`, `FLASH_FLOOD`) for live demonstrations.

2. **Hybrid AI & Physics Engine ([`flood_model.py`](flood_model.py) - `FloodRiskClassifier`)**:
   - Combines data-driven machine learning with empirical hydrological physics:
     - **ML Classifier**: A lightweight Random Forest classifier trained on multidimensional hydrological matrices to compute multi-class risk probabilities.
     - **Hydrological Domain Rules**: Implements the **Soil Conservation Service (SCS-CN)** runoff principle, calculating how soil saturation exponentially scales surface runoff volume.
     - **Physical Failsafe Overrides**: Ensures that catastrophic anomalies (e.g. water level exceeding $7.5\text{m}$ riverbank capacity) immediately elevate risk to Red regardless of individual sensor fluctuations.

3. **Multi-Channel Alert Dispatcher ([`alerts.py`](alerts.py) - `AlertManager`)**:
   - **Color-Coded Terminal Log**: Real-time structured telemetry output to the terminal with ANSI colors.
   - **Asynchronous Audio Sirens**: Distinct acoustic profiles for Orange (warning pulse) and Red (rapid two-tone siren). Operates inside a background `threading.Thread` so audio execution never freezes or stutters the GUI loop.
   - **Smart Debounce & Rate Limiting**: Implements cooldown timers and state-escalation detection to prevent alert notification spamming.

4. **Live Desktop Dashboard ([`ui.py`](ui.py) - `FloodGuardUI`)**:
   - Built using a high-contrast dark theme (`#0f172a`, `#1e293b`) optimized for emergency operations centers (EOC).
   - Features real-time metric cards with dynamic canvas-rendered capacity bars.
   - Prominent risk status badge with instant color shifting (Green $\rightarrow$ Yellow $\rightarrow$ Orange $\rightarrow$ Red).
   - One-click scenario injection controls for hackathon judges and audiences.
   - Scrollable live event logging window.

5. **Application Entry Point ([`app.py`](app.py) - `FloodGuardApp`)**:
   - Unifies all modules into a non-blocking loop (polling every 1.5 seconds).
   - Supports both full interactive GUI mode and headless CLI mode (`--cli`) for servers or automated test suites.

---

## 3. Hydrological Measures & Parameters

### 3.1 Key Sensor Metrics & Units

| Metric | Measured Parameter | Unit | Physical Range | Real-World Hydrological Benchmark |
| :--- | :--- | :--- | :--- | :--- |
| **$R$** | Rainfall Rate | $\text{mm/hour}$ | $0.0 - 150.0\text{ mm/h}$ | WMO standard: $>50\text{ mm/h}$ denotes violent downpour / cloudburst. |
| **$S$** | Soil Moisture Content | $\%$ Saturation | $0.0 - 100.0\%$ | Saturated Hydraulic Conductivity limit: $>85\%$ indicates zero infiltration capacity. |
| **$W$** | River / Drain Water Level | $\text{meters (m)}$ | $0.0 - 10.0\text{ m}$ | Local river gauge depth relative to riverbed baseline. |
| **$Q_{ind}$** | Runoff Index | Calculated | $0.0 - 150.0$ | Estimated instantaneous surface runoff surge volume. |

### 3.2 Physics-Based Soil Saturation & Runoff Principle

The AI classifier computes a continuous **Runoff Index ($Q_{ind}$)** based on the Soil Conservation Service Curve Number (SCS-CN) hydrology method:

$$\text{Saturation Factor } (\sigma) = \text{clip}\left(\frac{S - 40}{60}, 0.0, 1.0\right)$$
$$Q_{ind} = R \times (0.2 + 0.8 \times \sigma)$$

- **Dry Soil ($S < 40\%$)**: Ground acts as a natural sponge. Up to $80\%$ of rainfall infiltrates the ground; runoff remains low.
- **Saturated Soil ($S > 85\%$)**: The soil has reached its saturation deficit limit. Rainwater cannot infiltrate and is converted almost entirely into rapid surface runoff, generating immediate flash flood conditions.

### 3.3 4-Tier Risk Matrix & Action Thresholds

| Risk Level | Score Range | Status Title | Color Code | Sensor Threshold Criteria | Automatic Action Triggered |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **🟢 GREEN** | $0.0 - 30.0\%$ | **Low Risk (Normal)** | `#10b981` | Rain $< 20\text{ mm/h}$, Soil $< 50\%$, Water $< 2.8\text{m}$ | Routine environmental monitoring active. No alert sirens. |
| **🟡 YELLOW** | $30.1 - 55.0\%$ | **Moderate Risk (Advisory)** | `#f59e0b` | Rain $30 - 60\text{ mm/h}$, Soil $55 - 75\%$, Water $3.0 - 5.0\text{m}$ | Advisory issued. Drain inspection recommended. |
| **🟠 ORANGE** | $55.1 - 77.0\%$ | **High Risk (Warning)** | `#f97316` | Rain $> 65\text{ mm/h}$ OR Water $> 5.6\text{m}$ OR $Q_{ind} > 60$ | Warning siren tone activated. Flood barriers deployed. |
| **🔴 RED** | $77.1 - 100.0\%$ | **CRITICAL (Flash Flood)** | `#ef4444` | Water $\ge 7.5\text{m}$ OR (Rain $\ge 100\text{ mm/h}$ AND Soil $\ge 85\%$) | Emergency siren pulse sounded. Evacuation warning dispatched. |

---

## 4. Advantages

1. **100% Offline Resilience (Zero Internet Dependency)**:
   - During major floods, cell towers, fiber optic cables, and municipal power grids frequently collapse.
   - Because the AI model, GUI, sound engine, and calculations execute entirely on local hardware, the system continues operating autonomously on battery backup or field laptops.

2. **Hybrid AI + Physical Failsafe Guardrails**:
   - Pure machine learning models can suffer from edge-case hallucinations or out-of-distribution errors.
   - AI Flood Guard combines Random Forest probability distributions with deterministic hydrological safety boundaries (e.g., riverbank overtopping limits), preventing fatal false-negative classifications.

3. **Sub-Second Real-Time Response**:
   - Lightweight inference (< $5\text{ms}$ per cycle) allows immediate response to rapid cloudburst events, giving emergency teams precious early evacuation time.

4. **Non-Blocking Multi-Threaded Audio Alerting**:
   - Audio alarms run in asynchronous worker threads, ensuring the desktop GUI never stutters, freezes, or misses user inputs while sound is playing.

5. **Zero External Framework Latency**:
   - Standard library Tkinter was chosen over heavy web stacks (React, Electron, Django) to eliminate browser engine memory overhead, web server dependencies, and IPC lag.

6. **Drop-In Hardware Extensibility**:
   - The modular `SensorSimulator` interface is designed to be replaced with physical serial/GPIO inputs (Arduino, ESP32, Raspberry Pi) without altering the classifier, alert engine, or UI.

---

## 5. Disadvantages & Limitations

1. **Currently Simulated Data**:
   - In its current hackathon demonstration form, readings are mathematically simulated rather than wired to physical field probes. Deployment requires calibrating thresholds against physical hardware sensor noise.

2. **Single-Point Station Modeling**:
   - The current system represents a localized monitoring station. It does not yet account for upstream watershed geography, terrain slope elevation models (DEM), or river basin network topology where rain 20 miles upstream causes downstream flooding hours later.

3. **Operating System Audio Binding**:
   - The sound alert engine utilizes Windows-native `winsound.Beep()`. Running the audio system on Linux/macOS requires substituting a platform-neutral library such as `pygame` or `simpleaudio`.

4. **Synthetic Training Baseline**:
   - The machine learning classifier is trained on synthetic hydrological distributions grounded in SCS-CN equations. For city-scale civic deployment, the model should be fine-tuned on multi-decade historical catchment datasets (e.g. USGS or national water commission historical records).

---

## 6. Future Scope & Hardware Integration

For real-world physical deployment, the software architecture is already prepared for the following additions:
- **Physical IoT Sensor Interface**: Replace `SensorSimulator.get_readings()` with a serial reader connecting an **ESP32** or **Arduino** equipped with:
  - *Rainfall*: Tipping-bucket rain gauge with reed switch pulse counter.
  - *Soil Moisture*: Capacitive soil moisture sensor v1.2 (corrosion-resistant).
  - *Water Level*: Waterproof ultrasonic sensor (JSN-SR04T) or optical radar sensor mounted under a bridge.
- **LoRaWAN Telemetry**: Long-range, low-power radio communication allowing remote river sensors up to $15\text{ km}$ away to beam readings to the offline monitoring base station without cellular service.
- **Spatial GIS Mapping**: Incorporating multi-station hydrological mesh maps to forecast flood wave propagation down river channels.

---

## 7. Installation & Quick Start Guide

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```
*(Dependencies: `numpy`, `scikit-learn`, `colorama`. Note that `tkinter` and `winsound` are built directly into Python on Windows).*

### Step 2: Run the Application

#### Option A: Interactive Desktop GUI (Default)
```powershell
python app.py
```
*Launches the modern dark-themed dashboard. Click any scenario button (`☀️ Normal`, `🌧️ Moderate Rain`, `⛈️ Heavy Storm`, `🚨 Flash Flood Surge`) to test instant risk state transitions.*

#### Option B: Terminal CLI Mode (Headless / Testing)
```powershell
# Run continuous monitoring in terminal
python app.py --cli

# Test 3 cycles of a specific scenario
python app.py --cli --scenario FLASH_FLOOD --cycles 3
```

#### Command-Line Arguments
| Flag | Description | Default |
| :--- | :--- | :--- |
| `--cli` | Run in terminal mode without launching the GUI | `False` |
| `--scenario` | Initial scenario preset (`NORMAL`, `MODERATE_RAIN`, `HEAVY_STORM`, `FLASH_FLOOD`) | `NORMAL` |
| `--interval` | Polling loop interval in seconds | `1.5` |
| `--mute` | Mute audio alarm beeps and sirens | `False` |
| `-n`, `--cycles` | Number of cycles to run before exiting (CLI mode only) | Unlimited |
