#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Перевірка входу: форма /api/login, cookie пристрою, Basic як запасний шлях."""
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "gt_auth_test")
PORT = 8803
URL = f"http://127.0.0.1:{PORT}"
PASS = "localtestpass123"
res = []


def ok(name, cond, extra=""):
    res.append(bool(cond))
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f" — {extra}"))


def req(path, method="GET", body=None, headers=None):
    h = {"User-Agent": "gt-auth-test"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    r = urllib.request.Request(URL + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def prepare():
    shutil.rmtree(BASE, ignore_errors=True)
    os.makedirs(BASE)
    for m in ("game_tracker.py", "taobao_core.py", "taobao.py", "ui.py", "platforms.py"):
        shutil.copy2(os.path.join(REPO, m), os.path.join(BASE, m))
    now = int(time.time())
    json.dump({"ts": now, "attempt": now, "ok": True}, open(os.path.join(BASE, ".gt_sup_ts.json"), "w"))
    json.dump({"auth_user": "admin", "auth_pass": PASS, "collector_token": "tok-test-123"},
              open(os.path.join(BASE, ".gt_secrets.json"), "w"))
    for f, v in ((".gt_pl.json", []), (".gt_eldorado.json", []), (".gt_settings.json", {}),
                 (".gt_tg.json", {}), (".gt_cache.json", {}), (".gt_suppliers.json", []),
                 (".gt_mail_queue.json", [])):
        json.dump(v, open(os.path.join(BASE, f), "w"))


def start():
    env = dict(os.environ)
    env.update({"GT_NO_BROWSER": "1", "PORT": str(PORT), "GT_BIND": "127.0.0.1",
                "PYTHONUNBUFFERED": "1"})
    env.pop("GT_AUTH", None)
    env.pop("GT_AUTH_NO_LIMIT", None)
    p = subprocess.Popen([sys.executable, "-X", "utf8", "game_tracker.py"], cwd=BASE,
                         env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace")
    for _ in range(40):
        time.sleep(0.5)
        try:
            st, _b, _h = req("/api/health")
            if st == 200:
                return p
        except Exception:
            pass
    p.kill()
    print("не стартував:\n" + (p.stdout.read() if p.stdout else "")[-1200:])
    sys.exit(1)


prepare()
proc = start()
try:
    print("── сторінка входу ──")
    st, body, _ = req("/")
    html = body.decode("utf-8", "replace")
    ok("GET / без входу → 200 (форма)", st == 200, st)
    ok("це саме форма входу", "Увійти" in html and "password" in html and "ACCOUNT TRACKER" not in html)
    st, body, _ = req("/api/pl")
    ok("API без входу → 401", st == 401, st)

    print("\n── вхід паролем ──")
    st, body, _ = req("/api/login", "POST", {"password": "wrong"})
    ok("невірний пароль → 401", st == 401, st)
    st, body, hdrs = req("/api/login", "POST", {"password": PASS})
    ok("правильний пароль → 200", st == 200, st)
    cookie = hdrs.get("Set-Cookie") or ""
    ok("видано cookie gt_device", "gt_device=" in cookie, cookie[:80])
    dev = cookie.split("gt_device=")[1].split(";")[0] if "gt_device=" in cookie else ""

    print("\n── пристрій запам'ятовано ──")
    st, body, _ = req("/", headers={"Cookie": "gt_device=" + dev})
    html = body.decode("utf-8", "replace")
    ok("GET / з cookie → 200 (застосунок)", st == 200 and "ACCOUNT TRACKER" in html, st)
    st, _b, _h = req("/api/pl", headers={"Cookie": "gt_device=" + dev})
    ok("API з cookie → 200", st == 200, st)
    st, _b, _h = req("/api/taobao?agent=1", headers={"X-GT-TOKEN": "tok-test-123"})
    ok("колектор з токеном → 200 (без сесії)", st == 200, st)
    st, _b, _h = req("/api/taobao?agent=1", headers={"X-GT-TOKEN": "wrong"})
    ok("колектор з чужим токеном → не 200", st != 200, st)
    st, _b, _h = req("/", headers={"Cookie": "gt_device=123.bad"})
    ok("підроблений cookie → форма входу (200)", st == 200, st)

    print("\n── Basic як запасний шлях + анти-брутфорс ──")
    token = base64.b64encode(f"admin:{PASS}".encode()).decode()
    st, _b, hdrs = req("/", headers={"Authorization": "Basic " + token})
    ok("Basic-пароль → 200", st == 200, st)
    codes = [req("/")[0] for _ in range(15)]
    ok("15 анонімних → 200 форми (без 429)", all(c == 200 for c in codes), codes[:5])
    st, _b, _h = req("/api/logout", "POST", {})
    ok("/api/logout → 200", st == 200, st)
finally:
    proc.kill()

print("\n" + "=" * 50)
print(f"ПІДСУМОК: {sum(res)}/{len(res)} перевірок пройдено")
sys.exit(0 if all(res) else 1)
