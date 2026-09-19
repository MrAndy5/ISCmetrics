"""
Generates all files for the ISCmetrics releases repository
(MrAndy5/ISCmetrics), migrating from IFS08-TE to IFS09-TE.
Run from anywhere — paths are hardcoded.
"""
import pathlib

REPO = pathlib.Path(r"C:\Users\andre\Desktop\Universidad\ICAI\repos\ISCmetrics")

def w(rel, text):
    p = REPO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    print(f"  wrote {p}")

# ─────────────────────────────────────────────────────────────────────────────
# 1. GitHub Actions workflow
# ─────────────────────────────────────────────────────────────────────────────
WORKFLOW = """\
name: Build & Release ISCmetrics

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Override version (e.g. v2.9.0-test)'
        required: false

permissions:
  contents: write   # required to create GitHub Releases and upload assets

jobs:
  build-windows:
    name: Build Windows Installer
    runs-on: windows-latest

    steps:
      # ── 1. Checkout this releases repo (contains NSIS script) ────────────
      - name: Checkout releases repo
        uses: actions/checkout@v4

      # ── 2. Checkout ISCmetrics source (IFS09-TE, isc_realtime_26) ────────
      - name: Checkout ISCmetrics source
        uses: actions/checkout@v4
        with:
          repository: isc-fs/IFS09-TE
          ref: main
          sparse-checkout: isc_realtime_26
          sparse-checkout-cone-mode: false
          path: src

      # ── 3. Python setup ───────────────────────────────────────────────────
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Python dependencies
        working-directory: src/isc_realtime_26
        run: |
          pip install --upgrade pip
          pip install pyinstaller pyqt5 matplotlib numpy pyserial requests openpyxl influxdb-client pandas marpledata python-can

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
        working-directory: src/isc_realtime_26
        shell: pwsh
        run: |
          $v = "${{ steps.ver.outputs.VERSION }}" -replace '^v', ''
          $content = Get-Content ui.py -Raw
          $content = $content -replace 'APP_VERSION\\s*=\\s*"[^"]+"', "APP_VERSION = `"$v`""
          Set-Content ui.py $content -NoNewline
          Write-Host "APP_VERSION patched to: $v"
          Select-String -Path ui.py -Pattern APP_VERSION | Select-Object -First 3

      # ── 6. Build with PyInstaller ─────────────────────────────────────────
      - name: PyInstaller build
        working-directory: src/isc_realtime_26
        run: pyinstaller ISC_RTT.spec --clean --noconfirm

      # ── 7. Verify build output ────────────────────────────────────────────
      - name: Verify build
        working-directory: src/isc_realtime_26
        shell: pwsh
        run: |
          if (!(Test-Path "dist\\ISC_RTT\\ISC_RTT.exe")) {
            Get-ChildItem -Recurse dist -ErrorAction SilentlyContinue | Select-Object FullName
            Write-Error "PyInstaller output not found at dist\\ISC_RTT\\ISC_RTT.exe"
            exit 1
          }
          $count = (Get-ChildItem "dist\\ISC_RTT" -Recurse | Measure-Object).Count
          $sizeMB = [math]::Round((Get-ChildItem "dist\\ISC_RTT" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
          Write-Host "Build OK - $count files, $sizeMB MB in dist\\ISC_RTT"

      # ── 8. Install NSIS ───────────────────────────────────────────────────
      - name: Install NSIS
        run: choco install nsis -y --no-progress

      # ── 9. Stage NSIS script alongside build output ───────────────────────
      - name: Stage NSIS script
        shell: pwsh
        run: |
          Copy-Item "installer\\iscmetrics_setup.nsi" "src\\isc_realtime_26\\iscmetrics_setup.nsi"

      # ── 10. Compile installer EXE ─────────────────────────────────────────
      - name: Compile NSIS installer
        id: nsis
        working-directory: src/isc_realtime_26
        shell: pwsh
        run: |
          $v   = "${{ steps.ver.outputs.VERSION }}"
          $out = "ISCmetrics_Setup_$v.exe"
          $nsis = "C:\\Program Files (x86)\\NSIS\\makensis.exe"
          & $nsis /DAPP_VERSION="$v" /DOUTFILE="$out" iscmetrics_setup.nsi
          if ($LASTEXITCODE -ne 0) { Write-Error "NSIS failed"; exit 1 }
          $sizeMB = [math]::Round((Get-Item $out).Length / 1MB, 1)
          Write-Host "Installer created: $out ($sizeMB MB)"
          Add-Content $env:GITHUB_OUTPUT "INSTALLER=$out"

      # ── 11. Upload artifact (always — useful for debugging) ───────────────
      - name: Upload installer artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: installer
          path: src/isc_realtime_26/${{ steps.nsis.outputs.INSTALLER }}
          if-no-files-found: warn

      # ── 12. Publish GitHub Release ────────────────────────────────────────
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.ver.outputs.VERSION }}
          name: ISCmetrics ${{ steps.ver.outputs.VERSION }}
          body_path: CHANGELOG.md
          files: src/isc_realtime_26/${{ steps.nsis.outputs.INSTALLER }}
          fail_on_unmatched_files: true
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

w(".github/workflows/build-release.yml", WORKFLOW)

# ─────────────────────────────────────────────────────────────────────────────
# 2. NSIS installer script
# ─────────────────────────────────────────────────────────────────────────────
NSIS = r"""
; ISCmetrics NSIS installer
; Built by GitHub Actions — do not edit manually.
; Usage: makensis /DAPP_VERSION="2.9.0" /DOUTFILE="ISCmetrics_Setup_v2.9.0.exe" iscmetrics_setup.nsi

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

  ; Registry entry for Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "DisplayName" "ISCmetrics"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "Publisher" "ISC Formula Student"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\ISCmetrics" \
    "DisplayIcon" "$INSTDIR\ISC_RTT.exe"
  WriteRegStr HKLM "Software\ISCmetrics" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\ISCmetrics" "Version" "${APP_VERSION}"

  ; Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\ISCmetrics"
  CreateShortcut "$SMPROGRAMS\ISCmetrics\ISCmetrics.lnk" \
    "$INSTDIR\ISC_RTT.exe" "" "$INSTDIR\ISC_RTT.exe" 0
  CreateShortcut "$SMPROGRAMS\ISCmetrics\Uninstall ISCmetrics.lnk" \
    "$INSTDIR\uninstall.exe"

  ; Desktop shortcut
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
"""

w("installer/iscmetrics_setup.nsi", NSIS)

# ─────────────────────────────────────────────────────────────────────────────
# 3. CHANGELOG
# ─────────────────────────────────────────────────────────────────────────────
CHANGELOG = """\
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
"""

w("CHANGELOG.md", CHANGELOG)

print("All files written successfully.")
