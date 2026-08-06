<div align="center">

# 🏎️ ISCmetrics

**Real-time telemetry dashboard & data analytics suite for ISC Formula Student**

[![Release](https://img.shields.io/github/v/release/MrAndy5/ISCmetrics?color=008000&label=latest&style=flat-square)](https://github.com/MrAndy5/ISCmetrics/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://github.com/MrAndy5/ISCmetrics/releases/latest)
[![Python](https://img.shields.io/badge/python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)

### [⬇ Download Latest Installer](https://github.com/MrAndy5/ISCmetrics/releases/latest)

</div>

---

## What is ISCmetrics?

**ISCmetrics** is the **real-time telemetry, data analytics, and diagnostic suite** used by **ISC Formula Student** at the track. It connects wirelessly to the car's ECU via an nRF24L01+ radio link, decodes live fragmented snapshot data streams up to ~10 Hz, performs real-time predictive analytics, and displays telemetry in a high-contrast telemetry dashboard at the pit wall.

---

## Key Features

### 📡 Live Radio Telemetry & Signal Quality (LQI)
- Receives telemetry over a **2.4 GHz nRF24L01+ radio link** (RF-Nano USB receiver).
- Reassembles multi-fragment frames on the fly.
- **WiFi-style 4-bar signal strength indicator** tracks packet loss over a rolling 50-frame window with color-coded feedback (Green → Orange → Red).

### 🗺️ Real-Time Offline Vector GPS Track Map
- **Live 2D vector map canvas** in the Dynamics tab with local equirectangular projection (`(0,0)` anchored on first GPS fix).
- Displays vehicle trajectory trail, live position dot, heading direction arrow, north compass rose, total track distance, and satellite count.
- **100% Offline**: Requires zero external map tiles, internet connection, or third-party mapping services.
- Includes a manual `⟳ Reset Track` button and auto-clears trail at session start.

### 🔮 Predictive Analytics & Race Strategy Engine
- **Driver Efficiency Index**: Computes real-time energy consumption rate (`Wh/min`) and distance-specific efficiency (`Wh/km`).
- **Thermal Derating & Overtemp Predictor**: Monitors motor heating rate ($dT/dt$ in °C/min) and estimates time remaining until 90°C overtemp trip (`SAFE` when cool).
- **Battery Health & Internal Resistance Estimator ($R_{int}$ in mΩ)**: Dynamic rolling internal resistance estimation calculated during step-throttle current transitions ($\Delta I > 10	ext{A}, \Delta V < -1	ext{V}$).
- **Adaptive Driver Pace & Strategy Advisor**: Calculates recommended maximum torque limit (%) to pace the driver for completing the full 22-minute Endurance event within remaining battery Wh capacity.

### 🔍 Cross-Session Fault Pattern Database & Diagnostic Logger
- **Fault History Logger (`FaultHistoryDialog`)**: Tracks DEM diagnostic codes, inverter state changes, system alerts, and APPS implausibility events with precise timestamps and severity categories.
- **Cross-Session Analytics (`FaultPatternDialog`)**: Scans all historical telemetry CSV logs in `Documents/ISCmetrics/logs` to identify recurring fault trends, session occurrence percentages, first/last seen timestamps, and exportable CSV reports.
- **APPS Implausibility Detector (FMEA / EV 2.5 Compliance)**: Triggers a critical alert banner and logs a fault event if APPS 1 & APPS 2 agreement deviates by >10% for $\ge 3$ consecutive frames ($pprox 300	ext{ ms}$).

### 🔧 Interactive Sensor Calibration Wizard
- **Multi-step GUI Wizard (`BrakeCalibrationWizard`)**: Calibrates raw ADC bounds for APPS 1, APPS 2, and hydraulic Brake pressure sensors (`APPS1_MIN/MAX`, `APPS2_MIN/MAX`, `BRK_MIN/MAX`).
- Includes baseline zero & full depression capture steps, live pedal readout bars, and automatic persistence to `settings.json`.

### 📥 Post-Race LogFS CAN Extractor
- Retrieve raw high-frequency CAN/ISO-TP logs directly from the car's micro-SD log system over CAN (LogFS protocol over ISO-TP).
- Live progress bar, transfer rate monitoring, and direct file extraction.

### ⚡ Overview, Powertrain, Dynamics & Custom Dashboards
- **Overview Tab**: Live RPM, DC Bus Voltage, Pack Current, SoC, Torque %, Inverter State with short state string (`RUN`, `STDBY`, `SOFT`, `HARD`), Throttle/Brake overlay plot, and Status Indicators.
- **Powertrain Tab**: RPM arc gauge, NxTech inverter state machine decoding, DEM diagnostic codes (0–37), motor/IGBT/board/DC-DC temperature readouts, per-module min cell voltage and max temperature bars.
- **Dynamics Tab**: Real-time G-force circle plot with persistence trails, pedal meters, control FSM state, and the vector GPS track map.
- **Customize Tab**: Drag-and-drop **6 configurable plot panels** — assign any of the 45+ telemetry channels to custom live plots.

### 🌓 High-Contrast Light & Dark Theme Engine
- Seamless one-click dark/light mode toggle with automatic restyling of plotting canvases, widgets, panels, buttons, and custom controls.

### 📁 Session Logging & Marple Cloud Sync
- Automatically logs all live sessions to `Documents/ISCmetrics/logs/` as timestamped CSV files.
- Optional background upload to **Marple Data** cloud platform for post-race telemetry analysis.

### 🔊 Speech Alerts & Auto-Update Engine
- Voice alerts via Windows Speech for critical events (overtemp, low voltage, signal loss).
- Auto-update engine checks GitHub releases on startup and provides one-click in-app update downloading and silent installer execution.

---

## Installation & Setup

### Requirements
- Windows 10 / 11 (64-bit)
- RF-Nano USB receiver plugged in (for live data)

### Install
1. Download **`ISCmetrics_Setup_vX.Y.Z.exe`** from the [Releases](https://github.com/MrAndy5/ISCmetrics/releases/latest) page
2. Run the installer — accepts all defaults, no configuration needed
3. Launch **ISCmetrics** from the Desktop or Start Menu shortcut

### Update
When a new version is released, ISCmetrics will notify you automatically at startup. Click **Download Update** in the banner, run the new installer — it replaces the old version in-place with no manual uninstall required.

---

## Quick Start

1. Plug in the **RF-Nano USB receiver** and note the COM port (Device Manager → Ports)
2. Launch **ISCmetrics**
3. Click **⚙ Settings** → select the correct COM port → click **Apply & Close**
4. Click **▶ Start** — the status badge turns **LIVE** 🟢 when packets are received
5. Click **■ Stop** to end the session — the CSV log is saved automatically to the `logs/` folder

---

## Alert Thresholds

Configurable in **Settings**:

| Alert | Default |
|-------|---------|
| Max module temperature | > 40 °C |
| DC Bus voltage | < 380 V |
| Min cell voltage | < 3400 mV |

---

## Signal Strength Reference

| Bars | LQI | Meaning |
|------|-----|---------|
| ████ | ≥ 85 % | Excellent — full range |
| ███░ | ≥ 70 % | Good |
| ██░░ | ≥ 50 % | Fair — approaching range limit |
| █░░░ | ≥ 25 % | Poor — consider repositioning antenna |
| ░░░░ | < 25 % | Critical packet loss |

---

<div align="center">

**ISC Formula Student · Universidad Pontificia Comillas ICAI**

*Built for the track. Engineered for clarity.*

</div>
