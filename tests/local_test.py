#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ізольований локальний тест трекера: піднімає копію на 127.0.0.1:8799 і смикає всі API."""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

BASE = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "gt_local_test")
sys.path.insert(0, BASE)   # імпорт модулів з копії (не з tests/)
_HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(_HERE), "game_tracker.py")  # корінь репо
PORT = 8799
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"
TOKEN = "testtoken123"
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond), extra))
    print(("  ✓ " if cond else "  ✗ ") + name + ((" — " + str(extra)) if extra and not cond else ""))


def req(path, method="GET", body=None, headers=None, timeout=20):
    data = None
    h = {"User-Agent": "gt-local-test"}
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    r = urllib.request.Request(URL + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def jreq(path, method="GET", body=None, headers=None):
    st, raw, hd = req(path, method, body, headers)
    try:
        return st, json.loads(raw.decode("utf-8", "replace")), hd
    except Exception:
        return st, None, hd


def prepare():
    if os.path.isdir(BASE):
        shutil.rmtree(BASE, ignore_errors=True)
    os.makedirs(BASE, exist_ok=True)
    src_dir = os.path.dirname(os.path.abspath(SRC))
    for mod in ("game_tracker.py", "taobao_core.py", "taobao.py", "ui.py", "platforms.py"):
        _src = os.path.join(src_dir, mod)
        if os.path.exists(_src):
            shutil.copy2(_src, os.path.join(BASE, mod))
    now = int(time.time())
    # ізоляція: свіжа мітка оновлення постачальників => жодного скрейпінгу
    json.dump({"ts": now, "attempt": now, "ok": True},
              open(os.path.join(BASE, ".gt_sup_ts.json"), "w"))
    json.dump([{"id": "skye_1", "title": "Arknights starter", "price": 5.0,
                "source": "skye", "sourceName": "Skye1204", "sourceEmoji": "🟠",
                "sourceColor": "#f97316", "available": True, "isOnSale": False,
                "url": "https://example.com/1", "gone": False}],
              open(os.path.join(BASE, ".gt_suppliers.json"), "w"))
    json.dump({"auth_user": "admin", "auth_pass": "localtestpass",
               "collector_token": TOKEN},
              open(os.path.join(BASE, ".gt_secrets.json"), "w"))
    for f, v in ((".gt_pl.json", []), (".gt_eldorado.json", []), (".gt_goal.json", {}),
                 (".gt_mailq.json", []), (".gt_settings.json", {}),
                 (".gt_tg.json", {}), (".gt_cache.json", {})):
        json.dump(v, open(os.path.join(BASE, f), "w"))


def start():
    env = dict(os.environ)
    env.update({"GT_NO_BROWSER": "1", "GT_AUTH": "off", "PORT": str(PORT),
                "GT_BIND": HOST, "PYTHONUNBUFFERED": "1"})
    p = subprocess.Popen([sys.executable, "-X", "utf8", "game_tracker.py"],
                         cwd=BASE, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                         errors="replace")
    for _ in range(60):
        time.sleep(0.5)
        try:
            st, _, _ = req("/api/health", timeout=3)
            if st == 200:
                return p
        except Exception:
            pass
    p.kill()
    out = p.stdout.read() if p.stdout else ""
    print("НЕ СТАРТУВАВ:\n" + out[-3000:])
    sys.exit(1)



def test_mail_classifier():
    """Класифікація листів: статусні не сповіщають, посилання вирізаються."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gt_unit", os.path.join(BASE, "game_tracker.py"))
    gt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gt)
    cases = [
        ("no-reply@eldorado.gg", "Your order is now marked as Received", "marked as Received", "status"),
        ("no-reply@eldorado.gg", "You have a new order #1", "new order", "order"),
        ("no-reply@funpay.com", "New message from buyer", "hi", "message"),
        ("no-reply@zeusx.com", "Funds released", "funds released", "status"),
        ("no-reply@zeusx.com", "You have a new sale", "sold $12", "order"),
        ("no-reply@eldorado.gg", "Order update", "has been marked as Received", "status"),
    ]
    for sender, subj, body, want in cases:
        kind, _plat = gt._classify_mail(sender, subj, body)
        check("mail: %-28s -> %s" % (subj[:28], want), kind == want, kind)
    # Eldorado: сума лише в HTML-частині
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    m = MIMEMultipart("alternative")
    m["Subject"] = "New Order"
    m.attach(MIMEText("You have a new Order\nPlease go to the Order page", "plain", "utf-8"))
    m.attach(MIMEText("<html><body><p>Order price: 25.00 USD</p>"
                      "<p>Game: Monster Hunter Outlanders</p>"
                      "<p>Category: Accounts</p></body></html>", "html", "utf-8"))
    hp = gt._mail_body(m)
    hf = gt._parse_order_fields(hp)
    check("HTML-лист: ціна 25", hf["price"] == 25.0, hf)
    check("HTML-лист: гра", "Monster Hunter" in (hf["game"] or ""), hf)
    check("HTML-лист: kind=order",
          gt._classify_mail("no-reply@eldorado.gg", "New Order", hp)[0] == "order")
    # Order ID у Eldorado — це UUID
    m2 = MIMEMultipart("alternative")
    m2["Subject"] = "New Order"
    m2.attach(MIMEText("You have a new Order", "plain", "utf-8"))
    m2.attach(MIMEText("<html><body><p>Order ID: 15076cf4-bdc3-47ca-7240-08df478967ec "
                       "Category: Accounts Game: Monster Hunter Outlanders "
                       "Order price: 25.00 USD</p></body></html>", "html", "utf-8"))
    hb = gt._mail_body(m2)
    hf2 = gt._parse_order_fields(hb)
    check("Order ID (UUID) розпізнано",
          hf2["orderId"] == "15076cf4-bdc3-47ca-7240-08df478967ec", hf2["orderId"])
    check("ціна в тому ж листі", hf2["price"] == 25.0, hf2["price"])

    # Telegram: повідомлення має бути коротким і без сміття
    _mb = ("| [![Eldorado.gg](https://x/y.png)](https://eldorado.gg)\n| --- |\n"
           "| LivelyBurst-j3Sl sent you a messageReply to keep things moving. |\n"
           "| [Reply now](https://eldorado.gg/messages/123) |")
    _mm = gt._mail_notification("message", "Eldorado",
                                "LivelyBurst-j3Sl wants to chat with you on Eldorado", _mb)
    check("повідомлення: ≤3 рядки", len(_mm.splitlines()) <= 3, _mm)
    check("повідомлення: без URL/картинок", "http" not in _mm and "![" not in _mm, _mm)
    check("повідомлення: є імʼя", "LivelyBurst" in _mm, _mm)

    txt = gt._mail_notification("order", "Eldorado", "New order #1",
                                "Link: https://url6310.eldorado.gg/ls/click?upn=abc thanks")
    check("сповіщення без посилань", "http" not in txt.lower())


def main():
    prepare()
    proc = start()
    log = []
    try:
        print("\n── класифікація пошти ──")
        test_mail_classifier()

        print("\n── базове ──")
        st, raw, hd = req("/")
        check("GET / = 200", st == 200)
        check("сторінка містить вкладки", b"tab-platforms" in raw and b"tab-taobao" in raw)
        check("немає залишків цілі", b"goalProgress" not in raw and b"\xd0\xa6\xd0\x86\xd0\x9b\xd0\xac" not in raw)

        st, d, _ = jreq("/api/health")
        check("/api/health ok", st == 200 and d.get("ok") and d.get("version"))

        print("\n── P&L ──")
        st, d, _ = jreq("/api/pl")
        check("GET /api/pl порожній", st == 200 and isinstance(d, dict) and d.get("purchases") == [])
        rec = {"id": 1, "date": "2026-11-20", "title": "Test sale", "src": "funpay",
               "srcName": "FunPay", "buy": 1.0, "sell": 10.0, "qty": 1, "platform": "funpay"}
        st, d, _ = jreq("/api/pl/save", "POST", {"purchases": [rec]})
        check("POST /api/pl/save", st == 200 and d.get("ok") is not False)
        st, d, _ = jreq("/api/pl")
        check("запис зберігся", isinstance(d, dict) and len(d.get("purchases") or []) == 1)
        st, d, _ = jreq("/api/pl/save", "POST", {"purchases": []})
        check("порожній POST не стирає (409)", st == 409, st)
        st, d, _ = jreq("/api/pl")
        check("дані на місці після поганого POST", isinstance(d, dict) and len(d.get("purchases") or []) == 1)

        print("\n── ELDORADO ──")
        ed = {"id": 1, "date": "2026-11-20", "title": "ED test", "price": 20.0,
              "profit": 8.0, "src": "eldorado"}
        st, d, _ = jreq("/api/eldorado/save", "POST", {"sales": [ed]})
        check("POST /api/eldorado/save", st == 200)
        st, d, _ = jreq("/api/eldorado")
        check("ELDORADO зберігся", isinstance(d, dict) and len(d.get("sales") or []) == 1)

        print("\n── налаштування / Telegram ──")
        st, d, _ = jreq("/api/settings/save", "POST", {"sup_hours": 5})
        check("POST /api/settings/save", st == 200)
        st, d, _ = jreq("/api/settings")
        check("sup_hours = 5", (d or {}).get("sup_hours") == 5, (d or {}).get("sup_hours"))
        st, d, _ = jreq("/api/tg/test", "POST", {})
        check("/api/tg/test без токена не падає", st in (200, 400, 429))

        print("\n── Постачальники ──")
        st, d, _ = jreq("/api/suppliers?page=1&per=10")
        check("GET /api/suppliers", st == 200 and d.get("ok"))
        st, d, _ = jreq("/api/suppliers/status")
        check("GET /api/suppliers/status", st == 200 and "scraper" in d)
        st, d, _ = jreq("/api/suppliers/compare?id=skye_1")
        check("GET /api/suppliers/compare", st == 200)

        print("\n── Черга замовлень ──")
        st, d, _ = jreq("/api/mail/queue")
        check("черга порожня", st == 200 and d.get("items") == [])
        st, d, _ = jreq("/api/mail/clear", "POST", {})
        check("POST /api/mail/clear", st == 200)

        print("\n── Taobao ──")
        good = [{"title": "明日方舟 初始号 日服 12000石", "price": 15.0, "sold": "1万",
                 "href": "https://item.taobao.com/item.htm?id=111"}]
        st, d, _ = jreq("/api/taobao/import", "POST",
                        {"token": TOKEN, "game": "Arknights", "query": "明日方舟 初始号", "items": good})
        check("import з токеном", st == 200 and d.get("added") == 1, d)
        st, d, _ = jreq("/api/taobao/import", "POST",
                        {"token": "wrong", "game": "Arknights", "items": good})
        check("import з поганим токеном = 403", st == 403)
        bad = [{"title": "x", "price": 1, "href": "https://item.taobao.com/item.htm"}]
        st, d, _ = jreq("/api/taobao/import", "POST",
                        {"token": TOKEN, "game": "Arknights", "items": bad})
        check("href без id відкинуто", st == 200 and d.get("added") == 0)
        st, d, _ = jreq("/api/taobao/import", "POST",
                        {"token": TOKEN, "game": "Genshin", "query": "原神",
                         "items": [{"title": "原神 初始号 50000石", "price": 15.2,
                                    "href": "https://item.taobao.com/item.htm?id=222"}]})
        check("Genshin не приймається", st == 200 and d.get("added") == 0)
        st, d, _ = jreq("/api/taobao")
        check("GET /api/taobao", st == 200 and d.get("count") == 1)
        it = (d.get("items") or [{}])[0]
        check("переклад/тип/регіон/landed", it.get("segment") == "starter" and
              it.get("region") == "JP" and it.get("landed_usd", 0) > 0, it)
        check("різниця з постачальником", it.get("sup") and it.get("diff_usd") is not None, it.get("sup"))
        st, d, _ = jreq("/api/taobao/request", "POST", {})
        check("кулдаун після імпорту = 429", st == 429 and d.get("next_in", 0) > 0, d)

        print("\n── Склад ──")
        st, d, _ = jreq("/api/inventory")
        check("GET /api/inventory порожній", st == 200 and d.get("count") == 0)
        st, d, _ = jreq("/api/inventory/add", "POST",
                        {"title": "Arknights starter", "game": "Arknights", "cost": 3.5,
                         "source": "Taobao"})
        check("додати закупівлю", st == 200 and d.get("item", {}).get("cost") == 3.5, d)
        inv_id = (d.get("item") or {}).get("id")
        st, d, _ = jreq("/api/inventory")
        check("склад: 1 позиція, заморожено $3.5",
              d.get("in_stock") == 1 and d.get("frozen") == 3.5, d)
        # дані акаунта: додаємо з текстом, у списку їх НЕ має бути
        st, d, _ = jreq("/api/inventory/add", "POST",
                        {"title": "FGO acc", "game": "FGO", "cost": 5,
                         "source": "Taobao", "account": "login: fgo1\npass: secret123"})
        acc_id = (d.get("item") or {}).get("id")
        check("додати з даними акаунта", st == 200 and d.get("item", {}).get("account"), d)
        st, d, _ = jreq("/api/inventory")
        it = next((x for x in d.get("items") or [] if x.get("id") == acc_id), {})
        check("пароль НЕ у списку", "account" not in it and "secret123" not in json.dumps(d))
        check("є підказка + прапорець", it.get("has_account") is True and bool(it.get("account_hint")), it)
        st, d, _ = jreq("/api/inventory/secret?id=" + str(acc_id))
        check("секрет віддається окремо", st == 200 and "secret123" in (d.get("account") or ""), d)
        st, d, _ = jreq("/api/inventory/delete", "POST", {"id": acc_id})
        check("прибрати тестовий акаунт", st == 200 and d.get("removed") == 1)
        st, d, _ = jreq("/api/inventory/match?title=Arknights%20starter")
        check("пошук схожого на складі", st == 200 and len(d.get("matches") or []) >= 1, d)
        st, d, _ = jreq("/api/inventory/status", "POST", {"id": inv_id, "status": "sold"})
        check("позначити проданим", st == 200 and d.get("item", {}).get("status") == "sold", d)
        st, d, _ = jreq("/api/inventory")
        check("склад: продано 1, заморожено $0",
              d.get("sold") == 1 and d.get("frozen") == 0, d)
        st, d, _ = jreq("/api/inventory/add", "POST", {"title": "", "cost": 1})
        check("порожня назва відхилена", st == 400)
        st, d, _ = jreq("/api/inventory/delete", "POST", {"id": inv_id})
        check("видалити запис", st == 200 and d.get("removed") == 1, d)

        print("\n── Аналітика / CSV ──")
        st, d, _ = jreq("/api/analytics")
        check("GET /api/analytics", st == 200 and isinstance(d.get("games"), list))
        check("аналітика бачить продажі", any(x.get("n") for x in (d.get("games") or [])))
        st, raw, hd = req("/api/export/csv?what=pl")
        check("CSV P&L (BOM + ;)", st == 200 and raw[:3] == b"\xef\xbb\xbf" and b";" in raw, st)
        st, raw, hd = req("/api/export/csv?what=ed")
        check("CSV ELDORADO", st == 200 and raw[:3] == b"\xef\xbb\xbf", st)

        print("\n── Генератор лотів ──")
        # на складі є Arknights starter (cost 3.5) з попереднього блоку? додаємо свій
        st, d, _ = jreq("/api/inventory/add", "POST",
                        {"title": "Lot test acc", "game": "Arknights", "cost": 10,
                         "source": "Taobao", "account": "login: secret\npass: hidden"})
        lot_id = (d.get("item") or {}).get("id")
        st, raw, hd = req("/api/lots/export?source=inventory&markup=50")
        txt = raw.decode("utf-8-sig", "replace")
        check("CSV лотів зі складу", st == 200 and txt.startswith("title;price;"), txt[:60])
        check("націнка 50%: 10 -> 15", ";15.0;" in txt, txt[:200])
        check("дані акаунта НЕ в CSV", "hidden" not in txt and "secret" not in txt)
        st, raw, hd = req("/api/lots/export?source=suppliers&markup=50")
        txt2 = raw.decode("utf-8-sig", "replace")
        check("CSV лотів постачальників", st == 200 and ";7.5;" in txt2, txt2[:160])
        st, d, _ = jreq("/api/inventory/delete", "POST", {"id": lot_id})
        check("прибрати тестовий лот", st == 200)

        print("\n── Місячний звіт ──")
        st, d, _ = jreq("/api/report")
        check("GET /api/report", st == 200 and d.get("ok") and d.get("month"), d)
        check("звіт бачить 2 продажі", (d.get("sales") or {}).get("count") == 2,
              (d.get("sales") or {}).get("count"))
        check("виторг $30", (d.get("sales") or {}).get("revenue") == 30.0,
              (d.get("sales") or {}).get("revenue"))
        check("прибуток пораховано", (d.get("sales") or {}).get("profit", 0) > 0,
              (d.get("sales") or {}).get("profit"))
        _s = d.get("sales") or {}; _p = d.get("pl") or {}; _e = d.get("ed") or {}
        check("звіт: profit = after_fee + ed.profit",
              abs((_s.get("profit") or 0) - ((_p.get("after_fee") or 0) + (_e.get("profit") or 0))) < 0.01,
              (_s.get("profit"), _p.get("after_fee"), _e.get("profit")))
        check("звіт: fees = pl.fee + ed.fee (без закупівлі)",
              abs((_s.get("fees") or 0) - ((_p.get("fee") or 0) + (_e.get("fee") or 0))) < 0.01,
              (_s.get("fees"), _p.get("fee"), _e.get("fee")))
        st, raw, hd = req("/api/report/export")
        check("CSV звіту", st == 200 and raw[:3] == b"\xef\xbb\xbf" and b"\xd0\x9c\xd1\x96\xd1\x81\xd1\x8f\xd1\x86\xd1\x8c" in raw, st)
        st, raw, hd = req("/api/report/export?lang=en")
        check("CSV звіту EN локалізовано", st == 200 and b"Month" in raw and b"Profit" in raw and b"\xd0\x9c" not in raw, st)

        print("\n── Taobao: сміття по ¥0.01 не зберігається ──")
        _ct2 = (json.load(open(os.path.join(BASE, ".gt_secrets.json"))) or {}).get("collector_token", "")
        _it = {"game": "Arknights", "query": "q", "items": [
            {"href": "https://item.taobao.com/item.htm?id=1", "title": "cheap junk", "price": 0.08},
            {"href": "https://item.taobao.com/item.htm?id=2", "title": "normal acc 8000 gems", "price": 25.0}]}
        st, d, _ = jreq("/api/taobao/import", "POST", dict(_it, token=_ct2))
        check("імпорт ok", st == 200 and d.get("ok"), d)
        st, d, _ = jreq("/api/taobao")
        hrefs = [x.get("href") for x in (d.get("items") or [])]
        check("нижче порогу не збережено",
              not any(str(h).endswith("id=1") for h in hrefs), hrefs[:3])
        check("вище порогу збережено",
              any(str(h).endswith("id=2") for h in hrefs), hrefs[:3])

        print("\n── Taobao: видно, що агент живий ──")
        st, d, _ = jreq("/api/taobao?agent=1")
        check("taobao: поля агента", st == 200 and "agent_online" in d and "progress" in d, list(d)[:6])
        check("агент онлайн після пінгу", d.get("agent_online") is True, d.get("agent_online"))
        _ct = (json.load(open(os.path.join(BASE, ".gt_secrets.json"))) or {}).get("collector_token", "")
        st, d, _ = jreq("/api/taobao/progress", "POST",
                        {"token": _ct, "done": 3, "total": 31, "found": 12, "current": "FGO"})
        check("POST /api/taobao/progress", st == 200 and d.get("ok"), d)
        st, d, _ = jreq("/api/taobao")
        pg = d.get("progress") or {}
        check("прогрес видно в /api/taobao",
              pg.get("done") == 3 and pg.get("total") == 31, pg)

        print("\n── Telegram: watchdog працює навіть у тихому режимі ──")
        _src = open(os.path.join(BASE, "game_tracker.py"), encoding="utf-8").read()
        _i = _src.find("def _watchdog_loop")
        _body = _src[_i:_src.find("\ndef ", _i + 5)]
        check("watchdog сайту: прапорець watchdog",
              '_tg_flag("watchdog")' in _body and "_tg_send" in _body)
        _i2 = _src.find("def _agent_watchdog_loop")
        _body2 = _src[_i2:_src.find("\ndef ", _i2 + 5)]
        check("watchdog агента: прапорець agent",
              '_tg_flag("agent")' in _body2 and "_tg_send" in _body2)

        print("\n── Прибуток: завжди мінус закупівля (регресія) ──")
        import importlib.util as _ilp
        _spp = _ilp.spec_from_file_location("gt_prof", os.path.join(BASE, "game_tracker.py"))
        gtp = _ilp.module_from_spec(_spp)
        _spp.loader.exec_module(gtp)
        # ELDORADO: profit = price - fee - buy, якщо profit не заданий
        _r = gtp._clean_ed([{"date": "2026-11-23", "title": "x", "price": 12, "buy": 5, "fee": 1.2}])[0]
        check("ED: 12 − 1.2 − 5 = 5.8", abs(float(_r["profit"]) - 5.8) < 0.01, _r["profit"])
        _r2 = gtp._clean_pl([{"date": "2026-11-23", "title": "x", "sell": 14.61, "buy": 8,
                              "src": "funpay"}])[0]
        check("P&L: 14.61·0.90 − 8 = 5.15", abs(float(_r2["afterFee"]) - 5.149) < 0.02, _r2["afterFee"])
        # жоден шлях не передає profit/afterFee без закупівлі
        _src = open(os.path.join(BASE, "game_tracker.py"), encoding="utf-8").read()
        check("немає 'profit': round(price - fee, 2)",
              '"profit": round(price - fee, 2)' not in _src)
        check("немає afterFee без buy",
              '"afterFee": round(price * (1 - PLATFORM_FEES' not in _src)

        print("\n── Telegram: тільки продажі й повідомлення ──")
        import importlib.util as _ilt
        _sp2 = _ilt.spec_from_file_location("gt_tg", os.path.join(BASE, "game_tracker.py"))
        gtt = _ilt.module_from_spec(_sp2)
        _sp2.loader.exec_module(gtt)
        check("продажі увімкнено типово", gtt._tg_flag("order") is True)
        check("повідомлення увімкнено типово", gtt._tg_flag("message") is True)
        check("watchdog сайту увімкнено", gtt._tg_flag("watchdog") is True)
        check("watchdog агента вимкнено", gtt._tg_flag("agent") is False)
        check("дайджест вимкнено", gtt._tg_flag("digest") is False)
        check("дайджест не надсилається", gtt._digest_send() == 0)
        check("нові товари не надсилаються", gtt._notify_new_products() == 0)
        check("падіння цін не надсилається", gtt._notify_price_drops() == 0)
        # замовлення/повідомлення лишаються
        _m = gtt._mail_notification("order", "Eldorado", "New Order",
                                    "Order price: 25.00 USD\nGame: X")
        check("замовлення формується", "НОВЕ ЗАМОВЛЕННЯ" in _m, _m[:40])
        _m2 = gtt._mail_notification("message", "Eldorado",
                                     "LivelyBurst wants to chat with you on Eldorado", "hi")
        check("повідомлення формується", "LivelyBurst" in _m2, _m2[:40])

        print("\n── Валідація save (регресія після реального багу) ──")
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location("gt_val", os.path.join(BASE, "game_tracker.py"))
        gtv = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(gtv)
        check("_is_date('') → False", gtv._is_date("") is False)
        check("_is_date('2026-11-21') → True", gtv._is_date("2026-11-21") is True)
        try:
            gtv._clean_ed([{"bad": 1}])
            check("_clean_ed відхиляє битий запис", False, "не кинув помилку")
        except ValueError:
            check("_clean_ed відхиляє битий запис", True)
        before = len(jreq("/api/eldorado")[1].get("sales") or [])
        st, d, _ = jreq("/api/eldorado/save", "POST", {"sales": [{"bad": 1}]})
        check("save битого ELDORADO → 4xx", st in (400, 409, 422), st)
        after = len(jreq("/api/eldorado")[1].get("sales") or [])
        check("дані ELDORADO не постраждали", before == after, (before, after))

        print("\n── Черга: тільки замовлення + ручна сума ──")
        import json as _json, time as _time
        q = [
            {"id": "mq1", "ts": int(_time.time()), "platform": "Eldorado",
             "kind": "message", "subject": "wants to chat", "body": "hi", "status": "new"},
            {"id": "mq2", "ts": int(_time.time()), "platform": "Eldorado",
             "kind": "order", "subject": "New Order", "body": "no price here",
             "price": None, "status": "new"},
            {"id": "mq3", "ts": int(_time.time()), "platform": "Eldorado",
             "kind": "order", "subject": "New Order 2", "body": "no price too",
             "price": None, "status": "new"},
        ]
        _json.dump(q, open(os.path.join(BASE, ".gt_mail_queue.json"), "w"))
        st, d, _ = jreq("/api/mail/queue")
        ids = [x.get("id") for x in (d.get("items") or [])]
        check("повідомлення НЕ в черзі", st == 200 and ids == ["mq2", "mq3"], ids)
        st, d, _ = jreq("/api/mail/action", "POST", {"id": "mq2", "action": "add_ed", "price": 15})
        check("ED без суми + ручна ціна → ok", st == 200 and d.get("ok"), d)
        st, d, _ = jreq("/api/eldorado")
        check("у ELDORADO запис на $15",
              any(abs(float(x.get("price") or 0) - 15) < 0.01 for x in (d.get("sales") or [])), d)
        st, d, _ = jreq("/api/mail/action", "POST", {"id": "mq3", "action": "add_pl"})
        check("Eldorado → P&L заборонено (400)", st == 400, st)
        check("з поясненням про ELDORADO",
              "Eldorado" in (d.get("error") or "") and "ELDORADO" in (d.get("error") or ""), d)
        st, d, _ = jreq("/api/mail/action", "POST", {"id": "mq3", "action": "add_ed", "price": 30})
        check("Eldorado → ELDORADO ok", st == 200 and d.get("ok"), d)
        st, d, _ = jreq("/api/eldorado")
        check("у ELDORADO запис на $30",
              any(abs(float(x.get("price") or 0) - 30) < 0.01 for x in (d.get("sales") or [])), d)

        print("\n── Що купити сьогодні ──")
        # продаж саме по грі Arknights (щоб було з чим порівняти постачальника)
        import datetime as _dt
        _plp = os.path.join(BASE, ".gt_pl.json")
        _pl = json.load(open(_plp))
        _pl.append({"id": 999001, "date": _dt.date.today().isoformat(),
                    "title": "Arknights starter", "src": "zeusx", "srcName": "⚡ ZeusX",
                    "buy": 5.0, "sell": 10.0, "afterFee": 9.05, "qty": 1})
        json.dump(_pl, open(_plp, "w"))
        st, d, _ = jreq("/api/buy-list")
        items = d.get("items") or []
        check("GET /api/buy-list", st == 200 and d.get("ok"), d)
        check("є прибутковий варіант (Arknights $5 vs продаж $10)",
              any("Arknights" in (x.get("game") or "") for x in items), items[:2])
        first = items[0] if items else {}
        check("маржа додатна", (first.get("margin") or 0) > 0, first.get("margin"))
        check("ROI > 0", (first.get("roi") or 0) > 0, first.get("roi"))
        check("попит пораховано", (first.get("demand") or 0) >= 1, first.get("demand"))
        pl = json.load(open(os.path.join(BASE, ".gt_suppliers.json")))
        pl.append({"id": "cust_1", "title": "Custom Selective Starter Arknights",
                   "price": 1.0, "source": "skye", "sourceName": "Skye1204",
                   "url": "https://x/c"})
        json.dump(pl, open(os.path.join(BASE, ".gt_suppliers.json"), "w"))
        st, dc, _ = jreq("/api/buy-list")
        check("custom-лоти відфільтровано",
              all("Custom" not in (x.get("title") or "") for x in (dc.get("items") or [])),
              [x.get("title")[:30] for x in (dc.get("items") or [])][:3])
        st, d2, _ = jreq("/api/buy-list?limit=3")
        check("limit працює", len((d2.get("items") or [])) <= 3, len(d2.get("items") or []))

        print("\n── Мої лоти ZeusX ──")
        st, d, _ = jreq("/api/offers")
        check("/api/offers без cookie → ok:false (без падіння)",
              st == 200 and d.get("ok") is False and "error" in d, d)

        print("\n── Бекапи / експорт ──")
        st, d, _ = jreq("/api/backup/list")
        check("GET /api/backup/list", st == 200)
        st, raw, hd = req("/api/backup/export")
        ok_zip = st == 200 and raw[:2] == b"PK"
        check("GET /api/export = zip", ok_zip, st)
        if ok_zip:
            p = os.path.join(BASE, "x.zip")
            open(p, "wb").write(raw)
            with zipfile.ZipFile(p) as z:
                names = z.namelist()
            check("zip містить файли даних", any(n.endswith(".json") for n in names), names[:5])
            check("zip містить дані Taobao", ".gt_taobao.json" in names, names)

        print("\n── безпека / HTTP ──")
        st, d, _ = jreq("/api/pl/save", "POST", [rec],
                        {"Origin": "http://evil.example", "X-GT-CSRF": "bad"})
        check("CSRF: чужий Origin = 403", st == 403)
        st, raw, hd = req("/api/health", headers={"Accept-Encoding": "gzip"})
        check("gzip у відповіді", hd.get("Content-Encoding") == "gzip" or len(raw) < 2000,
              hd.get("Content-Encoding"))
        st, raw, hd = req("/api/suppliers?page=1&per=5")
        et = hd.get("ETag")
        check("ETag віддається", bool(et), et)
        if et:
            st2, raw2, _ = req("/api/suppliers?page=1&per=5", headers={"If-None-Match": et})
            check("304 на If-None-Match", st2 == 304, st2)
        st, d, _ = jreq("/api/nonexistent")
        check("невідомий API = 404", st == 404, st)
        st, raw, hd = req("/favicon.ico")
        check("favicon віддається", st in (200, 304), st)
        st, raw, hd = req("/%2e%2e/%2e%2e/etc/passwd")
        check("path traversal заблоковано", st in (400, 403, 404), st)

        print("\n── витривалість ──")
        big = "x" * (2 * 1024 * 1024)
        st, d, _ = jreq("/api/settings/save", "POST", {"junk": big})
        check("великий POST не валить сервер", st in (200, 400, 413), st)
        st, d, _ = jreq("/api/health")
        check("сервер живий після всього", st == 200 and d.get("ok"))
    finally:
        try:
            time.sleep(0.3)
            proc.kill()
            out = proc.stdout.read() if proc.stdout else ""
            log = out or ""
        except Exception:
            pass

    print("\n── журнал сервера (помилки) ──")
    errs = [ln for ln in log.splitlines()
            if any(k in ln for k in ("Traceback", "ERROR", "Exception", "⚠"))]
    for ln in errs[-12:]:
        print("  " + ln[:160])
    if not errs:
        print("  (помилок немає)")

    passed = sum(1 for _, ok, _ in results if ok)
    print("\n" + "=" * 50)
    print(f"ПІДСУМОК: {passed}/{len(results)} перевірок пройдено")
    fails = [(n, e) for n, ok, e in results if not ok]
    if fails:
        print("ПРОВАЛИ:")
        for n, e in fails:
            print("  ✗", n, "—", e)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())

