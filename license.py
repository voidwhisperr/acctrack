"""Ledger license tokens: compact Ed25519-signed, verified offline."""
import base64
import datetime
import os
import struct

PUBLIC_KEY_B64 = 'RqZ7PZMd+IJWMuNhrBysA9fGs/83WDYitTwfNKB9GII='

EPOCH = datetime.date(2020, 1, 1)
PLANS = {1: 'plus', 2: 'team', 3: 'trial'}
PLAN_IDS = {v: k for k, v in PLANS.items()}
FEATURES = {
    'auto_orders': 1,
    'taobao': 2,
    'hosted': 4,
    'team': 8,
    'priority': 16,
}
FEATURE_NAMES = {v: k for k, v in FEATURES.items()}


def _b64e(data):
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')


def _b64d(text):
    pad = '=' * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def pack_payload(plan, days, features, nonce=None):
    pid = PLAN_IDS.get(str(plan).lower())
    if not pid:
        raise ValueError('unknown plan: ' + str(plan))
    if not features:
        features = ['auto_orders', 'taobao', 'hosted'] if pid == 1 else []
    mask = 0
    for f in features:
        if f not in FEATURES:
            raise ValueError('unknown feature: ' + str(f))
        mask |= FEATURES[f]
    exp = (datetime.date.today() + datetime.timedelta(days=int(days)) - EPOCH).days
    nonce = nonce or os.urandom(4)
    return struct.pack('>BBHI', 1, pid, exp, mask) + nonce


def pack_payload_bound(plan, days, features, instance_id, nonce=None):
    import hashlib
    if not instance_id:
        raise ValueError('instance_id required for a bound license')
    base = pack_payload(plan, days, features, nonce)
    ih = hashlib.sha256(str(instance_id).encode('utf-8')).digest()[:8]
    ver, pid, exp, mask = struct.unpack('>BBHI', base[:8])
    nonce = int.from_bytes(os.urandom(4), 'big')
    return struct.pack('>BBHII', 2, pid, exp, mask, nonce) + ih


def unpack_payload(raw):
    if len(raw) not in (12, 20):
        raise ValueError('bad payload length')
    ver, pid, exp, mask = struct.unpack('>BBHI', raw[:8])
    if ver not in (1, 2) or pid not in PLANS:
        raise ValueError('bad payload')
    exp_date = EPOCH + datetime.timedelta(days=exp)
    feats = [FEATURE_NAMES[b] for b in sorted(FEATURE_NAMES) if mask & b]
    info = {
        'v': ver,
        'plan': PLANS[pid],
        'exp': exp_date.isoformat(),
        'days_left': (exp_date - datetime.date.today()).days,
        'features': feats,
        'nonce': raw[8:12].hex(),
        'bound': ver == 2,
    }
    if ver == 2:
        _v, _p, _e, _m, nonce = struct.unpack('>BBHII', raw[:12])
        info['nonce'] = nonce.to_bytes(4, 'big').hex()
        info['instance_hash'] = raw[12:20].hex()
    return info


def make_code(payload, signature, prefix='LDG'):
    return prefix + '.' + _b64e(payload) + '.' + _b64e(signature)


def split_code(code):
    parts = str(code or '').strip().split('.')
    if len(parts) != 3:
        raise ValueError('bad license format')
    return parts[0], _b64d(parts[1]), _b64d(parts[2])


def verify(code, instance_id=None):
    """Return payload dict if the signature and expiry are valid, else None.

    For a bound (v2) license, instance_id must be supplied and must match.
    """
    try:
        import hashlib
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        _, payload, sig = split_code(code)
        pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLIC_KEY_B64))
        pub.verify(sig, payload)
        info = unpack_payload(payload)
        if info['days_left'] < 0:
            return None
        if info.get('bound'):
            if not instance_id:
                return None
            want = hashlib.sha256(str(instance_id).encode('utf-8')).digest()[:8].hex()
            if info.get('instance_hash') != want:
                return None
        return info
    except Exception:
        return None


def has(code, feature):
    info = verify(code)
    return bool(info and feature in info['features'])


def save(data_dir, code):
    import json
    path = os.path.join(str(data_dir), '.gt_license.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump({'code': str(code).strip(), 'activated_at': int(datetime.datetime.now().timestamp())}, fh)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path


def load(data_dir, instance_id=None):
    import json
    path = os.path.join(str(data_dir), '.gt_license.json')
    try:
        with open(path, encoding='utf-8') as fh:
            code = json.load(fh).get('code')
        return verify(code, instance_id)
    except Exception:
        return None


def clear(data_dir):
    try:
        os.remove(os.path.join(str(data_dir), '.gt_license.json'))
    except OSError:
        pass

