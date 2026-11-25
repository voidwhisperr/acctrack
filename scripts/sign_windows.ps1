# Sign Ledger Windows binaries with an Authenticode certificate.
#
# The certificate is NOT in this repository. Provide it at runtime:
#   $env:LEDGER_SIGN_PFX  = 'C:\path\to\codesign.pfx'
#   $env:LEDGER_SIGN_PASS = 'pfx-password'
# or pass -Pfx / -Password.
#
# Example:
#   powershell -ExecutionPolicy Bypass -File scripts\sign_windows.ps1 -Files dist\Ledger.exe
param(
  [Parameter(Mandatory=$true)][string[]]$Files,
  [string]$Pfx = $env:LEDGER_SIGN_PFX,
  [string]$Password = $env:LEDGER_SIGN_PASS,
  [string]$Timestamp = 'http://timestamp.digicert.com',
  [string]$Description = 'Ledger'
)
$ErrorActionPreference = 'Stop'
if (-not $Pfx -or -not (Test-Path $Pfx)) { throw 'PFX not found. Set LEDGER_SIGN_PFX or pass -Pfx.' }
if (-not $Password) { throw 'PFX password missing. Set LEDGER_SIGN_PASS or pass -Password.' }
$signtool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
if (-not $signtool) {
  $signtool = Get-ChildItem 'C:\Program Files (x86)\Windows Kits\10\bin' -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match '\\x64\\' } | Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $signtool) { throw 'signtool.exe not found. Install Windows SDK.' }
$failed = @()
foreach ($f in $Files) {
  if (-not (Test-Path $f)) { Write-Warning "missing: $f"; $failed += $f; continue }
  Write-Host "Signing $f"
  & $signtool sign /fd SHA256 /f $Pfx /p $Password /tr $Timestamp /td SHA256 /d $Description $f
  if ($LASTEXITCODE -ne 0) { $failed += $f }
}
foreach ($f in $Files) {
  if (-not (Test-Path $f)) { continue }
  $sig = Get-AuthenticodeSignature $f
  Write-Host ("{0}: {1}" -f $f, $sig.Status)
  if ($sig.Status -ne 'Valid') { $failed += $f }
}
if ($failed.Count) { throw ('Signature verification failed: ' + (($failed | Select-Object -Unique) -join ', ')) }
Write-Host 'All signatures valid.'
