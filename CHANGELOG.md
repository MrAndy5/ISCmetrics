# Changelog

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
