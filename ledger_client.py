"""Ledger+ desktop client: hosted server inside a native WebView2 window,
system tray and Windows notifications.

client.json next to the exe:
  { "server": "https://...", "user": "admin", "pass": "dpapi:..." }
The password is optional; when present the proxy injects HTTP Basic auth so the
window opens straight into Ledger+ without a browser or a login form.
"""
import os
import sys
import json
import time
import html
import pathlib
import threading
import traceback

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
ASSET_DIR = pathlib.Path(getattr(sys, "_MEIPASS", APP_DIR)) / "assets"
CONFIG = APP_DIR / "client.json"
PREFS = APP_DIR / "desktop-plus.json"
DEFAULT_URL = "https://ledger.70-34-243-50.sslip.io/"
LOG = APP_DIR / "client.log"


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


def _show_error(webview, headline, detail):
    """Show a local error page instead of silently exiting (GUI subsystem)."""
    try:
        page = ("<!doctype html><meta charset=utf-8><title>Ledger+</title>"
                "<body style='font:16px Manrope,system-ui;background:#0d1017;"
                "color:#e9ebf2;padding:40px'><h2>%s</h2>"
                "<p style='color:#8b95a9'>%s</p></body>"
                % (html.escape(str(headline)), html.escape(str(detail))))
        webview.create_window("Ledger+", html=page, width=560, height=300)
        webview.start()
    except Exception:
        log("could not show error window:\n" + traceback.format_exc())


_MUTEX_HANDLE = None


def single_instance(mutex_name, title):
    global _MUTEX_HANDLE
    if os.name != "nt":
        return True
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        _MUTEX_HANDLE = k32.CreateMutexW(None, False, mutex_name)
        if k32.GetLastError() == 183:
            try:
                u32 = ctypes.windll.user32
                hwnd = u32.FindWindowW(None, title)
                if hwnd:
                    u32.ShowWindow(hwnd, 9)
                    u32.SetForegroundWindow(hwnd)
            except Exception:
                pass
            return False
    except Exception:
        log("single-instance check failed:\n" + traceback.format_exc())
    return True


def load_prefs():
    try:
        d = json.loads(PREFS.read_text(encoding="utf-8")) or {}
    except Exception:
        d = {}
    if not isinstance(d, dict):
        d = {}
    d.setdefault("close_to_tray", True)
    return d


def window_kwargs(prefs):
    try:
        w = max(980, min(3840, int(prefs.get("win_w") or 1500)))
        h = max(620, min(2160, int(prefs.get("win_h") or 950)))
    except Exception:
        w, h = 1500, 950
    return {"width": w, "height": h}


def remember_geometry(window):
    try:
        d = load_prefs()
        for k, attr in (("win_w", "width"), ("win_h", "height"),
                        ("win_x", "x"), ("win_y", "y")):
            try:
                v = getattr(window, attr)
                if v is not None:
                    d[k] = int(v)
            except Exception:
                pass
        # never persist minimized/off-screen geometry
        if int(d.get("win_x", 0)) < -10000 or int(d.get("win_y", 0)) < -10000:
            d["win_x"], d["win_y"] = 60, 60
        d["win_w"] = max(980, min(3840, int(d.get("win_w") or 1500)))
        d["win_h"] = max(620, min(2160, int(d.get("win_h") or 950)))
        save_prefs(d)
    except Exception:
        log("geometry save failed:\n" + traceback.format_exc())


def save_prefs(d):
    try:
        PREFS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        log("prefs save failed:\n" + traceback.format_exc())


def load_cfg():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _toast_safe(value):
    # winotify builds a PowerShell here-string; never allow expansion characters.
    import re as _re
    s = str(value or "")[:80]
    s = _re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ .,:;#/_\-+()\[\]@!?%]", "", s)
    return s or "order"


def notify(n, subject, lang="uk"):
    try:
        from winotify import Notification, audio
        subject = _toast_safe(subject if subject is not None else n)
        if str(lang).startswith("ru"):
            title, text = "Ledger+", "Новый заказ: " + (subject or str(n))
        elif str(lang).startswith("en"):
            title, text = "Ledger+", "New order: " + (subject or str(n))
        else:
            title, text = "Ledger+", "Нове замовлення: " + (subject or str(n))
        icon = str(ASSET_DIR / "ledger-plus-192.png")
        if not pathlib.Path(icon).exists():
            icon = str(ASSET_DIR / "app-icon-192.png")
        toast = Notification(app_id="Ledger+", title=title, msg=text, duration="short", icon=icon)
        try:
            toast.set_audio(audio.Default, loop=False)
        except Exception:
            pass
        toast.show()
    except Exception:
        log("toast failed:\n" + traceback.format_exc())


