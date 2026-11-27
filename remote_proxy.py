"""Shared helpers for the Ledger desktop apps: DPAPI config + reverse proxy.

The proxy gives WebView2 a stable http://127.0.0.1 origin while every request
is forwarded to the real server. It can inject HTTP Basic auth, so the hosted
Ledger+ opens without a login form.

What the proxy guarantees on the wire:

* ``Origin``/``Referer`` are rewritten from the loopback proxy origin to the
  upstream origin, so the upstream CSRF check (Origin netloc == Host) accepts
  legitimate browser mutations instead of rejecting every POST/PUT/DELETE.
* The proxy's own ``gt_proxy`` capability cookie is never forwarded upstream
  and the upstream cannot overwrite it via ``Set-Cookie``.
* Upstream cookies are re-scoped for plain loopback HTTP: ``Secure`` and
  ``Domain`` are stripped, ``SameSite=None`` is downgraded to ``Lax`` (it
  would be rejected without ``Secure``) and the upstream one-year
  ``gt_device`` device-login cookie is capped so it does not sit for a year on
  the port-agnostic 127.0.0.1 cookie scope.
"""
import os
import re
import json
import time
import base64
import hmac
import socket
import threading
import urllib.request
import urllib.error
import urllib.parse
import pathlib

APP_DIR = pathlib.Path(os.environ.get("LEDGER_APP_DIR") or pathlib.Path.cwd())

PROXY_COOKIE = "gt_proxy"
DEVICE_COOKIE = "gt_device"
# The upstream sends gt_device with Max-Age=31536000 (one year). On the
# plain-HTTP, port-agnostic 127.0.0.1 cookie scope that is a durable stored
# credential; cap it to half a day instead. Re-login is transparent when the
# proxy injects Basic auth and otherwise costs one password entry per day.
DEVICE_COOKIE_MAX_AGE = 12 * 3600
_RESERVED_COOKIES = frozenset({PROXY_COOKIE})
_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})
_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")
_PROXY_PATH = "/__ledger_proxy__"


class ConfigError(ValueError):
    """Invalid desktop client configuration (bad server URL, unreadable config)."""


def _dpapi_entropy(bind):
    """Optional entropy that binds a DPAPI blob to a destination server URL."""
    b = str(bind or "").strip()
    if not b:
        return None
    return b"ledger-client-v1|" + b.encode("utf-8")


