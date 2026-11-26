#!/usr/bin/env python3
'''Tests for license_signer.py and the game_tracker remote-signing path.

No live app and no real license key are used: every test generates a
throwaway Ed25519 key in a temporary directory. On platforms without AF_UNIX
the listener tests are skipped, but the request/response protocol is still
exercised through a socketpair and the game_tracker remote path through a
fake socket.
'''
import atexit
import base64
import datetime
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

_TMP = tempfile.mkdtemp(prefix='ledger-signer-tests-')
atexit.register(shutil.rmtree, _TMP, True)
os.environ.setdefault('GT_DATA_DIR', _TMP)
os.environ.setdefault('GT_NO_BROWSER', '1')

import license as lic                       # noqa: E402
import license_signer as signer             # noqa: E402
import game_tracker as gt                   # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: E402

HAS_UNIX = os.name == 'posix' and hasattr(socket, 'AF_UNIX')
EPOCH = datetime.date(2020, 1, 1)


def _skip(reason):
    raise unittest.SkipTest(reason)


def _tmpdir(prefix):
    return tempfile.mkdtemp(prefix=prefix, dir=_TMP)


def _new_key():
    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes(serialization.Encoding.Raw,
                            serialization.PrivateFormat.Raw,
                            serialization.NoEncryption())
    return key, raw


def _write_key(directory=None):
    directory = directory or _tmpdir('key-')
    key, raw = _new_key()
    path = os.path.join(directory, 'private.b64')
    with open(path, 'w', encoding='ascii') as handle:
        handle.write(base64.b64encode(raw).decode('ascii') + chr(10))
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return path, key


def _pub(key):
    return key.public_key().public_bytes(serialization.Encoding.Raw,
                                         serialization.PublicFormat.Raw)


def _payload(plan='plus', days=30, bound=False, instance='0123456789abcdef'):
    features = ['auto_orders', 'taobao', 'hosted']
    if plan == 'team':
        features.append('team')
    if bound:
        return lic.pack_payload_bound(plan, days, features, instance)
    return lic.pack_payload(plan, days, features)


def _request(payload):
    return {'payload_b64': base64.b64encode(payload).decode('ascii')}


def _sign_ok(key, payload):
    response = signer.handle_request(_request(payload), key)
    assert 'error' not in response, response
    signature = base64.b64decode(response['sig_b64'], validate=True)
    assert len(signature) == 64
    key.public_key().verify(signature, payload)
    return signature


