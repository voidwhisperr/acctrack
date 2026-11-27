$ErrorActionPreference='Stop'
$root = $PSScriptRoot
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$dst = Join-Path $root ('reset-backups\' + $stamp)
New-Item -ItemType Directory -Path $dst -Force | Out-Null
$items = Get-ChildItem -LiteralPath $root -Force | Where-Object { $_.Name -like '.gt_*' -or $_.Name -in @('desktop.json','desktop-plus.json','desktop.log','client.log') }
foreach($i in $items){ Move-Item -LiteralPath $i.FullName -Destination $dst -Force }
Start-Process -FilePath (Join-Path $root 'Ledger.exe')
Write-Host ('Clean data backed up to ' + $dst)