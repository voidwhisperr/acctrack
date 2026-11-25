# Changelog

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

- Dynamic app icon: A for AccTrack, L for Ledger.
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

First stable public release of AccTrack: manual bookkeeping by default, tokens optional.

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
