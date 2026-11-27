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


def summary(url, auth=None):
    """Return a tiny dashboard payload for the mini widget."""
    try:
        pl = _http_json(url.rstrip("/") + "/api/pl", auth, timeout=8)
        mq = _http_json(url.rstrip("/") + "/api/mail/queue?desktop=1", auth, timeout=8)
    except Exception as e:
        return {"ok": False, "error": str(e)[:120]}
    import datetime
    month = datetime.date.today().strftime("%Y-%m")
    profit = 0.0
    count = 0
    for row in (pl if isinstance(pl, list) else (pl.get("items") if isinstance(pl, dict) else []) or []):
        try:
            if str(row.get("date") or "")[:7] != month:
                continue
            profit += float(row.get("afterFee") if row.get("afterFee") is not None else (float(row.get("sell") or 0) - float(row.get("buy") or 0)))
            count += 1
        except Exception:
            pass
    new = int(mq.get("new") or 0) if isinstance(mq, dict) else 0
    return {"ok": True, "month": month, "profit": round(profit, 2), "deals": count, "new": new}


WIDGET_HTML = """<!doctype html><meta charset=utf-8><title>Ledger — Today</title>
<style>
*{box-sizing:border-box}html,body{margin:0;height:100%;background:#0d1017;color:#e8eaee;font-family:Segoe UI,system-ui,sans-serif;overflow:hidden}
body{border:1px solid #2a2f3a;border-radius:12px;padding:13px 14px;display:flex;flex-direction:column;gap:8px;user-select:none}
.top{display:flex;justify-content:space-between;color:#8a92a3;font-size:10px;letter-spacing:.08em}
.v{font-size:28px;font-weight:800;letter-spacing:-.02em;color:#7ae2a3;line-height:1.05}
.s{display:flex;justify-content:space-between;font-size:11px;color:#9aa3b4}.s b{color:#e8eaee;font-size:13px}
button{position:absolute;top:6px;right:8px;background:none;border:0;color:#6f788a;font-size:14px;cursor:pointer}
</style><body>
<button onclick="window.pywebview.api.hide_widget()">✕</button>
<div class="top"><span>LEDGER · TODAY</span><span id="st">●</span></div>
<div class="v" id="p">—</div>
<div class="s"><span>Deals <b id="d">—</b></span><span>New orders <b id="n">—</b></span></div>
<script>
async function tick(){try{if(!window.pywebview||!window.pywebview.api)return;const d=await window.pywebview.api.get_summary();if(!d||!d.ok){document.getElementById('st').textContent='○ offline';return}document.getElementById('st').textContent='●';document.getElementById('p').textContent=(d.profit>=0?'+':'')+d.profit.toFixed(2);document.getElementById('d').textContent=d.deals;document.getElementById('n').textContent=d.new;}catch(e){document.getElementById('st').textContent='○ offline'}}
setInterval(tick,15000);window.addEventListener('pywebviewready',tick);tick();
</script></body>"""


def first_link(argv):
    for a in (argv or []):
        if str(a).lower().startswith("ledger://"):
            return str(a)
    return ""


def link_tab(arg):
    s = str(arg or "").lower().split("ledger://", 1)[-1].strip("/")
    if s in ("deal", "deal/new", "new-deal", "new"):
        return "tracker"
    if s in ("orders", "order", "mail"):
        return "mail"
    if s in ("channels", "channel"):
        return "channels"
    if s in ("settings", "setup"):
        return "setup"
    if s in ("inventory",):
        return "inventory"
    return "overview"


def register_protocol(scheme="ledger", exe=None):
    if os.name != "nt":
        return False
    try:
        import winreg
        base = "Software\\Classes\\" + scheme
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, "URL:" + scheme)
            winreg.SetValueEx(k, "URL Protocol", 0, winreg.REG_SZ, "")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, base + "\\shell\\open\\command") as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, '"' + str(exe or sys.executable) + '" "%1"')
        return True
    except Exception:
        return False


def write_link(path, arg):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(str(arg))
    except Exception:
        pass


def watch_links(path, callback):
    import pathlib
    p = pathlib.Path(path)
    while True:
        try:
            if p.exists():
                raw = p.read_text(encoding="utf-8").strip()
                try:
                    p.unlink()
                except Exception:
                    pass
                if raw:
                    callback(link_tab(raw))
        except Exception:
            pass
        time.sleep(1)


def check_update(current):
    tag, url = latest_release()
    try:
        a = tuple(int(x) for x in str(current).split(".")[:3])
        b = tuple(int(x) for x in str(tag).lstrip("v").split(".")[:3])
        return {"ok": True, "current": current, "latest": tag, "url": url, "available": b > a}
    except Exception:
        return {"ok": False, "current": current, "latest": tag, "url": url, "available": False}