POLL_JS = r"""
(function(){
  if(window.__ledgerPlusPoll) return;
  window.__ledgerPlusPoll = true;
  let last = null;
  async function tick(){
    try{
      const r = await fetch('/api/mail/queue?desktop=1&t=' + Date.now(), {cache:'no-store'});
      if(!r.ok) return;
      const d = await r.json();
      if(!d || !d.ok) return;
      const n = Number(d.new || 0);
      if(last !== null && n > last && window.pywebview && window.pywebview.api){
        const items = d.items || [];
        const it = items.length ? items[items.length-1] : {};
        const lang = document.documentElement.lang || 'uk';
        window.pywebview.api.notify_order(n, it.subject || it.game || '', lang);
      }
      last = n;
    }catch(e){}
  }
  setInterval(tick, 30000);
  tick();
})();
"""


class Api:
    def notify_order(self, n, subject, lang="uk"):
        notify(n, subject, lang)
        return True

    def get_prefs(self):
        return load_prefs()

    def set_close_to_tray(self, value):
        d = load_prefs()
        d["close_to_tray"] = bool(value)
        save_prefs(d)
        return {"ok": True, "close_to_tray": d["close_to_tray"]}


def main():
    import remote_proxy as rp

    if "--set-password" in sys.argv:
        try:
            log(rp.cli_set_password(CONFIG))
        except Exception as e:
            log("set-password failed: %s" % e)
        return

    import webview

    cfg = load_cfg()
    if not single_instance("Global\\LedgerPlusDesktop", "Ledger+ — Game Account Tracker"):
        return

    # P-3: validate the configured URL before any Basic credential can be
    # decrypted or injected (https only outside loopback, no userinfo, no
    # file:/other schemes).
    raw_server = str(cfg.get("server") or "").strip() or DEFAULT_URL
    try:
        server = rp.normalize_server_url(raw_server)
    except rp.ConfigError as e:
        log("invalid client.json server: %s" % e)
        _show_error(webview, "Ledger+ configuration error",
                    "client.json server is not allowed: %s" % e)
        return

    user = str(cfg.get("user") or "")
    password = rp.unseal(cfg.get("pass") or "", bind=server,
                         warn=lambda m: log("client.json: " + m))
    if password:
        if not user:
            user = "admin"
        port, url = rp.start_proxy(server, user, password, "Ledger+")
    else:
        if cfg.get("pass"):
            log("client.json: stored password was refused; starting without Basic auth")
        url = server.rstrip("/") + "/"

    storage = pathlib.Path(os.environ.get("LOCALAPPDATA") or str(APP_DIR)) / "LedgerPlus" / "WebView"
    storage.mkdir(parents=True, exist_ok=True)
    first_run = not (storage / "EBWebView").exists()
    start_hidden = ("--tray" in sys.argv) and not first_run

    api = Api()
    _prefs = load_prefs()
    _prefs_kwargs = window_kwargs(_prefs)
    window = webview.create_window(
        "Ledger+ — Game Account Tracker",
        url,
        min_size=(980, 620),
        background_color="#0d1017",
        text_select=True,
        js_api=api,
        hidden=start_hidden,
        **_prefs_kwargs,
    )

    def inject():
        try:
            window.evaluate_js(POLL_JS)
        except Exception:
            log("inject failed:\n" + traceback.format_exc())

    window.events.loaded += inject

    tray = None
    try:
        import pystray
        from PIL import Image
        icon_path = ASSET_DIR / "ledger-plus-192.png"
        if not icon_path.exists():
            icon_path = ASSET_DIR / "app-icon-192.png"
        image = Image.open(icon_path)

        def show_window(icon=None, item=None):
            try:
                window.show()
                window.restore()
            except Exception:
                pass

        def quit_app(icon=None, item=None):
            try:
                if tray:
                    tray.stop()
            except Exception:
                pass
            try:
                window.destroy()
            except Exception:
                pass
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("Відкрити Ledger+", show_window, default=True),
            pystray.MenuItem("Вихід", quit_app),
        )
        tray = pystray.Icon("LedgerPlus", image, "Ledger+", menu)
        tray.run_detached()
    except Exception:
        log("tray failed:\n" + traceback.format_exc())

    def on_closing():
        remember_geometry(window)
        try:
            if bool(load_prefs().get("close_to_tray", True)) and tray is not None:
                window.hide()
                return False
        except Exception:
            log("close handler failed:\n" + traceback.format_exc())
        return True

    try:
        window.events.closing += on_closing
    except Exception:
        pass

    def _after_start():
        try:
            if _prefs.get("win_x") is not None and _prefs.get("win_y") is not None:
                window.move(int(_prefs["win_x"]), int(_prefs["win_y"]))
        except Exception:
            log("window move failed:\n" + traceback.format_exc())
    try:
        _win_icon = ASSET_DIR / ("ledger-plus.ico" if (ASSET_DIR / "ledger-plus.ico").exists() else "ledger.ico")
        webview.start(_after_start, debug=False, private_mode=False, storage_path=str(storage), icon=str(_win_icon))
    except Exception:
        log("webview failed:\n" + traceback.format_exc())
    finally:
        try:
            if tray:
                tray.stop()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()
