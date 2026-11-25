# Safe deploy of Ledger to a VPS: upload to a temp path, verify SHA-256,
# compile, then atomically replace and restart. Rolls back on failure.
#
# Required:
#   $env:LEDGER_SSH_KEY          = 'C:\path\id_ed25519'
#   $env:LEDGER_SSH_KNOWN_HOSTS  = 'C:\path\known_hosts'
# Example:
#   powershell -ExecutionPolicy Bypass -File scripts\deploy_vps.ps1
param(
  [string]$HostName = 'root@70.34.243.50',
  [string]$KeyPath = $env:LEDGER_SSH_KEY,
  [string]$KnownHosts = $env:LEDGER_SSH_KNOWN_HOSTS,
  [string[]]$Files = @('game_tracker.py','ui.py'),
  [string]$RemoteDir = '/root',
  [string]$Service = 'gametracker'
)
$ErrorActionPreference = 'Stop'
if (-not $KeyPath -or -not (Test-Path $KeyPath)) { throw 'SSH key missing. Set LEDGER_SSH_KEY.' }
$ssh = (Get-Command ssh.exe -ErrorAction SilentlyContinue).Source
$scp = (Get-Command scp.exe -ErrorAction SilentlyContinue).Source
if (-not $ssh -or -not $scp) { throw 'ssh/scp not found. Install OpenSSH client or add PortableGit usr/bin to PATH.' }
$sshArgs = @('-i', $KeyPath, '-o', 'UserKnownHostsFile=' + $KnownHosts, '-o', 'BatchMode=yes')
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$tmp = "$RemoteDir/.deploy-$stamp"
$backup = "$RemoteDir/gt_versions/$stamp"
Write-Host "Preparing $tmp and backup $backup"
& $ssh @sshArgs $HostName "mkdir -p '$tmp' '$backup' && cp -a '$RemoteDir/game_tracker.py' '$RemoteDir/ui.py' '$backup'/ 2>/dev/null; echo ready"
$hashes = @{}
foreach ($f in $Files) {
  $local = Join-Path (Get-Location) $f
  if (-not (Test-Path $local)) { throw "local file missing: $f" }
  $h = (Get-FileHash $local -Algorithm SHA256).Hash.ToLower()
  $hashes[$f] = $h
  Write-Host "Uploading $f -> $tmp/$f"
  & $scp -q -C @sshArgs $local "$HostName`:$tmp/$f"
  $remoteHash = (& $ssh @sshArgs $HostName "sha256sum '$tmp/$f' | cut -d' ' -f1").Trim().ToLower()
  if ($remoteHash -ne $h) { throw "SHA-256 mismatch for $f (local $h, remote $remoteHash). Nothing was replaced." }
  Write-Host "  hash ok: $h"
}
$replace = ($Files | ForEach-Object { "mv -f '$tmp/$_' '$RemoteDir/$_'" }) -join ' && '
Write-Host 'Replacing files and compiling'
& $ssh @sshArgs $HostName "$replace && python3 -m py_compile $($Files -join ' ') || (cp -a '$backup'/game_tracker.py '$backup'/ui.py '$RemoteDir'/ && systemctl restart $Service && exit 4)"
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Compile failed — restored backup and restarted.'
  & $ssh @sshArgs $HostName "cp -a '$backup'/game_tracker.py '$backup'/ui.py '$RemoteDir'/; systemctl restart $Service"
  throw 'Deploy aborted: compile failed.'
}
Write-Host 'Restarting service'
& $ssh @sshArgs $HostName "systemctl restart $Service && sleep 5 && curl -fsS http://127.0.0.1:8766/api/health"
if ($LASTEXITCODE -ne 0) {
  Write-Host 'Health check failed — rolling back.'
  & $ssh @sshArgs $HostName "cp -a '$backup'/game_tracker.py '$backup'/ui.py '$RemoteDir'/; systemctl restart $Service"
  throw 'Deploy aborted: health check failed.'
}
Write-Host 'Deploy OK. Verify the authenticated UI, not only /api/health:'
Write-Host '  curl -u admin:<password> -o /tmp/ui.html -w "%{http_code} %{size_download}" https://<host>/'
Write-Host '  grep -c "UI недоступний" /tmp/ui.html   # must be 0'
