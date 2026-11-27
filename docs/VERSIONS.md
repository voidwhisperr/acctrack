# Версії, теги та релізи

Ledger випускає **релізні** теги для версій, які реально збиралися. Частина номерів
була пропущена під час швидких ітерацій — це зафіксовано нижче, щоб не вигадувати
теги заднім числом.

| Версія | Тег | GitHub Release | Примітка |
|---|---|---|---|
| 1.66.42 | v1.66.42 (після релізу) | ні (заплановано) | відтворюваний build-скрипт, PyQt виключено, SRI, клавіатура/a11y, recovery-код 8 цифр, THIRD-PARTY-NOTICES; APP_VERSION треба виставити 1.66.42 перед тегом |
| 1.66.41 | v1.66.41 | так | post-audit security: cold-start auth, ролі, бекапи, SSRF, XSS, proxy, підпис ключа |
| 1.66.31 | v1.66.31 | так | signer окремо, app/bots/taobao non-root |
| 1.66.30 | v1.66.30 | так | admin cookie + POST/CSRF, прибрано shell, шифровані бекапи |
| 1.66.29 | v1.66.29 | так | безпека /docs, локалізація, демо-скріншоти |
| 1.66.27 | v1.66.27 | так | Eldorado always-online |
| 1.66.26 | v1.66.26 | так (historical) | стиль always-online |
| 1.66.25 | v1.66.25 | так (historical) | always-online для ZeusX/FunPay |
| 1.66.24 | — | ні | **не випускалась**: контактна пошта вийшла як 1.66.23, далі одразу 1.66.25 |
| 1.66.23 | v1.66.23 | так (historical) | контактна пошта ledgeros.gg@gmail.com |
| 1.66.22 | v1.66.22 | так (historical) | Каталог + кеш постачальників |
| 1.66.21 | v1.66.21 | так (historical) | Telegram/Discord у UI |
| 1.66.20 | v1.66.20 | ні | pricing link fix |
| 1.66.19 | — | ні | пропущена ітерація (без окремого коміту) |
| 1.66.18 | v1.66.18 | ні | per-IP login limit |
| 1.66.14 | v1.66.14 | ні | collector auth fix |
| 1.66.13 | v1.66.13 | ні | mobile orders header |
| 1.66.12 | v1.66.12 | ні | clean console |
| 1.66.11 | — | ні | пропущена ітерація |
| 1.66.10 | v1.66.10 | так | іконки/бейдж |
| 1.66.1 | — | ні | пропущена ітерація |

Правило: один реліз = один тег vX.Y.Z + GitHub Release з Ledger.exe,
LedgerPlus.exe, source zip і SHA256SUMS.txt. Пропущені історичні теги не
створюються штучно, бо вони вказували б на код іншої версії.

## Як збирається реліз (v1.66.42+)

Windows-збірка тепер відтворювана: піни й команда лежать у репозиторії, а не в
голові того, хто збирає.

1. Встановити **Python 3.14.2 x64** (python.org, `py -3.14`).
2. Встановити піни:

```powershell
py -3.14 -m pip install -r scripts\build-requirements.txt
```

3. Зібрати обидва exe (скрипт сам перевіряє версії Python/пакетів і те, що
   `APP_VERSION` у `game_tracker.py` збігається з `version_info*.txt`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
```

4. Для підписаного релізу задати PFX і додати source zip:

```powershell
$env:LEDGER_SIGN_PFX  = "C:\secure\codesign.pfx"
$env:LEDGER_SIGN_PASS = "<pfx-password>"
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1 -SourceZip
```

Результат у `dist\`: `Ledger.exe`, `LedgerPlus.exe`, `SHA256SUMS.txt`,
`BUILD-INFO.txt` (версія, коміт, піни, хеші) і, з `-SourceZip`,
`ledger-vX.Y.Z.zip`.

Скрипт падає, якщо в зібраному exe знайдено PyQt5/PySide/Qt — саме ця
залежність була зайвою у v1.66.41 і раніше.

Супутні документи:

- [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md) — ліцензії всього, що
  входить у exe або вантажиться з CDN;
- [DEPLOY.md](DEPLOY.md) — кроки релізу, перевірка підпису й залишкові ризики;
- [SIGNING.md](SIGNING.md) — самопідписаний сертифікат і як його перевірити.

