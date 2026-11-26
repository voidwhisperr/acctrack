"""Ledger desktop launcher.

Modes:
  * client.json has "server"  -> opens that Ledger/Ledger+ server (sync with browser)
  * a local Ledger is running -> attaches to http://127.0.0.1:8766
  * otherwise                 -> starts the bundled server on port 8766
Data lives next to the exe; the browser version opened at the same URL sees the
same records, so the browser and the desktop app stay in sync.
"""
import os
import sys
import json
import time
import pathlib
import threading
import traceback

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))
LOG = APP_DIR / "desktop.log"
# Ledger+ uses client.json; the free Ledger must not pick up the hosted
# account by accident, so it has its own file.
CONFIG = APP_DIR / "ledger.client.json"
PREFS = APP_DIR / "desktop.json"


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


def load_prefs():
    try:
        d = json.loads(PREFS.read_text(encoding="utf-8")) or {}
    except Exception:
        d = {}
    if not isinstance(d, dict):
        d = {}
    d.setdefault("close_to_tray", True)
    return d


def save_prefs(d):
    try:
        PREFS.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception:
        log("prefs save failed:\n" + traceback.format_exc())


class DesktopApi:
    def get_prefs(self):
        return load_prefs()

    def set_close_to_tray(self, value):
        d = load_prefs()
        d["close_to_tray"] = bool(value)
        save_prefs(d)
        return {"ok": True, "close_to_tray": d["close_to_tray"]}


def start_local(is_plus):
    import remote_proxy as rp
    os.environ["GT_DATA_DIR"] = str(APP_DIR)
    os.environ["GT_AUTH"] = "off"
    os.environ["GT_BIND"] = "127.0.0.1"
    os.environ["GT_PAID"] = "1" if is_plus else "0"
    os.environ["GT_NO_BROWSER"] = "1"
    os.environ["GT_DESKTOP"] = "1"
    port = rp.free_port(8766)
    os.environ["PORT"] = str(port)

    import game_tracker as gt

    def serve():
        try:
            gt.main()
        except SystemExit:
            pass
        except Exception:
            log("server failed:\n" + traceback.format_exc())

    threading.Thread(target=serve, daemon=True, name="ledger-server").start()
    url = "http://127.0.0.1:%d/" % port
    for _ in range(200):
        if rp.health(url):
            log("local %s" % url)
            return url
        time.sleep(0.25)
    return ""


def main():
    import remote_proxy as rp
    is_plus = ("plus" in pathlib.Path(sys.executable).stem.lower()) or (os.environ.get("LEDGER_PLUS") == "1")
    title = "Ledger+ — Game Account Tracker" if is_plus else "Ledger — Game Account Tracker"
    cfg = rp.load_config(CONFIG)
    server = str(cfg.get("server") or "").strip()
    url = ""

    local_only = (os.environ.get("GT_DESKTOP_MODE") or "").strip().lower() == "local"
    if local_only:
        # Portable/offline mode: always start the bundled server, ignore 8766
        # and client.json. Useful for testing and for running from a USB stick.
        url = start_local(is_plus)
    elif server:
        if not server.startswith("http"):
            server = "https://" + server
        port, url = rp.start_proxy(server, str(cfg.get("user") or ""), rp.unseal(cfg.get("pass") or ""), title)
    elif rp.health("http://127.0.0.1:8766/"):
        port, url = rp.start_proxy("http://127.0.0.1:8766", title=title)
    else:
        url = start_local(is_plus)

    try:
        import webview
    except Exception:
        log("webview import failed:\n" + traceback.format_exc())
        return

    if not url:
        webview.create_window("Ledger", html="<h2>Ledger could not start</h2><p>See desktop.log next to the exe.</p>", width=520, height=260)
        webview.start()
        return

    prefs = load_prefs()
    api = DesktopApi()
    start_hidden = ("--tray" in sys.argv) and bool(prefs.get("close_to_tray", True))
    window = webview.create_window(title, url, width=1500, height=950, min_size=(980, 620),
                                   background_color="#0d1017", text_select=True,
                                   js_api=api, hidden=start_hidden)

    tray = None
    try:
        import pystray
        from PIL import Image
        icon_path = APP_DIR / "assets" / ("ledger-192.png" if not is_plus else "ledger-plus-192.png")
        if not icon_path.exists():
            icon_path = pathlib.Path(getattr(sys, "_MEIPASS", APP_DIR)) / "assets" / "ledger-192.png"
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

        tray = pystray.Icon("Ledger", image, "Ledger", pystray.Menu(
            pystray.MenuItem("Відкрити Ledger", show_window, default=True),
            pystray.MenuItem("Вихід", quit_app)))
        tray.run_detached()
    except Exception:
        log("tray failed:\n" + traceback.format_exc())

    def on_closing():
        # "Close to tray" setting: hide the window when a tray icon exists,
        # otherwise let the app exit (no way to bring it back without a tray).
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

    try:
        _win_icon = APP_DIR / "assets" / "ledger.ico"
        if not _win_icon.exists():
            _win_icon = pathlib.Path(getattr(sys, "_MEIPASS", APP_DIR)) / "assets" / "ledger.ico"
        webview.start(debug=False, private_mode=False, icon=str(_win_icon))
    finally:
        try:
            if tray:
                tray.stop()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()
