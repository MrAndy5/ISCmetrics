# Changelog

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
