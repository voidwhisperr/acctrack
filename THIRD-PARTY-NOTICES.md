# Third-party notices

Ledger is MIT licensed (see [LICENSE](LICENSE)). The Windows executables
(`Ledger.exe`, `LedgerPlus.exe`) and the dashboard embedded in this repository
include or load the third-party components listed below.

Last updated: 2026-11-27, for **v1.66.42**. Versions in the Windows builds are
pinned by [scripts/build-requirements.txt](scripts/build-requirements.txt) and
checked by [scripts/build_release.ps1](scripts/build_release.ps1).

This file is informational and not legal advice. Full licence texts are
available from the upstream projects linked to in each section.

## 1. Bundled in the Windows executables

Both exes are PyInstaller `--onefile` bundles built from the pinned environment.
Versions below are the ones inside v1.66.42 builds.

| Component | Version | Licence | Used for |
|---|---|---|---|
| CPython | 3.14.2 | PSF-2.0 | Python runtime inside the exes |
| PyInstaller bootloader | 6.22.3 | GPL-2.0-or-later with the PyInstaller bootloader exception | build tool; its bootloader is embedded in each exe |
| pywebview | 6.2.1 | BSD-3-Clause | native window (Microsoft Edge WebView2 backend) |
| pythonnet | 3.2.1 | MIT | CLR bridge required by pywebview on Windows |
| clr-loader | 0.3.1 | MIT | pythonnet loader |
| pystray | 0.19.5 | LGPL-3.0 | system tray icon and menu |
| Pillow | 13.0.0 | HPND / MIT-CMU | tray icon bitmaps |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | encrypted backups and licence payloads |
| qrcode | 8.2 | BSD | QR code for mobile access |
| winotify | 1.1.0 | MIT | Windows toast notifications (Ledger+ only) |
| numpy | 2.4.1 | BSD-3-Clause and 0BSD and MIT and Zlib and CC0-1.0 | dependency of the pywebview / pythonnet stack |
| pywin32 | 311 | PSF-2.0 | Windows API used by pystray and winotify |
| pywin32-ctypes | 0.2.3 | BSD-3-Clause | Windows API helper (build/runtime) |
| PyYAML | 6.0.4 | MIT | dependency of the pywebview / pythonnet stack |
| setuptools | 84.2.1 | MIT | runtime import helper |
| typing_extensions | 4.16.0 | PSF-2.0 | pywebview typing support |
| cffi | 2.1.1 | MIT-0 | cryptography backend |
| pycparser | 3.12 | BSD-3-Clause | cffi parser |
| colorama | 0.4.6 | BSD-3-Clause | qrcode terminal helper |
| six | 1.17.0 | MIT | legacy compatibility helper |
| proxy_tools | 0.1.0 | MIT | pywebview helper |
| altgraph | 0.17.5 | MIT | build tooling (not imported at runtime) |
| pefile | 2024.8.26 | MIT | build tooling (not imported at runtime) |
| packaging | 26.4 | Apache-2.0 OR BSD-2-Clause | build/dependency tooling |

The **Microsoft Edge WebView2 Runtime** is a Microsoft component of Windows and
is not redistributed with Ledger. The desktop apps require it; on current
Windows 10/11 systems it is normally already installed.

## 2. Loaded from CDNs at runtime (not bundled)

The dashboard is a single HTML page emitted from `ui.py`. Three external
resources are fetched by the browser:

| Resource | Version | Licence | Source |
|---|---|---|---|
| Chart.js | 4.4.1 | MIT | `https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js` |
| SheetJS Community Edition (`xlsx`) | 0.18.5 | Apache-2.0 | `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js` |
| Manrope font, served by Google Fonts | current | SIL OFL 1.1 | `https://fonts.googleapis.com/css2?family=Manrope...`, files from `https://fonts.gstatic.com` |

Chart.js and SheetJS are pinned with Subresource Integrity (SRI) SHA-384
hashes in `ui.py`, and both hashes were verified against cdnjs on 2026-11-27.
The Google Fonts stylesheet cannot be safely pinned because it varies by
browser; if it fails, the UI falls back to the `system-ui` font stack.

Residual risks, stated honestly:

- the dashboard still depends on runtime CDN availability (cdnjs and Google
  Fonts are allow-listed in the Content-Security-Policy);
- SheetJS `0.18.5` is end-of-life and has advisories for **read** paths
  (CVE-2023-30533, CVE-2024-22363). Ledger only uses the export/write path
  (`XLSX.utils.book_new` / `aoa_to_sheet` / `book_append_sheet` /
  `writeFile`) and never calls `XLSX.read` on user input, but a maintained
  vendored build is still the recommended follow-up.

