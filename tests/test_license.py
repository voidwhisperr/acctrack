"""License payload unit tests (no private signing key required)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import license as lic


def test_unpack_v1():
    raw = lic.pack_payload('plus', 30, ['auto_orders', 'taobao', 'hosted'])
    info = lic.unpack_payload(raw)
    assert info['plan'] == 'plus'
    assert info['bound'] is False
    assert 'auto_orders' in info['features']
    assert info['days_left'] in (29, 30)


def test_unpack_bound():
    raw = lic.pack_payload_bound('team', 30, ['auto_orders', 'taobao', 'hosted', 'team'], 'abc123')
    info = lic.unpack_payload(raw)
    assert info['plan'] == 'team'
    assert info['bound'] is True
    assert len(info['instance_hash']) == 16
    assert 'team' in info['features']


def test_bad_tokens_rejected():
    assert lic.verify('') is None
    assert lic.verify('LDG.bad.bad') is None
    assert lic.verify('nonsense') is None


def test_bound_requires_instance():
    raw = lic.pack_payload_bound('plus', 30, ['auto_orders'], 'abc123')
    code = lic.make_code(raw, b'\x00' * 64)
    assert lic.verify(code) is None



if __name__ == "__main__":
    import inspect as _inspect
    _failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print("ok", _name)
            except Exception as _e:
                _failed += 1
                print("FAIL", _name, _e)
    raise SystemExit(1 if _failed else 0)
