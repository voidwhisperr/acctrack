"""Ledger+ desktop client: hosted server + WebView2 window + tray + Windows toasts."""
import os
import sys
import json
import time
import pathlib
import threading
import traceback

APP_DIR = pathlib.Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else pathlib.Path(__file__).resolve().parent
ASSET_DIR = pathlib.Path(getattr(sys, "_MEIPASS", APP_DIR)) / "assets"
CONFIG = APP_DIR / "client.json"
DEFAULT_URL = "https://ledger.70-34-243-50.sslip.io/"
LOG = APP_DIR / "client.log"


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + str(msg) + "\n")
    except Exception:
        pass


def load_url():
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        return str(cfg.get("server") or DEFAULT_URL).rstrip("/") + "/"
    except Exception:
        return DEFAULT_URL


def notify(n, subject, lang="uk"):
    try:
        from winotify import Notification, audio
        if lang.startswith("ru"):
            title, text = "Ledger+", "Новый заказ: " + (subject or str(n))
        elif lang.startswith("en"):
            title, text = "Ledger+", "New order: " + (subject or str(n))
        else:
            title, text = "Ledger+", "Нове замовлення: " + (subject or str(n))
        icon = str(ASSET_DIR / "ledger-plus-192.png")
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


def main():
    import webview

    url = load_url()
    storage = pathlib.Path(os.environ.get("LOCALAPPDATA") or str(APP_DIR)) / "LedgerPlus" / "WebView"
    storage.mkdir(parents=True, exist_ok=True)
    first_run = not (storage / "EBWebView").exists()
    start_hidden = ("--tray" in sys.argv) and not first_run

    api = Api()
    window = webview.create_window(
        "Ledger+ — Game Account Tracker",
        url,
        width=1500,
        height=950,
        min_size=(980, 620),
        background_color="#0d1017",
        text_select=True,
        js_api=api,
        hidden=start_hidden,
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
        image = Image.open(icon_path)
        def show_window(icon=None, item=None):
            try:
                window.show()
                window.restore()
            except Exception:
                pass
        def quit_app(icon=None, item=None):
            try:
                if tray: tray.stop()
            except Exception:
                pass
            try:
                window.destroy()
            except Exception:
                pass
            os._exit(0)
        menu = pystray.Menu(
            pystray.MenuItem("Открыть Ledger+", show_window, default=True),
            pystray.MenuItem("Выход", quit_app),
        )
        tray = pystray.Icon("LedgerPlus", image, "Ledger+", menu)
        tray.run_detached()
    except Exception:
        log("tray failed:\n" + traceback.format_exc())

    def on_closing():
        try:
            window.hide()
        except Exception:
            pass
        return False

    try:
        window.events.closing += on_closing
    except Exception:
        pass

    try:
        webview.start(debug=False, private_mode=False, storage_path=str(storage), icon=str(ASSET_DIR / "ledger-plus.ico"))
    except Exception:
        log("webview failed:\n" + traceback.format_exc())
    finally:
        try:
            if tray: tray.stop()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()
