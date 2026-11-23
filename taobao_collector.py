#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taobao-колектор для трекера (режим-агент).

- Стежить за трекером: коли ви натискаєте «▶ Зібрати зараз» — запускає збір.
- Також збирає сам раз на INTERVAL_H годин.
- Працює у ВАШОМУ вікні браузера (start_cf_debug.bat), капчу проходите ви.

Запуск:  python taobao_collector.py        (агент, працює постійно)
         python taobao_collector.py --once (один збір і вихід)
"""
import json
import re
import sys
import os
import socket
import subprocess
import threading
import time
import urllib.parse
import urllib.request

_pw_path = os.environ.get("GT_PW_PATH", "")
if _pw_path:
    sys.path.insert(0, _pw_path)

# Адреса трекера й токен агента — з оточення або config.json
SERVER = os.environ.get("GT_SERVER", "")
TOKEN = os.environ.get("GT_TOKEN", "")
try:
    _cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"),
                          encoding="utf-8"))
    SERVER = SERVER or _cfg.get("server", "")
    TOKEN = TOKEN or _cfg.get("token", "")
except Exception:
    pass
if not SERVER or not TOKEN:
    print("⚠ Задайте GT_SERVER і GT_TOKEN (або config.json)");
CDP = "http://127.0.0.1:9222"

INTERVAL_H = 0           # 0 = автозбір ВИМКНЕНО (тільки кнопка «Зібрати зараз»)
POLL_SEC = 20            # як часто перевіряти кнопку в трекері
MAX_PER_QUERY = 10
WAIT_PAGE = 8
SLEEP_BETWEEN = 5
CAPTCHA_WAIT = 300

# гра → китайський запит. Genshin і Star Rail НЕ збираємо (не продаються).
QUERIES = [
    ("Arknights", "明日方舟 初始号"), ("Arknights", "明日方舟 成品号"),
    ("Arknights Endfield", "明日方舟终末地 初始号"),
    ("FGO", "FGO 初始号"), ("FGO", "FGO 成品号"), ("FGO", "FGO 毕业号"),
    ("Zenless Zone Zero", "绝区零 初始号"), ("Zenless Zone Zero", "绝区零 成品号"),
    ("Wuthering Waves", "鸣潮 初始号"), ("Wuthering Waves", "鸣潮 成品号"),
    ("Wuthering Waves", "鸣潮 毕业号"),
    ("Nikke", "NIKKE 初始号"), ("Nikke", "NIKKE 成品号"),
    ("Blue Archive", "碧蓝档案 初始号"), ("Blue Archive", "碧蓝档案 成品号"),
    ("Dokkan", "七龙珠爆裂大战 初始号"),
    ("Cookie Run", "姜饼人王国 初始号"), ("Cookie Run", "姜饼人王国 成品号"),
    ("Epic Seven", "第七史诗 初始号"), ("Epic Seven", "第七史诗 成品号"),
    ("Dragon Ball Legends", "龙珠激斗 初始号"), ("Dragon Ball Legends", "龙珠激斗 成品号"),
    ("One Piece", "海贼王 初始号"),
    ("Reverse 1999", "重返未来1999 初始号"),
    ("Uma Musume", "赛马娘 初始号"), ("Uma Musume", "赛马娘 成品号"),
    ("Princess Connect", "公主连结 初始号"),
    ("Granblue Fantasy", "碧蓝幻想 初始号"),
    ("Limbus Company", "边狱公司 初始号"),
    ("Snowbreak", "尘白禁区 初始号"),
    ("Bleach", "死神brave souls 初始号"),
]

JS_PARSE = r"""
() => {
  const out = [], seen = new Set();
  for (const a of document.querySelectorAll('a[href*="item.taobao.com"]')) {
    const t = (a.innerText || '').replace(/\s+/g, ' ').trim();
    const m = t.match(/¥\s*([0-9]+(?:\s*[.,]\s*[0-9]+)?)/);
    if (!m || seen.has(a.href)) continue;
    seen.add(a.href);
    const price = parseFloat(m[1].replace(/\s/g, '').replace(',', '.'));
    if (!(price > 0) || price > 100000) continue;
    const idm = a.href.match(/[?&]id=(\d+)/);
    if (!idm) continue;
    out.push({
      title: t.split('¥')[0].slice(0, 120),
      price: price,
      sold: (t.match(/([0-9.]+万?)\+?人付款/) || ['', ''])[1],
      href: 'https://item.taobao.com/item.htm?id=' + idm[1]
    });
    if (out.length >= %d) break;
  }
  return out;
}
""" % MAX_PER_QUERY

JS_CAPTCHA = r"""
() => {
  const t = (document.body && document.body.innerText || '').toLowerCase();
  const marks = ['滑动验证', '验证码', '安全验证', '请按住滑块', 'nc_1_wrapper'];
  const els = document.querySelectorAll('#nc_1_wrapper, .nc-container, [id*="nocaptcha"]');
  return els.length > 0 || marks.some(m => t.includes(m.toLowerCase()));
}
"""


def post(items, game, query):
    body = json.dumps({"token": TOKEN, "game": game, "query": query,
                       "items": items}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(SERVER + "/api/taobao/import", data=body, headers={
        "Content-Type": "application/json", "User-Agent": "gt-taobao-agent/1.0",
        "X-GT-TOKEN": TOKEN})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def status():
    req = urllib.request.Request(SERVER + "/api/taobao?agent=1",
                                 headers={"User-Agent": "gt-taobao-agent/1.0",
                                          "X-GT-TOKEN": TOKEN})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def cdp_up(timeout=2):
    """Чи відкритий порт 9222 (вікно браузера для збору)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex(("127.0.0.1", 9222)) == 0
    except Exception:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def ensure_browser(wait=90):
    """Якщо вікна немає — відкриває його тим самим .bat, що й ви вручну."""
    if cdp_up():
        return True
    here = os.path.dirname(os.path.abspath(__file__))
    print("  🌐 вікно браузера не знайдено — відкриваю Edge з профілем gt", flush=True)
    send_progress(0, len(QUERIES), 0, "відкриваю вікно браузера")
    prof = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
                        "gt-cf-profile-edge")
    edge = next((x for x in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                             r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")
                 if os.path.exists(x)), None)
    try:
        if edge:
            flags = 0
            for nm in ("DETACHED_PROCESS", "CREATE_NO_WINDOW"):
                flags |= getattr(subprocess, nm, 0)
            subprocess.Popen([edge, "--remote-debugging-port=9222",
                              "--user-data-dir=" + prof, "--no-first-run",
                              "--no-default-browser-check",
                              "https://www.taobao.com/", "https://zeusx.com/"],
                             creationflags=flags, close_fds=True)
        else:
            bat = os.path.join(here, "start_cf_debug.bat")
            if os.path.exists(bat):
                subprocess.Popen(["cmd", "/c", "start", "", bat], cwd=here,
                                 creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
    except Exception as e:
        print("  ✗ не вдалось запустити браузер:", str(e)[:120], flush=True)
    t0 = time.time()
    while time.time() - t0 < wait:
        if cdp_up():
            print("  ✓ вікно відкрито (порт 9222 живий)", flush=True)
            return True
        time.sleep(3)
    print("  ✗ порт 9222 так і не піднявся", flush=True)
    return False


JS_DETAIL = r"""() => {
  const txt = document.body.innerText || '';
  const card = /信用卡支付|信用卡|credit card|Apple Pay/i.test(txt);
  // варіанти: кнопки SKU/DLC та опції вибору
  const sel = 'button, [role=option], [class*=sku] [class*=item], [class*=sku] button';
  let opts = 0;
  for (const el of document.querySelectorAll(sel)) {
    const t = (el.innerText || '').trim();
    if (/^DLC\s*\d+$/i.test(t) || /^\d+$/.test(t)) opts++;
  }
  const m = txt.match(/已售\s*([\d.,]+\s*[万+]?)/);
  return {card_pay: card, options: opts, sold: m ? m[1].trim() : ''};
}"""


def wait_captcha(page, limit=300, tag=""):
    """Якщо вискочила капча — стоїмо й чекаємо, поки людина її пройде."""
    try:
        if not page.evaluate(JS_CAPTCHA):
            return True
    except Exception:
        return True
    print("  ⚠ КАПЧА%s — пройдіть її у вікні браузера (чекаю до %d хв)..." % (tag, limit // 60), flush=True)
    send_progress(0, 1, 0, "⚠ КАПЧА — пройдіть у вікні браузера")
    try:
        import winsound
        winsound.Beep(880, 900)
    except Exception:
        pass
    t0 = time.time()
    while time.time() - t0 < limit:
        time.sleep(3)
        try:
            if not page.evaluate(JS_CAPTCHA):
                print("  ✓ капчу пройдено, продовжую", flush=True)
                send_progress(0, 0, 0, "продовжую")
                time.sleep(1.5)
                return True
        except Exception:
            pass
    print("  ✗ капча не пройдена за %d хв — пропускаю лот" % (limit // 60), flush=True)
    return False


def enrich(hrefs):
    """Відкриває сторінки лотів і збирає: оплата карткою, кількість варіантів, продано."""
    from playwright.sync_api import sync_playwright
    rows, blocked = [], 0
    with sync_playwright() as pw:
        try:
            b = pw.chromium.connect_over_cdp(CDP)
            ctx = b.contexts[0]
            page = ctx.new_page()
            for i, href in enumerate(hrefs[:10], 1):
                try:
                    page.goto(href, wait_until="domcontentloaded", timeout=45000)
                    try:
                        page.wait_for_load_state("networkidle", timeout=7000)
                    except Exception:
                        pass
                    time.sleep(1.5)
                    if not wait_captcha(page, tag=" (перевірка оплати)"):
                        continue
                    d = page.evaluate(JS_DETAIL)
                    if (d.get("options") or 0) == 0:
                        # SKU іноді в іншому фреймі — читаємо текст усіх фреймів
                        blob = ""
                        try:
                            for fr in page.frames:
                                try:
                                    blob += "\n" + (fr.evaluate(
                                        "() => document.body ? document.body.innerText : ''") or "")
                                except Exception:
                                    pass
                        except Exception:
                            pass
                        import re as _re2
                        dlc = len(_re2.findall(r"DLC\s*\d+", blob, _re2.I))
                        if dlc > (d.get("options") or 0):
                            d["options"] = dlc
                    if not (d.get("card_pay") or (d.get("options") or 0) > 1 or d.get("sold")):
                        blocked += 1
                        print("  · %s — сторінка без даних (вхід у Taobao?)" % href[:50], flush=True)
                        continue
                    rows.append({"href": href, **d})
                    time.sleep(3)
                    print("  [%d/%d] %s варіантів %s%s" % (
                        i, len(hrefs[:10]), d.get("options"), d.get("sold"),
                        " · 💳" if d.get("card_pay") else ""), flush=True)
                except Exception as e:
                    print("  ✗ %s: %s" % (href[:60], str(e)[:60]), flush=True)
            page.close()
        except Exception as e:
            print("  ✗ enrich: %s" % str(e)[:100], flush=True)
    if rows or blocked:
        try:
            body = json.dumps({"token": TOKEN, "rows": rows, "blocked": blocked,
                               "requested": len(hrefs)}).encode()
            req = urllib.request.Request(SERVER + "/api/taobao/enrich", data=body,
                                         headers={"Content-Type": "application/json",
                                                  "X-GT-TOKEN": TOKEN})
            urllib.request.urlopen(req, timeout=30).read()
            print("  ✓ збагачено %d лотів" % len(rows), flush=True)
        except Exception as e:
            print("  ✗ не зберіг збагачення: %s" % str(e)[:80], flush=True)


def send_progress(done, total, found, current="", finished=False):
    """Повідомляє трекер, скільки вже зібрано (видно в UI)."""
    try:
        body = json.dumps({"token": TOKEN, "done": done, "total": total,
                           "found": found, "current": current,
                           "finished": finished}).encode()
        req = urllib.request.Request(SERVER + "/api/taobao/progress", data=body,
                                     headers={"Content-Type": "application/json",
                                              "User-Agent": "gt-taobao-agent/1.0",
                                              "X-GT-TOKEN": TOKEN})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception:
        pass


def wait_for_results(p, deadline):
    while time.time() < deadline:
        try:
            n = p.evaluate("() => document.querySelectorAll('a[href*=\"item.taobao.com\"]').length")
            if n > 0:
                return n
            if p.evaluate(JS_CAPTCHA):
                print("  ⚠ КАПЧА — пройдіть її у вікні браузера (чекаю до 10 хв)...", flush=True)
                try:
                    import winsound
                    winsound.Beep(880, 700)
                except Exception:
                    pass
        except Exception:
            pass
        time.sleep(3)
    return 0


def run_all():
    """Один повний збір. Повертає (успішних запитів, лотів)."""
    _collecting["on"] = True
    try:
        return _run_all_inner()
    finally:
        _collecting["on"] = False


def _run_all_inner():
    """Тіло збору (щоб прапорець _collecting знімався завжди)."""
    from playwright.sync_api import sync_playwright
    ok, total = 0, 0
    if not ensure_browser():
        send_progress(0, len(QUERIES), 0, "браузер не запустився", finished=True)
        return 0, 0
    send_progress(0, len(QUERIES), 0, "підключення до браузера")
    print("· браузер є, стартую playwright...", flush=True)
    with sync_playwright() as pw:
        print("· playwright стартував", flush=True)
        try:
            print("· підключаюсь до CDP...", flush=True)
            b = pw.chromium.connect_over_cdp(CDP, timeout=20000)
            print("· CDP підключено", flush=True)
        except Exception as e:
            print("✗ Немає вікна браузера (порт 9222): %s" % str(e)[:100], flush=True)
            send_progress(0, len(QUERIES), 0, "браузер не відповідає (порт 9222)", finished=True)
            return 0, 0
        try:
            ctx = b.contexts[0]
            # завжди відкриваємо власну вкладку: перебір чужих може зависнути
            p = ctx.new_page()
            p.set_default_timeout(45000)
            print("· вкладку відкрито", flush=True)
        except Exception as e:
            print("✗ Проблема зі сторінкою: %s" % str(e)[:100], flush=True)
            send_progress(0, len(QUERIES), 0, "проблема зі сторінкою браузера", finished=True)
            return 0, 0
        send_progress(0, len(QUERIES), 0, "старт")
        for i, (game, q) in enumerate(QUERIES, 1):
            print("[%d/%d] %s — %s" % (i, len(QUERIES), game, q), flush=True)
            send_progress(i - 1, len(QUERIES), total, game)
            try:
                p.goto("https://s.taobao.com/search?q=" + urllib.parse.quote(q),
                       wait_until="domcontentloaded", timeout=60000)
                time.sleep(WAIT_PAGE)
                if wait_for_results(p, time.time() + CAPTCHA_WAIT * 2) == 0:
                    print("  ✗ порожньо (або капча не пройдена)", flush=True)
                    continue
                items = p.evaluate(JS_PARSE)
                if not items:
                    print("  ✗ не розібралось", flush=True)
                    continue
                res = post(items, game, q)
                total = int(res.get("total") or total or 0)
                send_progress(i, len(QUERIES), total, game)
                print("  ✓ %d лотів → нових %s, оновлено %s (всього %s)" % (
                    len(items), res.get("added"), res.get("updated"), res.get("total")), flush=True)
                ok += 1
                total += len(items)
            except Exception as e:
                print("  ✗", str(e)[:120], flush=True)
            time.sleep(SLEEP_BETWEEN)
    print("\nГотово: запитів %d, лотів %d" % (ok, total), flush=True)
    send_progress(len(QUERIES), len(QUERIES), total, "готово", finished=True)
    try:
        p.close()          # прибираємо свою вкладку
    except Exception:
        pass
    return ok, total


_collecting = {"on": False}


def heartbeat_loop():
    """Тримає статус «онлайн» у трекері навіть під час довгого збору."""
    while True:
        try:
            status()
        except Exception:
            pass
        time.sleep(POLL_SEC)


def enrich_loop():
    """Перевірка оплати/варіантів — окремим потоком, не чекаючи кінця збору."""
    last = 0
    while True:
        try:
            st = status()
            req = int(st.get("enrich_request") or 0)
            if req and req > last and not _collecting["on"]:
                last = req
                items = [x for x in (st.get("items") or []) if not x.get("enriched")]
                items.sort(key=lambda x: -float(x.get("price_cny") or 0))
                hrefs = [x.get("href") for x in items[:10] if x.get("href")]
                if hrefs:
                    if ensure_browser():
                        print("💳 Перевіряю оплату/варіанти у %d лотів" % len(hrefs), flush=True)
                        enrich(hrefs)
                else:
                    print("💳 нічого перевіряти — усі лоти вже перевірені", flush=True)
        except Exception as e:
            print("⚠ enrich loop: %s" % str(e)[:120], flush=True)
        time.sleep(15)


_lock_sock = None


def _single_instance():
    """Один екземпляр агента: тримаємо локальний порт 8768 (Windows-safe)."""
    global _lock_sock
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # на Windows SO_REUSEADDR дозволяє ДВОМ процесам один порт —
        # тому явно забороняємо це, якщо опція доступна
        ex = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
        if ex is not None:
            s.setsockopt(socket.SOL_SOCKET, ex, 1)
        s.bind(("127.0.0.1", 8768))
        s.listen(1)
        _lock_sock = s
        return True
    except OSError:
        print("Агент уже працює (порт 8768 зайнятий) — виходжу.", flush=True)
        return False


def _zeusx_token_net(ctx):
    """Ловить Bearer-токен із запитів сторінки до api.zeusx.com."""
    toks = []
    p = ctx.new_page()
    try:
        def on_req(r):
            try:
                if "api.zeusx.com" in r.url:
                    h = r.headers.get("authorization") or r.headers.get("Authorization") or ""
                    if h.lower().startswith("bearer "):
                        toks.append(h[7:].strip())
            except Exception:
                pass
        p.on("request", on_req)
        for url in ("https://zeusx.com/profile", "https://zeusx.com/", "https://zeusx.com/my-orders"):
            try:
                p.goto(url, wait_until="domcontentloaded", timeout=30000)
                p.wait_for_timeout(3500)
            except Exception:
                pass
            if toks:
                break
    finally:
        try:
            p.close()
        except Exception:
            pass
    return toks[0] if toks else ""


def _zeusx_token(ctx):
    """access_token ZeusX лежить у localStorage — дістаємо його зі сторінки."""
    try:
        p = ctx.new_page()
        p.goto("https://zeusx.com/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(1.5)
        tok = p.evaluate("""() => {
          const keys = Object.keys(localStorage);
          for (const k of keys) {
            const v = localStorage.getItem(k) || '';
            if (!/token|auth|jwt/i.test(k) || !v) continue;
            try { const j = JSON.parse(v); if (j && (j.access_token || j.token)) return j.access_token || j.token; } catch(e){}
            if (v.length > 20 && v[0] !== '{') return v;
          }
          return '';
        }""")
        p.close()
        return tok or ""
    except Exception as e:
        print("  ⚠ zeusx token:", str(e)[:80], flush=True)
        return ""


def _cookie_from_browser(what="both"):
    """Бере cookie FunPay/ZeusX із відкритого вікна браузера (CDP)."""
    from playwright.sync_api import sync_playwright
    urls = {"funpay": ["https://funpay.com/"], "zeusx": ["https://zeusx.com/"]}
    keys = ["funpay", "zeusx"] if what == "both" else [what if what in urls else "funpay"]
    out = {}
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP, timeout=15000)
        ctx = b.contexts[0]
        for k in keys:
            try:
                cs = ctx.cookies(urls[k])
            except Exception:
                cs = []
            if cs:
                out[k] = "; ".join("%s=%s" % (c["name"], c["value"]) for c in cs)
    if out.get("zeusx") and "access_token=" not in out["zeusx"]:
        with sync_playwright() as pw:
            b = pw.chromium.connect_over_cdp(CDP, timeout=15000)
            ctx2 = b.contexts[0]
            tok = _zeusx_token(ctx2) or _zeusx_token_net(ctx2)
        if tok:
            out["zeusx"] = "access_token=" + tok + "; " + out["zeusx"]
            print("  ✓ zeusx: access_token знайдено в localStorage", flush=True)
    return out


def push_cookie(what):
    try:
        data = _cookie_from_browser(what)
        if not data:
            send_progress(0, 0, 0, "cookie: браузер не має цих cookies", True)
            return
        saved = []
        for k, v in data.items():
            body = json.dumps({k + "_cookie": v}).encode("utf-8")
            req = urllib.request.Request(SERVER + "/api/secrets/save", data=body, headers={
                "Content-Type": "application/json", "User-Agent": "gt-taobao-agent/1.0",
                "X-GT-TOKEN": TOKEN})
            try:
                with urllib.request.urlopen(req, timeout=25) as r:
                    if (json.loads(r.read().decode("utf-8", "replace")) or {}).get("ok"):
                        saved.append(k)
            except Exception as e:
                print("  ⚠ cookie save:", str(e)[:80], flush=True)
        body = json.dumps({"clear": True}).encode("utf-8")
        req = urllib.request.Request(SERVER + "/api/secrets/request", data=body, headers={
            "Content-Type": "application/json", "User-Agent": "gt-taobao-agent/1.0",
            "X-GT-TOKEN": TOKEN})
        try:
            urllib.request.urlopen(req, timeout=15).read()
        except Exception:
            pass
        print("  🔑 cookie з браузера:", ", ".join(saved) or "нічого", flush=True)
    except Exception as e:
        print("  ⚠ cookie з браузера:", str(e)[:120], flush=True)


def agent():
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    threading.Thread(target=enrich_loop, daemon=True).start()
    print("Агент Taobao запущено. Чекаю кнопку «Зібрати зараз» у трекері.", flush=True)
    if INTERVAL_H:
        print("Авто-збір кожні %d год. Ctrl+C — вихід.\n" % INTERVAL_H, flush=True)
    else:
        print("Автозбір ВИМКНЕНО — збір лише кнопкою «Зібрати зараз». Ctrl+C — вихід.\n", flush=True)
    last_run = 0
    while True:
        try:
            st = status()
            _cr = st.get("cookie_request") or {}
            if _cr.get("what"):
                print("▶ Копіюю cookie з браузера…", flush=True)
                threading.Thread(target=push_cookie, args=(_cr["what"],), daemon=True).start()
            req = int(st.get("request") or 0)
            due = bool(INTERVAL_H) and (time.time() - last_run) >= INTERVAL_H * 3600
            if req > 0 or due:
                print("▶ Старт збору (%s)" % ("кнопка з трекера" if req > 0 else "за розкладом"),
                      flush=True)
                run_all()
                last_run = time.time()
                print("Наступний авто-збір через %d год.\n" % INTERVAL_H, flush=True)
        except Exception as e:
            print("⚠ трекер недоступний:", str(e)[:100], flush=True)
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    if "--once" in sys.argv:
        run_all()
    else:
        if not _single_instance():
            sys.exit(0)
        try:
            agent()
        except KeyboardInterrupt:
            print("\nЗупинено.")
