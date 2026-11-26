# License signer (isolated Ed25519 signing)

Status: implemented in `license_signer.py`; not deployed to the VPS yet.
The hosted web app can issue and bind licenses without holding the Ed25519
private key. The key lives with a small local signing service instead.

## Why

`game_tracker.py` used to read the Ed25519 private key itself
(`~/.ledger-license/private.b64`) and sign license payloads in the web
process. Anyone who could read the app account or its backups could mint
licenses. The app now needs only the public key (`license.PUBLIC_KEY_B64`):
signing is delegated over a Unix socket to a separate service that owns the
private key.

```
  Ledger web app (user ledger)          license signer (user ledger-signer)
  ─────────────────────────────         ──────────────────────────────────
  license.PUBLIC_KEY_B64                /etc/ledger-signer/private.b64  (0600)
        │                                        │
        └── AF_UNIX /run/ledger-signer/signer.sock ──> Ed25519 sign()
                 newline-delimited JSON                 │
                 {"payload_b64": "..."} <──────────────┘
                                       {"sig_b64": "..."}
```

Putting the signer on a different host (forwarding the socket) is the next
step; same-host UID separation is the first step and already removes the key
from the web app process, its backups and its data directory.

## Files and environment

| Item | Default | Meaning |
|---|---|---|
| `LEDGER_LICENSE_PRIVATE_FILE` | `/etc/ledger-signer/private.b64` | base64 of the 32-byte Ed25519 seed; mode 600, owner-only |
| `LEDGER_SIGNER_SOCKET` | `/run/ledger-signer/signer.sock` | Unix socket the service listens on and the app connects to |
| app env `LEDGER_SIGNER_SOCKET` | empty | explicitly select the signer; **no local fallback** if set (fail closed) |
| app env `LEDGER_SIGNER_AUTO` | enabled | `0` disables auto-detection of the default socket |
| app env `LEDGER_LICENSE_PRIVATE_FILE` | `~/.ledger-license/private.b64` | desktop/offline local-key fallback only |

The app chooses the remote signer when `LEDGER_SIGNER_SOCKET` is set, or, on
POSIX, when `/run/ledger-signer/signer.sock` exists and `LEDGER_SIGNER_AUTO`
is not `0`. Desktop/offline builds (Windows, no socket) keep the old local-key
path. An explicitly configured socket is never silently bypassed: if the
signer is down, signing fails instead of falling back to a local key.

## Protocol

Newline-delimited JSON over a stream socket. One request per line; several
requests may share one connection.

Request:

```json
{"payload_b64": "AQEHICAAAAAAAAAAAAA="}
```

Response on success (64-byte Ed25519 signature, base64):

```json
{"sig_b64": "..."}
```

Response on rejection:

```json
{"error": "payload too long (limit 4096 bytes)"}
```

### What the signer accepts

1. **The existing binary Ledger payload** (`license.py`), signed byte-for-byte
   so `license.make_code` / `license.verify` keep working:
   - v1 claim payload: 12 bytes `>BBHI` + 4-byte nonce (`version=1`);
   - v2 instance-bound payload: 20 bytes `>BBHII` + 8-byte instance hash
     (`version=2`).
   Validation: known version, plan id (1 plus, 2 team, 3 trial), feature mask
   limited to the five known bits, expiry not in the past and at most 3650
   days ahead. The signer clock must be correct (NTP).
2. **A JSON claim object**, for tooling/tests:

```json
{"plan": "solo", "days": 30,
 "features": ["auto_orders", "taobao"],
 "instance": "0123456789abcdef"}
```

   `plan` is one of `plus`, `team`, `solo`; `days` is an integer 1..3650;
   `features` is a list of non-empty strings up to 32 chars; `instance` is
   optional hex (8..64 chars). The JSON bytes are signed as sent.

Hard limits: payload <= 4096 bytes, one line <= 13312 bytes, 30 s per
connection. The private key is never logged, returned, or included in an
error message.

## Key provisioning

Reuse the existing production key so already-sold claim keys keep working.
The key is the raw 32-byte seed, base64 encoded, matching
`license.PUBLIC_KEY_B64` in the app.

```bash
# on the signer host, as root
install -d -m 0700 -o ledger-signer -g ledger-signer /etc/ledger-signer
install -m 0600 -o ledger-signer -g ledger-signer \
    /root/.ledger-license/private.b64 /etc/ledger-signer/private.b64
# verify the fingerprint printed by --check matches the deployed app, then
# remove the key from the web app host and from old backups you no longer trust
```

Generating a **new** key pair (only when rotating; existing licenses become
invalid unless the app is updated to trust the old public key too):

