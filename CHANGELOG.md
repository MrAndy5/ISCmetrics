# Changelog

## v2.8.0 — 2026-08-06 — The Barcelona Update
### Added
- **Cross-Session Fault Pattern Database (`FaultPatternDialog`)**:
  - Scans all historical telemetry CSV logs in `Documents/ISCmetrics/logs` to identify recurring fault trends across all previous runs
  - Computes fault code occurrences, percentage of sessions affected, first/last seen timestamps, and severity categorization
  - Highlights top recurring ECU/Inverter DEM codes, cell imbalance events, and APPS implausibility occurrences with export capabilities
- **Brake Hydraulic Pressure Sensor Calibration**:
  - Full hydraulic brake pressure ADC calibration (`BRK_MIN` to `BRK_MAX`) integrated into `BrakeCalibrationWizard`
  - Normalizes brake percentage readouts across plots, pedal widgets, and persists parameters in `settings.json`
- **Session Energy Counter & Cell Imbalance Meter**:
  - Real-time `Session Energy (Wh)` accumulator counter tracking cumulative energy consumed ($P 	imes \Delta t$)
  - `Cell Imbalance (mV)` metric card tracking maximum cell voltage spread ($V_{max} - V_{min}$) with configurable threshold alerts (default 100 mV)
- **Enhanced Settings Controls**:
  - Added `alert_cell_imb_mv` threshold control to `SettingsDialog` with persistence in `settings.json`

## v2.7.3 — 2026-08-03
### Fixed
- **Fixed Startup `AttributeError: 'MainWindow' object has no attribute '_log'`**:
  - Reordered `MainWindow.__init__` initialization sequence to guarantee `self._log` attribute is defined before `self._load_settings_from_file()` executes
  - Made `self._log_append()` defensive against uninitialized UI log widgets, falling back safely to standard logging `logger.info()`
  - Prevented redundant file writes to `settings.json` during initial application startup settings load

## v2.7.2 — 2026-08-03
### Added
- **Interactive Brake & APPS Sensor Calibration Wizard (`BrakeCalibrationWizard`)**:
  - Multi-step interactive GUI wizard for calibrating raw ADC bounds (`APPS1_MIN/MAX`, `APPS2_MIN/MAX`, `BRK_MIN/MAX`) with live pedal readout bars and baseline capture steps
  - Automatically updates live scaling parameters and persists custom pedal calibration into `settings.json`
- **Fault History Logger & Diagnostic Viewer (`FaultHistoryDialog`)**:
  - Live and historical ECU fault log table tracking DEM diagnostic codes, inverter state changes, and system errors with timestamps, category tags, error descriptions, and clear/export options
- **APPS Implausibility Detector (FMEA / EV 2.5 Rule Compliance)**:
  - Continuously monitors percentage position agreement between APPS 1 & APPS 2 pedal sensors while high-voltage bus is energized
  - Triggers a critical UI alert banner and logs a fault event if position disagreement exceeds 10% for $\ge 3$ consecutive frames ($pprox 300	ext{ ms}$)
- **Human-Readable Inverter State Mapping**:
  - Displays human-readable state names alongside numeric codes in Overview and Powertrain panels (`6 RUN`, `1 STDBY`, `5 SOFT`, `7 HARD`, etc.)
- **Persistent Predictive Analytics Logging**:
  - Writes calculated predictive analytics (`eff_wh_min`, `eff_wh_km`, `thermal_dt_dt`, `thermal_t_overtemp`, `batt_r_int`, `strategy_rec_torque`) directly into the shared snapshot dictionary, enabling real-time logging into CSV session files

## v2.7.1 — 2026-07-29 — The Endurance Update
### Added
- **Predictive Analytics Engine & Endurance Strategy Advisor (`PredictiveAnalyticsEngine`)**:
  - **Driver Efficiency Index**: Real-time energy consumption rate (`Wh/min`) and distance-based efficiency (`Wh/km`)
  - **Thermal Derating & Overtemp Predictor**: Motor heating rate ($dT/dt$ in °C/min) and projected time remaining until 90°C overtemp trip (`SAFE` when cool)
  - **Battery Health & Internal Resistance Estimator ($R_{int}$ in mΩ)**: Dynamic rolling internal resistance estimation calculated during step-throttle current transitions ($\Delta I > 10	ext{A}, \Delta V < -1	ext{V}$)
  - **Adaptive Driver Pace & Strategy Advisor**: Calculates recommended maximum torque limit (%) to pace the driver for completing the full 22-minute Endurance event within remaining battery Wh capacity
  - **Powertrain UI Cards & Customize Channels**: Added dedicated status cards to Powertrain tab (`Consumption Rate`, `Heating Rate`, `Est. Overtemp`, `Pack Internal R`, `Rec. Torque %`) and exposed channels for custom plotting
- **SoC Monotonic Non-Increasing Latch & Safeguards**:
  - Monotonic non-increasing SoC latch (`_session_min_soc`) during active runs: prevents SoC from falsely ticking upward during voltage relaxation/rebound after throttle lifts
  - Active current sign rectification safeguard: automatically rectifies negative current readings when motor is spinning/drawing torque
  - Automatic state reset on new session start

## v2.7.0 — 2026-07-29
### Added
- **Real-Time Vector GPS Track Map (`GPSTrackWidget`)**:
  - Live offline 2D vector map canvas in Dynamics tab using local equirectangular projection anchored to first GPS fix
  - Displays vehicle trajectory trail, live position dot, heading direction arrow, north compass rose, track distance, and satellite count
  - Manual `⟳ Reset Track` button and automatic trail reset on new session start
