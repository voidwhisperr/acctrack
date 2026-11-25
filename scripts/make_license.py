"""Generate Ledger license keys (admin only).

Private key: ~/.ledger-license/private.b64 (or LEDGER_LICENSE_PRIVATE_FILE).
Never ship this file with the app.
"""
import argparse
import base64
import os
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import license as lic


def sign(code_bytes_to_sign, private_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    raw = base64.b64decode(open(private_path, encoding='ascii').read().strip())
    return Ed25519PrivateKey.from_private_bytes(raw).sign(code_bytes_to_sign)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', default='plus', choices=['plus', 'team', 'trial'])
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--features', default='auto_orders,taobao,hosted')
    ap.add_argument('--count', type=int, default=1)
    ap.add_argument('--out', default='')
    a = ap.parse_args()
    priv = os.environ.get('LEDGER_LICENSE_PRIVATE_FILE') or os.path.expanduser('~/.ledger-license/private.b64')
    if not os.path.exists(priv):
        raise SystemExit('private key not found: ' + priv)
    feats = [x.strip() for x in a.features.split(',') if x.strip()]
    codes = []
    prefix = 'TRIAL' if a.plan == 'trial' else 'LDG'
    for _ in range(max(1, a.count)):
        payload = lic.pack_payload(a.plan, a.days, feats)
        codes.append(lic.make_code(payload, sign(payload, priv), prefix))
    print('\n'.join(codes))
    if a.out:
        pathlib.Path(a.out).write_text('\n'.join(codes) + '\n', encoding='ascii')


if __name__ == '__main__':
    main()
