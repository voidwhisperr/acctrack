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

## Manual steps still required

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