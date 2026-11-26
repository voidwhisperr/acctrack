# Ledger infrastructure (VPS)

Host: `70.34.243.50` (Vultr), domain `ledger.70-34-243-50.sslip.io`.

## Topology

- Caddy :443 (Let's Encrypt) -> 127.0.0.1:8766 (Ledger app, bound to localhost).
- Caddy :8765 (`tls internal`) -> 127.0.0.1:8766: legacy Taobao collector endpoint.
- UFW allows 22, 80, 443, 8765. Port 80 packets are dropped upstream by the Vultr firewall, so the HTTP->HTTPS 308 redirect exists in Caddy but is unreachable from the internet.

## Hardening done (v1.66.18)

- `8765` restricted by UFW to the collector source IP `46.33.230.57`; the public allow rule was removed.
- Caddy access logging disabled for the `:8765` site and the old log truncated (it contained `X-Gt-Token` headers).
- App login rate limiting/logging uses `X-Forwarded-For` from Caddy, so limits are per client IP instead of shared `127.0.0.1`.

## Live paths (v1.66.31)

- Web app: `/opt/ledger` (owner `ledger`, unit `gametracker`, `User=ledger`). Do **not** deploy new code to `/root`; the live service reads `/opt/ledger`.
- License signer: `/opt/ledger-signer/license_signer.py`, key `/etc/ledger-signer/private.b64` (root 600), socket `/run/ledger-signer/signer.sock` (root:ledger 660). The app user cannot read the key.
- Bots: `/opt/ledger-bots` (`User=ledgerbot`).
- Legacy data under `/root` is kept only for rollback/backup.

## Additional hardening (v1.66.30)

- Collector token rotated; old gametracker.log.bak.* files with X-Gt-Token removed. The collector agent uses the new token.
- Public Taobao Flask app bound to 127.0.0.1:5001; UFW 5001 removed. Cloudflared quick tunnel disabled.
- /admin and /hosting use a signed HttpOnly cookie; actions are POST + CSRF. URL tokens only bootstrap the session.
- Backups are encrypted by default (.ledger.enc); a local key is generated on first run.
- Telegram and Discord bots run as the non-root ledgerbot user from /opt/ledger-bots.
- systemd drop-ins add NoNewPrivileges, PrivateTmp, ProtectSystem=full, ProtectHome=read-only, ProtectKernelTunables, ProtectControlGroups, RestrictSUIDSGID.
- Private license key directory is 700; the key is not reachable through the web app.

## Manual steps still required

1. License key separation: the signer service (`license_signer.py`, see `docs/LICENSE-SIGNER.md`) is implemented but not deployed. The Ed25519 private key still lives on the same VPS until the signer runs under its own UID/socket (or on a separate host); automatic key issuance needs that signer.
2. Main app still runs as root. Migrating needs code/data under /opt/ledger and /var/lib/ledger plus User=ledger; bots are already non-root.

1. ~~Open TCP 80 in the Vultr firewall~~ done: port 80 now returns 308 to HTTPS.
2. Rotate the collector token (old value was written to Caddy logs): generate a new `collector_token` in `.gt_secrets.json`, update the agent config, then remove the legacy `:8765` Caddy site entirely once the agent uses `https://ledger.70-34-243-50.sslip.io` (valid TLS).
3. Optional: move the collector to the main domain on 443 so no self-signed endpoint is public.

## Checks

```bash
systemctl status gametracker caddy
curl -s https://ledger.70-34-243-50.sslip.io/api/health
ufw status | grep 8765
curl -sI https://ledger.70-34-243-50.sslip.io/api/health
```

Backups: `/root/gt_backups/archive/` daily tarballs, verify status in Settings; cloud backup is not configured.