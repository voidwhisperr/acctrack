#!/usr/bin/env python3
'''Ledger license signer: Ed25519 signing service on a Unix socket.

The web app (game_tracker.py) keeps only the public verification key. This
service is the only process that reads the Ed25519 private key and signs
license payloads on request over a local Unix socket.

Protocol: one JSON object per line (UTF-8, newline terminated).

    request : {'payload_b64': '<base64 of the payload bytes>'}
    response: {'sig_b64': '<base64 Ed25519 signature>'}  or  {'error': '...'}

Allowed payloads (the payload bytes are signed exactly as received):

  * the existing Ledger binary license payload (see license.py): 12 bytes
    v1 (claim) or 20 bytes v2 (instance-bound). Version, plan, feature mask
    and expiry are validated before signing;
  * a JSON claim object:
        {'plan': 'plus'|'team'|'solo', 'days': 1..3650,
         'features': ['short-string', ...], 'instance': '<hex>' (optional)}

Environment:
    LEDGER_LICENSE_PRIVATE_FILE  key file (default /etc/ledger-signer/private.b64)
    LEDGER_SIGNER_SOCKET         socket path (default /run/ledger-signer/signer.sock)

Run with --check to validate the key (mode 600) and socket path, then exit.
The private key is never logged or included in responses.

The only non-stdlib dependency is cryptography (Ed25519), which the app
already uses.
'''
import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import signal
import socket
import stat
import struct
import sys
import threading

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except Exception:  # pragma: no cover - reported by load_private_key()
    serialization = None
    Ed25519PrivateKey = None

DEFAULT_KEY_FILE = '/etc/ledger-signer/private.b64'
DEFAULT_SOCKET = '/run/ledger-signer/signer.sock'
MAX_PAYLOAD = 4096
MAX_LINE = MAX_PAYLOAD * 3 + 1024
CONNECTION_TIMEOUT = 30.0
SOCKET_MODE = 0o660
KEY_MODE_FORBIDDEN = 0o077
EPOCH = datetime.date(2020, 1, 1)   # same epoch as license.py
PLAN_IDS = (1, 2, 3)                # plus, team, trial
CLAIM_PLANS = ('plus', 'team', 'solo')
CLAIM_FIELDS = ('plan', 'days', 'features', 'instance')
FEATURE_BITS = 0x1F                 # auto_orders|taobao|hosted|team|priority
MAX_DAYS = 3650
MAX_FEATURE_LEN = 32
INSTANCE_RE = re.compile(r'^[0-9a-fA-F]{8,64}$')


class SignerError(Exception):
    '''Configuration or payload error that is safe to show to the caller.'''


def _log(message):
    sys.stderr.write('license_signer: ' + str(message) + '\n')
    sys.stderr.flush()


def key_path():
    return (os.environ.get('LEDGER_LICENSE_PRIVATE_FILE') or '').strip() or DEFAULT_KEY_FILE


def socket_path():
    return (os.environ.get('LEDGER_SIGNER_SOCKET') or '').strip() or DEFAULT_SOCKET


def load_private_key(path=None):
    '''Load the raw Ed25519 seed without ever echoing its contents.'''
    path = path or key_path()
    if Ed25519PrivateKey is None:
        raise SignerError('cryptography is not installed; cannot sign')
    try:
        info = os.stat(path)
    except OSError as exc:
        raise SignerError('cannot stat private key file ' + path + ': ' + (exc.strerror or 'error')) from None
    if not stat.S_ISREG(info.st_mode):
        raise SignerError('private key path is not a regular file: ' + path)
    if os.name == 'posix' and (info.st_mode & KEY_MODE_FORBIDDEN):
        mode = format(stat.S_IMODE(info.st_mode), '04o')
        raise SignerError('private key file ' + path + ' has mode ' + mode + '; expected 600')
    try:
        with open(path, 'r', encoding='ascii') as handle:
            raw = base64.b64decode(handle.read().strip(), validate=True)
    except Exception:
        raise SignerError('cannot read or decode private key file ' + path) from None
    if len(raw) != 32:
        raise SignerError('private key file ' + path + ' must hold a 32-byte Ed25519 seed')
    try:
        return Ed25519PrivateKey.from_private_bytes(raw)
    except Exception:
        raise SignerError('invalid Ed25519 private key in ' + path) from None


def public_key_b64(key):
    '''Return the base64 raw public key (safe to log; never the private key).'''
    raw = key.public_key().public_bytes(serialization.Encoding.Raw,
                                        serialization.PublicFormat.Raw)
    return base64.b64encode(raw).decode('ascii')


