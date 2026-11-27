# Ledger 1.66.42 — leaner builds, keyboard access, honest notes

Ledger 1.66.42 is a maintenance release for the free desktop app and the hosted
Ledger+ edition. It makes the Windows builds reproducible and **about 33 MB
smaller per exe**, adds keyboard and screen-reader access to the dashboard,
strengthens the email recovery code, and writes down what is still imperfect.
Your data and settings stay in place.

## Short version (mirrors the Telegram / Discord post)

- Windows builds are reproducible: pinned toolchain, one script, `SHA256SUMS.txt` and `BUILD-INFO.txt`
- PyQt5/Qt removed from the exes: none of it was used, and each exe is about 33 MB smaller
- `THIRD-PARTY-NOTICES.md`: every bundled and CDN component with its licence
- Chart.js and SheetJS pinned with SRI; keyboard access, dialog roles and labels, mobile More menu
- Password recovery code is now 8 digits (10 minutes, same rate limits)
- Backups no longer export team invite tokens or the audit IP log
- Fixed, honest notes about what is still risky

Release: https://github.com/voidwhisperr/ledger/releases/tag/v1.66.42

## What changed in 1.66.42

### Reproducible, smaller Windows builds

- [scripts/build_release.ps1](https://github.com/voidwhisperr/ledger/blob/main/scripts/build_release.ps1)
  builds `Ledger.exe` and `LedgerPlus.exe` from Python 3.14.2 and PyInstaller
  6.22.3 with every package pinned in `scripts/build-requirements.txt`. The script
  refuses to build on version drift, checks that `APP_VERSION` matches both
  version resources, writes `SHA256SUMS.txt` and `BUILD-INFO.txt`, and signs
  with Authenticode when `LEDGER_SIGN_PFX` / `LEDGER_SIGN_PASS` are set.
- **PyQt5/PySide6/Qt are no longer bundled.** They were pulled in by
  pywebview's optional Qt backend although the app never imports PyQt5; Windows
  builds use the system WebView2 runtime. In local test builds Ledger.exe went
  from 77.6 MB to 44.8 MB and LedgerPlus.exe from 68.6 MB to 34.7 MB. The build
  script also fails if a Qt payload is found in the output.
- **THIRD-PARTY-NOTICES.md** lists every bundled and CDN component with version
  and licence, notes that PyQt5 was removed, and repeats the obligations for the
  LGPL-3.0 and Apache-2.0 components.

### Security and quality

- **SRI:** Chart.js 4.4.1 and SheetJS 0.18.5 are pinned with SHA-384
  `integrity` hashes; both hashes were recomputed from cdnjs on 2026-11-27 and
  match. The Google Fonts stylesheet cannot be pinned the same way — see the
  residual risks below.
- **Email recovery:** the one-time code is now **8 digits** instead of 6
  (space 10^8, brute force 100x more expensive). The 10-minute TTL and the rate
  limits are unchanged; a valid code is never locked by earlier failed attempts.
- **Backups:** export no longer includes the audit log with client IPs, and team
  invite tokens are stripped from `.gt_team.json` in the archive, so a backup
  cannot be used as a set of live invite links.
- **Accessibility:** navigation tabs are real `tab`/`tablist` controls:
  Enter/Space activate, arrow keys and Home/End move between them, with
  `aria-selected`, `tabindex`, labels and visible focus rings. Dialogs expose
  `role=dialog`, `aria-modal` and a title reference, move focus to the first
  control, trap Tab, close on Escape and restore focus. Settings and deal inputs
  got programmatic labels; the mobile bottom bar has a More menu for secondary
  sections.

### Carried from 1.66.41 (for anyone skipping it)

- 2FA and step-up confirmation for password and 2FA changes; email password recovery.
- License signing key isolated on a separate host; encrypted offsite backups to R2 and PC.
- Post-audit fixes: cold-start auth, team roles, restore atomicity, session revocation,
  recovery lockout, update version check, SSRF via supplier URLs, stored XSS, P&L CSV
  formula injection, NaN/Infinity, license activation race.
- Ledger+ proxy: forwarded `Origin`/`Referer` rewritten for CSRF, proxy capability
  cookie stripped upstream, `client.json` server URL validated (https outside loopback,
  no credentials in URL), paid mode no longer derived from the exe name or an env var.

## Residual risks, stated honestly

- The dashboard still loads Chart.js, SheetJS and the Manrope font from CDNs at
  runtime. JavaScript is SRI-pinned; fonts are not (the CSS varies by browser).
  If the CDN is unreachable, charts and Excel export stop working.
- SheetJS 0.18.5 is end-of-life and has advisories for its **read** paths. Ledger
  only writes exports and never reads untrusted workbooks, but moving to a
  maintained vendored build is still a follow-up.
- The build pins package **versions, not hashes**; a `pip --require-hashes` lock
  file is still missing. Build on a trusted machine.
- PyInstaller `--onefile` unpacks to `%TEMP%\_MEI*` on every launch. Do not run
  the exe from a world-writable folder; `--onedir` is a possible future change.
- The code-signing certificate is **self-signed**: the signature is valid but not
  trusted on other PCs unless `docs/ledger-codesign.cer` is installed, and
  SmartScreen may warn. A public OV/EV certificate is needed for a clean download.
- v1.66.41 and older exes still contain PyQt5/Qt. Do not redistribute those
  binaries; rebuild from this version instead.

## Verify the download

Compare the SHA-256 of both exes with `SHA256SUMS.txt` attached to the release,
and check the Authenticode signature (`Get-AuthenticodeSignature Ledger.exe`).
The build provenance, including the commit and pins, is in `BUILD-INFO.txt`.

## Full update in your language

- [UA](https://github.com/voidwhisperr/ledger/blob/main/docs/update-16642-ua.md) — повне оновлення українською
- [RU](https://github.com/voidwhisperr/ledger/blob/main/docs/update-16642-ru.md) — полное обновление по-русски

