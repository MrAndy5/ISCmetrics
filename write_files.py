"""Helper script — writes all ISCmetrics-releases repository files."""
import os, pathlib

ROOT = pathlib.Path(__file__).parent

def w(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"  wrote {p}")

# ── GitHub Actions workflow ──────────────────────────────────────────────────
w(".github/workflows/build-release.yml", """\
name: Build & Release ISCmetrics

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Override version (e.g. v2.0.0-test)'
        required: false

permissions:
  contents: write   # required to create GitHub Releases and upload assets

jobs:
  build-windows:
    name: Build Windows Installer
    runs-on: windows-latest

    steps:
      # ── 1. Checkout this releases repo (contains installer script) ────────
      - name: Checkout releases repo
        uses: actions/checkout@v4

      # ── 2. Checkout ISCmetrics source ─────────────────────────────────────
      - name: Checkout ISCmetrics source
        uses: actions/checkout@v4
        with:
          repository: isc-fs/IFS08-TE
          ref: feat/receptor_08
          sparse-checkout: ISC_REAL_TIME_25
          sparse-checkout-cone-mode: false
          path: src

      # ── 3. Python setup ───────────────────────────────────────────────────
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        working-directory: src/ISC_REAL_TIME_25
        run: |
          pip install --upgrade pip
          pip install pyinstaller pyqt5 matplotlib numpy pyserial requests openpyxl influxdb-client pandas marpledata

      # ── 4. Resolve version ────────────────────────────────────────────────
      - name: Get version
        id: ver
        shell: pwsh
        run: |
          $t = "${{ github.ref_name }}"
          if ([string]::IsNullOrEmpty($t) -or $t -eq "refs/heads/main") {
            $t = "${{ github.event.inputs.version }}"
          }
          if ([string]::IsNullOrEmpty($t)) { $t = "v0.0.0-dev" }
          Add-Content $env:GITHUB_OUTPUT "VERSION=$t"
          Write-Host "Version resolved: $t"

      # ── 5. Patch APP_VERSION in ui.py ─────────────────────────────────────
      - name: Patch APP_VERSION
        working-directory: src/ISC_REAL_TIME_25
        shell: pwsh
        run: |
          $v = "${{ steps.ver.outputs.VERSION }}" -replace '^v', ''
          $content = Get-Content ui.py -Raw
          $content = $content -replace 'APP_VERSION\\s*=\\s*"[^"]+"', "APP_VERSION = `"$v`""
          Set-Content ui.py $content -NoNewline
          Write-Host "APP_VERSION patched to: $v"

      # ── 6. Build with PyInstaller ─────────────────────────────────────────
      - name: PyInstaller build
        working-directory: src/ISC_REAL_TIME_25
        run: pyinstaller ISC_RTT.spec --clean --noconfirm

      # ── 7. Verify build output ────────────────────────────────────────────
      - name: Verify build
        working-directory: src/ISC_REAL_TIME_25
        shell: pwsh
        run: |
          if (!(Test-Path "dist\\ISC_RTT\\ISC_RTT.exe")) {
            Write-Error "PyInstaller output not found!"
            exit 1
          }
          Write-Host "Build OK — $(Get-ChildItem dist\\ISC_RTT | Measure-Object).Count files in dist\\ISC_RTT"

      # ── 8. Install NSIS ───────────────────────────────────────────────────
      - name: Install NSIS
        run: choco install nsis -y --no-progress

      # ── 9. Stage NSIS script alongside build output ───────────────────────
      - name: Stage NSIS script
        shell: pwsh
        run: |
          Copy-Item "installer\\iscmetrics_setup.nsi" "src\\ISC_REAL_TIME_25\\iscmetrics_setup.nsi"

      # ── 10. Compile installer EXE ─────────────────────────────────────────
      - name: Compile NSIS installer
        id: nsis
        working-directory: src/ISC_REAL_TIME_25
        shell: pwsh
        run: |
          $v   = "${{ steps.ver.outputs.VERSION }}"
          $out = "ISCmetrics_Setup_$v.exe"
          $nsis = "C:\\Program Files (x86)\\NSIS\\makensis.exe"
          & $nsis /DAPP_VERSION="$v" /DOUTFILE="$out" iscmetrics_setup.nsi
          if ($LASTEXITCODE -ne 0) { Write-Error "NSIS failed"; exit 1 }
          Write-Host "Installer created: $out ($('{0:N1}' -f ((Get-Item $out).Length / 1MB)) MB)"
          Add-Content $env:GITHUB_OUTPUT "INSTALLER=$out"

      # ── 11. Upload artifact (for debugging) ───────────────────────────────
      - name: Upload installer artifact
        uses: actions/upload-artifact@v4
        with:
          name: installer
          path: src/ISC_REAL_TIME_25/${{ steps.nsis.outputs.INSTALLER }}

      # ── 12. Publish GitHub Release ────────────────────────────────────────
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.ver.outputs.VERSION }}
          name: ISCmetrics ${{ steps.ver.outputs.VERSION }}
          body_path: CHANGELOG.md
          files: src/ISC_REAL_TIME_25/${{ steps.nsis.outputs.INSTALLER }}
          fail_on_unmatched_files: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
""")

