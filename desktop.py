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
import html
import pathlib
import threading
import traceback

import desktop_shell as shell

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
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


_MUTEX_HANDLE = None


def single_instance(mutex_name, title):
    """Return False when another copy is already running; focus its window."""
    global _MUTEX_HANDLE
    if os.name != "nt":
        return True
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        _MUTEX_HANDLE = k32.CreateMutexW(None, False, mutex_name)
        if k32.GetLastError() == 183:      # ERROR_ALREADY_EXISTS
            try:
                u32 = ctypes.windll.user32
                hwnd = u32.FindWindowW(None, title)
                if hwnd:
                    u32.ShowWindow(hwnd, 9)      # SW_RESTORE
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
    # Clamp stored geometry: a minimized/off-screen 160x28 window must not
    # become the next launch size.
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


WIDGET = None


class DesktopApi:
    url = ""
    auth = None

    def get_summary(self):
        try:
            return shell.summary(self.url, self.auth)
        except Exception as e:
            return {"ok": False, "error": str(e)[:120]}

    def hide_widget(self):
        try:
            if WIDGET is not None:
                WIDGET.hide()
        except Exception:
            pass
        return True

    def get_prefs(self):
        return load_prefs()

    def set_close_to_tray(self, value):
        d = load_prefs()
        d["close_to_tray"] = bool(value)
        save_prefs(d)
        return {"ok": True, "close_to_tray": d["close_to_tray"]}


