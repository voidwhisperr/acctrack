#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Платформи: ZeusX (профіль, баланс, замовлення, мої лоти), FunPay, Eldorado.

Мережа й файли — тут; залежності з game_tracker ін'єктуються через configure().
"""
import datetime
import json
import os
import re
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request

UD = {}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 OPR/127.0.0.0")
SECRETS_FILE = ""
ED_FILE = ""


def configure(**kw):
    global UA, SECRETS_FILE, ED_FILE
    UD.update(kw)
    UA = kw.get("ua") or UA
    SECRETS_FILE = kw.get("secrets_file") or SECRETS_FILE
    ED_FILE = kw.get("ed_file") or ED_FILE


def _read_json(path, default=None):
    try:
        return UD["read_json"](path, default)
    except Exception:
        return default


def _game_of(title):
    """Гра з назви (хост game_tracker підкладає свою функцію)."""
    try:
        if "game_of" in UD:
            return UD["game_of"](title)
    except Exception:
        pass
    return ""


def _mailq_add(item):
    return UD["mailq_add"](item) if "mailq_add" in UD else False


def _imported_mark(ids):
    if "imported_mark" in UD:
        return UD["imported_mark"](ids)


def _imp_ids():
    return UD["imported_ids"]() if "imported_ids" in UD else set()


def _mailq_list():
    return UD["mail_queue"]() if "mail_queue" in UD else []


def _sup_cache():
    return UD["supplier_cache"]() if "supplier_cache" in UD else []


_platform_cache = {"ts": 0, "data": None}
PLATFORM_TTL = 300


def _sec_get(key, default=""):
    try:
        if not os.path.exists(SECRETS_FILE):
            return default
        return (json.loads(open(SECRETS_FILE, encoding="utf-8").read()).get(key) or default)
    except Exception:
        return default


def _cookie_parse(cookie):
    out = {}
    for part in (cookie or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k:
            out[k.strip()] = v.strip()
    return out


def _zx_call(path, cookie, timeout=20, method="GET", body=None):
    """Запит до api.zeusx.com з Bearer-токеном із cookie."""
    token = _cookie_parse(cookie).get("access_token", "")
    if not token:
        raise RuntimeError("missing access_token in zeusx_cookie")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request("https://api.zeusx.com" + path, data=data, headers={
        "Authorization": "Bearer " + token, "Cookie": cookie, "User-Agent": UA,
        "Accept": "application/json, text/plain, */*", "Content-Type": "application/json",
        "Origin": "https://zeusx.com", "Referer": "https://zeusx.com/",
        "Zeusx-Currency": "USD"}, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _platform_zeusx():
    cookie = _sec_get("zeusx_cookie")
    if not cookie:
        return {"ok": False, "error_code": "zeusx_not_connected",
                "error": "ZeusX is not connected: the access_token cookie is missing. "
                         "Paste it on the Channels tab."}
    try:
        prof = (_zx_call("/v1/user/me", cookie) or {}).get("data") or {}
        bal = (_zx_call("/v1/user/get-user-balance", cookie) or {}).get("data") or {}
        st = (_zx_call("/v1/earning/ongoing-earning-statistic", cookie) or {}).get("data") or {}
        return {"ok": True, "id": prof.get("id"), "name": prof.get("display_name"),
                "email": prof.get("email_address"),
                "seller_tier": prof.get("seller_tier"), "buyer_tier": prof.get("buyer_tier"),
                "verified": bool(prof.get("is_phone_verified")),
                "balance": bal.get("user_balance"), "on_going": bal.get("user_onGoing"),
                "on_hold": bal.get("user_onHold"), "withdraw": bal.get("user_withdraw"),
                "orders_all": st.get("all"), "orders_good": st.get("good_delivery_count"),
                "orders_pending": st.get("pending_delivery_count"),
                "orders_refunded": st.get("refunded_count"),
                "error_code": None, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False,
                "error_code": "zeusx_auth_failed" if e.code in (401, 403) else "zeusx_api_error",
                "error": "HTTP %s: ZeusX request failed" % e.code}
    except Exception as e:
        return {"ok": False, "error_code": "zeusx_api_error",
                "error": f"{type(e).__name__}: {e}"}


def _platform_zeusx_orders(cookie, limit=20):
    """Справжні продажі ZeusX → у чергу 📥 (щоб додати в P&L одним кліком)."""
    added = 0
    try:
        d = _zx_call("/v1/earning/ongoing-earning", cookie, method="POST",
                     body={"pageIndex": 0})
        for e in ((d or {}).get("data") or {}).get("earnings") or []:
            if (e.get("transaction_status") or "").upper() != "SUCCEEDED":
                continue
            oid = "zx-" + str(e.get("transaction_id") or e.get("offer_code") or "")[:40]
            if oid in _imp_ids():
                continue
            price = e.get("listed_price")
            net = e.get("earning_amount")
            item = {
                "id": oid, "ts": int(time.time()), "platform": "ZeusX", "kind": "order",
                "subject": (e.get("title") or "")[:200],
                "body": ("Покупець: %s\nOffer: %s\nЦіна: $%s\nНа руки: $%s\nДата: %s"
                         % (e.get("buyer_login_name") or e.get("buyer_display_name") or "?",
                            e.get("offer_code") or "", price, net,
                            (e.get("purchase_date") or "")[:10])),
                "orderId": str(e.get("offer_code") or ""),
                "price": float(price) if price is not None else None,
                "game": "", "status": "new", "source": "zeusx_api",
            }
            if _mailq_add(item):
                added += 1
            _imported_mark([oid])
            if added >= limit:
                break
    except Exception as e:
        print(f"  ⚠ ZeusX замовлення: {e}", flush=True)
    return added


def _funpay_fetch_orders(cookie):
    """Парсить 'Мої продажі' FunPay (HTML) → список замовлень."""
    req = urllib.request.Request("https://funpay.com/orders/trade", headers={
        "Cookie": cookie, "User-Agent": UA, "Accept": "text/html",
        "Referer": "https://funpay.com/"})
    with urllib.request.urlopen(req, timeout=25) as r:
        html = r.read().decode("utf-8", "replace")
    if "Мої продажі" not in html and "My sales" not in html:
        raise RuntimeError("FunPay cookie is expired - the seller cabinet is not shown")
    out = []
    for m in re.finditer(r'<a href="https://funpay\.com/[^"]*/orders/([A-Z0-9]{4,})/"[^>]*>(.*?)</a>',
                         html, re.S):
        code, block = m.group(1), m.group(2)
        tm = re.search(r'class="tc-date-time">([^<]+)<', block)
        om = re.search(r'class="tc-order">#?([^<]+)<', block)
        stm = re.search(r'class="tc-status[^"]*">([^<]+)<', block)
        pm = re.search(r'class="tc-price[^"]*">([\d.,]+)', block)
        dm = re.search(r'class="order-desc">\s*<div>([^<]+)<', block)
        # другий рядок опису: «Identity V, Аккаунти» = гра + категорія
        gm = re.search(r'class="text-muted">\s*([^<]+)<', block)
        game, cat = "", ""
        if gm:
            meta = " ".join(gm.group(1).split())
            parts = [x.strip() for x in meta.rsplit(",", 1)]
            if len(parts) == 2:
                game, cat = parts[0][:60], parts[1][:40]
            else:
                game = meta[:60]
        price = None
        if pm:
            try:
                price = float(pm.group(1).replace(",", "."))
            except ValueError:
                price = None
        out.append({"code": code, "order_no": (om.group(1).strip() if om else code),
                    "title": " ".join((dm.group(1) if dm else "").split())[:200],
                    "game": game, "category": cat,
                    "status": (stm.group(1).strip() if stm else ""),
                    "date": (tm.group(1).strip() if tm else ""), "price": price})
        if len(out) >= 30:
            break
    return out


def _platform_funpay():
    cookie = _sec_get("funpay_cookie")
    if not cookie:
        return {"ok": False, "error_code": "funpay_not_connected",
                "error": "FunPay is not connected: the golden_key cookie is missing. "
                         "Paste it on the Channels tab."}
    try:
        orders = _funpay_fetch_orders(cookie)
        return {"ok": True, "orders": [o["code"] for o in orders][:20],
                "orders_count": len(orders), "counter": 0, "chats": 0,
                "list": orders[:15], "error_code": None, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False,
                "error_code": "funpay_cookie_expired" if e.code in (401, 403) else "funpay_api_error",
                "error": "HTTP %s: FunPay request failed" % e.code}
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        low = msg.lower()
        code = ("funpay_cookie_expired" if ("expired" in low or "cookie" in low)
                else "funpay_api_error")
        return {"ok": False, "error_code": code, "error": msg}


def _platform_funpay_orders(cookie, limit=20, orders=None):
    """Нові продажі FunPay → у чергу 📥 (orders можна передати, щоб не робити 2 запити)."""
    added = 0
    try:
        for o in (orders if orders is not None else _funpay_fetch_orders(cookie)):
            st = (o.get("status") or "").lower()
            if st and not any(k in st for k in ("сплач", "paid", "заверш", "completed",
                                                "викон", "выполн")):
                continue
            if not o.get("price"):
                continue
            fid = "fp-" + o["code"]
            if fid in _imp_ids():
                continue
            item = {"id": fid, "ts": int(time.time()), "platform": "FunPay",
                    "kind": "order", "subject": o.get("title") or ("Замовлення " + o["code"]),
                    "body": ("Замовлення: %s\nГра: %s\nКатегорія: %s\nСтатус: %s\n"
                             "Сума «на руки»: $%s\nКоли: %s"
                             % (o.get("order_no"), o.get("game") or "—",
                                o.get("category") or "—", o.get("status"),
                                o.get("price"), o.get("date"))),
                    "orderId": str(o.get("order_no") or o["code"]),
                    "price": float(o["price"]),
                    "game": (o.get("game") or _game_of("%s %s" % (
                        o.get("title") or "", o.get("category") or ""))),
                    "category": o.get("category") or "",
                    "status": "new", "source": "funpay_html"}
            if _mailq_add(item):
                added += 1
            _imported_mark([fid])
            if added >= limit:
                break
    except Exception as e:
        print(f"  ⚠ FunPay замовлення: {e}", flush=True)
    return added


def _platform_eldorado():
    """Eldorado API немає — показуємо те, що вже є в трекері (пошта + ручний облік)."""
    try:
        data = _read_json(ED_FILE, []) or []
        if not isinstance(data, list):
            data = []
        mon = datetime.date.today().strftime("%Y-%m")
        month = [x for x in data if str(x.get("date") or "").startswith(mon)]
        return {"ok": True, "count": len(data),
                "revenue": round(sum(float(x.get("price") or 0) for x in data), 2),
                "profit": round(sum(float(x.get("profit") or 0) for x in data), 2),
                "month_count": len(month),
                "month_profit": round(sum(float(x.get("profit") or 0) for x in month), 2),
                "source": "email + manual", "error_code": None, "error": None}
    except Exception as e:
        return {"ok": False, "error_code": "eldorado_api_error",
                "error": f"{type(e).__name__}: {e}"}


_offers_cache = {"ts": 0, "data": None}

_STOP_WORDS = {
    "global", "server", "instant", "starter", "account", "accounts", "android", "ios",
    "delivery", "custom", "version", "packs", "gems", "rank", "fresh", "available",
    "characters", "with", "more", "multiple", "combinations", "from", "this", "that",
    "your", "have", "sale", "cheap", "best", "shop", "store", "blueprint", "skin",
    "level", "levels", "auto", "fast", "safe", "verified", "region", "service",
}


def _title_tokens(text):
    words = re.findall(r"[A-Za-z][A-Za-z0-9']{3,}", str(text or "").lower())
    return [w for w in words if w not in _STOP_WORDS]


def _supplier_match(title, game=""):
    """Мін/медіана постачальників за спільними словами назви (без мапінгу ігор)."""
    toks = set(_title_tokens(title)) | set(_title_tokens(game))
    if not toks:
        return None
    prices = []
    for p in _sup_cache():
        if not (toks & set(_title_tokens(p.get("title")))):
            continue
        try:
            v = float(p.get("price") or 0)
        except (TypeError, ValueError):
            continue
        if v > 0:
            prices.append(v)
    if not prices:
        return None
    return {"min": round(min(prices), 2),
            "median": round(statistics.median(prices), 2), "n": len(prices)}


def my_offers(cookie=None, limit=60):
    """Мої активні лоти на ZeusX (публічний список продавця)."""
    cookie = cookie or _sec_get("zeusx_cookie")
    if not cookie:
        return {"ok": False, "error_code": "zeusx_not_connected",
                "error": "ZeusX is not connected: the access_token cookie is missing. "
                         "Paste it on the Channels tab."}
    try:
        prof = (_zx_call("/v1/user/me", cookie) or {}).get("data") or {}
        seller_id = prof.get("id")
        if not seller_id:
            return {"ok": False, "error_code": "zeusx_seller_missing",
                    "error": "Could not determine the ZeusX seller_id"}
        path = ("/v1/offer/get-selling-offers-by-seller?seller_id=%s"
                "&pageIndex=0&sort=newest&product_state=Available" % seller_id)
        d = _zx_call(path, cookie) or {}
        items = ((d.get("data") or {}).get("sellingProducts") or [])[:limit]
        out = []
        for x in items:
            try:
                price = float(x.get("listed_price") or x.get("item_price") or 0)
            except (TypeError, ValueError):
                price = 0.0
            out.append({
                "id": x.get("offer_id") or "",
                "title": str(x.get("title") or "")[:180],
                "game": str(x.get("base_name") or "")[:60],
                "price": round(price, 2),
                "qty": x.get("quantity"),
                "status": x.get("offer_status") or "",
                "slug": x.get("slug") or "",
                "url": ("https://zeusx.com/offer/" + str(x.get("slug"))) if x.get("slug") else "",
                "created": x.get("created_date") or "",
                "likes": x.get("liking_count") or 0,
                "rating": x.get("seller_rating"),
            })
        return {"ok": True, "items": out, "count": len(out), "seller_id": seller_id,
                "error_code": None, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False,
                "error_code": "zeusx_auth_failed" if e.code in (401, 403) else "zeusx_api_error",
                "error": "HTTP %s: ZeusX request failed" % e.code}
    except Exception as e:
        return {"ok": False, "error_code": "zeusx_api_error",
                "error": f"{type(e).__name__}: {e}"}


_platform_refreshing = {"on": False}


def _platforms_refresh_bg():
    """Фонове оновлення (щоб UI не чекав 8-10 с на зовнішні API)."""
    if _platform_refreshing["on"]:
        return
    _platform_refreshing["on"] = True
    try:
        platforms_data(force=True)
    except Exception as e:
        print(f"  ⚠ platforms bg: {e}", flush=True)
    finally:
        _platform_refreshing["on"] = False


def platforms_data(force=False):
    """Профілі, баланси, статистика + імпорт нових продажів у чергу.

    Застарілий кеш віддаємо одразу, а оновлення йде у фоні.
    """
    now = time.time()
    if not force and _platform_cache["data"]:
        if now - _platform_cache["ts"] < PLATFORM_TTL:
            return _platform_cache["data"]
        import threading
        threading.Thread(target=_platforms_refresh_bg, daemon=True).start()
        return _platform_cache["data"]
    z = _platform_zeusx()
    f = _platform_funpay()
    iz = _platform_zeusx_orders(_sec_get("zeusx_cookie")) if z.get("ok") else 0
    ifp = (_platform_funpay_orders(_sec_get("funpay_cookie"), orders=f.get("list"))
           if f.get("ok") else 0)
    # «чати»: кількість нових повідомлень з пошти по платформах
    msgs = {}
    for it in (_mailq_list() or []):
        if it.get("kind") == "message" and it.get("status") == "new":
            p = it.get("platform") or "?"
            msgs[p] = msgs.get(p, 0) + 1
    data = {"zeusx": z, "funpay": f, "eldorado": _platform_eldorado(),
            "mail_msgs": msgs, "zeusx_imported": iz, "funpay_imported": ifp, "ts": int(now)}
    _platform_cache.update({"ts": now, "data": data})
    return data