def _validate_binary(raw):
    version, plan_id, expiry, features = struct.unpack('>BBHI', raw[:8])
    if version not in (1, 2):
        raise SignerError('unsupported license payload version')
    if (version == 1 and len(raw) != 12) or (version == 2 and len(raw) != 20):
        raise SignerError('bad license payload length for version ' + str(version))
    if plan_id not in PLAN_IDS:
        raise SignerError('unknown license plan id in payload')
    if features & ~FEATURE_BITS:
        raise SignerError('unknown license feature bits in payload')
    today = (datetime.date.today() - EPOCH).days
    if expiry < today:
        raise SignerError('license payload is expired')
    if expiry > today + MAX_DAYS:
        raise SignerError('license expiry is more than ' + str(MAX_DAYS) + ' days away')


def _validate_claim(raw):
    try:
        claim = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        raise SignerError('payload is neither a Ledger license payload nor a JSON claim') from None
    if not isinstance(claim, dict):
        raise SignerError('JSON claim payload must be an object')
    extra = sorted(set(claim) - set(CLAIM_FIELDS))
    if extra:
        raise SignerError('unexpected JSON claim field(s): ' + ', '.join(extra))
    plan = claim.get('plan')
    if plan not in CLAIM_PLANS:
        raise SignerError('plan must be one of: ' + ', '.join(CLAIM_PLANS))
    days = claim.get('days')
    if type(days) is not int or not 1 <= days <= MAX_DAYS:
        raise SignerError('days must be an integer between 1 and ' + str(MAX_DAYS))
    features = claim.get('features')
    if not isinstance(features, list):
        raise SignerError('features must be a list')
    if len(features) > 32:
        raise SignerError('features list is too long')
    for item in features:
        if not isinstance(item, str) or not item:
            raise SignerError('features must be non-empty strings')
        if len(item) > MAX_FEATURE_LEN:
            raise SignerError('feature name is longer than ' + str(MAX_FEATURE_LEN) + ' characters')
    instance = claim.get('instance')
    if instance is not None:
        if not isinstance(instance, str) or not INSTANCE_RE.match(instance):
            raise SignerError('instance must be a hex string (8..64 characters)')


def validate_payload(raw):
    '''Raise SignerError unless raw is a payload this service signs.'''
    if not isinstance(raw, (bytes, bytearray)):
        raise SignerError('payload must be bytes')
    raw = bytes(raw)
    if not raw:
        raise SignerError('empty payload')
    if len(raw) > MAX_PAYLOAD:
        raise SignerError('payload too long (limit ' + str(MAX_PAYLOAD) + ' bytes)')
    if raw.lstrip()[:1] in (b'{', b'['):
        _validate_claim(raw)
    elif len(raw) in (12, 20):
        _validate_binary(raw)
    else:
        _validate_claim(raw)


def handle_request(request, key):
    '''Validate one decoded request object and return a response object.'''
    if not isinstance(request, dict):
        return {'error': 'request must be a JSON object'}
    extra = sorted(set(request) - {'payload_b64'})
    if extra:
        return {'error': 'unexpected request field(s): ' + ', '.join(extra)}
    encoded = request.get('payload_b64')
    if not isinstance(encoded, str):
        return {'error': 'payload_b64 must be a base64 string'}
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception:
        return {'error': 'payload_b64 is not valid base64'}
    try:
        validate_payload(raw)
    except SignerError as exc:
        return {'error': str(exc)}
    try:
        signature = key.sign(raw)
    except Exception:
        return {'error': 'signing failed'}
    return {'sig_b64': base64.b64encode(signature).decode('ascii')}


