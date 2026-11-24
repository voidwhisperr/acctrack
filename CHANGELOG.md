# Changelog

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