- **Dual-Source Battery SoC & Energy Estimator**:
  - Primary estimation from DC Bus Voltage (`inv_dc_bus_V`) between 400 V (100% SoC) and 280 V (0% accumulator cutoff)
  - Secondary blending with IR-compensated per-cell OCV (`0.35 mV/A` per 6p group) when cell-level telemetry is valid
  - Eliminates false 0% SoC readings when cell-level telemetry is un-decoded or missing
  - Monotonic non-increasing SoC latch during active runs: prevents SoC from falsely ticking upward during voltage relaxation/rebound after throttle lifts
- **Dual-Source Remaining Battery Duration Estimator**:
  - Source A: 60-second rolling average power calculation (`corriente_accu × Vbus`)
  - Source B: Linear voltage-drop rate extrapolation (`dv/dt` over session elapsed time) down to 280 V cutoff
  - Displays the more conservative (lower) time estimate to prevent unexpected battery depletion
  - Minimum 20A racing current floor while inverter is running (state 6) to avoid unrealistically high estimates during coasting
  - Active current sign rectification safeguard: automatically rectifies negative current readings when motor is spinning/drawing torque to prevent calculation corruption from sensor noise or inverted CAN signals

### Fixed
- Corrected accumulator discharge current (`corriente_accu`) polarity across telemetry decoders and UI metrics

## v2.6.11 — 2026-07-29
### Added & Fixed
- **Dual-Source Battery SoC Calibration (280V–400V range)**:
  - Calibrated 100% SoC to 400V (4.211V/cell) and 0% cutoff to 280V (2.947V/cell) for 95s6p Sony VTC6 accumulator.
  - Primary SoC estimation uses `inv_dc_bus_V` (always active even if cell sensors are unpopulated), blended with fine-grained per-cell OCV table when cell voltages are present.
- **Dual Time-Remaining Estimator**:
  - Wh-based calculation (`6120 Wh` pack capacity × current SoC fraction ÷ average power).
  - 60-second rolling power average (`corriente_accu × Vbus`).
  - Added a 20A racing power floor while inverter is in State 6 (Running) to prevent artificially inflated estimates during coasting.
  - Linear voltage-drop rate extrapolation (`dV/dt`) fallback when current readings are unpopulated or uncalibrated.
- **Current Sign Fix**:
  - Inverted `corriente_accu` decoding sign to represent discharge (driving) as positive current and regen as negative current.

## v2.6.10 — 2026-07-21
### Fixed
- Fixed `ModuleNotFoundError: No module named 'pydoc'` executable crash by retaining `pydoc` in PyInstaller build spec (`ISC_RTT.spec`) — required by `pyarrow.vendored.docscrape` which is imported transitively through `pandas → pyarrow`

## v2.6.9 — 2026-07-21
### Added
- **Live GPS from radio snapshot** (ECU feat/gps-position-speed / issue #147):
  - Decodes GPS position, speed, course, satellite count and fix flag directly from the nRF24 radio snapshot bytes 82–95
  - `gps_lat_deg`, `gps_lon_deg`, `gps_speed_kmh`, `gps_course_deg`, `gps_sats`, `gps_has_fix` fields added to decoder, CSV log headers, and SNAPSHOT_CHANNELS data table
  - All GPS fields are gated on `gps_has_fix` in the CSV log and UI (last valid position is not shown as live after fix drops)
  - Overview tab indicator bar shows live `GPS ✓  lat° lon°  speed km/h  [N sats]` when fix is active (green) or `GPS: NO FIX` when searching (grey)
  - Debug log prints GPS lat/lon/speed/course/sats every 2s when fix is active
  - Backward compatible: unchanged radio wire format (102 bytes), un-updated ECUs silently skip GPS bytes (all zero = no fix)

## v2.6.8 — 2026-07-21
### Fixed
- Added Power Stage (IGBT) metric card and reorganized Inverter Status & Diagnostics grid layout in Powertrain tab

## v2.6.7 — 2026-07-21
### Fixed
- Updated Marple Data SDK integration (`db.push_file`) for direct stream uploads during telemetry session sync

## v2.6.6 — 2026-07-21
### Fixed
- Fixed `ModuleNotFoundError: No module named 'unittest'` executable crash by retaining `unittest` in PyInstaller build spec (`ISC_RTT.spec`) required by Matplotlib/PyParsing
- Fixed vehicle speed calculation math from motor inverter RPM
- Suppressed flashing PowerShell console window during TTS alert speech generation on Windows
- Separated Motor Temperature (KTY) and Power Stage Temperature (IGBT) in Powertrain status metrics

## v2.6.5 — 2026-07-21
### Added
- Real-time vehicle speed calculation (km/h) derived directly from motor inverter RPM
- Detailed DEM Code fault description readout in Powertrain status tab (e.g., `8 - EMachine Overtemperature`)

### Fixed
- Fixed black PowerShell pop-up windows flashing on Windows when voice alerts (TTS) trigger without SAPI win32com dependencies
- Inverted current signs (`corriente_accu`, `corriente_dcdc`, `inv_current_actual`) to align with discharge polarity conventions
- Non-destructive post-race CSV export (`*_merged.csv`) when integrating GPS or AMS micro-SD logs
- Replaced text `degC` with proper degree symbol `ºC` across dashboard metrics, plot titles, and TTS alerts

### Performance & Optimization
- Optimized PyInstaller build spec (`ISC_RTT.spec`) with bytecode optimization level 2 and excluded heavy unused modules (`QtWebEngine`, `QtQml`, `QtMultimedia`, `scipy`)

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