def handle_line(line, key):
    '''Decode one JSON line and return the response object.'''
    try:
        request = json.loads(line.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        return {'error': 'invalid JSON request'}
    return handle_request(request, key)


def _send_response(connection, response):
    connection.sendall(json.dumps(response, separators=(',', ':')).encode('utf-8') + b'\n')


def serve_connection(connection, key):
    '''Serve newline-delimited requests on one connected socket.'''
    handle = None
    try:
        connection.settimeout(CONNECTION_TIMEOUT)
        handle = connection.makefile('rb')
        while True:
            line = handle.readline(MAX_LINE + 1)
            if not line:
                break
            if len(line) > MAX_LINE:
                _send_response(connection, {'error': 'request too large'})
                break
            if not line.endswith(b'\n'):
                _send_response(connection, {'error': 'request must end with a newline'})
                break
            line = line.rstrip(b'\r\n')
            if not line:
                _send_response(connection, {'error': 'empty request'})
                continue
            _send_response(connection, handle_line(line, key))
    except (OSError, socket.timeout):
        pass
    finally:
        if handle is not None:
            try:
                handle.close()
            except OSError:
                pass
        try:
            connection.close()
        except OSError:
            pass


def _prepare_socket(path):
    encoded = os.fsencode(path)
    if len(encoded) >= 108:
        raise SignerError('socket path is too long for a Unix socket: ' + path)
    parent = os.path.dirname(os.path.abspath(path))
    try:
        os.makedirs(parent, mode=0o755, exist_ok=True)
    except OSError as exc:
        raise SignerError('cannot create socket directory ' + parent + ': ' + (exc.strerror or 'error')) from None
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return parent
    except OSError as exc:
        raise SignerError('cannot inspect socket path ' + path + ': ' + (exc.strerror or 'error')) from None
    if not stat.S_ISSOCK(info.st_mode):
        raise SignerError('refusing to replace non-socket path ' + path)
    try:
        os.unlink(path)
    except OSError as exc:
        raise SignerError('cannot remove stale socket ' + path + ': ' + (exc.strerror or 'error')) from None
    return parent


def run_server(key=None, path=None, stop_event=None):
    '''Bind the Unix socket and serve until stop_event is set.'''
    if not hasattr(socket, 'AF_UNIX'):
        raise SignerError('Unix sockets are not available on this platform')
    if key is None:
        key = load_private_key()
    path = path or socket_path()
    stop_event = stop_event or threading.Event()
    parent = _prepare_socket(path)
    _grp_name = os.environ.get('LEDGER_SIGNER_GROUP', '').strip()
    if _grp_name:
        try:
            import grp as _grp_mod2
            _gid = _grp_mod2.getgrnam(_grp_name).gr_gid
            os.chown(parent, -1, _gid)
            os.chmod(parent, 0o750)
        except Exception as _exc:
            _log('warning: cannot set socket directory group %r: %s' % (_grp_name, _exc))
    if os.name == 'posix' and (os.stat(parent).st_mode & 0o002):
        _log('warning: socket directory is world-writable: ' + parent)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        server.bind(path)
        try:
            os.chmod(path, SOCKET_MODE)
        except OSError:
            pass
        _grp = os.environ.get('LEDGER_SIGNER_GROUP', '').strip()
        if _grp:
            try:
                import grp as _grp_mod
                os.chown(path, -1, _grp_mod.getgrnam(_grp).gr_gid)
            except Exception as _exc:
                _log('warning: cannot set socket group %r: %s' % (_grp, _exc))
        server.listen(16)
        server.settimeout(1.0)
        _log('listening on ' + path)
        while not stop_event.is_set():
            try:
                connection, _address = server.accept()
            except socket.timeout:
                continue
            except OSError:
                if stop_event.is_set():
                    break
                raise
            worker = threading.Thread(target=serve_connection, args=(connection, key), daemon=True)
            worker.start()
    finally:
        try:
            server.close()
        except OSError:
            pass
        try:
            os.unlink(path)
        except OSError:
            pass


def _install_stop_handlers(stop_event):
    def _stop(signum, frame):
        _log('received signal ' + str(signum) + ', stopping')
        stop_event.set()
    for name in ('SIGINT', 'SIGTERM'):
        sig = getattr(signal, name, None)
        if sig is None:
            continue
        try:
            signal.signal(sig, _stop)
        except (OSError, ValueError):
            pass


def check_config():
    '''Validate key, permissions and socket path without starting the server.'''
    result = {'ok': True}
    path = key_path()
    sock = socket_path()
    try:
        key = load_private_key(path)
        public_raw = key.public_key().public_bytes(serialization.Encoding.Raw,
                                                   serialization.PublicFormat.Raw)
        result['key_file'] = path
        if os.name == 'posix':
            result['key_mode'] = format(stat.S_IMODE(os.stat(path).st_mode), '04o')
        result['public_key_b64'] = public_key_b64(key)
        result['public_key_fingerprint'] = 'sha256:' + hashlib.sha256(public_raw).hexdigest()[:32]
    except SignerError as exc:
        result['ok'] = False
        result['error'] = str(exc)
    result['socket'] = sock
    try:
        if len(os.fsencode(sock)) >= 108:
            raise SignerError('socket path is too long for a Unix socket')
        if os.path.exists(sock) and not stat.S_ISSOCK(os.lstat(sock).st_mode):
            raise SignerError('socket path exists and is not a Unix socket')
        parent = os.path.dirname(os.path.abspath(sock))
        result['socket_dir'] = parent
        result['socket_dir_exists'] = os.path.isdir(parent)
        if os.path.isdir(parent) and os.name == 'posix' and (os.stat(parent).st_mode & 0o002):
            result['warning'] = 'socket directory is world-writable'
    except (SignerError, OSError) as exc:
        result['ok'] = False
        result.setdefault('error', str(exc))
    if not hasattr(socket, 'AF_UNIX'):
        result['ok'] = False
        result.setdefault('error', 'Unix sockets are not available on this platform')
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result.get('ok') else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ledger license signing service (Unix socket).')
    parser.add_argument('--check', action='store_true',
                        help='validate key permissions and socket configuration, then exit')
    args = parser.parse_args(argv)
    if args.check:
        return check_config()
    try:
        key = load_private_key()
    except SignerError as exc:
        _log(str(exc))
        return 1
    stop_event = threading.Event()
    _install_stop_handlers(stop_event)
    try:
        run_server(key=key, stop_event=stop_event)
    except SignerError as exc:
        _log(str(exc))
        return 1
    except OSError as exc:
        _log('cannot start signer: ' + str(exc))
        return 1
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    sys.exit(main())