If you self-host a hardened copy, serve pinned local copies of Chart.js,
SheetJS and the font instead, and update the `Content-Security-Policy` in
`game_tracker.py` accordingly.

## 3. Components excluded from v1.66.42 builds

- **PyQt5 5.15.11 / Qt 5.15.2** were pulled into the v1.66.41 and older exes
  by PyInstaller analyzing pywebview's optional Qt backend, although the app
  never imports PyQt5 and uses the WebView2 backend on Windows. PyQt5 is
  GPLv3 or commercial (Riverbank), Qt 5.15.2 is GPLv3/LGPLv3, and an MIT-only
  binary carrying them without notices is a licensing problem.
  v1.66.42 builds explicitly exclude `PyQt5`, `PyQt6`, `PySide2`, `PySide6`
  and the `webview.platforms.qt/gtk/cocoa/android/cef` modules, and the build
  script fails if a Qt payload is found in the output. Do not redistribute
  v1.66.41 or older exes without reviewing those obligations; rebuild from
  the v1.66.42 source instead.
- **PySide6** is not installed or included.
- **PyQt5 is deliberately absent from v1.66.42.** The exes are smaller and
  use only the system WebView2 runtime.

## 4. Development and test tooling (not shipped)

- **pytest** (MIT) runs the test suite in CI.
- **Playwright** (Apache-2.0) is used by maintainers for browser smoke tests.
- **GitHub Actions** runners and their preinstalled tools are not part of any
  release artifact.

## 5. Redistribution obligations

If you redistribute a Ledger binary or the source package, keep `LICENSE` and
this file together with it, and preserve the upstream notices for every
component listed above. In particular:

- **MIT / BSD / PSF / HPND** components: keep their copyright and licence
  notices. Full texts are in the upstream repositories and inside the
  `*.dist-info` metadata of each wheel.
- **pystray (LGPL-3.0)**: the exes include unmodified pystray code and the
  full LGPL-3.0 text is distributed by the pystray project. If you modify or
  relink pystray, you must comply with LGPL-3.0 section 4 (source and
  re-linking). The upstream source is
  https://github.com/moses-palmer/pystray.
- **cryptography (Apache-2.0 OR BSD-3-Clause)**: a dual licence; pick either.
  Apache-2.0 requires keeping the licence and any `NOTICE` file supplied by
  the project.
- **SheetJS (Apache-2.0)**: loaded from cdnjs, not redistributed; Apache-2.0
  obligations apply if you vendor it.
- **Manrope (SIL OFL 1.1)**: if you self-host the font files, include the OFL
  text and do not sell the font by itself.
- **PyInstaller bootloader**: GPL-2.0-or-later with an exception that
  explicitly permits building and distributing applications under other
  licences. The bootloader is embedded inside each exe.
- **CPython**: PSF-2.0, including the historical notices shipped by CPython.
- **PyQt5 / Qt (v1.66.41 and older binaries only)**: GPLv3 and commercial
  licensing from Riverbank; Qt 5.15.2 is GPLv3/LGPLv3. Rebuild instead of
  redistributing those binaries.

Code-signing with a self-signed certificate is separate from these notices;
see [docs/SIGNING.md](docs/SIGNING.md).

## 6. Full licence texts

- MIT: https://spdx.org/licenses/MIT.html
- BSD-3-Clause: https://spdx.org/licenses/BSD-3-Clause.html
- BSD-2-Clause: https://spdx.org/licenses/BSD-2-Clause.html
- Apache-2.0: https://spdx.org/licenses/Apache-2.0.html
- LGPL-3.0: https://spdx.org/licenses/LGPL-3.0-only.html
- GPL-2.0: https://spdx.org/licenses/GPL-2.0-or-later.html
- PSF-2.0: https://spdx.org/licenses/PSF-2.0.html
- MIT-0: https://spdx.org/licenses/MIT-0.html
- HPND: https://spdx.org/licenses/HPND.html
- SIL OFL 1.1: https://openfontlicense.org/

## 7. How this list was verified

- `scripts/build-requirements.txt` pins every version above and
  `scripts/build_release.ps1` refuses to build on any version drift.
- The component list was cross-checked against the `*.dist-info` metadata and
  extracted contents of the v1.66.41 bundles (the last release before the Qt
  exclusion was added); v1.66.42 removes PyQt5/Qt from that list.
- Chart.js and SheetJS SRI hashes were downloaded from cdnjs and recomputed
  with SHA-384 on 2026-11-27; both matched the values pinned in `ui.py`.
- To inspect a build yourself:

```powershell
py -3.14 -m PyInstaller.utils.cliutils.archive_viewer -l dist\Ledger.exe
```

  The listing must not contain `PyQt5`, `PySide`, `Qt5Core.dll` or
  `Qt6Core.dll`.

