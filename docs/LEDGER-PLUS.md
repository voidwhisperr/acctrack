# Ledger+ licenses and sales

## Free vs Ledger+

| Feature | Ledger (free) | Ledger+ |
|---|---|---|
| Deals, P&L, analytics, inventory, vault, backups | yes | yes |
| Local desktop app | yes | yes |
| Hosted instance (always online) | no | yes |
| Taobao agent | no | yes |
| Automatic order -> deal (auto-add) | no | yes |
| Team roles / shared workspace | no | Team plan (planned) |
| Priority support | no | yes |

## Plans

- **Ledger+ Solo** — $7/month (30-day key)
- **Ledger+ Team** — $29/month (30-day key, team feature bit reserved)
- **Done-for-you setup** — $29 one-time (installation, Telegram, channels, Taobao, import, training)
- **Trial** — 14 days, all features; keys are generated in batches for giveaways

## Key format

`LDG.<payload>.<signature>` for paid keys, `TRIAL.<payload>.<signature>` for trials.
Payload is 12 bytes (version, plan, expiry day, feature mask, nonce), signed with Ed25519.
Verification is **offline** — the app only needs the embedded public key; no license server call.

Features bits: `auto_orders`, `taobao`, `hosted`, `team`, `priority`.

## Generate keys (admin only)

Private key lives outside the repo: `~/.ledger-license/private.b64` (created once; never ship it).

```powershell
# 5 paid keys, 30 days
python scripts/make_license.py --plan plus --days 30 --count 5 --out plus_keys.txt
# 20 trial keys, 14 days
python scripts/make_license.py --plan trial --days 14 --count 20 --out trial_keys.txt
# Team plan with team feature
python scripts/make_license.py --plan team --days 30 --features auto_orders,taobao,hosted,team --count 3
```

## Activate

Ledger → **Ledger+** tab → paste key → Activate. The app stores `.gt_license.json` in the data folder.
Deactivate removes it. Status and days left are shown on the same page.

## Sales flow (manual, works today)

1. Client pays (USDT / Binance Pay / Payoneer / Telegram Stars / platform balance).
2. You generate a key with `make_license.py` (or use a pre-generated batch).
3. Send the key + short activation instructions.
4. For setup service: connect channels/Telegram/Taobao remotely, import data, 60-minute call.

Payment details shown in the Ledger+ tab are stored in that instance's settings (`pay_usdt`, `pay_binance`, `pay_payoneer`, `pay_tg`).
Fill them on your own instance before sending screenshots to clients.

## Limits of offline keys

- A key cannot be revoked offline and can technically be shared. Acceptable for early access.
- Later: online activation + instance binding + revocation list when the hosted flow is ready.
- Do not put the private key on client machines or in the repo.


---

## One key = one instance (v1.54+)

Paid and trial keys are now **bound to a single installation**:

1. Client opens Ledger → Ledger+ tab → pastes the key.
2. The app sends `{key, instance_id}` to the license server (`GT_LICENSE_SERVER`, default the hosted Ledger+ URL).
3. Server checks the key signature, revocation and existing binding, stores `key_hash -> instance`, and returns a **bound** signed license (payload v2 contains the instance hash).
4. The app stores that bound license; the same key on another device is rejected with `409 key is already activated on another device`.
5. Deactivate releases the binding on the server, after which the key can be moved to another device.

Server side:

- `license_server_mode: true` in settings (or `GT_LICENSE_SERVER_MODE=1`) makes this instance the licensing server.
- Private signing key: `~/.ledger-license/private.b64` (or `LEDGER_LICENSE_PRIVATE_FILE`); **never ship it**.
- Registry: `.gt_license_registry.json` in the server data dir.
- Admin token lives in `.gt_secrets.json` as `license_admin_token`.

Admin API:

```bash
TOKEN=<license_admin_token>
curl -s -X POST https://<host>/api/license/admin/list -H "X-Admin-Token: $TOKEN" -H "Content-Type: application/json" -d '{}'
curl -s -X POST https://<host>/api/license/admin/revoke -H "X-Admin-Token: $TOKEN" -H "Content-Type: application/json" -d '{"key_id":"..."}'
```

Local test without the VPS:

```powershell
$env:GT_LICENSE_SERVER_MODE='1'   # this server signs licenses
$env:GT_DATA_DIR='C:\temp\lic'
python game_tracker.py
# in another instance:
$env:GT_LICENSE_SERVER='http://127.0.0.1:8766'
```

Offline key tokens (`LDG.` / `TRIAL.`) are only **claim codes** now; the app accepts the bound token returned by the server. Old unbound tokens stop working for paid features until activated online.


---

## Telegram Stars checkout

The bot accepts `/buy` (Solo) and `/buy team` (Team). It sends an XTR invoice; after a successful payment it generates a one-device claim key, records the payment in `.gt_payments.json` and sends the key to the buyer.

Prices (Stars): `stars_solo` default 500, `stars_team` default 1500. Override in `.gt_settings.json`.

## Admin panel

Open `/admin?token=<license_admin_token>` on the license server.

- keys: plan, expiry, state (free/bound/revoked), instance, revoke link
- payments: time, platform, plan, amount, key prefix
- total keys/bound/revoked and revenue by currency

The panel and the license register/release endpoints are public (no dashboard password) but protected by the key signature or the admin token. Admin API also works with `X-Admin-Token`.

## Team roles

Team plan entitlement is reserved; multi-user roles (owner/manager/viewer) are the next step and currently not enforced.
