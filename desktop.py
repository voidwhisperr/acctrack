"""Ledger desktop launcher: Python server + native WebView2 window."""
import os
import sys
import time
import socket
import threading
import urllib.request
import pathlib
import traceback

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
LOG = APP_DIR / "desktop.log"


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def main():
    port = free_port()
    os.environ["GT_DATA_DIR"] = str(APP_DIR)
    os.environ["GT_AUTH"] = "off"
    os.environ["GT_BIND"] = "127.0.0.1"
    os.environ["PORT"] = str(port)
    os.environ["GT_PAID"] = "1"
    os.environ["GT_NO_BROWSER"] = "1"
    os.environ["GT_DESKTOP"] = "1"

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
    last = None
    for _ in range(160):
        try:
            with urllib.request.urlopen(url + "api/health", timeout=1) as r:
                if r.status == 200:
                    last = None
                    break
        except Exception as e:
            last = e
            time.sleep(0.25)

    try:
        import webview
    except Exception:
        log("webview import failed:\n" + traceback.format_exc())
        return

    if last is not None:
        log("server did not start: %r" % (last,))
        webview.create_window("Ledger", html="<h2>Ledger could not start</h2><p>See desktop.log next to Ledger.exe.</p>", width=520, height=260)
        webview.start()
        return

    webview.create_window(
        "Ledger+ — Game Account Tracker",
        url,
        width=1500,
        height=950,
        min_size=(980, 620),
        background_color="#0d1017",
        text_select=True,
    )
    webview.start(debug=False, private_mode=False)
    os._exit(0)


if __name__ == "__main__":
    main()
