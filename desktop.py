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
import time
import pathlib
import threading
import traceback

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))
LOG = APP_DIR / "desktop.log"
CONFIG = APP_DIR / "client.json"


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


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

    if server:
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

    webview.create_window(title, url, width=1500, height=950, min_size=(980, 620),
                          background_color="#0d1017", text_select=True)
    webview.start(debug=False, private_mode=False)
    os._exit(0)


if __name__ == "__main__":
    main()
