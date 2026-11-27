# Reproducible Windows release build for Ledger and Ledger+.
#
# Prerequisites (pinned, see scripts/build-requirements.txt):
#   * Windows 10/11 x64
#   * CPython 3.14.2 x64 from python.org, available as "py -3.14"
#   * py -3.14 -m pip install -r scripts/build-requirements.txt
#   * Windows SDK signtool.exe only when signing (scripts/sign_windows.ps1)
#
# What it does:
#   1. verifies Python and every package version against the pins;
#   2. verifies game_tracker.py APP_VERSION and both version resources agree;
#   3. builds Ledger.exe (desktop.py) and LedgerPlus.exe (ledger_client.py)
#      with a fixed PyInstaller command, excluding PyQt5/PySide6/Qt;
#   4. asserts that no Qt/PySide payload ended up inside the exes;
#   5. signs with Authenticode when LEDGER_SIGN_PFX and LEDGER_SIGN_PASS are set;
#   6. writes SHA256SUMS.txt and BUILD-INFO.txt into the output directory.
#
# Examples:
#   powershell -ExecutionPolicy Bypass -File scripts/build_release.ps1
#   powershell -ExecutionPolicy Bypass -File scripts/build_release.ps1 -OutDir dist-16642 -Force
#   $env:LEDGER_SIGN_PFX = "C:\secure\codesign.pfx"
#   $env:LEDGER_SIGN_PASS = "pfx-password"
#   powershell -ExecutionPolicy Bypass -File scripts/build_release.ps1 -SourceZip
#
# Notes:
#   * onefile builds are not byte-for-byte reproducible; reproducibility here
#     means the same pins and the same command produce the same behavior;
#   * -SourceZip needs a clean git checkout and uses "git archive HEAD".
[CmdletBinding()]
param(
  [string]$Python = $env:LEDGER_BUILD_PYTHON,
  [string]$Version = "",
  [string]$OutDir = "",
  [switch]$SkipSign,
  [switch]$RequireSignature,
  [switch]$SourceZip,
  [switch]$KeepBuild,
  [switch]$Force
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$pins = [ordered]@{
  "pyinstaller" = "6.22.3"
  "pyinstaller-hooks-contrib" = "2026.10"
  "pywebview" = "6.2.1"
  "pythonnet" = "3.2.1"
  "clr_loader" = "0.3.1"
  "pystray" = "0.19.5"
  "pillow" = "13.0.0"
  "cryptography" = "50.0.2"
  "qrcode" = "8.2"
  "winotify" = "1.1.0"
  "numpy" = "2.4.1"
  "pywin32" = "311"
  "pyyaml" = "6.0.4"
  "setuptools" = "84.2.1"
  "typing_extensions" = "4.16.0"
  "cffi" = "2.1.1"
  "pycparser" = "3.12"
  "colorama" = "0.4.6"
  "six" = "1.17.0"
  "proxy_tools" = "0.1.0"
  "altgraph" = "0.17.5"
  "pefile" = "2024.8.26"
  "pywin32-ctypes" = "0.2.3"
  "packaging" = "26.4"
}

# ---- pinned Python ----
if (-not $Python) {
  $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
  if (-not $pyLauncher) { throw "py.exe not found. Install Python 3.14.2 x64 or pass -Python C:\path\python.exe." }
  $Python = (& py -3.14 -c "import sys; print(sys.executable)" 2>$null | Select-Object -First 1)
}
if (-not $Python -or -not (Test-Path -LiteralPath $Python)) { throw "Build Python not found: $Python" }
$Python = [IO.Path]::GetFullPath($Python)
$pyVer = (& $Python -c "import sys; print('{0}.{1}.{2}'.format(*sys.version_info[:3]))").Trim()
$pyBits = (& $Python -c "import struct; print(struct.calcsize('P') * 8)").Trim()
if ($pyVer -ne "3.14.2") { throw "Pinned build uses Python 3.14.2, found $pyVer. Update scripts/build-requirements.txt and this pin deliberately." }
if ($pyBits -ne "64") { throw "Pinned build uses 64-bit Python, found $pyBits-bit." }
Write-Host "== Python $pyVer ($pyBits-bit): $Python"

# ---- pinned packages ----
$freeze = & $Python -m pip freeze
if ($LASTEXITCODE -ne 0) { throw "pip freeze failed for $Python" }
$have = @{}
foreach ($line in $freeze) {
  if ($line -match "^([A-Za-z0-9_.-]+)==(.+)$") { $have[$Matches[1].ToLowerInvariant()] = $Matches[2] }
}
$bad = @()
foreach ($name in $pins.Keys) {
  $want = $pins[$name]
  $got = if ($have.ContainsKey($name)) { $have[$name] } else { "missing" }
  if ($got -ne $want) { $bad += ("{0}=={1} (found {2})" -f $name, $want, $got) }
}
if ($bad.Count -gt 0) {
  throw ("Build environment does not match scripts/build-requirements.txt:`n  " + ($bad -join "`n  ") + "`nInstall with: `"$Python`" -m pip install -r scripts/build-requirements.txt")
}
Write-Host "== environment matches scripts/build-requirements.txt"

# ---- version consistency ----
$required = @("game_tracker.py", "ui.py", "desktop.py", "ledger_client.py", "remote_proxy.py", "assets/ledger.ico", "assets/ledger-plus.ico", "version_info.txt", "version_info_plus.txt")
foreach ($f in $required) {
  if (-not (Test-Path -LiteralPath (Join-Path $root $f))) { throw "missing build input: $f" }
}
$gtText = Get-Content -LiteralPath (Join-Path $root "game_tracker.py") -Raw
$m = [regex]::Match($gtText, '(?m)^APP_VERSION\s*=\s*"([^"]+)"')
if (-not $m.Success) { throw "APP_VERSION not found in game_tracker.py" }
$appVersion = $m.Groups[1].Value
if ($Version -and $Version -ne $appVersion) { throw "-Version $Version does not match APP_VERSION $appVersion. Bump game_tracker.py first." }
if (-not $Version) { $Version = $appVersion }
foreach ($vf in @("version_info.txt", "version_info_plus.txt")) {
  $text = Get-Content -LiteralPath (Join-Path $root $vf) -Raw
  $vm = [regex]::Match($text, 'filevers=\((\d+),\s*(\d+),\s*(\d+),\s*\d+\)')
  if (-not $vm.Success) { throw "filevers not found in $vf" }
  $resVersion = "{0}.{1}.{2}" -f $vm.Groups[1].Value, $vm.Groups[2].Value, $vm.Groups[3].Value
  if ($resVersion -ne $appVersion) { throw "$vf is $resVersion but APP_VERSION is $appVersion. Update both before building." }
}
Write-Host "== version $Version is consistent (APP_VERSION + version_info.txt + version_info_plus.txt)"
$compile = @("game_tracker.py", "ui.py", "desktop.py", "ledger_client.py", "remote_proxy.py")
& $Python -m py_compile @compile
if ($LASTEXITCODE -ne 0) { throw "py_compile failed; fix the source before building" }
Write-Host "== py_compile OK"

# ---- output directory ----
if (-not $OutDir) { $OutDir = Join-Path $root "dist" }
elseif (-not [IO.Path]::IsPathRooted($OutDir)) { $OutDir = Join-Path $root $OutDir }
$OutDir = [IO.Path]::GetFullPath($OutDir)
$exeNames = @("Ledger.exe", "LedgerPlus.exe")
if (Test-Path -LiteralPath $OutDir) {
  $old = @(Get-ChildItem -LiteralPath $OutDir -Filter "*.exe" -File -ErrorAction SilentlyContinue)
  if ($old.Count -gt 0 -and -not $Force) { throw "$OutDir already contains exes. Pass -Force to replace them." }
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if ($Force) {
  foreach ($n in ($exeNames + @("SHA256SUMS.txt", "BUILD-INFO.txt"))) {
    $p = Join-Path $OutDir $n
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force }
  }
}
$work = Join-Path $OutDir "_build"
if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
New-Item -ItemType Directory -Force -Path $work | Out-Null

# ---- fixed PyInstaller configuration ----
$excludes = @(
  "PyQt5", "PyQt6", "PySide2", "PySide6",
  "webview.platforms.qt", "webview.platforms.gtk", "webview.platforms.cocoa",
  "webview.platforms.android", "webview.platforms.cef"
)
$common = @("--noconfirm", "--clean", "--onefile", "--windowed", "--distpath", $OutDir, "--specpath", $work)

function Invoke-Build([string]$Entry, [string]$Name, [string]$Icon, [string]$VersionFile, [string[]]$AddData, [string[]]$Hidden) {
  $a = @()
  $a += $common
  # PyInstaller resolves icon/version/data paths relative to the spec file, so pass absolutes.
  $iconPath = if ([IO.Path]::IsPathRooted($Icon)) { $Icon } else { Join-Path $root $Icon }
  $versionPath = if ([IO.Path]::IsPathRooted($VersionFile)) { $VersionFile } else { Join-Path $root $VersionFile }
  $entryPath = if ([IO.Path]::IsPathRooted($Entry)) { $Entry } else { Join-Path $root $Entry }
  $a += @("--name", $Name, "--icon", $iconPath, "--version-file", $versionPath, "--workpath", (Join-Path $work $Name))
  foreach ($d in $AddData) {
    $parts = $d.Split(";", 2)
    $src = $parts[0]
    if (-not [IO.Path]::IsPathRooted($src)) { $src = Join-Path $root $src }
    $a += @("--add-data", ("{0};{1}" -f $src, $parts[1]))
  }
  foreach ($x in $excludes) { $a += @("--exclude-module", $x) }
  foreach ($h in $Hidden) { $a += @("--hidden-import", $h) }
  $a += $entryPath
  Write-Host ""
  Write-Host ("== PyInstaller: {0} <- {1}" -f $Name, $Entry)
  & $Python -m PyInstaller @a
  if ($LASTEXITCODE -ne 0) { throw ("PyInstaller failed for {0} (exit {1})" -f $Name, $LASTEXITCODE) }
}

Invoke-Build -Entry "desktop.py" -Name "Ledger" -Icon "assets/ledger.ico" -VersionFile "version_info.txt" `
  -AddData @("assets;assets", "docs;docs") -Hidden @("webview.platforms.edgechromium", "webview.platforms.winforms")
Invoke-Build -Entry "ledger_client.py" -Name "LedgerPlus" -Icon "assets/ledger-plus.ico" -VersionFile "version_info_plus.txt" `
  -AddData @("assets;assets") -Hidden @("webview.platforms.edgechromium", "webview.platforms.winforms", "winotify")

# ---- assert the artifacts exist and carry no Qt payload ----
$exes = @()
foreach ($n in $exeNames) {
  $p = Join-Path $OutDir $n
  if (-not (Test-Path -LiteralPath $p)) { throw "build output missing: $p" }
  $exes += (Get-Item -LiteralPath $p)
}
function Get-ArchiveListing([string]$Exe) {
  $out = & $Python -m PyInstaller.utils.cliutils.archive_viewer -l $Exe 2>&1
  if ($LASTEXITCODE -ne 0) { throw "pyi-archive_viewer failed for $Exe" }
  return ($out -join "`n")
}
$forbidden = @("PyQt5", "PyQt6", "PySide2", "PySide6", "Qt5Core.dll", "Qt6Core.dll")
foreach ($exe in $exes) {
  $listing = Get-ArchiveListing $exe.FullName
  $hits = @($forbidden | Where-Object { $listing.Contains($_) })
  if ($hits.Count -gt 0) { throw ("Qt payload found in {0}: {1}" -f $exe.Name, ($hits -join ", ")) }
  if (-not $listing.Contains("webview")) { throw "archive listing for $exe.Name does not contain webview; pywebview data would be missing" }
  Write-Host ("== no Qt payload in {0}" -f $exe.Name)
}

# ---- optional Authenticode signing ----
$signed = $false
if (-not $SkipSign -and $env:LEDGER_SIGN_PFX -and $env:LEDGER_SIGN_PASS) {
  $signScript = Join-Path $root "scripts/sign_windows.ps1"
  Write-Host "== signing with $env:LEDGER_SIGN_PFX"
  & $signScript -Files ($exes | ForEach-Object { $_.FullName })
  if ($LASTEXITCODE -ne 0) { throw "sign_windows.ps1 failed" }
  $signed = $true
} elseif ($RequireSignature) {
  throw "Signature required but LEDGER_SIGN_PFX / LEDGER_SIGN_PASS are not both set."
} else {
  Write-Warning "Build is unsigned. Set LEDGER_SIGN_PFX and LEDGER_SIGN_PASS to sign before publishing."
}

# ---- optional source zip from a clean checkout ----
$zip = $null
if ($SourceZip) {
  $gitCmd = Get-Command git -ErrorAction SilentlyContinue
  if (-not $gitCmd) { throw "-SourceZip needs git in PATH" }
  Push-Location $root
  try {
    & git rev-parse --is-inside-work-tree 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "-SourceZip needs $root to be a git checkout (run it from the repository, not an extracted zip)" }
    $dirty = & git status --porcelain --untracked-files=no
    if ($dirty) { throw "-SourceZip needs a clean working tree; commit the release changes first" }
    $zip = Join-Path $OutDir ("ledger-v{0}.zip" -f $Version)
    & git archive --format=zip --output $zip HEAD
    if ($LASTEXITCODE -ne 0) { throw "git archive failed" }
    Write-Host ("== source zip: {0}" -f $zip)
  } finally { Pop-Location }
}

# ---- SHA256SUMS.txt + BUILD-INFO.txt ----
$artifacts = @()
foreach ($exe in $exes) { $artifacts += $exe }
if ($zip) { $artifacts += (Get-Item -LiteralPath $zip) }
$sums = @()
foreach ($f in ($artifacts | Sort-Object Name)) {
  $h = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $sums += ("{0}  {1}" -f $h, $f.Name)
}
$sumsPath = Join-Path $OutDir "SHA256SUMS.txt"
Set-Content -LiteralPath $sumsPath -Value $sums -Encoding ascii

$commit = "unknown"
$gitAny = Get-Command git -ErrorAction SilentlyContinue
if ($gitAny) {
  Push-Location $root
  try { $c = & git rev-parse HEAD 2>$null; if ($LASTEXITCODE -eq 0 -and $c) { $commit = $c.Trim() } } finally { Pop-Location }
}
$info = @()
$info += ("Version: {0}" -f $Version)
$info += ("Built (UTC): {0}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))
$info += ("Python: {0} ({1}-bit) at {2}" -f $pyVer, $pyBits, $Python)
$info += ("PyInstaller: {0}" -f $pins["pyinstaller"])
$info += ("Commit: {0}" -f $commit)
$info += ("Signed: {0}" -f $(if ($signed) { "yes (Authenticode SHA-256, RFC 3161 timestamp)" } else { "no" }))
$info += "Artifacts:"
foreach ($f in ($artifacts | Sort-Object Name)) {
  $h = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $info += ("  {0}  {1} bytes  {2}" -f $f.Name, $f.Length, $h)
}
$info += ""
$info += "PyInstaller onefile builds are not byte-for-byte reproducible. This file records"
$info += "the pinned inputs and the output hashes so a release can be re-verified."
Set-Content -LiteralPath (Join-Path $OutDir "BUILD-INFO.txt") -Value $info -Encoding ascii

if ($KeepBuild) { Write-Host "== build work kept at $work" } else { Remove-Item -LiteralPath $work -Recurse -Force }

Write-Host ""
Write-Host ("== release {0} built in {1}" -f $Version, $OutDir)
foreach ($f in ($artifacts | Sort-Object Name)) {
  Write-Host ("   {0,-20} {1,12:N0} bytes" -f $f.Name, $f.Length)
}
Write-Host ("   checksums: {0}" -f $sumsPath)
if (-not $signed) { Write-Warning "Artifacts are unsigned; sign and verify before publishing." }

[pscustomobject]@{
  Version = $Version
  OutDir = $OutDir
  Signed = $signed
  Exes = @($exes | ForEach-Object { $_.FullName })
  SHA256SUMS = $sumsPath
  SourceZip = $zip
}
