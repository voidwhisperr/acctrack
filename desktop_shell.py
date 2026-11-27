"""Small Windows desktop-shell features shared by Ledger and Ledger+.

No webview imports here: callers pass window/tray objects in.
"""
import ctypes
import json
import os
import sys
import threading
import time
import urllib.request
import webbrowser

APP_NAME = "Ledger"


def _http_json(url, auth=None, timeout=5):
    req = urllib.request.Request(url, headers={"User-Agent": "LedgerDesktop/1"})
    if auth:
        import base64
        req.add_header("Authorization", "Basic " + base64.b64encode(
            (str(auth[0]) + ":" + str(auth[1])).encode("utf-8")).decode("ascii"))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _set_title(window, tray, base, n):
    t = (base + " · " + str(n)) if n else base
    try:
        if hasattr(window, "set_title"):
            window.set_title(t)
    except Exception:
        pass
    try:
        window.evaluate_js("document.title=" + json.dumps(t))
    except Exception:
        pass
    try:
        if tray is not None:
            tray.title = t
    except Exception:
        pass


def badge_loop(api_url, base_title, window, tray_getter, auth=None):
    """Poll new-order count and show it in the native title/tray tooltip."""
    last = None
    while True:
        try:
            d = _http_json(api_url.rstrip("/") + "/api/mail/queue?desktop=1&t=" + str(int(time.time())), auth)
            n = int(d.get("new") or 0) if isinstance(d, dict) else 0
            if n != last:
                _set_title(window, tray_getter(), base_title, n)
                last = n
        except Exception:
            pass
        time.sleep(20)


def _run_key():
    import winreg
    return winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"


def autostart_enabled():
    if os.name != "nt":
        return False
    try:
        import winreg
        h, path = _run_key()
        with winreg.OpenKey(h, path, 0, winreg.KEY_READ) as k:
            winreg.QueryValueEx(k, "Ledger")
        return True
    except Exception:
        return False


def set_autostart(enabled, exe=None):
    if os.name != "nt":
        return False
    try:
        import winreg
        h, path = _run_key()
        with winreg.OpenKey(h, path, 0, winreg.KEY_SET_VALUE) as k:
            if enabled:
                cmd = '"' + str(exe or sys.executable) + '" --tray'
                winreg.SetValueEx(k, "Ledger", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(k, "Ledger")
                except FileNotFoundError:
                    pass
        return True
    except Exception:
        return False


def latest_release():
    try:
        d = _http_json("https://api.github.com/repos/voidwhisperr/ledger/releases/latest", timeout=8)
        return str(d.get("tag_name") or ""), str(d.get("html_url") or "")
    except Exception:
        return "", ""


def open_release():
    tag, url = latest_release()
    if url:
        webbrowser.open(url)
    return tag, url


def register_hotkeys(on_show, on_new_deal):
    """Ctrl+Alt+L opens the window; Ctrl+Alt+N opens a new-deal form."""
    if os.name != "nt":
        return False
    def worker():
        try:
            u32 = ctypes.windll.user32
            MOD_ALT, MOD_CONTROL = 0x1, 0x2
            u32.RegisterHotKey(None, 101, MOD_CONTROL | MOD_ALT, ord("L"))
            u32.RegisterHotKey(None, 102, MOD_CONTROL | MOD_ALT, ord("N"))
            msg = ctypes.wintypes.MSG()
            while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:
                    if msg.wParam == 101:
                        on_show()
                    elif msg.wParam == 102:
                        on_new_deal()
        except Exception:
            pass
    try:
        import ctypes.wintypes  # noqa: F401
        threading.Thread(target=worker, daemon=True, name="ledger-hotkeys").start()
        return True
    except Exception:
        return False


def nav_js(tab):
    tab = str(tab).replace("'", "")
    focus = "setTimeout(function(){var f=document.getElementById('plTitle');if(f)f.focus();},250);" if tab == "tracker" else ""
    return ("(function(){var t=[...document.querySelectorAll('.tabs .tab')]"
            ".find(x=>String(x.getAttribute('onclick')||'').includes(\"'"+tab+"'\"));"
            "if(t){sw('"+tab+"',t);window.scrollTo(0,0);}"+focus+"})();")
