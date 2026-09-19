# Changelog

## v2.9.0 — 2026-09-19
### Fixed
- **Settings Dialog Layout**: `Apply & Close` and `Calibrate Pedals` buttons were on the same grid row (overwriting each other). They are now on separate, distinct rows with a horizontal separator between the threshold fields and the action buttons.
- **Pedal Calibration — Live Serial Read**: `BrakeCalibrationWizard` was reading ADC values from a frozen in-memory snapshot instead of live car data. The wizard now automatically starts the nRF24 serial receiver on the configured COM port before opening, reads live `apps1_raw`/`apps2_raw`/`brake_raw` in real time, and cleanly stops the temporary session after calibration completes.
- **COM Port Refresh Without Dialog Restart**: Added an inline `⟳` refresh button next to the COM port combo in Settings.

### Added
- **Live Calibration Status Indicator**: Calibration wizard shows `🟢 Live data from car` when ADC data is streaming, or `⚠ Waiting for car data…` when idle.
- **Solid Filled Buttons**: All default buttons across the UI are now fully filled with a solid dark background and green text, improving readability on dark backgrounds.
- **Danger Button Variant**: New `'danger'` button style (dark red → bright red on hover) for destructive actions.

### Build / CI
- Migrated source checkout from `isc-fs/IFS08-TE` (`ISC_REAL_TIME_25`) → `isc-fs/IFS09-TE` (`isc_realtime_26`).
- Added `python-can` to installer pip dependencies.
- Upload installer artifact with `if: always()` for debugging on failed runs.
- Added build size reporting in verify and NSIS compile steps.
- Fixed artifact upload path to match new `isc_realtime_26` source directory.
- Added `DisplayIcon` registry entry to NSIS installer for correct icon in Add/Remove Programs.

## v2.8.1 — 2026-09-07
### Added
- **ECU FSM & AMS FSM Textual State Decoding**: Human-readable state names (`WAIT_VDC`, `PRECHARGE`, `WAIT_START`, `R2D_BUZZER`, `WAIT_STANDBY`, `ACTIVE`, `AMS_ERROR` / `STANDBY`, `PRECHARGE`, `ARMED`, `R2D`, `CHARGE`, `ERROR`) alongside numeric codes across indicator bars, Powertrain tab, and Dynamics tab.
- **GPS Heading**: Live course heading readout (`hdg: XXX°`) in Overview tab GPS status bar.
- **Telemetry Protocol Alignment with ECU v2.1.1**: Aligned nRF24 receiver config (`0x4543553031` / `'ECU01'`) and raw electrical RPM decoding.

## v2.8.0 — 2026-08-06 — The Barcelona Update
### Added
- **Cross-Session Fault Pattern Database (`FaultPatternDialog`)**: Scans all historical CSV logs to identify recurring fault trends, compute occurrences, percentage of sessions affected, and first/last seen timestamps.
- **Brake Hydraulic Pressure Sensor Calibration**: Full ADC calibration (`BRK_MIN`→`BRK_MAX`) integrated into wizard.
- **Session Energy Counter & Cell Imbalance Meter**: Real-time Wh accumulator and cell voltage spread metric with configurable threshold alert.
- **Enhanced Settings**: `alert_cell_imb_mv` threshold control with persistence.

## v2.7.3 — 2026-08-03
### Fixed
- Fixed Startup `AttributeError: 'MainWindow' object has no attribute '_log'` — reordered `__init__` initialization sequence.

## v2.7.2 — 2026-08-03
### Added
- Interactive Brake & APPS Sensor Calibration Wizard (`BrakeCalibrationWizard`) with live pedal readout bars.
- Fault History Logger (`FaultHistoryDialog`) with timestamps, severity, clear/export options.
- APPS Implausibility Detector (FMEA / EV 2.5 Rule Compliance): triggers critical alert if APPS disagreement >10% for ≥3 frames (~300 ms).
- Human-Readable Inverter State Mapping across Overview and Powertrain panels.

