"""Shared helpers for the Ledger desktop apps: DPAPI config + reverse proxy.

The proxy gives WebView2 a stable http://127.0.0.1 origin while every request
is forwarded to the real server. It can inject HTTP Basic auth, so the hosted
Ledger+ opens without a login form, and it strips Secure/Domain from cookies so
the session survives on localhost.
"""
import os
import json
import time
import base64
import hmac
import socket
import threading
import urllib.request
import urllib.error
import pathlib

APP_DIR = pathlib.Path(os.environ.get("LEDGER_APP_DIR") or pathlib.Path.cwd())


def _dpapi(data, protect=True):
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

        buf = ctypes.create_string_buffer(data, len(data))
        blob_in = BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        blob_out = BLOB()
        fn = ctypes.windll.crypt32.CryptProtectData if protect else ctypes.windll.crypt32.CryptUnprotectData
        if not fn(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            return None
        try:
            return ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    except Exception:
        return None


def seal(text):
    raw = str(text or "").encode("utf-8")
    enc = _dpapi(raw, True)
    if enc is None:
        # Never silently store a plaintext fallback (b64) for a saved password.
        raise RuntimeError("Windows DPAPI unavailable; refusing to save the password")
    return "dpapi:" + base64.b64encode(enc).decode("ascii")


def unseal(value):
    s = str(value or "")
    try:
        if s.startswith("dpapi:"):
            raw = _dpapi(base64.b64decode(s[6:]), False)
            return raw.decode("utf-8") if raw else ""
        if s.startswith("b64:"):
            return base64.b64decode(s[4:]).decode("utf-8")
    except Exception:
        pass
    return s


def free_port(start):
    for port in range(int(start), int(start) + 40):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", port))
            return port
        except OSError:
            continue
        finally:
            s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def health(url, timeout=1.2):
    try:
        with urllib.request.urlopen(str(url).rstrip("/") + "/api/health", timeout=timeout) as r:
            if r.status != 200:
                return False
            return bool(json.loads(r.read().decode("utf-8", "replace") or "{}").get("ok"))
    except Exception:
        return False


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(_NoRedirect)


def start_proxy(remote, user="", password="", title="Ledger"):
    import http.server
    import secrets as _secrets
    import urllib.parse as _urlparse

    remote = remote.rstrip("/")
    token = _secrets.token_urlsafe(24)
    auth = ""
    if user or password:
        auth = "Basic " + base64.b64encode(("%s:%s" % (user, password)).encode("utf-8")).decode("ascii")

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "LedgerDesktop"

        def log_message(self, *a):
            pass

        def _copy(self, headers):
            for k, v in headers.items():
                lk = k.lower()
                if lk in ("connection", "keep-alive", "transfer-encoding", "content-length",
                          "proxy-connection", "content-encoding", "server", "date"):
                    continue
                if lk == "location" and v.startswith(remote):
                    v = v[len(remote):] or "/"
                if lk == "set-cookie":
                    v = v.replace("; Secure", "").replace("; secure", "")
                    import re as _re
                    v = _re.sub(r";\s*Domain=[^;]+", "", v, flags=_re.I)
                self.send_header(k, v)

        def _deny(self):
            data = b"403 forbidden"
            self.send_response(403)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _proxy_ok(self):
            host = (self.headers.get("Host") or "").lower()
            if host not in ("127.0.0.1:%d" % port, "localhost:%d" % port):
                return False
            origin = (self.headers.get("Origin") or "").lower()
            if origin and not (origin == "http://127.0.0.1:%d" % port or origin == "http://localhost:%d" % port):
                return False
            cookie = self.headers.get("Cookie") or ""
            for part in cookie.split(";"):
                k, _, v = part.strip().partition("=")
                if k == "gt_proxy":
                    return hmac.compare_digest(v, token)
            return False

        def _serve(self):
            path = self.path.split("?", 1)[0]
            if path == "/__ledger_proxy__":
                qs = _urlparse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
                if (qs.get("t") or [""])[0] != token:
                    return self._deny()
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", "gt_proxy=%s; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400" % token)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if not self._proxy_ok():
                return self._deny()
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except Exception:
                length = 0
            body = self.rfile.read(length) if length else None
            hdrs = {}
            for k, v in self.headers.items():
                if k.lower() in ("host", "connection", "proxy-connection", "accept-encoding", "authorization"):
                    continue
                hdrs[k] = v
            hdrs["Accept-Encoding"] = "identity"
            if auth:
                hdrs["Authorization"] = auth
            req = urllib.request.Request(remote + self.path, data=body, headers=hdrs, method=self.command)
            try:
                resp = OPENER.open(req, timeout=90)
                data = resp.read()
                self.send_response(resp.status)
                self._copy(resp.headers)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(data)
            except urllib.error.HTTPError as e:
                data = e.read() or b""
                self.send_response(e.code)
                self._copy(e.headers)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(data)
            except Exception as e:
                page = ("<!doctype html><meta charset=utf-8><title>%s</title>"
                        "<body style='font:16px Manrope,system-ui;background:#0d1017;color:#e9ebf2;padding:40px'>"
                        "<h2>%s</h2><p style='color:#8b95a9'>%s</p>"
                        "<p style='color:#8b95a9'>Перевірте інтернет і адресу сервера.</p>"
                        "<button onclick='location.reload()' style='padding:10px 18px;font-size:15px;border-radius:8px'>"
                        "Повторити</button></body>") % (title, title + " недоступний", str(e)[:300])
                data = page.encode("utf-8")
                self.send_response(502)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        do_GET = _serve
        do_POST = _serve
        do_PUT = _serve
        do_DELETE = _serve
        do_HEAD = _serve

    port = free_port(18766)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True, name="ledger-proxy").start()
    return port, "http://127.0.0.1:%d/__ledger_proxy__?t=%s" % (port, token)


def load_config(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
