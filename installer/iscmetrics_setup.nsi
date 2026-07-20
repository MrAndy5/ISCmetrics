
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
