# Changelog

## v2.6.4 — 2026-07-20
### Performance & Optimization
- Enabled SOLID LZMA compression with 64MB dictionary size in NSIS setup script for smaller installer size and faster update downloads

## v2.6.3 — 2026-07-20
### Fixed
- Updated default Post-Race AMS CAN Node ID to Node 1 (`0x001` / `0x011`) per firmware spec #406 / #403
- Added support for zero-CRC (`expected_crc == 0`) responses from firmware LogFS `OPEN` to avoid SD card read stalls

## v2.6.2 — 2026-07-20
### Fixed
- Applied empirical APPS calibration bounds (`APPS1_MIN/MAX` & `APPS2_MIN/MAX`) to Overview Throttle/Brake overlay plot, eliminating false 60% throttle readouts at pedal rest

## v2.6.1 — 2026-07-20
### Fixed
- Internal resistance (IR) voltage drop compensation for Sony VTC6 SoC estimation (`0.35 mV/A` per 6p group) to eliminate false SoC sags during high current acceleration spikes

### Added
- Real-time 30-second rolling average battery duration estimator (calculates remaining run time to 5% SoC cutoff in `minutes & seconds`)
- New `EST REMAINING` dashboard card on Overview tab and `Est. Cut-off` card on Powertrain tab

## v2.6.0 — 2026-07-20
### Added
- Full NxTech Inverter State Machine decoding (INIT, STANDBY, READY, TORQUE/SPEED/CURRENT Active, FAULT_SOFT, FAULT_HARD, DISCHARGE, SHUTDOWN)
- Comprehensive NxTech DEM Diagnostic Code decoding (0–37) with safe-state reaction indicators (Freewheeling, Degrade, None)
- Dual Motor Temperature Sensor support (`EMachine_Temp_1` and `EMachine_Temp_2`) with `-50°C` DBC physical offset scaling
- Automatic detection and visual tagging for disconnected temperature sensors (`N/C (Disconnected)`)
- FOC BitState and DEM Code metrics in telemetry stream, CSV log headers, Overview tab, and Powertrain tab

## v2.5.1 — 2026-07-20
### Fixed
- Scaled motor inverter RPM by 10 for accurate speed readout
- Scaled accumulator current (`corriente_accu`) and DC-DC current (`corriente_dcdc`) to Amperes (A) across telemetry decoder and UI
- Fixed post-race GPS/AMS merge alignment signal scaling

### Added
- Empirical APPS 1 & APPS 2 ADC calibration bounds for accurate 0-100% throttle normalization
- High-contrast Matplotlib plot grid, tick, and spine styling across Light & Dark themes
- Direct saving of extracted raw AMS log files to `AMS_data/` directory with "Date / Modified" column and custom styled popups

## v2.5.0 — 2026-07-18
### Added
- New **Post-Race** tab supporting CAN/ISO-TP log retrieval directly from the car's log system (LogFS protocol over CAN), with live download progress and transfer statistics
- Optional `python-can` dependency integration (`import can`) for native CAN interface communication

### Fixed
- Reset active alerts and telemetry LQI indicators to idle defaults when the application is not receiving data

## v2.4.0 — 2026-07-17
### Added
- Pit-Wall Session Notes with real-time logging synced to session CSV files
- Live ECU & Inverter Fault decoding aligned with ePowerLabs error specifications
- G-Force persistence trails showing vehicle dynamics history on the G-Force circle plot
- High-priority audible alarms for critical status and telemetry alerts

## v2.3.0 — 2026-07-16
### Added
- Dynamic Light and Dark Mode switching support with a button in the top bar
- Automatic restyling of plotting canvases, widgets, panels, buttons, and custom controls upon theme toggling

## v2.2.0 — 2026-07-16
### Added
- In-app automatic update downloader (downloads setup EXE, displays progress dialog, runs the installer, and closes the app automatically to apply the update)
- Thread-safe GUI signal communication for background update detection and download operations
- Exposed the application version in the main window title and header bar

## v2.1.0 — 2026-07-16
### Added
- Toggle option in Settings to enable/disable Text-to-Speech (TTS) voice alerts
- Slower TTS rate for improved intelligibility at the track and auto-selection of high-quality voices (Zira/Helena/Hazel/Sabina)
- High-contrast premium style sheet with custom SVG checkbox indicators in Settings dialog

### Fixed
- Run Marple Data cloud upload in a background thread to prevent UI freezing/blocking
- Correctly reset snapshot state and LQI history on session start (fixes session restart bugs)
- PermissionError when creating logs folder or saving settings when installed (saved under Documents/ISCmetrics)
- Resolved window icon resolution path mismatch when run from installer shortcuts

## v2.0.0 — 2026-07-16
### Added
- WiFi-style signal-strength (LQI) indicator in status bar
- LQI now tracks KIND_SNAPSHOT packets (fragmented protocol)
- Password protection for Marple cloud upload (`ISC_telemetry_2026`)
- Auto-update check on startup — banner with download link

### Fixed
- NSIS installer replaces existing installation in-place (no manual uninstall)