## v2.7.1 — 2026-07-29 — The Endurance Update
### Added
- Predictive Analytics Engine: Driver Efficiency Index, Thermal Derating & Overtemp Predictor, Battery Internal Resistance Estimator, Adaptive Driver Pace Advisor.
- SoC Monotonic Non-Increasing Latch & Safeguards.

## v2.7.0 — 2026-07-29
### Added
- Real-Time Vector GPS Track Map (`GPSTrackWidget`) — fully offline 2D vector canvas.
- Dual-Source Battery SoC & Energy Estimator.
- Dual-Source Remaining Battery Duration Estimator.

## v2.6.11 — 2026-07-29
### Added & Fixed
- Dual-Source SoC calibration (280V–400V), Dual Time-Remaining Estimator, Current Sign Fix.

## v2.6.10 — 2026-07-21
### Fixed
- `ModuleNotFoundError: No module named 'pydoc'` crash (required by `pyarrow.vendored.docscrape` via `pandas`).

## v2.6.9 — 2026-07-21
### Added
- Live GPS from radio snapshot — bytes 82–95 decode GPS position, speed, course, sats, fix flag.

## v2.6.8 — 2026-07-21
### Fixed
- Added Power Stage (IGBT) metric card and reorganized Inverter Status grid in Powertrain tab.

## v2.6.7 — 2026-07-21
### Fixed
- Updated Marple Data SDK integration (`db.push_file`) for direct stream uploads.

## v2.6.6 — 2026-07-21
### Fixed
- `ModuleNotFoundError: No module named 'unittest'` crash (required by Matplotlib/PyParsing).
- Fixed vehicle speed calculation from motor inverter RPM.
- Suppressed flashing PowerShell console window during TTS alerts.
- Separated Motor Temperature (KTY) and Power Stage Temperature (IGBT) metrics.

## v2.6.5 — 2026-07-21
### Added
- Real-time vehicle speed calculation (km/h) from motor inverter RPM.
- Detailed DEM Code fault description readout in Powertrain tab.

### Fixed
- Flashing PowerShell windows on TTS trigger.
- Inverted current signs for discharge polarity convention.
- Non-destructive post-race CSV export.
- Replaced `degC` with `°C`.

### Performance
- PyInstaller optimization level 2, excluded heavy unused Qt modules.

## v2.6.4 — 2026-07-20
### Performance
- SOLID LZMA compression with 64MB dictionary in NSIS setup.

## v2.6.3 — 2026-07-20
### Fixed
- Default Post-Race AMS CAN Node ID updated to Node 1.
- Support for zero-CRC responses from LogFS `OPEN`.

## v2.6.2 — 2026-07-20
### Fixed
- Applied empirical APPS calibration bounds to Overview Throttle/Brake overlay plot.

## v2.6.1 — 2026-07-20
### Fixed
- IR voltage drop compensation for Sony VTC6 SoC estimation.

### Added
- 30-second rolling average battery duration estimator.

## v2.6.0 — 2026-07-20
### Added
- Full NxTech Inverter State Machine decoding and DEM Diagnostic Code decoding (0–37).
- Dual Motor Temperature Sensor support with -50°C DBC offset.
- FOC BitState and DEM Code in telemetry stream, CSV log headers, UI.

## v2.5.0 — 2026-07-18
### Added
- Post-Race tab: CAN/ISO-TP log retrieval via LogFS protocol.

## v2.4.0 — 2026-07-17
### Added
- Pit-Wall Session Notes, Live ECU & Inverter Fault decoding, G-Force persistence trails, high-priority audible alarms.

## v2.3.0 — 2026-07-16
### Added
- Dynamic Light and Dark Mode switching.

## v2.2.0 — 2026-07-16
### Added
- In-app automatic update downloader.

## v2.1.0 — 2026-07-16
### Added
- TTS voice alerts toggle, high-contrast settings style sheet.

### Fixed
- Marple upload in background thread, session restart bugs, PermissionError on installed path, window icon path.

## v2.0.0 — 2026-07-16
### Added
- WiFi-style LQI indicator, Marple password protection, auto-update check.

### Fixed
- NSIS installer in-place replacement.
