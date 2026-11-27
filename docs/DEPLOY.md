# Deploying to a VPS

## Safe deploy (recommended)

Use `scripts/deploy_vps.ps1`. It:

1. backs up `game_tracker.py` and `ui.py` to `/root/gt_versions/<timestamp>`;
2. uploads each file to a temp directory and verifies SHA-256 before replacing anything;
3. runs `python3 -m py_compile` on the server;
4. restarts the service only if compilation succeeds;
5. checks `/api/health`;
6. rolls back automatically if compile or health fails.

```powershell
$env:LEDGER_SSH_KEY = 'C:\Users\...\id_ed25519'
$env:LEDGER_SSH_KNOWN_HOSTS = 'C:\Users\...\known_hosts'
powershell -ExecutionPolicy Bypass -File scripts\deploy_vps.ps1
```

## Why the old way is dangerous

On 2026-11-25 a plain `scp` of `ui.py` was truncated by a connection reset. The service was
restarted anyway, `api/health` still returned 200 (it does not import the UI), but every
authenticated page showed:

> UI недоступний — Не знайдено модуль ui.py

Always verify the **authenticated dashboard**, not only the health endpoint:

```bash
PW=$(python3 -c "import json;print(json.load(open('/root/.gt_secrets.json'))['auth_pass'])")
curl -s -u admin:$PW -o /tmp/ui.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8766/
grep -c 'UI недоступний' /tmp/ui.html   # must print 0
```

## Rollback

```bash
ls -1 /root/gt_versions | tail -3
cp -a /root/gt_versions/<timestamp>/game_tracker.py /root/gt_versions/<timestamp>/ui.py /root/
systemctl restart gametracker
```

---

# Building the Windows release (v1.66.42+)

The desktop exes are built from a pinned environment and a fixed PyInstaller
command by `scripts/build_release.ps1`. The script verifies Python and package
versions, checks that `APP_VERSION` in `game_tracker.py` matches
`version_info.txt` / `version_info_plus.txt`, excludes PyQt5/PySide6/Qt, fails
if a Qt payload is found in the built exe, optionally signs, and writes
`SHA256SUMS.txt` + `BUILD-INFO.txt`.

## Prerequisites

- Windows 10/11 x64.
- **Python 3.14.2 x64** from python.org, available as `py -3.14`.
- `py -3.14 -m pip install -r scripts\build-requirements.txt` (exact pins).
- Windows SDK `signtool.exe` only when signing; `scripts/sign_windows.ps1`
  finds it in PATH or under `C:\Program Files (x86)\Windows Kits\10\bin`.
- No PyQt5 needed: v1.66.42 builds use the system WebView2 runtime.

## Build a tagged release

```powershell
git checkout vX.Y.Z          # clean tag, no local edits
py -3.14 -m pip install -r scripts\build-requirements.txt
$env:LEDGER_SIGN_PFX  = 'C:\secure\codesign.pfx'
$env:LEDGER_SIGN_PASS = '<pfx-password>'
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1 -SourceZip
```

Without `LEDGER_SIGN_PFX` / `LEDGER_SIGN_PASS` the build is unsigned and the
script prints a warning; add `-RequireSignature` to make that fatal. Use
`-OutDir` to keep several versions side by side. `-SourceZip` needs a clean git
checkout (it runs `git archive HEAD`) and adds `ledger-vX.Y.Z.zip`.

Output in `dist\`:

- `Ledger.exe`, `LedgerPlus.exe`;
- `SHA256SUMS.txt` (`sha256sum -c` compatible);
- `BUILD-INFO.txt` (version, UTC build time, commit, Python/pyinstaller pins,
  signing state, per-file size and SHA-256);
- `ledger-vX.Y.Z.zip` (only with `-SourceZip`).

## Verify before uploading

```powershell
Get-FileHash dist\Ledger.exe -Algorithm SHA256
Get-AuthenticodeSignature dist\Ledger.exe | Format-List Status, SignerCertificate
py -3.14 -m PyInstaller.utils.cliutils.archive_viewer -l dist\Ledger.exe | Select-String 'PyQt5|PySide|Qt5Core|Qt6Core'
# the last command must print nothing
```

Smoke-test a copy in an isolated folder, not next to real data:

```powershell
$dir = Join-Path $env:TEMP 'ledger-release-smoke'
New-Item -ItemType Directory -Force $dir | Out-Null
Copy-Item dist\Ledger.exe $dir
$env:GT_DESKTOP_MODE = 'local'
Start-Process (Join-Path $dir 'Ledger.exe')
# default URL and any port change are written to $dir\desktop.log
Invoke-RestMethod http://127.0.0.1:8766/api/health
```

The health answer must report the version being released. Check the window
renders and the tray icon appears, then close the process.

Attach to the GitHub release: both exes, `ledger-vX.Y.Z.zip`, `SHA256SUMS.txt`
and a link to `THIRD-PARTY-NOTICES.md`. Bump the version in `game_tracker.py`,
`version_info.txt` and `version_info_plus.txt` before the build; the script
refuses to build when they disagree. Update the `docs/update-XYZ` pages and
`CHANGELOG.md` before tagging.

## Residual build risks

These are known and documented rather than hidden:

- **Versions are pinned, hashes are not.** `scripts/build-requirements.txt`
  pins exact versions, but a full `pip --require-hashes` lock file is still a
  follow-up. Treat the build machine as trusted.
- **Onefile extraction.** PyInstaller `--onefile` unpacks to `%TEMP%\_MEI*` on
  every run. A future release may switch to `--onedir`; until then do not run
  the exe from a world-writable directory.
- **Self-signed signing certificate.** The signature is valid but not trusted
  by other machines unless `docs/ledger-codesign.cer` is installed; SmartScreen
  may still warn. Buy an OV/EV certificate for public distribution.
- **CDN dependency.** Chart.js and SheetJS are loaded from cdnjs at runtime
  (SRI-pinned) and the Manrope font from Google Fonts (not SRI-pinnable).
  Offline use falls back to system fonts but charts and Excel export need the
  CDN. SheetJS 0.18.5 is EOL; the app only uses its write path.
- **Not byte-for-byte reproducible.** The same pins and command produce the
  same behavior and the same sources, but timestamps inside the PE/archive
  differ between runs; `BUILD-INFO.txt` records the exact inputs.

