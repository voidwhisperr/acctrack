# Встановлення

## Windows (ПК)

1. Python 3.11+ → https://python.org (галочка «Add to PATH»).
2. Покладіть папку з застосунком, наприклад `C:\AccTrack`.
3. Запустіть `run.bat` (або `python game_tracker.py`).
4. Відкрийте http://127.0.0.1:8766, задайте пароль при першому вході.
5. Автозапуск: Win+R → `shell:startup` → покладіть туди ярлик на `run.bat`.

**Важливо:** на ПК застосунок працює, лише коли компʼютер увімкнений.

## VPS (24/7)

Ubuntu 22.04+, 1 vCPU / 1 GB.

```bash
sudo apt update && sudo apt install -y python3 python3-venv caddy
sudo mkdir -p /opt/acctrack && sudo chown $USER /opt/acctrack
# скопіюйте файли в /opt/acctrack

sudo tee /etc/systemd/system/acctrack.service >/dev/null <<'EOF'
[Unit]
Description=AccTrack
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/acctrack
ExecStart=/usr/bin/python3 /opt/acctrack/game_tracker.py
Environment=GT_BIND=127.0.0.1
Environment=GT_PORT=8766
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload && sudo systemctl enable --now acctrack
```

Caddy (TLS автоматично):

```
your-domain.example {
    reverse_proxy 127.0.0.1:8766
}
```

## Токени каналів

**FunPay:** F12 → Application → Cookies → `https://funpay.com` → скопіюйте `golden_key`.
**ZeusX:** F12 → Network → будь-який запит до `api.zeusx.com` → Request Headers → `Authorization: Bearer <token>`.
**Eldorado:** публічного API немає — облік вручну або через листи пошти.
