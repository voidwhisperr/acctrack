# Changelog

## v1.66.26 — polished always-online widgets
- Always-online blocks use a switch, compact time inputs, status dot and refresh pill instead of the raw checkbox/fields.

## v1.66.25 — always online (5-min keepalive)

## v1.66.25 — always online for ZeusX and FunPay
- Channels cards get an “Always online” toggle with a daily time window, server-side activity keepalive, and a real status (online / scheduled / off / error + last check).
- Eldorado has no public API, so it stays accounting-only.

## v1.66.24 — contact email
- Contact panel and pricing page use ledgeros.gg@gmail.com; docs and tests updated.

## v1.66.22 — catalog tab and supplier cache fixes
- Settings panels are now inside the Setup tab again; they no longer appear under Catalog/other tabs.
- Supplier refresh refuses to wipe the cache when no suppliers are configured (restores the lost list from cache/settings).

## v1.66.21 — community links in the app
- Header now has branded Telegram and Discord buttons (icons + labels; icons only on phones).
- Contact panel, login page and pricing CTA link to both the Telegram channel and Discord server.
- Discord server hardened: verification level Medium, explicit content filter All Members, Server Hub removed.

## v1.66.20 — pricing Telegram link fix
- Fixed `/pricing` 500 after replacing the personal Telegram handle with the channel; CTA now points to https://t.me/ledger_os.
- Ledger OS channel links in dashboard header, contact panel, login page and docs.

