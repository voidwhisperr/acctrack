# Deploying to a VPS

## Safe deploy (recommended)

Use `scripts/deploy_vps.ps1`. It:

1. backs up `game_tracker.py` and `ui.py` to `/root/gt_versions/<timestamp>`;
2. uploads each file to a temp directory and verifies SHA-256 before replacing anything;
3. runs `python3 -m py_compile` on the server;
4. restarts the service only if compilation succeeds;
5. checks `/api/health`;
6. rolls back automatically if compile or health fails.

```powershell
$env:LEDGER_SSH_KEY = 'C:\Users\...\id_ed25519'
$env:LEDGER_SSH_KNOWN_HOSTS = 'C:\Users\...\known_hosts'
powershell -ExecutionPolicy Bypass -File scripts\deploy_vps.ps1
```

## Why the old way is dangerous

On 2026-11-25 a plain `scp` of `ui.py` was truncated by a connection reset. The service was
restarted anyway, `api/health` still returned 200 (it does not import the UI), but every
authenticated page showed:

> UI недоступний — Не знайдено модуль ui.py

Always verify the **authenticated dashboard**, not only the health endpoint:

```bash
PW=$(python3 -c "import json;print(json.load(open('/root/.gt_secrets.json'))['auth_pass'])")
curl -s -u admin:$PW -o /tmp/ui.html -w '%{http_code} %{size_download}\n' http://127.0.0.1:8766/
grep -c 'UI недоступний' /tmp/ui.html   # must print 0
```

## Rollback

```bash
ls -1 /root/gt_versions | tail -3
cp -a /root/gt_versions/<timestamp>/game_tracker.py /root/gt_versions/<timestamp>/ui.py /root/
systemctl restart gametracker
```
