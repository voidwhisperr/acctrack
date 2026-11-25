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