```bash
sudo -u ledger-signer python3 - <<'PY'
import base64, os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
key = Ed25519PrivateKey.generate()
raw = key.private_bytes(serialization.Encoding.Raw,
                        serialization.PrivateFormat.Raw,
                        serialization.NoEncryption())
pub = key.public_key().public_bytes(serialization.Encoding.Raw,
                                    serialization.PublicFormat.Raw)
path = '/etc/ledger-signer/private.b64'
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, 'wb') as handle:
    handle.write(base64.b64encode(raw) + b'\n')
os.chmod(path, 0o600)
print('license.py PUBLIC_KEY_B64:', base64.b64encode(pub).decode('ascii'))
PY
```

The command writes the private key directly to the 0600 file and prints only
the public key. Store the public key in `license.PUBLIC_KEY_B64` before
shipping the app.

Permissions:

- key directory `/etc/ledger-signer` — `0700`, owner `ledger-signer`;
- key file — `0600`, owner `ledger-signer`; the service refuses group/other
  permissions;
- socket `/run/ledger-signer/signer.sock` — created `0660` by the service;
- socket group — `ledger-signer`; add the web app user with
  `usermod -aG ledger-signer ledger` (the app user must not be the signer
  user).

## systemd unit example

`/etc/systemd/system/ledger-signer.service`:

```ini
[Unit]
Description=Ledger license signer
After=network.target

[Service]
Type=simple
User=ledger-signer
Group=ledger-signer
RuntimeDirectory=ledger-signer
RuntimeDirectoryMode=0755
UMask=0077
Environment=LEDGER_LICENSE_PRIVATE_FILE=/etc/ledger-signer/private.b64
Environment=LEDGER_SIGNER_SOCKET=/run/ledger-signer/signer.sock
ExecStartPre=/usr/bin/python3 /opt/ledger-signer/license_signer.py --check
ExecStart=/usr/bin/python3 /opt/ledger-signer/license_signer.py
Restart=on-failure
RestartSec=2
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictSUIDSGID=yes
RestrictAddressFamilies=AF_UNIX
PrivateNetwork=yes
LimitCORE=0
ReadOnlyPaths=/etc/ledger-signer

[Install]
WantedBy=multi-user.target
```

Deploy the file to `/opt/ledger-signer/license_signer.py` (it needs
`cryptography`, already used by the app), then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ledger-signer
sudo -u ledger-signer /usr/bin/python3 /opt/ledger-signer/license_signer.py --check
sudo -u ledger test -w /run/ledger-signer/signer.sock && echo socket-writable-for-app
ls -l /run/ledger-signer/signer.sock   # srw-rw---- ledger-signer ledger-signer
```

`--check` validates the key file, its mode and the socket path, prints a JSON
summary with the public key (base64, same value as `license.PUBLIC_KEY_B64`)
and its fingerprint, and exits non-zero on a problem. It never prints the
private key.

For the web app service add:

```ini
Environment=LEDGER_SIGNER_SOCKET=/run/ledger-signer/signer.sock
SupplementaryGroups=ledger-signer
```

Restart the app after the change. Keeping the key on the app host after this
point defeats the separation: remove it and set only the signer env.

## What depends on the signer

- **Automatic issuance** — Telegram Stars purchases, Telegram `/buy`, and
  any code path that mints a claim key (`_license_make_claim`) or a bound
  license (`_license_register_local`) calls `_license_sign`, so it needs the
  signer. The Stars payment handler logs `⚠ Stars payment: ...` and does not
  send a key when the signer is unavailable; the customer must be handled
  manually. Hosted activation returns HTTP 400 with the signer error text.
- **Desktop/offline installs** — unchanged: they do not set
  `LEDGER_SIGNER_SOCKET`, so `make_license.py` and the local-key fallback keep
  working on a machine that owns the key.
- **License verification** — still completely offline in client apps; it
  needs only `license.PUBLIC_KEY_B64` and never calls the signer.

## Tests

```bash
python -m py_compile license_signer.py game_tracker.py tests/test_license_signer.py
python tests/test_license_signer.py
```

On Linux the test file starts the real signer with a throwaway key and a
temporary socket. On Windows (no `AF_UNIX` in CPython there) the listener
tests are skipped, while request validation, the socketpair protocol and the
game_tracker remote path (fake socket) are still exercised.

## Residual risks

1. Same-host compromise (root or both service accounts) still reaches the
   key. True isolation requires a separate host and a forwarded socket.
2. The signer is a single point of failure for automatic issuance; monitor
   `systemctl status ledger-signer` and alert on failure. Failed Stars
   fulfillments are logged but not retried automatically.
3. The socket is an unauthenticated signing oracle for any process in the
   `ledger-signer` group. Validation limits payload shape, plan, features and
   expiry, but does not enforce per-customer business rules, rate limits or
   an audit log.
4. Key rotation invalidates existing licenses unless the app is taught to
   trust multiple public keys; the current app embeds one key.
5. The signer trusts its host clock for expiry validation; keep NTP working.
6. The JSON-claim form is for tooling/tests; the shipped app and verifier use
   the binary payload format. Do not build a second license format on it.