## v1.66.19 — Telegram channel links
- Added Ledger OS Telegram channel (https://t.me/ledger_os) to the dashboard header, login page and pricing CTA.
- Replaced the old personal Telegram contact with the channel in app, pricing, demo and docs.

## v1.66.18 — per-IP login limit behind proxy
- Rate limiting and auth logs use `X-Forwarded-For` when behind Caddy, so one client cannot block everyone.
- Infra: 8765 collector endpoint restricted by UFW to the agent IP; Caddy access logging disabled for 8765 (collector token no longer written to disk); prior log truncated.

## v1.66.17 — tablet table scroll
- Tables now scroll horizontally on ≤860px too, so the hosted Channels “recent sales” table is fully reachable at 768px.

## v1.66.16 — responsive tables and catalog cards
- Catalog card action buttons wrap instead of overflowing on phones.
- Tables scroll horizontally inside panels on ≤640px (Channels/ZeusX tables no longer clip).
- Tabs wrap on tablets ≤860px so Inventory/Analytics/Ledger+/Settings stay visible.

## v1.66.15 — security fixes from multi-agent audit
- Fixed reflected XSS in `/admin/revoke` (invalid token now 403; redirect token URL-encoded).
- Login form now honours rate limiting; removed `GT_AUTH_NO_LIMIT` on the VPS.
- `HEAD` supported; single `charset` in Content-Type; settings PII masked for non-owner roles; hosted `/api/license/status` reports plan `plus` consistently; license activation preserves server error text; startup banner no longer says “no password” when auth is on.
- CI runs `tests/verify_auth.py`; `tests/test_license.py` standalone.

## v1.66.14 — collector token auth fix
- Fixed `_role_gate` blocking `X-GT-TOKEN` requests with 401 on password-protected instances; Taobao collector now works on hosted Ledger+ again (verify_auth 14/14).
- CI runs `tests/verify_auth.py`; `tests/test_license.py` runs standalone without pytest.

## v1.66.13 — orders header wraps on mobile
- Panel header controls now wrap (`flex-wrap`) so “звук”, “авто в P&L”, Demo and Refresh stay visible on narrow screens.

## v1.66.12 — clean console in free edition
- `/api/team` returns 200 with `ok:false` when the team plan is missing, instead of 402, so the free dashboard no longer logs a failed network request.

## v1.66.11 — mobile layout fixes
- No horizontal page scroll on phones (body/wrapper overflow guard).
- Mobile navigation tabs wrap into rows instead of a clipped horizontal strip; all labels visible.
- Tested at 360/390/768 px across all 11 tabs.

## v1.66.10 — icon fills the tile
- Shield mark enlarged to ~70% of the tile (like other iOS apps) and the green plus badge reduced to r8.5.
- iOS 96% scale, maskable 68%; validated 0 clipped pixels against iOS squircle and Android circle masks.

## v1.66.9 — balanced plus badge
- Badge radius set to 10.5 (between the clipped 14 and the too-small 8.5), moved to (46,46); iOS 180 at 86% scale, maskable at 72%.
- Validated: 0 clipped pixels against iOS squircle and Android circle masks.

## v1.66.8 — smaller Ledger+ badge
- Redesigned Ledger+ mark: the green plus badge is smaller and moved inward; content stays within 80% of the canvas on iOS and inside the Android maskable safe circle.
- New full-bleed SVG/PNG/ICO assets; iOS 180 at 85%, PWA any 85%, maskable 70%.

## v1.66.7 — icon safe areas
- iOS apple-touch icon at 75% logo size (no clipping under the squircle mask).
- PWA manifest now has separate `any` (80%) and `maskable` (55%, inside the Android 80% safe circle) icons.
- Removed the residual outer border from generated icons; validated against iOS squircle and Android circle masks.

## v1.66.6 — QR visibly regenerates
- Mobile access refresh now adds a version parameter to the encoded URL, so the QR image itself changes on every click (previously the same URL produced an identical QR).

## v1.66.5 — visible mobile QR refresh
- Mobile access refresh now reloads the QR image (cache-busted), shows “Updated HH:MM:SS” and a toast, so it is obvious the button works.
- LedgerPlus rebuilt with the same UI translations.

## v1.66.4 — missing translations for mobile/desktop panels
- Added UA/EN/RU strings for Mobile access, App window and Quick start; the refresh button no longer shows the raw `mobile.refresh` key and still regenerates the QR.

## v1.66.3 — single instance and login favicon
- Desktop app is single-instance: a second launch focuses the existing window instead of opening another copy (important when the first is hidden in the tray).
- Login page now declares PNG favicons and apple-touch-icon (Safari does not use SVG favicons, so the tab showed a globe before login).

## v1.66.2 — desktop startup fix
- Fixed `create_window() got an unexpected keyword argument 'win_x'`: width/height are passed at creation, x/y are applied after the GUI starts.

## v1.66.1 — stable icon URLs
- Favicons/PWA icons now use versioned paths (`/app-icon-32-v5.png`, `/app-icon-180-v5.png`, `/app-icon-v5.svg`, `/favicon-v5.ico`) so Safari/Chrome fetch a fresh URL instead of a cached failure.
- Versioned SVG served as `image/svg+xml`.

## v1.66.0 — desktop quick wins and Safari icons
- Safari/favicon aliases (`/favicon-32x32.png`, `/favicon-16x16.png`, `/apple-touch-icon-precomposed.png`, `/apple-touch-icon-180x180.png`) are public and served for the current edition.
- Overview shows a quick-start card when there are no deals (add deal / connect channel / import orders / demo order).
- Compact mode in Settings → Window (denser panels and tables).
- Ctrl/Cmd+K command palette to jump to any tab.
- Window size/position is remembered between launches for both editions.

## v1.65.0 — close to tray for both editions
- Free Ledger now has a tray icon and the same close-to-tray behavior as Ledger+.
- New desktop setting “Close to tray instead of exiting” (Settings → Window), persisted in `desktop.json` next to the exe.
- Closing via X hides the window when the setting is on; full exit is available from the tray menu. If the tray failed to start, closing exits normally.

## v1.64.0 — full-bleed iOS/Android icons
- Apple touch icon and PWA icons are now full-bleed 180/192/512 with the logo scaled up; no transparent corners or empty padding.
- Icon/manifest URLs bumped to `?v=4`.

## v1.63.0 — language and currency are independent
- Changing the interface language no longer resets the display currency (UA + USD is now possible).
- Onboarding language buttons no longer overwrite the chosen currency.
- The currency selector keeps all 29 currencies in Settings; `currency_manual` stays set across language switches.

## v1.62.2 — mobile hint scope
- `GT_BIND` hint is shown only when the dashboard's own origin is localhost.

## v1.62.1 — LAN hint
- Mobile access shows LAN links only when the server is actually bound beyond 127.0.0.1 and explains `GT_BIND=0.0.0.0` otherwise.

## v1.62.0 — mobile access link and QR
- Settings → Mobile access: current public link and LAN links, copy button and a generated QR code.
- `/api/mobile/info` returns origin/LAN URLs and auth state; `/api/mobile/qr?url=...` renders a PNG QR (qrcode + Pillow).
- QR is generated locally, no external service.

## v1.61.0 — green icons everywhere
- Ledger+ badge recolored from blue to the green UI accent across SVG, PNG (32/180/192/512/master) and ICO.
- Rebuilt Ledger and LedgerPlus so the exe, window and tray icons use the new asset.
- Favicon/manifest links cache-busted with `?v=3` and icon cache shortened to 60s.

## v1.60.1 — pricing polish
- Pricing page: separate “Plans” heading (no duplicate), “on request” defaults for empty payment fields.
- Demo screenshots refreshed for v1.60 (13 per language incl. pricing), CI workflow and license unit tests, audit update.

## v1.60.0 — client monitor
- Provisioned clients are checked every 5 minutes; Telegram alerts on down/recovered transitions.
- Hosting page shows down count and a “check all” action.

## v1.59.0 — client backups and public pricing
- Per-client backups to `/root/backups/<id>` (latest 7), daily loop and restore-latest with a safety copy of the current data dir.
- Public `/pricing?lang=uk|en|ru` landing with plans and payment details from settings.

## v1.58.0 — one-click client provisioning
- Provision a real client instance: app copy, data dir, random password, systemd unit, optional Caddy subdomain with validate/rollback, health check.
- Delete stops/removes the unit, Caddy block and optionally data.

## v1.57.0 — hosting clients panel
- `/hosting?token=...` client registry with plan, paid-until, health, days-left and expiring-in-7-days summary.

## v1.56.0 — team seats
- One-time invite links `/join?token=...` with owner/manager/viewer roles; team API and panel in the Ledger+ tab.

## v1.55.0 — Telegram Stars and admin panel
- `/buy` and `/buy team` Stars invoices; successful payment auto-generates a one-device key.
- `/admin?token=...` keys, bindings, revocations and payments.

## v1.54.0 — one key, one instance
- Offline claim keys are bound to a single instance by the license server; second device gets 409; release/transfer and admin revoke.

## v1.53.0 — Ledger+ licenses
- Ed25519 license keys (`LDG.`/`TRIAL.`), activation page, plans ($7 Solo, $29 Team, $29 setup), auto-add gated to Ledger+.

## v1.52.0 — automation, vault, restock
- Auto-add priced orders to P&L/Eldorado (toggle), encrypted account vault with masked credentials, restock suggestions.
## v1.51.4 — polish pass

- Action log no longer shows raw `id=… title=… cost=…`: labels are localized and prices are formatted.
- Percentages, chart axes and thousands separators follow the selected locale (comma in UK/RU).
- Channels month total now uses the same conversion as Overview (no cent drift).
- Catalog empty state is shown once instead of four times.
- Theme picker shows the new split mark instead of the old letter L.
- Supplier status shows hours/days instead of “1659 min ago”.
- Inventory form fits on one row in RU; RU filter no longer wraps alone.
- Desktop launcher supports `GT_DESKTOP_MODE=local` for portable/offline launch without attaching to a running 8766.
- Release ZIP now contains only runtime files (no tests, Docker files or internal audit report).

## v1.51.3 — currency, RU and polish

- Currency is now consistent everywhere: overview, P&L totals, analytics cards/charts/table, inventory, balances and report use the selected currency and its own rate; USD no longer multiplies by the UAH rate.
- Catalog and Plan no longer can stay on “loading” forever: the supplier request aborts the previous one and always renders a result.
- RU localization closed: 294 missing TR_RU entries (server/token labels, status texts, toasts), plus demo orders, 2FA, diagnostics and update-check are localized for EN/RU.
- Demo order body is generated in the current UI language instead of always Ukrainian.
- Money formatting adds thousands separators; long stat values no longer wrap the sign onto a second line.
- exe now carries a Windows version resource (FileVersion 1.51.3.0, ProductName Ledger).
- Screenshots refreshed for all 3 languages (10 screens + appearance block).

## v1.51.2 — audit fixes

- Currency: no more repeated conversion for $-symbol currencies (C$ / A$ / NZ$ …); text stays stable instead of C$ → CC$ → CCC$.
- Security: a public bind without a password now refuses to expose the dashboard and listens on 127.0.0.1 only; GT_ALLOW_OPEN=1 overrides for a trusted LAN. Docker publishes on 127.0.0.1 by default.
- Branding: legacy /favicon.ico, /favicon-32.png, /apple-touch-icon.png, /icon-192.png, /icon-512.png, /icon.svg and /ledger.svg now serve the new mark; the desktop window icon uses ledger-plus.ico; ICO files contain 16–256 px frames; unreferenced AcctTrack/old-icon assets removed.
- Ledger+: the header uses the plain mark and a text “+”, so the icon badge and the wordmark no longer show two pluses.
- i18n: 2FA panel, diagnostics block and update-check are translated to EN/RU; inventory cost labels say USD instead of $.
- Analytics: chart legend, axis, tooltips and the platform table use the selected currency and symbol.
- Tests: verify_auth and api_smoke updated for the Ledger brand and 1.51.2.

## v1.51.1 — readable Ledger+ badge

- The green dot was the plus badge: its arms were too thin and disappeared at 32–53 px.
- It is now a larger badge with a bold plus, in the app accent gradient (indigo → cyan).
- The “+” next to the wordmark is now a plain accent character that follows the theme, so it does not duplicate the badge inside the icon.

## v1.51.0 — new mark and cleaner header

- New monochrome mark: a metal tile split by a diagonal blade (no letter, no gold, no LoL resemblance).
- Ledger+ uses the same mark with a green plus badge.
- The mark is larger in the header (50 px instead of 36 px) and the wordmark is bigger.
- Font size controls moved out of every page header into Settings → Interface theme → Font size (with a reset button).
- New favicon, PWA icons, tray icon and exe icon built from the same geometry.

## v1.50.0 — full free-version audit

- Audited the free Ledger UI end to end: 201 visible controls clicked, all links checked, downloads verified.
- Fixed the “Вставити cookie” button on the mail page: the inline handler had a broken quote and threw “Invalid or unexpected token”.
- 2FA setup is disabled with a hint when no login password is set (instead of returning 400).
- Encrypted backup export now works out of the box: the cryptography package is bundled into the desktop build; export/import round-trip verified.
- Verified imports: P&L CSV, Eldorado CSV, payout CSV, generic CSV, ZIP backup and encrypted .enc backup — all add or restore records.
- Verified destructive actions: clear deals, clear mail queue, disconnect cookies, erase data.
- Release notes and audit report updated with the exact results.

## v1.49.1 — working demo link and honest token checks

- “Screenshots” button in the desktop app no longer opens a 404: the docs are bundled into the exe, and a missing demo page falls back to the GitHub gallery.
- Demo gallery images now match the v1.49 screenshot names (9/9 load, 0 broken).
- New “Check tokens” button performs a real FunPay / ZeusX / Gmail check and shows **active / expired / not set / check failed** instead of a green tick for a non-empty cookie.
- The diagnostics line no longer claims tokens are valid just because a value is stored.

## v1.49.0 — language, currency and desktop pass

- Language switching reloads the page, so no UA/EN/RU text is left over from the previous language.
- Replaced word-by-word translation (which produced “because of”, “with папки”, “Done к установке”) with exact string translation plus numeric patterns.
- Currency now follows the interface language: Ukrainian → ₴, English → $, Russian → ₽.
- The exchange-rate cache is stored per currency, so balances are no longer converted with the previous currency's rate.
- Fixed Russian plurals (“записей”), Sell-through / Hold / Payout CSV labels and the raw “keys=…” line in the audit log.
- Header no longer shows the stale “v5” next to the real version.
- New gold L monogram for Ledger and L+ badge for Ledger+; sharper 32–512 px icons and SVG.
- Ledger.exe attaches to a running local server or a remote one; LedgerPlus.exe connects to the hosted account without a login form (Basic auth proxy) and keeps the tray/notifications.
- README: Ledger vs Ledger+, desktop apps, current screenshots in Ukrainian, English and Russian.
- MIT copyright line now says “Ledger contributors”.

## v1.48.0 — icon content-type fix

- Fixed `/app-icon-*.png` UnboundLocalError when the icon exists.
- Rebuilt public desktop app.

## v1.47.0 — larger logo

- L mark fills more of the icon tile.
- Header mark 30px instead of 22px.
- Ledger+ plus badge larger and high-contrast.

## v1.46.0 — chosen Ledger mark

- Base Ledger icon: L monogram (variant 1).
- Ledger+ icon: same L with green plus badge.
- Updated header, favicon, PWA icons, desktop EXE and tray.

## v1.45.0 — Ledger and Ledger+ apps

- `Ledger.exe` — public app, no paid automation.
- `LedgerPlus.exe` — automation edition with Ledger+ badge.
- Both are native WebView2 apps with embedded server.

## v1.44.0 — one brand: Ledger and Ledger+

- Public product renamed to **Ledger** everywhere.
- Paid/automation instance shows **Ledger+** badge and window title.
- GitHub repository renamed to `ledger`; old links redirect.
- Desktop app rebuilt as Ledger+.

## v1.43.0 — desktop application

- Native Windows app `Ledger.exe` (WebView2 + embedded Python server).
- No browser tab and no PWA installation; data stored next to the exe.
- Fluid full-width layout.

## v1.42.0 — fluid layout

- Removed fixed 1560px content width; UI fills the window.
- Uses dynamic viewport height; no horizontal overflow.
- PWA window still uses browser-controlled size, but content adapts to any window.

## v1.41.0 — closable install dialog

- Fixed modal close: global close handler, backdrop click and Escape.
- Copy-link and download-shortcut handlers exposed globally for inline buttons.

## v1.40.0 — Opera install help

- Opera detected: install button opens a clear help dialog instead of a silent no-op.
- Fallback offers link copy and a Windows `.url` shortcut.
- PWA icons made public; early install prompt capture.

## v1.39.0 — reliable PWA prompt

- Early `beforeinstallprompt` capture in the page head.
- Install button uses the captured prompt even if it fired before app scripts.
- Public app icons so the manifest passes installability checks.

## v1.38.0 — working install button

- Install button explains the HTTPS requirement and opens the secure URL on HTTP.
- Added valid HTTPS endpoint `ledger.70-34-243-50.sslip.io`.
- PWA status shows installability and HTTPS hint.

## v1.37.0 — updated screenshots and demo fix

- `/demo?lang=...` is public and no longer returns 404 behind auth.
- Screenshots refreshed for all main screens in UA/EN/RU.
- Demo gallery adds Orders, Taobao and Backups/settings.
- `docs/` is included in release builds.

## v1.36.0 — more reply variants

- Ten reply variants per language.
- Removed platform names from replies and the generator hint.
- Regenerate cycles through different wording.

## v1.35.0 — reply generator

- Orders tab: three-language reply generator based on the order.
- Three rotating variants per language; copy button; regenerate without reload.
- Generated text is excluded from the global UI translator.

## v1.34.0 — update and backup translations

- Update panel, P&L backup and cloud backup fully localized UA/EN/RU.
- Removed English buttons (`Check`, `Run now`, `Restore-test`, `Save`) from translated UI.
- Auto-backup status follows the selected language.

## v1.33.1 — launcher paths

- Agent setup path updated to `launchers/install_taobao_agent.bat`.
- Launcher folder documented.

## v1.33.0 — organized repo

- Icons moved to `assets/`.
- Optional launchers moved to `launchers/`; root `start.bat` remains.
- Release and repository root no longer filled with icon and batch files.

## v1.32.0 — free/paid Taobao, form labels, console language

- Free Taobao page hides automation controls, data list and agent setup; paid keeps them.
- Marketplace calculator and deal form labels localized; amount labels no longer say $ when a deal currency is chosen.
- Console startup/status text follows the selected UI language (uk/en/ru).

## v1.31.0 — free/paid Taobao split and form labels

- Free Taobao page hides automation buttons, filters, data list and agent setup; paid keeps them.
- Marketplace table headers, names and notes localized UA/EN/RU.
- Deal form labels localized; removed misleading $ from amount labels; added currency/rate hint.

## v1.30.0 — human Taobao copy

- Rewritten Taobao hero and benefit copy in UA/EN/RU.
- Demo lot labels and badges localized.
- Demo stays in USD and is excluded from display conversion.

## v1.29.0 — demo currency and brand polish

- Taobao demo lots stay in USD and are excluded from the display-currency converter.
- Demo heading and note translated UA/EN/RU.
- Dynamic A/L icon and manifest; alert state clears when Orders opens.

## v1.28.0 — brand icons

- Dynamic app icon: L monogram for Ledger, L+ badge for Ledger+.
- Manifest, favicon, Apple touch icon and PWA icons use the active brand.
- Windows shortcut icon updated to the A mark.

## v1.27.0 — localization and alert cleanup

- Three-language labels for cashflow, import, supplier ROI, report, order banner and buttons.
- Dynamic tables re-render on language change.
- Opening Orders clears the alert banner and favicon/title animation.

## v1.26.0 — animated tab and custom app name

- All favicon links switch to the pulsing alert icon (32/svg/192).
- Tab title alternates `(N) 🔔 name`.
- Notification title uses configured app name; live instance set to Ledger.

## v1.25.0 — louder alert and animated tab

- Three-tone louder order sound with AudioContext resume.
- Animated favicon (pulsing green/amber ring) and alternating 🔔 title.
- Banner remains visible until Orders opened.

## v1.24.0 — visible order alert

- New-order banner with "Open" button; cannot be missed.
- Browser notification shows even when the tab is visible.
- Sound test button; demo plays a sound immediately on click.

## v1.23.0 — demo order

- Test order button in Orders; creates a clearly labelled demo order and triggers the new-order alert.
- Endpoint `/api/mail/demo` for testing notification flow.

## v1.22.0 — background order notifications

- Browser notification on new order when the tab is in background.
- Two-tone sound alert with a toggle.
- Enable-notifications button in Orders; permission status.

## v1.21.0 — unified totals and new-order alert

- P&L cards now show P&L + Eldorado combined; separate Eldorado row removed.
- New orders animate the header mark, show a favicon badge and title count.
- Mail queue auto-refreshes every 45 seconds.

## v1.20.0 — DPAPI backup password

- On Windows, the backup encryption password is protected with user DPAPI instead of plaintext.
- Existing backups and verification/restore use the protected secret transparently.
- Settings shows DPAPI protection status.

## v1.19.0 — restore test

- Encrypted backup is restored into a temp folder and parsed after creation.
- Status shows restore-test result and P&L count.
- Restore-test button in backup settings.

## v1.18.0 — backup integrity verification

- Encrypted backup is verified (manifest + sha256) immediately after creation.
- Settings shows last verification status and a "Verify" button.
- Verification endpoint checks the latest encrypted backup.

## v1.17.0 — backup restore preview

- Backup import validates the zip/encrypted archive before writing.
- Shows manifest created date, file count and P&L/Eldorado counts.
- Restore requires explicit confirmation after preview.

## v1.16.0 — encrypted automatic backups

- Optional AES-GCM encrypted backup on each scheduled run.
- Password stored in `.gt_secrets.json` (or `GT_BACKUP_PASSWORD`); never returned by API.
- Encrypted `.ledger.enc` files are copied to the cloud folder and pruned with retention.

## v1.15.0 — scheduled cloud backups

- Configurable backup interval (hours) and retention count.
- Automatic backup loop checks the schedule every 5 minutes.
- Settings shows last backup time/status and a "Backup now" button.
- Google Drive for desktop: set its folder as the cloud backup path.

## v1.14.0 — tax and cashflow in report

- Configurable tax rate in the monthly report.
- PDF shows cashflow hold/available/withdrawn, net profit tax base and estimated tax.
- Report loads automatically when Analytics opens.

## v1.13.0 — payout rules

- Configurable payout hold days per platform (G2G, Gameflip, PlayerAuctions, ZeusX, FunPay, Eldorado, other).
- New Hold gets an automatic Available date from the sale date + platform rule.
- Manual available date still overrides the rule.

## v1.12.0 — payout reconciliation

- Payout CSV matches open Hold/Available entries by order, then by platform + amount.
- Matched entries are marked withdrawn instead of creating duplicates.
- Unmatched payout rows are added as withdrawn.

## v1.11.0 — payout automation

- Cashflow entries support an available date; Hold auto-promotes to Available when the date arrives.
- Payout CSV import into cashflow.
- Cashflow table shows the available date.

## v1.10.0 — auto cashflow and PDF line items

- Imported sales create a linked cashflow Hold (saleId/order dedupe).
- Cashflow entries store saleId/order; repeated imports do not duplicate holds.
- PDF monthly report includes the deal list with date, title, platform, sale, fee, cost and profit.

## v1.9.1 — automatic cost matching on import

- CSV preview matches rows to in-stock inventory by title.
- Matched cost is used for profit; matched stock is marked sold after import.
- Unmatched rows are flagged with needsCost.

## v1.9.0 — sales import, cashflow, one-click targets

- CSV import for G2G/Gameflip/PlayerAuctions with preview and duplicate order filtering.
- Cashflow ledger: hold / available / withdrawn with totals and status controls.
- One-click target price from catalog rows.

## v1.8.0 — PDF report and marketplace fees

- Monthly report PDF via print dialog (no extra dependency).
- Gameflip added to marketplace fee calculator; G2G/PlayerAuctions fees wired into defaults.

## v1.7.0 — supplier ROI and agent setup

- Supplier ROI table: items, sold, cost, revenue, profit, ROI, sell-through, days.
- Taobao agent setup panel with server + token copy.
- One-click Windows installer `install_taobao_agent.bat` (Python check, Playwright, Chromium, config).

## v1.6.0 — PWA install and target prices

- Install Ledger as an app from Settings (Chrome/Android prompt, iOS instructions).
- Target prices: game/lot name + max USD, checked against supplier cache.
- Daily Telegram alert when a target is reached; enable Price-drop notifications.
- Paid Ledger hides the Taobao sales page; free release keeps it.

## v1.5.2 — Taobao sales page

- Taobao tab redesigned as an automation showcase.
- Benefit cards, demo lots with margin, CTA and collapsible technical setup.
- Demo preview labelled clearly; real lots appear after agent connection.

## v1.5.1 — order-to-draft

- Orders from mail have a "Draft" button.
- Draft pre-fills platform, title, price and matching stock cost.
- Saving the draft removes the order from the mail queue and marks linked stock sold.

## v1.5.0 — deal currency and stock aging

- Each deal now has its own currency and historical USD rate.
- Amounts are entered in the deal currency; storage/reporting normalize to USD.
- Deal rows show the original currency and amount.
- Inventory aging buckets: 7/30/60/90 days, frozen value, sell-through and average days to sell.
- Sold inventory records `sold_at`.

## v1.4.7 — currency hints

- Onboarding says both language and currency can be changed later.
- Settings explains that manual currency choice is not overridden by language.

## v1.4.6 — automatic exchange-rate refresh

- Selected-currency rate refreshes every 6 hours in the background.
- Stale rate is refreshed automatically on page load.
- Settings explains the 6-hour schedule and the manual refresh button.
- Manual currency choice is preserved when the UI language changes.

## v1.4.5 — currency follows language

- Switching UI language maps UA→UAH, EN→USD, RU→RUB when currency was not manually chosen.
- Manual currency selection now persists via `currency_manual` and is not overridden.
- Live backend now stores and returns currency.

## v1.4.4 — readable schedule settings

- Each schedule field now explains what it controls and what a safe value means.
- Added recommended defaults and units.
- Translated UA/EN/RU.

## v1.4.3 — audit log localization

- Action log headers, event names and empty state now follow UA/EN/RU.
- Switching language re-renders the audit table immediately.
- Added translations for login, logout-all and 2FA recovery events.

## v1.4.2 — onboarding language picks currency

- Ukrainian → UAH, English → USD, Russian → RUB.
- Manual currency choice wins over later language clicks.

## v1.4.1 — currency applied to displayed amounts

### Fixed
- Selecting a currency now converts displayed amounts across the dashboard, deals, analytics, inventory and channels.
- Currency switch reloads the page, so values are not double-converted.
- Form inputs remain in USD; a note explains that display is in the selected currency.

## v1.4.0 — recovery, devices, updates, encryption

### Added
- 2FA recovery codes (one-time, hashed at rest).
- Logout from all devices (device token version bump).
- In-app update checker against the latest GitHub release.
- Password-encrypted backup export (.ledger.enc, AES-GCM + PBKDF2).
- Encrypted backup import with password.
- Currency selection on the first onboarding screen with 29 popular currencies.
- Currency changes are applied everywhere and can be changed later in Settings.

### Changed
- Exchange-rate fallback: Frankfurter, then open.er-api; NBU for UAH.

## v1.3.2 — Ledger icon and PWA branding

### Changed
- New **Ledger** icon: white L, green ledger lines and underline.
- Manifest name: **Ledger — Game Account Tracker**, short name **Ledger**.
- New cache-busted icon URLs: `ledger-192.png`, `ledger-512.png`, `ledger.svg`, `ledger-touch.png`.
- Browser title and iOS app title: **Ledger**.
- PWA notifications use the Ledger icon.

### Note
- Android/iPhone cache the home-screen icon. Remove the old shortcut and add the site again to see the new icon.

## v1.3.1 — mobile view

### Added
- Mobile bottom navigation: Overview, Deals, Orders, Inventory, Analytics.
- Sticky horizontal tab strip on phones; active tab stays in sync.
- Touch-friendly controls: 40–42 px inputs and buttons, 36 px row actions.
- Responsive forms, fee/discount panels and tables.
- Safe-area padding for iPhone/Android.

### Fixed
- Mobile tables no longer force the whole page wider than the screen.

## v1.3.0 — audit log, 2FA, dead-stock alerts

### Added
- **Action log**: last 500 changes to deals, Eldorado, stock, settings and 2FA, visible in Settings.
- **Two-factor login (TOTP)**: 6-digit code from Google Authenticator / Aegis / 1Password.
- 2FA setup, enable and disable in Settings; Basic auth cannot bypass it.
- **Dead-stock alert**: Telegram notification for in-stock items older than 30 days, with 60/90-day counts and frozen value.
- New Telegram switch: "Мертвий склад (30+ днів)".

## v1.2.0 — platform profitability

### Added
- Analytics now shows **profit by platform**: deals, revenue, fees, expenses, net profit and net %.
- Platform totals respect the current platform and period filter.
- Eldorado is included from its own ledger.

### Fixed
- Analytics, game table and month-over-month comparison now use **net profit** (after other expenses), not after-fee profit.
- Summary totals no longer overstate profit when a deal has other expenses.

## v1.1.2 — bulk commission

### Added
- **Bulk commission**: apply one percentage to every deal in the current filter.
- Works for both P&L deals and Eldorado sales.
- Recalculates fee, after-fee and net profit; other expenses are untouched.
- Confirmation shows the percentage and the number of deals.

## v1.1.1 — default fee profiles

### Added
- Settings → **Default marketplace fees**: FunPay, Eldorado, Other.
- **Game overrides**: one line per game, e.g. "GTA 5 | eldorado | 30".
- New deals use the saved profile automatically; a title match applies the game override.
- Custom commission still overrides the profile for a specific deal.
- Profiles are saved in settings and survive restart.

## v1.1.0 — stock-linked sales and net profit

### Added
- **Sell from stock**: the 💰 button on an inventory item opens the deal form with the title and cost pre-filled.
- After saving the deal, the inventory item is marked **sold** automatically.
- **Other expenses** field on every deal: withdrawals, refunds, promotion, intermediaries.
- **Net profit** = after-fee profit minus other expenses.
- A separate **Expenses** summary card and per-deal expense row.
- Expenses are included in analytics, monthly report, CSV and Excel exports.

### Fixed
- Totals, margin, report and exports no longer stop at the marketplace fee; they show the real net result.

## v1.0.4 — persisted ZeusX tier

### Fixed
- The selected ZeusX seller tier is now saved and restored after a page refresh.
- It is stored in `gt_settings.json` as `zeusx_tier` and mirrored in localStorage for instant restore.
- Gold, Silver, Platinum and Vibranium no longer fall back to Iron 10% after reload.
- The custom fee field still overrides the tier preset for a specific deal.

## v1.0.3 — exact ZeusX tier table

### Changed
- ZeusX tiers are now the official six-step table: Iron 10%, Bronze 9%, Silver 8%, Gold 7%, Platinum 6%, Vibranium 5%.
- Tier criteria are shown in the selector: $300 / $1,000 / $10,000 / $100,000 / invitation.
- ZeusX withdrawal cost is reflected as 1.5% + $3 in the marketplace comparison note; the sales fee remains 5–10% by tier.
- The old approximate "Diamond" tier was removed; the correct top tier is **Vibranium**.

## v1.0.2 — real marketplace fees and ZeusX tiers

### Added
- **Real defaults**: FunPay 10% (section-dependent), ZeusX 10% on the starting Iron tier, Eldorado 10% for accounts.
- **ZeusX seller tier selector**: Iron 10%, Bronze 9%, Silver 8%, Gold 7%, Platinum 6%, Diamond 5%.
- The exact ZeusX rate can differ by account; the tier preset is only a starting point, and the custom fee field still overrides it.
- Per-deal `feePct` and custom "Other" fees remain from v1.0.1.

### Changed
- Plan/calculator hints now say ZeusX is 5–10% by tier, not a fixed 9.5%.
- Market comparison notes explain that FunPay depends on the section and ZeusX depends on the seller tier.

### Fixed
- Existing records keep their historical fee; only new records use the updated defaults.

## v1.0.1 — custom marketplace fees

### Added
- **Per-deal commission**: every P&L record stores its own fee percentage, so historical deals keep the rate they were entered with.
- **Editable fee in the add form**: changing the marketplace pre-fills its default, but the user can override it before saving.
- **Editable fee when editing a deal**: existing deals can be corrected without deleting and re-adding them.
- **Custom "Other" fee**: any percentage from 0% to 100% for non-standard marketplaces.
- **CSV import**: optional `fee` / `feePct` / `afterFee` columns are recognised; `9.5` and `9.5%` are both accepted.
- Defaults still come from `PLATFORM_FEES`, but they are no longer hard-coded into reports or totals.

### Fixed
- Marketplace fees are now read from the record instead of the global default, so changing a default no longer rewrites history.
- Old records without `feePct` recover their rate from `afterFee` on save.
- P&L totals, monthly report, analytics, CSV/Excel exports, and row cards all use the per-record fee.

## v1.0.0 — first public release

First stable public release of Ledger: manual bookkeeping by default, tokens optional.

### Added
- **Deals / P&L**: buy and sell prices, marketplace fee, net profit, filters, search, bulk rename, CSV and Excel export.
- **Inventory**: purchased accounts, statuses (in stock / sold / written off), account data, dead-stock warning, CSV.
- **Channels**: Eldorado manual ledger, FunPay (`golden_key`), ZeusX (`access_token`), fee comparison and balances.
- **Orders from mail**: Gmail IMAP → queue → one-click P&L or Eldorado entry.
- **Analytics**: monthly profit, top games, margin, 30-day chart, month-over-month comparison, monthly report and CSV.
- **Catalog**: Shopify `products.json`, price history, cheaper-elsewhere comparison, lot calculator.
- **Buy plan**: supplier price vs. the median of your own sales.
- **Backups**: snapshots before writes, ZIP export/import, optional cloud copy, restore for all supported snapshot types.
- **Diagnostics**: version, uptime, record counts, file sizes, token status.
- **Demo data**: 20 deals + 4 inventory items with one click.
- **Onboarding**: language → name/theme → optional channel tokens.
- **3 languages** (Ukrainian, English, Russian), **5 themes**.
- **Docker** and Windows launcher.
- **Admin login** with optional password, CSRF protection, HTTPS certificate fields.
- **English README** with installation, configuration, and troubleshooting.

### Fixed in this release
- Monthly report no longer counts the purchase cost as a marketplace fee or subtracts it twice.
- All Settings actions work: diagnostics, demo load/clear, CSV import, supplier add, password enable/disable.
- Password status and validation are consistent (minimum 8 characters).
- CSRF token is refreshed after a password change or restart.
- Cookies and Telegram/Gmail credentials can be disconnected.
- Backup types are labeled correctly and restore works for settings, P&L, Eldorado, mail, and inventory snapshots.
- Catalog no longer shows "no suppliers" when cached products exist; sale discount no longer renders as `undefined`.
- Deal/Eldorado deletion asks for confirmation; editing a deal no longer duplicates the channel icon.
- Full English/Russian localization for dynamic UI, toasts, dialogs, reports, and CSV/Excel exports.
- Mobile layout for Channels, Taobao status, and navigation.

### Known limitations
- FunPay/ZeusX/Gmail/Telegram require your own credentials and were validated without live tokens.
- Eldorado has no public API; use manual entry or mail.
- Taobao live collection needs the optional Playwright collector and may be blocked by Taobao.
- Chart.js and SheetJS are loaded from cdnjs for charts and Excel export.

### License
MIT.