def _start_signer(key_path, sock_path):
    env = dict(os.environ)
    env['LEDGER_LICENSE_PRIVATE_FILE'] = key_path
    env['LEDGER_SIGNER_SOCKET'] = sock_path
    proc = subprocess.Popen([sys.executable, os.path.join(REPO, 'license_signer.py')],
                            cwd=REPO, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.time() + 15
    while time.time() < deadline:
        if os.path.exists(sock_path):
            return proc
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    if proc.poll() is None:
        proc.kill()
    out, err = proc.communicate(timeout=10)
    raise AssertionError('signer did not start: '
                         + (err or out).decode('utf-8', 'replace')[:500])


def _stop_signer(proc):
    if proc.poll() is None:
        proc.terminate()
    try:
        out, err = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
    return (out or b'').decode('utf-8', 'replace'), (err or b'').decode('utf-8', 'replace')


def _ask_signer(sock_path, payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        client.settimeout(10)
        client.connect(sock_path)
        client.sendall((json.dumps(_request(payload)) + chr(10)).encode('utf-8'))
        handle = client.makefile('rb')
        try:
            line = handle.readline()
        finally:
            handle.close()
    finally:
        client.close()
    return json.loads(line.decode('utf-8'))


def _set_env(name, value):
    old = os.environ.get(name)
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value
    return old


def _restore_env(name, old):
    if old is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = old


# ── service configuration ──────────────────────────────────────────
def test_check_mode_ok():
    if not HAS_UNIX:
        _skip('AF_UNIX sockets are unavailable on this platform')
    key_path, key = _write_key()
    sock_path = os.path.join(_tmpdir('check-'), 'signer.sock')
    env = dict(os.environ)
    env.update({'LEDGER_LICENSE_PRIVATE_FILE': key_path,
                'LEDGER_SIGNER_SOCKET': sock_path})
    result = subprocess.run([sys.executable, os.path.join(REPO, 'license_signer.py'), '--check'],
                            cwd=REPO, env=env, capture_output=True, text=True, timeout=60)
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    data = json.loads(result.stdout)
    assert data['ok'] is True
    assert data['socket'] == sock_path
    assert data['public_key_b64'] == base64.b64encode(_pub(key)).decode('ascii')
    assert data['public_key_fingerprint'].startswith('sha256:')
    with open(key_path, encoding='ascii') as handle:
        raw_b64 = handle.read().strip()
    assert raw_b64 not in output, 'the private key must never be logged'


def test_check_mode_rejects_missing_key():
    missing = os.path.join(_tmpdir('missing-'), 'private.b64')
    env = dict(os.environ)
    env.update({'LEDGER_LICENSE_PRIVATE_FILE': missing,
                'LEDGER_SIGNER_SOCKET': os.path.join(_TMP, 'missing.sock')})
    result = subprocess.run([sys.executable, os.path.join(REPO, 'license_signer.py'), '--check'],
                            cwd=REPO, env=env, capture_output=True, text=True, timeout=60)
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'cannot stat private key file' in output


def test_check_mode_rejects_open_key_permissions():
    if os.name != 'posix':
        _skip('POSIX file permissions are not available here')
    key_path, _key = _write_key()
    os.chmod(key_path, 0o644)
    env = dict(os.environ)
    env.update({'LEDGER_LICENSE_PRIVATE_FILE': key_path,
                'LEDGER_SIGNER_SOCKET': os.path.join(_TMP, 'mode.sock')})
    result = subprocess.run([sys.executable, os.path.join(REPO, 'license_signer.py'), '--check'],
                            cwd=REPO, env=env, capture_output=True, text=True, timeout=60)
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'expected 600' in output


# ── request validation and signing ─────────────────────────────────
def test_valid_binary_payloads():
    key, _raw = _new_key()
    claim = _payload()
    _sign_ok(key, claim)
    bound = _payload('team', bound=True)
    _sign_ok(key, bound)


def test_signatures_form_valid_licenses():
    key, _raw = _new_key()
    saved = lic.PUBLIC_KEY_B64
    lic.PUBLIC_KEY_B64 = base64.b64encode(_pub(key)).decode('ascii')
    try:
        claim = _payload()
        code = lic.make_code(claim, _sign_ok(key, claim), 'LDG')
        info = lic.verify(code)
        assert info and info['plan'] == 'plus', info
        bound = _payload('plus', bound=True)
        code = lic.make_code(bound, _sign_ok(key, bound), 'LDG')
        info = lic.verify(code, '0123456789abcdef')
        assert info and info['bound'] is True, info
    finally:
        lic.PUBLIC_KEY_B64 = saved


def test_valid_json_claim_payload():
    key, _raw = _new_key()
    claim = {'plan': 'solo', 'days': 30,
             'features': ['auto_orders', 'taobao'],
             'instance': '0123456789abcdef'}
    _sign_ok(key, json.dumps(claim).encode('utf-8'))
    _sign_ok(key, json.dumps({'plan': 'team', 'days': 3650,
                              'features': []}).encode('utf-8'))


def test_reject_invalid_payloads():
    key, _raw = _new_key()
    today = (datetime.date.today() - EPOCH).days
    cases = [
        (b'\x00' * 4097, 'too long'),
        (b'', 'empty'),
        (struct.pack('>BBHI', 9, 1, today + 1, 1) + b'\x00' * 4, 'version'),
        (struct.pack('>BBHI', 1, 9, today + 1, 1) + b'\x00' * 4, 'plan'),
        (struct.pack('>BBHI', 1, 1, today + 1, 0xFF) + b'\x00' * 4, 'feature'),
        (struct.pack('>BBHI', 1, 1, today - 1, 1) + b'\x00' * 4, 'expired'),
        (struct.pack('>BBHI', 1, 1, today + 3651, 1) + b'\x00' * 4, '3650 days'),
        (b'not a license payload', 'neither'),
        (json.dumps({'plan': 'gold', 'days': 30, 'features': []}).encode(), 'plan'),
        (json.dumps({'plan': 'plus', 'days': 0, 'features': []}).encode(), 'days'),
        (json.dumps({'plan': 'plus', 'days': 3651, 'features': []}).encode(), 'days'),
        (json.dumps({'plan': 'plus', 'days': True, 'features': []}).encode(), 'days'),
        (json.dumps({'plan': 'plus', 'days': 30, 'features': 'auto_orders'}).encode(), 'features'),
        (json.dumps({'plan': 'plus', 'days': 30, 'features': ['x' * 40]}).encode(), 'longer'),
        (json.dumps({'plan': 'plus', 'days': 30, 'features': [],
                     'instance': 'zz'}).encode(), 'instance'),
        (json.dumps({'plan': 'plus', 'days': 30, 'features': [],
                     'extra': 1}).encode(), 'field'),
    ]
    for payload, needle in cases:
        response = signer.handle_request(_request(payload), key)
        assert 'error' in response, (payload[:40], response)
        assert needle in response['error'].lower(), (payload[:40], response)


def test_reject_invalid_requests():
    key, _raw = _new_key()
    good = base64.b64encode(_payload()).decode('ascii')
    cases = [
        (None, 'object'),
        ([], 'object'),
        ({}, 'payload_b64'),
        ({'payload_b64': 123}, 'base64'),
        ({'payload_b64': '!!!'}, 'base64'),
        ({'payload_b64': good, 'extra': 1}, 'field'),
        ({'payload_b64': base64.b64encode(b'\x00' * 4097).decode('ascii')}, 'too long'),
    ]
    for request, needle in cases:
        response = signer.handle_request(request, key)
        assert 'error' in response, (request, response)
        assert needle in response['error'].lower(), (request, response)


# ── socket protocol and listener ───────────────────────────────────
def test_socket_protocol_socketpair():
    key, _raw = _new_key()
    server_sock, client_sock = socket.socketpair()
    thread = threading.Thread(target=signer.serve_connection,
                              args=(server_sock, key), daemon=True)
    thread.start()
    try:
        first = _payload()
        third = json.dumps({'plan': 'solo', 'days': 30,
                            'features': ['taobao']}).encode('utf-8')
        client_sock.sendall((json.dumps(_request(first)) + chr(10)).encode('utf-8'))
        client_sock.sendall((json.dumps({'payload_b64': '!!!'}) + chr(10)).encode('utf-8'))
        client_sock.sendall((json.dumps(_request(third)) + chr(10)).encode('utf-8'))
        handle = client_sock.makefile('rb')
        try:
            responses = [json.loads(handle.readline().decode('utf-8'))
                         for _ in range(3)]
        finally:
            handle.close()
    finally:
        try:
            client_sock.close()
        except OSError:
            pass
        thread.join(timeout=10)
    assert not thread.is_alive(), 'signer connection handler did not stop'
    assert 'sig_b64' in responses[0], responses[0]
    key.public_key().verify(base64.b64decode(responses[0]['sig_b64'], validate=True), first)
    assert 'error' in responses[1], responses[1]
    assert 'sig_b64' in responses[2], responses[2]
    key.public_key().verify(base64.b64decode(responses[2]['sig_b64'], validate=True), third)


def test_unix_socket_listener():
    if not HAS_UNIX:
        _skip('AF_UNIX sockets are unavailable on this platform')
    directory = _tmpdir('listener-')
    key_path, key = _write_key(directory)
    sock_path = os.path.join(directory, 'signer.sock')
    proc = _start_signer(key_path, sock_path)
    try:
        payload = _payload('team', bound=True)
        response = _ask_signer(sock_path, payload)
        assert 'sig_b64' in response, response
        signature = base64.b64decode(response['sig_b64'], validate=True)
        key.public_key().verify(signature, payload)
        assert (os.stat(sock_path).st_mode & 0o777) == 0o660
    finally:
        out, err = _stop_signer(proc)
        with open(key_path, encoding='ascii') as handle:
            raw_b64 = handle.read().strip()
        assert raw_b64 not in out and raw_b64 not in err, 'the private key must never be logged'
        for _ in range(100):
            if not os.path.exists(sock_path):
                break
            time.sleep(0.05)
        assert not os.path.exists(sock_path), 'signer left its socket behind'


# ── game_tracker integration ───────────────────────────────────────
def test_game_tracker_remote_sign_fake_socket():
    key, _raw = _new_key()
    server_sock, client_sock = socket.socketpair()
    thread = threading.Thread(target=signer.serve_connection,
                              args=(server_sock, key), daemon=True)
    thread.start()
    old_connect = gt._license_signer_connect
    old_socket = _set_env('LEDGER_SIGNER_SOCKET', os.path.join(_TMP, 'fake-signer.sock'))
    def _fake_connect(_path):
        return client_sock
    gt._license_signer_connect = _fake_connect
    try:
        payload = _payload('team', bound=True)
        signature = gt._license_sign(payload)
        key.public_key().verify(signature, payload)
    finally:
        gt._license_signer_connect = old_connect
        _restore_env('LEDGER_SIGNER_SOCKET', old_socket)
        thread.join(timeout=10)


def test_game_tracker_binds_license_without_local_key():
    key, _raw = _new_key()
    saved_public = lic.PUBLIC_KEY_B64
    lic.PUBLIC_KEY_B64 = base64.b64encode(_pub(key)).decode('ascii')
    try:
        claim_payload = _payload('plus', days=30)
        claim_code = lic.make_code(claim_payload, key.sign(claim_payload), 'LDG')
        try:
            os.remove(gt._lic_registry_path())
        except OSError:
            pass
        server_sock, client_sock = socket.socketpair()
        thread = threading.Thread(target=signer.serve_connection,
                                  args=(server_sock, key), daemon=True)
        thread.start()
        old_connect = gt._license_signer_connect
        old_socket = _set_env('LEDGER_SIGNER_SOCKET', os.path.join(_TMP, 'bind.sock'))
        old_key = _set_env('LEDGER_LICENSE_PRIVATE_FILE', None)
        def _fake_connect(_path):
            return client_sock
        gt._license_signer_connect = _fake_connect
        try:
            instance = '0123456789abcdef'
            result = gt._license_register_local(claim_code, instance)
            assert result.get('ok') is True, result
            bound = result['license']['code']
            info = lic.verify(bound, instance)
            assert info is not None, 'bound license did not verify'
            assert info['plan'] == 'plus' and info['bound'] is True, info
        finally:
            gt._license_signer_connect = old_connect
            _restore_env('LEDGER_SIGNER_SOCKET', old_socket)
            _restore_env('LEDGER_LICENSE_PRIVATE_FILE', old_key)
            thread.join(timeout=10)
    finally:
        lic.PUBLIC_KEY_B64 = saved_public


def test_game_tracker_does_not_fallback_on_signer_failure():
    key_path, _key = _write_key()
    old_socket = _set_env('LEDGER_SIGNER_SOCKET', os.path.join(_TMP, 'absent.sock'))
    old_key = _set_env('LEDGER_LICENSE_PRIVATE_FILE', key_path)
    old_connect = gt._license_signer_connect
    def _refuse(_path):
        raise ConnectionRefusedError('signer is down')
    gt._license_signer_connect = _refuse
    try:
        try:
            gt._license_sign(_payload())
        except (OSError, ValueError):
            pass
        else:
            raise AssertionError('signing silently fell back to the local key')
    finally:
        gt._license_signer_connect = old_connect
        _restore_env('LEDGER_SIGNER_SOCKET', old_socket)
        _restore_env('LEDGER_LICENSE_PRIVATE_FILE', old_key)


def test_game_tracker_local_key_fallback():
    key_path, key = _write_key()
    old_socket = _set_env('LEDGER_SIGNER_SOCKET', None)
    old_auto = _set_env('LEDGER_SIGNER_AUTO', '0')
    old_key = _set_env('LEDGER_LICENSE_PRIVATE_FILE', key_path)
    try:
        payload = _payload()
        signature = gt._license_sign(payload)
        key.public_key().verify(signature, payload)
    finally:
        _restore_env('LEDGER_SIGNER_SOCKET', old_socket)
        _restore_env('LEDGER_SIGNER_AUTO', old_auto)
        _restore_env('LEDGER_LICENSE_PRIVATE_FILE', old_key)


def test_game_tracker_remote_sign_real_socket():
    if not HAS_UNIX:
        _skip('AF_UNIX sockets are unavailable on this platform')
    directory = _tmpdir('gt-remote-')
    key_path, key = _write_key(directory)
    sock_path = os.path.join(directory, 'signer.sock')
    proc = _start_signer(key_path, sock_path)
    old_socket = _set_env('LEDGER_SIGNER_SOCKET', sock_path)
    old_key = _set_env('LEDGER_LICENSE_PRIVATE_FILE', None)
    try:
        payload = _payload('plus', bound=True)
        signature = gt._license_sign(payload)
        key.public_key().verify(signature, payload)
    finally:
        _restore_env('LEDGER_SIGNER_SOCKET', old_socket)
        _restore_env('LEDGER_LICENSE_PRIVATE_FILE', old_key)
        _stop_signer(proc)


def test_game_tracker_rejects_oversize_payload():
    old_socket = _set_env('LEDGER_SIGNER_SOCKET', os.path.join(_TMP, 'never.sock'))
    try:
        try:
            gt._license_sign(b'\x00' * 4097)
        except ValueError as exc:
            assert 'too long' in str(exc), exc
        else:
            raise AssertionError('oversize payload was not rejected')
    finally:
        _restore_env('LEDGER_SIGNER_SOCKET', old_socket)


def _run_all():
    names = sorted(name for name, value in globals().items()
                   if name.startswith('test_') and callable(value))
    failed = 0
    skipped = 0
    for name in names:
        try:
            globals()[name]()
        except unittest.SkipTest as exc:
            skipped += 1
            print('SKIP', name, '-', exc)
        except Exception as exc:
            failed += 1
            print('FAIL', name, type(exc).__name__, exc)
        else:
            print('ok  ', name)
    passed = len(names) - failed - skipped
    print('license signer tests: %d passed, %d skipped, %d failed' % (passed, skipped, failed))
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(_run_all())
