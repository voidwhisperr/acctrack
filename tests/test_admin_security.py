#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused security tests for /admin and /hosting auth in game_tracker.py.

Covers:
  * token-in-URL is exchanged for a signed HttpOnly cookie and never authorizes actions;
  * GET on action endpoints is rejected (405);
  * POST without the admin cookie or without the cookie-bound CSRF is rejected (403);
  * a valid cookie + CSRF performs a real action against a throwaway instance;
  * shell-injection payloads in name/subdomain/port/id are rejected by validation.

The test starts its own copy of the app in %TEMP% on a free loopback port and
kills it afterwards; it never touches the user's running services or real data.
"""
import importlib.util
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "gt_admin_security_test")
sys.path.insert(0, BASE)   # import modules from the throwaway copy, not from tests/
ADMIN_TOKEN = secrets.token_hex(16)   # test-only value, never printed
TEST_KEY = "testkey-0123456789abcdef"
results = []


def _free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


PORT = _free_port()
URL = "http://127.0.0.1:%d" % PORT


def check(name, cond, extra=""):
    results.append((name, bool(cond), extra))
    print(("  \u2713 " if cond else "  \u2717 ") + name
          + ((" \u2014 " + str(extra)) if extra and not cond else ""))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def req(path, method="GET", form=None, headers=None, timeout=15):
    data = None
    h = {"User-Agent": "gt-admin-security-test"}
    if form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        h["Content-Type"] = "application/x-www-form-urlencoded"
    h.update(headers or {})
    r = urllib.request.Request(URL + path, data=data, headers=h, method=method)
    try:
        with _opener.open(r, timeout=timeout) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def hget(hd, name):
    for k, v in (hd or {}).items():
        if k.lower() == name.lower():
            return v
    return ""


def text(raw):
    return raw.decode("utf-8", "replace")


def csrf_from(html):
    m = re.search(r"name='csrf' value='([^']+)'", html)
    return m.group(1) if m else ""


def read_json(name, default):
    try:
        with open(os.path.join(BASE, name), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return default


def prepare():
    shutil.rmtree(BASE, ignore_errors=True)
    os.makedirs(BASE, exist_ok=True)
    for mod in ("game_tracker.py", "taobao_core.py", "taobao.py", "ui.py", "platforms.py"):
        src = os.path.join(REPO, mod)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(BASE, mod))
    now = int(time.time())
    json.dump({"ts": now, "attempt": now, "ok": True},
              open(os.path.join(BASE, ".gt_sup_ts.json"), "w"))
    json.dump({"auth_user": "admin", "auth_pass": "localtestpass123",
               "collector_token": "tok-test-123",
               "license_admin_token": ADMIN_TOKEN},
              open(os.path.join(BASE, ".gt_secrets.json"), "w"))
    json.dump([], open(os.path.join(BASE, ".gt_clients.json"), "w"))
    json.dump({"keys": {TEST_KEY: {"plan": "solo", "exp": "2027-01-01",
                                    "revoked": False}}},
              open(os.path.join(BASE, ".gt_license_registry.json"), "w"))
    for f, v in ((".gt_pl.json", []), (".gt_eldorado.json", []),
                 (".gt_goal.json", {}), (".gt_mailq.json", []),
                 (".gt_settings.json", {}), (".gt_tg.json", {}),
                 (".gt_cache.json", {}), (".gt_suppliers.json", []),
                 (".gt_payments.json", [])):
        json.dump(v, open(os.path.join(BASE, f), "w"))


def start():
    env = dict(os.environ)
    env.update({"GT_NO_BROWSER": "1", "GT_AUTH": "off", "GT_NO_SUPPLIERS": "1",
                "PORT": str(PORT), "GT_BIND": "127.0.0.1", "PYTHONUNBUFFERED": "1"})
    p = subprocess.Popen([sys.executable, "-X", "utf8", "game_tracker.py"],
                         cwd=BASE, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                         errors="replace")
    for _ in range(60):
        time.sleep(0.5)
        try:
            st, _b, _h = req("/api/health", timeout=3)
            if st == 200:
                return p
        except Exception:
            pass
    p.kill()
    out = p.stdout.read() if p.stdout else ""
    print("SERVER DID NOT START:\n" + out[-3000:])
    sys.exit(1)


def load_module():
    spec = importlib.util.spec_from_file_location("gt_admin_unit",
                                                  os.path.join(BASE, "game_tracker.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    prepare()
    proc = start()
    log = ""
    try:
        print("\n\u2500\u2500 login page / token bootstrap \u2500\u2500")
        st, body, hd = req("/admin")
        html = text(body)
        check("GET /admin without cookie -> token form (200)",
              st == 200 and "placeholder='admin token'" in html, st)
        check("GET /admin without cookie sets no cookie",
              "gt_admin=" not in hget(hd, "set-cookie"))
        st, _b, hd = req("/admin?token=" + urllib.parse.quote("wrong-token"))
        check("GET /admin?token=wrong -> 403", st == 403, st)
        check("wrong token sets no admin cookie",
              "gt_admin=" not in hget(hd, "set-cookie"))

        st, _b, hd = req("/admin?token=" + urllib.parse.quote(ADMIN_TOKEN))
        loc = hget(hd, "location")
        sc = hget(hd, "set-cookie")
        check("valid token -> 302 redirect", st == 302, st)
        check("redirect drops the token", loc == "/admin", loc)
        check("signed admin cookie issued", "gt_admin=" in sc, sc[:40])
        slow = sc.lower()
        check("cookie is HttpOnly", "httponly" in slow)
        check("cookie is SameSite=Strict", "samesite=strict" in slow)
        check("cookie is not Secure over plain http", "secure" not in slow)
        cval = sc.split("gt_admin=", 1)[1].split(";")[0] if "gt_admin=" in sc else ""
        parts = cval.split(".")
        check("cookie value is signed (v1.ts.nonce.hmac)",
              len(parts) == 4 and parts[0] == "v1" and len(parts[3]) == 64, cval[:24])
        cookie = "gt_admin=" + cval

        print("\n\u2500\u2500 cookie-authenticated pages, POST forms + CSRF \u2500\u2500")
        st, body, _hd = req("/admin", headers={"Cookie": cookie})
        ahtml = text(body)
        check("GET /admin with cookie -> dashboard (200)",
              st == 200 and "Payments" in ahtml, st)
        check("admin page contains no token URL links", "?token=" not in ahtml)
        check("admin action is a POST form",
              "method='post' action='/admin/revoke'" in ahtml)
        acsrf = csrf_from(ahtml)
        check("admin page embeds a CSRF value", bool(acsrf))
        check("CSRF value equals the nonce inside the cookie",
              bool(acsrf) and acsrf == parts[2] if len(parts) == 4 else False)

        st, body, _hd = req("/hosting", headers={"Cookie": cookie})
        hhtml = text(body)
        check("GET /hosting with cookie -> dashboard (200)",
              st == 200 and "Hosting clients" in hhtml, st)
        check("hosting page contains no token URL links", "?token=" not in hhtml)
        posts = ("/hosting/save", "/hosting/provision", "/hosting/monitor")
        check("hosting forms are POST with CSRF",
              all(("method='post' action='%s'" % x) in hhtml for x in posts)
              and "name='csrf'" in hhtml, posts)
        hcsrf = csrf_from(hhtml)
        check("hosting CSRF equals cookie nonce", hcsrf == acsrf)

        st, body, _hd = req("/admin", headers={"Cookie": cookie + "zz"})
        check("tampered admin cookie -> token form, no dashboard",
              st == 200 and "placeholder='admin token'" in text(body)
              and "Payments" not in text(body), st)

        st, _b, hd = req("/hosting?token=" + urllib.parse.quote(ADMIN_TOKEN))
        check("GET /hosting?token=valid -> 302 /hosting",
              st == 302 and hget(hd, "location") == "/hosting", st)
        st, _b, _h = req("/hosting?token=" + urllib.parse.quote("wrong"))
        check("GET /hosting?token=wrong -> 403", st == 403, st)

        print("\n\u2500\u2500 URL token cannot perform GET actions \u2500\u2500")
        action_gets = (
            "/hosting/check?id=0123456789ab",
            "/hosting/backup?id=0123456789ab",
            "/hosting/restore?id=0123456789ab",
            "/hosting/delete?id=0123456789ab",
            "/hosting/save?name=URLTokenHack",
            "/hosting/provision?name=URLTokenHack",
            "/hosting/monitor",
            "/admin/revoke?key_id=" + TEST_KEY,
        )
        for path in action_gets:
            sep = "&" if "?" in path else "?"
            st, _b, _h = req(path + sep + "token=" + urllib.parse.quote(ADMIN_TOKEN))
            check("GET %s -> 405" % path.split("?")[0], st == 405, st)
        clients = read_json(".gt_clients.json", [])
        check("token-in-URL GET did not create a client",
              not any(str(c.get("name")) == "URLTokenHack" for c in clients))
        reg = read_json(".gt_license_registry.json", {"keys": {}})
        check("token-in-URL GET did not revoke a key",
              reg.get("keys", {}).get(TEST_KEY, {}).get("revoked") is False)

        print("\n\u2500\u2500 POST actions require cookie + bound CSRF \u2500\u2500")
        st, _b, _h = req("/hosting/save", "POST", form={"name": "NoCookieNoCsrf"})
        check("POST action without cookie/csrf -> 403", st == 403, st)
        st, _b, _h = req("/hosting/save", "POST",
                         form={"csrf": acsrf, "name": "NoCookie"})
        check("POST action with CSRF but no cookie -> 403", st == 403, st)
        st, _b, _h = req("/hosting/save", "POST", form={"name": "NoCsrf"},
                         headers={"Cookie": cookie})
        check("POST action with cookie but no CSRF -> 403", st == 403, st)
        st, _b, _h = req("/hosting/save", "POST",
                         form={"csrf": "bogus", "name": "BadCsrf"},
                         headers={"Cookie": cookie})
        check("POST action with wrong CSRF -> 403", st == 403, st)
        st, _b, _h = req("/admin/revoke", "POST", form={"key_id": TEST_KEY},
                         headers={"Cookie": cookie})
        check("POST /admin/revoke without CSRF -> 403", st == 403, st)
        st, _b, _h = req("/hosting/save?token=" + urllib.parse.quote(ADMIN_TOKEN),
                         "POST", form={"csrf": acsrf, "name": "TokenOnly"})
        check("POST action authorized by URL token only -> 403", st == 403, st)
        st, _b, _h = req("/hosting/save", "POST",
                         form={"csrf": acsrf, "name": "CrossOrigin"},
                         headers={"Cookie": cookie,
                                  "Origin": "http://evil.example"})
        check("cross-origin POST with valid cookie+CSRF -> 403", st == 403, st)
        clients = read_json(".gt_clients.json", [])
        check("rejected POSTs did not mutate client state",
              not any(str(c.get("name")) in ("NoCookie", "NoCsrf", "BadCsrf",
                                              "TokenOnly", "CrossOrigin")
                      for c in clients))
        reg = read_json(".gt_license_registry.json", {"keys": {}})
        check("rejected POST did not revoke the key",
              reg.get("keys", {}).get(TEST_KEY, {}).get("revoked") is False)

        print("\n\u2500\u2500 valid cookie + CSRF performs real actions \u2500\u2500")
        st, _b, hd = req("/hosting/save", "POST",
                         form={"csrf": hcsrf, "name": "Valid Client",
                               "plan": "solo", "paid_until": "2027-01-01",
                               "notes": "created by test"},
                         headers={"Cookie": cookie})
        check("POST /hosting/save -> 303 to /hosting",
              st == 303 and hget(hd, "location") == "/hosting", st)
        clients = read_json(".gt_clients.json", [])
        rec = next((c for c in clients if c.get("name") == "Valid Client"), None)
        check("client persisted to the temp instance", rec is not None)
        cid = str((rec or {}).get("id") or "")
        check("generated client id is 8..16 hex",
              bool(re.fullmatch(r"[0-9a-f]{8,16}", cid)), cid)
        st, body, _hd = req("/hosting", headers={"Cookie": cookie})
        check("saved client is shown on /hosting", "Valid Client" in text(body))
        st, _b, hd = req("/hosting/check", "POST", form={"csrf": hcsrf, "id": cid},
                         headers={"Cookie": cookie})
        check("POST /hosting/check with cookie+CSRF -> 303",
              st == 303 and hget(hd, "location") == "/hosting", st)
        st, _b, hd = req("/admin/revoke", "POST",
                         form={"csrf": acsrf, "key_id": TEST_KEY},
                         headers={"Cookie": cookie})
        check("POST /admin/revoke with cookie+CSRF -> 303",
              st == 303 and hget(hd, "location") == "/admin", st)
        reg = read_json(".gt_license_registry.json", {"keys": {}})
        check("key was actually revoked",
              reg.get("keys", {}).get(TEST_KEY, {}).get("revoked") is True)

        print("\n\u2500\u2500 shell-injection payloads are rejected \u2500\u2500")
        marker = os.path.join(BASE, "pwned-marker")
        payloads = (
            ("name semicolon", {"name": "Evil; touch " + marker, "subdomain": "", "port": ""}),
            ("name backticks", {"name": "Evil`touch " + marker + "`", "subdomain": "", "port": ""}),
            ("subdomain semicolon", {"name": "Evil", "subdomain": "x; touch " + marker, "port": ""}),
            ("subdomain $()", {"name": "Evil", "subdomain": "$(touch " + marker + ")", "port": ""}),
            ("subdomain newline", {"name": "Evil", "subdomain": "x\ntouch " + marker, "port": ""}),
            ("port out of range", {"name": "Evil", "subdomain": "", "port": "80"}),
            ("port non-numeric", {"name": "Evil", "subdomain": "", "port": "abc"}),
        )
        for label, fields in payloads:
            form = {"csrf": hcsrf}
            form.update(fields)
            st, body, _h = req("/hosting/provision", "POST", form=form,
                               headers={"Cookie": cookie})
            check("provision %s payload -> 400" % label, st == 400, st)
        check("injection payload created no marker file",
              not os.path.exists(marker), marker)
        clients = read_json(".gt_clients.json", [])
        check("rejected provision attempts created no client record",
              not any(str(c.get("name")) == "Evil" for c in clients))
        for bad_id in ("abc;touch " + marker, "../../etc/passwd", "XYZ", ""):
            st, _b, _h = req("/hosting/delete", "POST",
                             form={"csrf": hcsrf, "id": bad_id},
                             headers={"Cookie": cookie})
            check("delete id %r -> 400" % bad_id[:18], st == 400, st)
        check("delete validation created no marker",
              not os.path.exists(marker))

        print("\n\u2500\u2500 public pages unaffected \u2500\u2500")
        st, body, _hd = req("/pricing")
        check("GET /pricing still 200", st == 200 and "Ledger" in text(body), st)
        st, _b, _h = req("/join?token=bogus")
        check("GET /join with bad invite still 400", st == 400, st)

        print("\n\u2500\u2500 direct validation unit checks \u2500\u2500")
        gt = load_module()
        bad = (
            ("name", ("Evil; touch " + marker, 0, "")),
            ("name newline", ("Evil\nrm -rf /", 0, "")),
            ("subdomain", ("ok", 0, "x;touch " + marker)),
            ("subdomain $()", ("ok", 0, "$(id)")),
            ("subdomain path", ("ok", 0, "../../etc")),
            ("subdomain uppercase", ("ok", 0, "Client.Example.com")),
            ("port 80", ("ok", 80, "")),
            ("port 70000", ("ok", 70000, "")),
            ("port text", ("ok", "1;id", "")),
        )
        for label, args in bad:
            try:
                gt._validate_instance_params(*args)
                ok = False
            except ValueError:
                ok = True
            except Exception:
                ok = False
            check("validator rejects %s" % label, ok)
        try:
            got = gt._validate_instance_params("\u041a\u043b\u0456\u0454\u043d\u0442 1", 0,
                                              "client1.70-34-243-50.sslip.io")
            ok = got == ("\u041a\u043b\u0456\u0454\u043d\u0442 1", 0,
                         "client1.70-34-243-50.sslip.io")
        except Exception:
            ok = False
        check("validator accepts a normal name and FQDN subdomain", ok)
        check("_valid_client_id accepts hex, rejects shell text",
              gt._valid_client_id("0123456789ab")
              and not gt._valid_client_id("0123456789ab;id"))
        rc, out, err = gt._run([sys.executable, "-c", "print(1)"])
        check("_run executes an argv list without a shell",
              rc == 0 and out.strip() == "1", (rc, out, err))
    finally:
        try:
            time.sleep(0.3)
            proc.kill()
            log = proc.stdout.read() if proc.stdout else ""
        except Exception:
            pass

    errs = [ln for ln in (log or "").splitlines()
            if "Traceback" in ln or "SyntaxError" in ln]
    if errs:
        print("\nserver tracebacks:")
        for ln in errs[-5:]:
            print("  " + ln[:160])

    passed = sum(1 for _n, ok, _e in results if ok)
    print("\n" + "=" * 56)
    print("RESULT: %d/%d checks passed" % (passed, len(results)))
    fails = [(n, e) for n, ok, e in results if not ok]
    if fails:
        print("FAILURES:")
        for n, e in fails:
            print("  x", n, "-", e)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