def _dpapi(data, protect=True, entropy=None):
    if os.name != "nt" or not data:
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class BLOB(ctypes.Structure):
            _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

        buf = ctypes.create_string_buffer(data, len(data))
        blob_in = BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
        blob_out = BLOB()
        ent_ptr = None
        if entropy:
            ent_buf = ctypes.create_string_buffer(entropy, len(entropy))
            ent_blob = BLOB(len(entropy), ctypes.cast(ent_buf, ctypes.POINTER(ctypes.c_char)))
            ent_ptr = ctypes.byref(ent_blob)
        fn = ctypes.windll.crypt32.CryptProtectData if protect else ctypes.windll.crypt32.CryptUnprotectData
        if not fn(ctypes.byref(blob_in), None, ent_ptr, None, None, 0, ctypes.byref(blob_out)):
            return None
        try:
            return ctypes.string_at(blob_out.pbData, blob_out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    except Exception:
        return None


def seal(text, bind=""):
    """DPAPI-encrypt a password for client.json.

    ``bind`` is the normalised server URL. When it is given, the blob can only
    be decrypted for that server (``unseal(value, bind=server)``), so editing
    the plaintext ``server`` field cannot redirect the saved password to
    another host. Without ``bind`` the legacy unbound format is produced;
    ``--set-password`` always binds.
    """
    raw = str(text or "").encode("utf-8")
    if not raw:
        raise RuntimeError("refusing to seal an empty password")
    entropy = _dpapi_entropy(bind)
    enc = _dpapi(raw, True, entropy)
    if enc is None:
        # Never silently store a plaintext fallback (b64) for a saved password.
        raise RuntimeError("Windows DPAPI unavailable; refusing to save the password")
    prefix = "dpapi2:" if entropy else "dpapi:"
    return prefix + base64.b64encode(enc).decode("ascii")


def sealed_kind(value):
    """Classify a stored credential: dpapi-bound / dpapi-legacy / b64 / plaintext / none."""
    s = str(value or "")
    if s.startswith("dpapi2:"):
        return "dpapi-bound"
    if s.startswith("dpapi:"):
        return "dpapi-legacy"
    if s.startswith("b64:"):
        return "b64"
    return "plaintext" if s else "none"


def _b64decode(text):
    try:
        return base64.b64decode(str(text or ""), validate=True)
    except Exception:
        return None


def unseal(value, bind="", warn=None):
    """Decrypt a saved client password.

    Only DPAPI blobs are accepted:

    * ``dpapi2:`` - bound to ``bind`` (the server URL); fails closed when the
      config was copied to another server.
    * ``dpapi:``  - legacy unbound blob from older configs; still decrypted so
      existing installs keep working, but reported through ``warn`` so the
      launcher can tell the user to re-save with ``--set-password``.
    * ``b64:`` / plaintext - refused with a warning (base64 is not encryption;
      a plaintext password in client.json is what this fix exists to stop).

    Returns "" when nothing usable is stored. ``warn`` is an optional callable
    receiving a human-readable warning string.
    """
    s = str(value or "")
    kind = sealed_kind(s)
    if kind == "none":
        return ""
    if kind == "dpapi-bound":
        blob = _b64decode(s[7:])
        raw = _dpapi(blob, False, _dpapi_entropy(bind)) if blob else None
        if not raw:
            if warn:
                warn("saved password could not be decrypted for this server "
                     "(was client.json copied or edited?); ignoring it")
            return ""
        return raw.decode("utf-8", "replace")
    if kind == "dpapi-legacy":
        blob = _b64decode(s[6:])
        raw = _dpapi(blob, False) if blob else None
        if not raw:
            if warn:
                warn("saved password could not be decrypted; ignoring it")
            return ""
        if warn:
            warn("saved password uses an old DPAPI blob that is not bound to the "
                 "server; re-save it with --set-password")
        return raw.decode("utf-8", "replace")
    if warn:
        warn("refusing unencrypted 'pass' value (%s); store it with --set-password"
             " (DPAPI-encrypted and server-bound)" % kind)
    return ""


def normalize_server_url(raw):
    """Validate a client.json / ledger.client.json server URL.

    Only ``http``/``https`` are allowed, embedded credentials are rejected,
    and plain ``http`` is accepted only for loopback hosts (127.0.0.1,
    localhost, ::1) - everything else must use TLS. A missing scheme is
    treated as ``https``. Returns the normalised base URL without a trailing
    slash and without query/fragment. Raises :class:`ConfigError`.
    """
    s = str(raw or "").strip()
    if not s:
        raise ConfigError("server URL is empty")
    if not _SCHEME_RE.match(s):
        s = "https://" + s
    try:
        p = urllib.parse.urlsplit(s)
    except Exception as e:
        raise ConfigError("invalid server URL: %s" % e)
    scheme = (p.scheme or "").lower()
    if scheme not in ("http", "https"):
        raise ConfigError("server URL must use http or https, not %r" % (p.scheme or "?"))
    if p.username or p.password:
        raise ConfigError("server URL must not contain a username or password")
    host = (p.hostname or "").lower()
    if not host:
        raise ConfigError("server URL has no host")
    try:
        p.port
    except ValueError:
        raise ConfigError("server URL has an invalid port") from None
    if p.query or p.fragment:
        raise ConfigError("server URL must not contain a query or fragment")
    loopback = host in _LOOPBACK_HOSTS or host.endswith(".localhost")
    if scheme != "https" and not loopback:
        raise ConfigError("plain http is only allowed for loopback servers; use https:// for %s" % host)
    netloc = p.netloc.lower()
    return "%s://%s%s" % (scheme, netloc, p.path.rstrip("/"))


def _origin_of(url):
    try:
        p = urllib.parse.urlsplit(str(url or ""))
    except Exception:
        return ""
    if not p.scheme or not p.netloc:
        return ""
    return "%s://%s" % (p.scheme.lower(), p.netloc.lower())


def _without_reserved_cookies(cookie):
    """Drop proxy-private cookies (the capability token) from a Cookie header."""
    keep = []
    for part in str(cookie or "").split(";"):
        item = part.strip()
        if not item:
            continue
        name = item.split("=", 1)[0].strip().lower()
        if name in _RESERVED_COOKIES:
            continue
        keep.append(item)
    return "; ".join(keep)


def _rewrite_origin(value, local_origins, target_origin):
    """Map a loopback proxy Origin to the upstream origin ("" = drop header)."""
    origin = _origin_of(value)
    return target_origin if origin and origin in local_origins else ""


def _rewrite_referer(value, local_origins, target_origin):
    """Map a loopback proxy Referer to the upstream origin ("" = drop header)."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        p = urllib.parse.urlsplit(raw)
    except Exception:
        return ""
    if _origin_of(raw) not in local_origins:
        return ""
    path = p.path or "/"
    if path == _PROXY_PATH:
        # The first navigation carries the capability token in the query. Never
        # forward it upstream, not even as a Referer.
        return target_origin + "/"
    out = target_origin + path
    if p.query:
        out += "?" + p.query
    return out


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

    remote = str(remote or "").rstrip("/")
    if not remote:
        raise ConfigError("remote server URL is empty")
    upstream_origin = _origin_of(remote)
    token = _secrets.token_urlsafe(24)
    auth = ""
    if user or password:
        auth = "Basic " + base64.b64encode(("%s:%s" % (user, password)).encode("utf-8")).decode("ascii")

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "LedgerDesktop"

        def log_message(self, *a):
            pass

        def _rewrite_location(self, value):
            loc = str(value or "").strip()
            if not loc or loc.startswith("/"):
                return loc
            try:
                p = urllib.parse.urlsplit(loc)
            except Exception:
                return loc
            if not p.scheme or not p.netloc or _origin_of(loc) != upstream_origin:
                return loc
            base = urllib.parse.urlsplit(remote)
            path = p.path or "/"
            base_path = base.path.rstrip("/")
            if base_path and path.startswith(base_path):
                path = path[len(base_path):] or "/"
            out = path
            if p.query:
                out += "?" + p.query
            if p.fragment:
                out += "#" + p.fragment
            return out

        def _rewrite_set_cookie(self, value):
            """Re-scope an upstream cookie for the plain-HTTP loopback origin.

            Returns None when the cookie must be dropped (the proxy reserves
            its own capability-cookie name).
            """
            raw = str(value or "").strip()
            if not raw:
                return None
            parts = [x.strip() for x in raw.split(";")]
            pair = parts[0]
            name = pair.split("=", 1)[0].strip()
            if not name or name.lower() in _RESERVED_COOKIES:
                return None
            out = [pair]
            same_site_none = False
            for attr in parts[1:]:
                if not attr:
                    continue
                key, _, val = attr.partition("=")
                lk = key.strip().lower()
                if lk == "secure":
                    continue          # the proxy origin is plain http loopback
                if lk == "domain":
                    continue          # re-scope as host-only 127.0.0.1 cookie
                if lk == "samesite":
                    if val.strip().lower() == "none":
                        same_site_none = True
                        continue
                    out.append(attr)
                    continue
                if name.lower() == DEVICE_COOKIE and lk in ("max-age", "expires"):
                    continue          # replaced by the capped lifetime below
                out.append(attr)
            if same_site_none:
                # SameSite=None requires Secure, which cannot survive on the
                # plain-http loopback origin, so downgrade to Lax.
                out.append("SameSite=Lax")
            if name.lower() == DEVICE_COOKIE:
                out.append("Max-Age=%d" % DEVICE_COOKIE_MAX_AGE)
            return "; ".join(out)

        def _copy(self, headers):
            for k, v in headers.items():
                lk = k.lower()
                if lk in ("connection", "keep-alive", "transfer-encoding", "content-length",
                          "proxy-connection", "content-encoding", "server", "date"):
                    continue
                if lk == "location":
                    v = self._rewrite_location(v)
                elif lk == "set-cookie":
                    v = self._rewrite_set_cookie(v)
                    if v is None:
                        continue
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
            if host not in local_hosts:
                return False
            origin = (self.headers.get("Origin") or "").lower()
            if origin and origin not in local_origins:
                return False
            cookie = self.headers.get("Cookie") or ""
            for part in cookie.split(";"):
                k, _, v = part.strip().partition("=")
                if k == PROXY_COOKIE:
                    return hmac.compare_digest(v, token)
            return False

        def _serve(self):
            path = self.path.split("?", 1)[0]
            if path == _PROXY_PATH:
                qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
                if (qs.get("t") or [""])[0] != token:
                    return self._deny()
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header("Set-Cookie", "%s=%s; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400" % (PROXY_COOKIE, token))
                self.send_header("Cache-Control", "no-store")
                self.send_header("Referrer-Policy", "no-referrer")
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
                lk = k.lower()
                if lk in ("host", "connection", "proxy-connection", "accept-encoding", "authorization"):
                    continue
                if lk == "cookie":
                    v = _without_reserved_cookies(v)
                    if not v:
                        continue
                elif lk == "origin":
                    v = _rewrite_origin(v, local_origins, upstream_origin)
                    if not v:
                        continue
                elif lk == "referer":
                    v = _rewrite_referer(v, local_origins, upstream_origin)
                    if not v:
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
    local_hosts = ("127.0.0.1:%d" % port, "localhost:%d" % port)
    local_origins = ("http://127.0.0.1:%d" % port, "http://localhost:%d" % port)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True, name="ledger-proxy").start()
    return port, "http://127.0.0.1:%d%s?t=%s" % (port, _PROXY_PATH, token)


def load_config(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def cli_set_password(config_path):
    """Interactive ``--set-password`` helper: store a server-bound DPAPI password.

    Run it from a source checkout console::

        python ledger_client.py --set-password
        python desktop.py --set-password

    (frozen GUI builds have no console, so this is mainly a source/tooling
    path). Returns a human-readable status line; raises on failure.
    """
    import getpass
    path = pathlib.Path(config_path)
    cfg = load_config(path)
    if not isinstance(cfg, dict):
        cfg = {}
    server_raw = str(cfg.get("server") or "").strip()
    if not server_raw:
        server_raw = input("Server URL (https://...): ").strip()
    server = normalize_server_url(server_raw)
    user = str(cfg.get("user") or "").strip()
    if not user:
        user = input("User [admin]: ").strip() or "admin"
    pw1 = getpass.getpass("Password: ")
    pw2 = getpass.getpass("Repeat password: ")
    if not pw1 or pw1 != pw2:
        raise ConfigError("passwords are empty or do not match; nothing saved")
    cfg["server"] = server
    cfg["user"] = user
    cfg["pass"] = seal(pw1, bind=server)
    try:
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:
        raise ConfigError("could not write %s: %s" % (path, e))
    return "saved DPAPI password bound to %s in %s" % (server, path)