# ── NSIS installer script ────────────────────────────────────────────────────
w("installer/iscmetrics_setup.nsi", r"""
; ISCmetrics NSIS installer
; Built by GitHub Actions — do not edit manually.
; Usage: makensis /DAPP_VERSION="2.0.0" /DOUTFILE="ISCmetrics_Setup_v2.0.0.exe" iscmetrics_setup.nsi

SetCompressor /SOLID lzma
SetCompressorDictSize 64

!include "MUI2.nsh"

; Command-line overridable defines
!ifndef APP_VERSION
  !define APP_VERSION "0.0.0"
!endif
!ifndef OUTFILE
  !define OUTFILE "ISCmetrics_Setup_v${APP_VERSION}.exe"
!endif

Name          "ISCmetrics ${APP_VERSION}"
OutFile       "${OUTFILE}"
InstallDir    "$PROGRAMFILES64\ISCmetrics"
InstallDirRegKey HKLM "Software\ISCmetrics" "Install_Dir"
RequestExecutionLevel admin

; ── MUI pages ────────────────────────────────────────────────────────────────
!define MUI_ABORTWARNING
!define MUI_ICON   "isc_logo.ico"
!define MUI_UNICON "isc_logo.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Install section ───────────────────────────────────────────────────────────
Section "ISCmetrics (required)" SecMain
  SectionIn RO
  SetOutPath "$INSTDIR"

  ; Copy the entire PyInstaller dist folder
  File /r "dist\ISC_RTT\*.*"

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Registry entry
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "DisplayName" "ISCmetrics"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "Publisher" "ISC Formula Student"
  WriteRegStr HKLM "Software\ISCmetrics" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\ISCmetrics" "Version" "${APP_VERSION}"

  ; Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\ISCmetrics"
  CreateShortcut "$SMPROGRAMS\ISCmetrics\ISCmetrics.lnk" \
    "$INSTDIR\ISC_RTT.exe" "" "$INSTDIR\ISC_RTT.exe" 0
  CreateShortcut "$SMPROGRAMS\ISCmetrics\Uninstall ISCmetrics.lnk" \
    "$INSTDIR\uninstall.exe"

  ; Desktop shortcut (optional — user can delete)
  CreateShortcut "$DESKTOP\ISCmetrics.lnk" \
    "$INSTDIR\ISC_RTT.exe" "" "$INSTDIR\ISC_RTT.exe" 0
SectionEnd

; ── Uninstall section ─────────────────────────────────────────────────────────
Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\ISCmetrics\ISCmetrics.lnk"
  Delete "$SMPROGRAMS\ISCmetrics\Uninstall ISCmetrics.lnk"
  RMDir  "$SMPROGRAMS\ISCmetrics"
  Delete "$DESKTOP\ISCmetrics.lnk"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics"
  DeleteRegKey HKLM "Software\ISCmetrics"
SectionEnd
""")

