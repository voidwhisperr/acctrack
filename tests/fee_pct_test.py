"""Fee percentage and expenses regression tests (v1.1.0)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import game_tracker as g


def test_default_when_nothing_known():
    assert abs(g._fee_pct_of({"src": "zeusx", "sell": 100, "buy": 20}) - 0.10) < 1e-9


def test_recovers_from_after_fee():
    # old record: after 70 on sell 100 / buy 20 => 10% fee
    rec = {"src": "zeusx", "sell": 100, "buy": 20, "afterFee": 70}
    assert abs(g._fee_pct_of(rec) - 0.10) < 1e-9


def test_explicit_fraction_and_percent():
    assert abs(g._fee_pct_of({"src": "other", "feePct": 0.123}) - 0.123) < 1e-9
    assert abs(g._fee_pct_of({"src": "other", "feePct": 12.3}) - 0.123) < 1e-9


def test_clean_pl_persists_fee_pct():
    out = g._clean_pl([{
        "date": "2026-01-01", "src": "other", "sell": 100, "buy": 20,
        "feePct": 0.123,
    }])[0]
    assert abs(out["feePct"] - 0.123) < 1e-9
    assert abs(out["afterFee"] - 67.7) < 1e-9


def test_expenses_persist():
    out = g._clean_pl([{
        "date": "2026-01-01", "src": "other", "sell": 100, "buy": 20,
        "expenses": 5,
    }])[0]
    assert abs(out["expenses"] - 5) < 1e-9
    assert abs(out["afterFee"] - 80) < 1e-9


if __name__ == "__main__":
    test_default_when_nothing_known()
    test_recovers_from_after_fee()
    test_explicit_fraction_and_percent()
    test_clean_pl_persists_fee_pct()
    test_expenses_persist()
    print("fee_pct tests: ok")