def start_local():
    import remote_proxy as rp
    os.environ["GT_DATA_DIR"] = str(APP_DIR)
    os.environ["GT_AUTH"] = "off"
    os.environ["GT_BIND"] = "127.0.0.1"
    # Paid features are granted only by the signed licence that
    # game_tracker._license_info() verifies. The desktop build must never
    # derive them from the exe name, LEDGER_PLUS or an inherited GT_PAID
    # variable (D-2: renaming Ledger.exe used to unlock Ledger+ features).
    os.environ.pop("GT_PAID", None)
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
    if "--set-password" in sys.argv:
        try:
            log(rp.cli_set_password(CONFIG))
        except Exception as e:
            log("set-password failed: %s" % e)
        return
    # Branding only (title + icons). It must never influence entitlements:
    # the free exe renamed to *plus* still runs free unless a signed licence
    # is activated (D-2).
    is_plus = ("plus" in pathlib.Path(sys.executable).stem.lower()) or (os.environ.get("LEDGER_PLUS") == "1")
    title = "Ledger+ — Game Account Tracker" if is_plus else "Ledger — Game Account Tracker"
    if not single_instance("Global\\LedgerDesktopFree", title):
        return
    cfg = rp.load_config(CONFIG)
    server = str(cfg.get("server") or "").strip()
    url = ""
    config_error = ""

    local_only = (os.environ.get("GT_DESKTOP_MODE") or "").strip().lower() == "local"
    if local_only:
        # Portable/offline mode: always start the bundled server, ignore 8766
        # and client.json. Useful for testing and for running from a USB stick.
        url = start_local()
    elif server:
        try:
            server = rp.normalize_server_url(server)
        except rp.ConfigError as e:
            # P-3: never inject Basic credentials into an unvalidated host.
            config_error = str(e)
            log("invalid ledger.client.json: %s" % e)
        else:
            user = str(cfg.get("user") or "")
            password = rp.unseal(cfg.get("pass") or "", bind=server,
                                 warn=lambda m: log("ledger.client.json: " + m))
            if password and not user:
                user = "admin"
            if password:
                port, url = rp.start_proxy(server, user, password, title)
            else:
                # No usable DPAPI password: still proxy for a stable origin, but
                # without Basic auth (the server shows its own login form).
                port, url = rp.start_proxy(server, title=title)
    elif rp.health("http://127.0.0.1:8766/"):
        port, url = rp.start_proxy("http://127.0.0.1:8766", title=title)
    else:
        url = start_local()

    try:
        import webview
    except Exception:
        log("webview import failed:\n" + traceback.format_exc())
        return

    if not url:
        detail = config_error or "See desktop.log next to the exe."
        page = ("<h2>Ledger could not start</h2><p>%s</p>"
                % html.escape(detail))
        webview.create_window("Ledger", html=page, width=520, height=260)
        webview.start()
        return

    prefs = load_prefs()
    api = DesktopApi()
    api.url = url
    start_hidden = ("--tray" in sys.argv) and bool(prefs.get("close_to_tray", True))

    def _menu_nav(tab):
        try:
            window.show(); window.restore()
            window.evaluate_js(shell.nav_js(tab))
        except Exception:
            pass

    def _toggle_widget():
        try:
            if WIDGET is None:
                return
            if WIDGET.is_visible():
                WIDGET.hide()
            else:
                WIDGET.show()
        except Exception:
            pass

    try:
        from webview.menu import Menu, MenuAction
        _menu = [
            Menu("Файл", [MenuAction("➕ Додати угоду", lambda: _menu_nav("tracker")),
                         MenuAction("Замовлення", lambda: _menu_nav("mail")),
                         MenuAction("Канали", lambda: _menu_nav("channels"))]),
            Menu("Вигляд", [MenuAction("Огляд", lambda: _menu_nav("overview")),
                           MenuAction("Налаштування", lambda: _menu_nav("setup")),
                           MenuAction("Міні-віджет", lambda: _toggle_widget())]),
            Menu("Довідка", [MenuAction("Перевірити оновлення", lambda: shell.open_release())]),
        ]
    except Exception:
        _menu = []
    window = webview.create_window(title, url, min_size=(980, 620),
                                   background_color="#0d1017", text_select=True,
                                   js_api=api, hidden=start_hidden, menu=_menu,
                                   **window_kwargs(prefs))
    global WIDGET
    try:
        WIDGET = webview.create_window("Ledger — Today", html=shell.WIDGET_HTML,
                                       width=330, height=205, frameless=True, on_top=True,
                                       resizable=False, js_api=api, hidden=True)
    except Exception:
        log("widget failed:\n" + traceback.format_exc())
        WIDGET = None

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

        def nav(tab):
            try:
                window.show(); window.restore()
            except Exception:
                pass
            try:
                window.evaluate_js(shell.nav_js(tab))
            except Exception:
                pass

        def toggle_autostart(icon=None, item=None):
            shell.set_autostart(not shell.autostart_enabled(), sys.executable)

        def update_check(icon=None, item=None):
            shell.open_release()

        tray = pystray.Icon("Ledger", image, "Ledger", pystray.Menu(
            pystray.MenuItem("Відкрити Ledger", show_window, default=True),
            pystray.MenuItem("➕ Додати угоду", lambda i=None, x=None: nav("tracker")),
            pystray.MenuItem("Замовлення", lambda i=None, x=None: nav("mail")),
            pystray.MenuItem("Канали", lambda i=None, x=None: nav("channels")),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Міні-віджет", lambda i=None, x=None: _toggle_widget()),
            pystray.MenuItem("Міні-віджет", lambda i=None, x=None: _toggle_widget()),
            pystray.MenuItem("Запускати з Windows", toggle_autostart,
                             checked=lambda item: shell.autostart_enabled()),
            pystray.MenuItem("Перевірити оновлення", update_check),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Вихід", quit_app)))
        tray.run_detached()
        threading.Thread(target=shell.badge_loop,
                         args=(url, title, window, lambda: tray, None),
                         daemon=True, name="ledger-badge").start()
        shell.register_hotkeys(show_window, lambda: nav("tracker"))
    except Exception:
        log("tray failed:\n" + traceback.format_exc())

    def on_closing():
        # "Close to tray" setting: hide the window when a tray icon exists,
        # otherwise let the app exit (no way to bring it back without a tray).
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
            # never restore an off-screen window (minimize/close-to-tray sets -32000)
            x = prefs.get("win_x"); y = prefs.get("win_y")
            if x is None or y is None or int(x) < -10000 or int(y) < -10000:
                x, y = 60, 60
            window.move(int(x), int(y))
        except Exception:
            log("window move failed:\n" + traceback.format_exc())
        if start_hidden:
            try:
                window.hide()
            except Exception:
                pass
    try:
        _win_icon = APP_DIR / "assets" / "ledger.ico"
        if not _win_icon.exists():
            _win_icon = pathlib.Path(getattr(sys, "_MEIPASS", APP_DIR)) / "assets" / "ledger.ico"
        webview.start(_after_start, debug=False, private_mode=False, icon=str(_win_icon))
    finally:
        try:
            if tray:
                tray.stop()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()