# ── README ───────────────────────────────────────────────────────────────────
w("README.md", """\
<div align="center">

# ISCmetrics

**Real-time telemetry dashboard for ISC Formula Student**

[![Release](https://img.shields.io/github/v/release/MrAndy5/ISCmetrics?color=008000&label=latest&style=flat-square)](https://github.com/MrAndy5/ISCmetrics/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Windows-blue?style=flat-square)](https://github.com/MrAndy5/ISCmetrics/releases/latest)

### [⬇ Download Latest Installer](https://github.com/MrAndy5/ISCmetrics/releases/latest)

</div>

---

## What is ISCmetrics?

ISCmetrics is the **real-time telemetry and data visualization system** used by ISC Formula Student at the track. It connects wirelessly to the car's ECU via an nRF24L01+ radio link, decodes the live data stream and presents it in a Grafana-inspired dark dashboard — all running on a Windows laptop at the pit wall.

---

## Features

### 📡 Live Radio Telemetry
Receives data from the car over a **2.4 GHz nRF24L01+ radio link** (RF-Nano USB receiver). A fragmented snapshot protocol reassembles multi-packet frames on the fly at up to ~10 Hz update rate.

### 📶 Signal Quality Indicator
A **WiFi-style 4-bar signal strength indicator** shows the link quality in real time. It tracks packet loss over a rolling window of the last 50 frames — bars turn from green → orange → red as reception degrades, giving the engineer instant situational awareness at range.

### ⚡ Overview Dashboard
At-a-glance view of the most critical car parameters:
- **RPM**, **DC Bus Voltage**, **Pack Current**, **State of Charge**
- **Torque %**, **Inverter State**, **Error flags**
- **Live throttle / brake overlay plot**
- **Precharge**, **INV OK** and **AMS state** indicators

### 🔋 Powertrain Tab
Detailed powertrain health panel:
- **RPM arc gauge** with actual speed readout
- **Per-inverter temperatures** (Motor, Power Stage, Board, DC-DC)
- **Battery summary**: DC Bus, SoC (VTC6 OCV curve), Pack Current, Min Cell Voltage
- **Per-module cell voltage and temperature bars** (5 modules, color-coded with configurable alert thresholds)

### 🏎️ Dynamics Tab
Driver inputs and vehicle dynamics:
- **Throttle & Brake pedal meters** (APPS 1, APPS 2, Brake raw ADC)
- **Control signals**: Torque %, Start Button, EV2/3, T11, Controller State
- **G-force circle plot** (lateral vs. longitudinal)

### 📊 Customise Tab
Drag-and-drop **6 configurable plot panels** — pick any ECU channel from the full signal list and assign it to a panel for live plotting during the session.

### 📁 Session Logging
Every live session is automatically saved as a **timestamped CSV file** with all ECU channels at full resolution. Sessions can be reviewed in the built-in **Post-Race Viewer** or opened in Excel / Marple for post-processing analysis.

### ☁️ Marple Cloud Upload *(password protected)*
Optionally stream session data live to **Marple Data** for cloud analysis. This feature requires team authentication — contact the telemetry engineer for access.

### 🔊 Voice Alerts
Critical events are announced over TTS (Windows Speech):
- High battery temperature
- Low DC bus or cell voltage
- Radio signal lost
- USB receiver disconnected

### 🔄 Auto-Update
ISCmetrics checks for new releases every time it starts. If an update is available, a **green banner** appears with a one-click download link — no need to manually check this page.

### 🎬 Demo Mode
Run the full dashboard offline with **simulated telemetry data** — useful for UI testing, presentations, or training new team members without needing the car.

---

## Installation

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
""")

# ── CHANGELOG ────────────────────────────────────────────────────────────────
w("CHANGELOG.md", """\
# Changelog

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
""")

print("All release repo files written successfully.")
