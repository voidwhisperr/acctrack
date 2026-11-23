#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taobao: стан, імпорт лотів, порівняння з постачальниками, дані для вкладки.

Стан живе тут; залежності з game_tracker передаються через configure(),
тому циклічних імпортів немає.
"""
import json
import re
import statistics
import threading
import time
import types

import taobao_core

UD = {}                      # ін'єкції
SETTINGS_FILE = ""
TAOBAO_FILE = ""
_WRITE_LOCK = threading.Lock()
_html_mod = types.SimpleNamespace(escape=lambda x: str(x))


def configure(**kw):
    global SETTINGS_FILE, TAOBAO_FILE, _WRITE_LOCK, _html_mod
    UD.update(kw)
    SETTINGS_FILE = kw.get("settings_file") or SETTINGS_FILE
    TAOBAO_FILE = kw.get("data_file") or TAOBAO_FILE
    _WRITE_LOCK = kw.get("write_lock") or _WRITE_LOCK
    _html_mod = kw.get("html_mod") or _html_mod
    _taobao_load()


def _read_json(path, default=None):
    try:
        return UD["read_json"](path, default)
    except Exception:
        return default


def _atomic_dump(path, obj):
    UD["atomic_dump"](path, obj)


def _tg_cfg():
    return UD["tg_cfg"]() if "tg_cfg" in UD else {}


def _tg_send(text):
    return UD["tg_send"](text) if "tg_send" in UD else {"ok": False}


def _sup():
    return UD["supplier_cache"]() if "supplier_cache" in UD else []


def _taobao_en(title):
    return taobao_core.translate(title)


def _taobao_segment(title):
    return taobao_core.segment(title)


def _taobao_region(title):
    return taobao_core.region(title)


USD_CNY = taobao_core.USD_CNY
LANDED_PCT = taobao_core.LANDED_PCT
TAOBAO_SKIP_GAMES = set(taobao_core.SKIP_GAMES)
_TAOBAO_GAME_PATTERNS = taobao_core.GAME_PATTERNS


_taobao = {"items": [], "runs": [], "ts": 0, "request": 0, "last_run": 0,
           "agent_seen": 0, "progress": {}}
TAOBAO_COOLDOWN = 3 * 3600      # не частіше ніж раз на 3 год (анти-блок)
LANDED_PCT = taobao_core.LANDED_PCT if taobao_core else 0.07
TAOBAO_SKIP_GAMES = set(taobao_core.SKIP_GAMES) if taobao_core else {"Genshin", "Honkai Star Rail"}
_taobao_lock = threading.Lock()
USD_CNY = taobao_core.USD_CNY if taobao_core else 7.2





def _taobao_load():
    d = _read_json(TAOBAO_FILE, {})
    if isinstance(d, dict):
        for k in ("items", "runs", "ts", "request", "last_run", "agent_seen", "progress"):
            if k in d:
                _taobao[k] = d[k]
    if not isinstance(_taobao.get("items"), list):
        _taobao["items"] = []
    if not isinstance(_taobao.get("runs"), list):
        _taobao["runs"] = []
    # прибрати ігри, які не продаються
    _taobao["items"] = [x for x in _taobao["items"]
                        if not (isinstance(x, dict) and x.get("game") in TAOBAO_SKIP_GAMES)]
    # перерахувати переклад/тип для вже збережених лотів
    for x in _taobao["items"]:
        if not isinstance(x, dict):
            continue
        if x.get("title_cn"):
            x["title_en"] = _taobao_en(x["title_cn"])
            x["segment"] = _taobao_segment(x["title_cn"])
            x["region"] = _taobao_region(x["title_cn"])
            if "终末地" in x["title_cn"]:
                x["game"] = "Arknights Endfield"



def _taobao_save():
    try:
        _atomic_dump(TAOBAO_FILE, _taobao)
    except Exception:
        pass



# Реклама «зайди на сайт і вибери акаунт» — не товар, а приманка за копійку
_TAOBAO_ADS = re.compile(
    r"自定义|自选|选号|挑选|选择账号|selectable|select account|choose your account|"
    r"custom\s*select|custom\s*account|build your account|套餐|代充|充值|客服咨询|"
    r"话费|点卡|游戏币|虚拟商品|预约|预售|预定",
    re.I)


def _taobao_is_ad(title):
    return bool(_TAOBAO_ADS.search(str(title or "")))


def _taobao_manual(body):
    """Додати лот вручну: посилання, назва, ціна ¥, картка, варіанти."""
    href = str(body.get("href") or "").strip()
    if "item.taobao.com" not in href and "detail.tmall.com" not in href:
        return {"ok": False, "error": "посилання має бути на item.taobao.com або detail.tmall.com"}
    if "id=" not in href:
        return {"ok": False, "error": "у посиланні немає id= (відкрийте лот і скопіюйте адресу)"}
    try:
        price = float(body.get("price_cny") or 0)
    except (TypeError, ValueError):
        price = 0
    if price <= 0:
        return {"ok": False, "error": "вкажіть ціну в юанях"}
    title = str(body.get("title") or "").strip()[:200]
    res = _taobao_upsert({"game": str(body.get("game") or "Other")[:40],
                          "query": "manual", "manual": True,
                          "items": [{"href": href, "title": title or "Manual lot",
                                     "price": price}]})
    if not res.get("ok"):
        return res
    _taobao_mark(href, bool(body.get("card_pay")), int(body.get("options") or 0))
    rec = next((x for x in _taobao["items"] if x.get("href") == href), None)
    return {"ok": True, "item": rec}


def _taobao_mark(href, card_pay=None, options=None, cart=None):
    """Ручна мітка лота: оплата карткою / кількість варіантів (з ваших очей)."""
    with _taobao_lock:
        rec = next((x for x in _taobao["items"] if x.get("href") == href), None)
        if not rec:
            return {"ok": False, "error": "лот не знайдено"}
        if card_pay is not None:
            rec["card_pay"] = bool(card_pay)
            rec["card_manual"] = True
        if options is not None:
            try:
                rec["options"] = max(0, min(999, int(options)))
            except (TypeError, ValueError):
                pass
        if cart is not None:
            rec["cart"] = bool(cart)
        rec["enriched"] = int(time.time())
        _taobao_save()
        return {"ok": True, "href": href, "card_pay": rec.get("card_pay"),
                "options": rec.get("options")}


def _taobao_enrich(rows, blocked=0, requested=0):
    """Збагачення лотів даними зі сторінки: оплата карткою, к-сть варіантів, продано."""
    if not isinstance(rows, list):
        return {"ok": False, "error": "rows має бути списком"}
    with _taobao_lock:
        by_href = {x.get("href"): x for x in _taobao["items"]}
        n = 0
        for r in rows[:200]:
            href = str(r.get("href") or "")
            rec = by_href.get(href)
            if not rec:
                continue
            rec["card_pay"] = bool(r.get("card_pay"))
            try:
                rec["options"] = max(0, int(r.get("options") or 0))
            except (TypeError, ValueError):
                rec["options"] = 0
            sold = str(r.get("sold") or "")[:20]
            if sold:
                rec["sold"] = sold
            rec["enriched"] = int(time.time())
            n += 1
        _taobao["enrich_request"] = 0
        _taobao["enrich_last"] = {"ts": int(time.time()), "checked": n,
                                  "blocked": int(blocked or 0),
                                  "requested": int(requested or 0)}
        _taobao_save()
    return {"ok": True, "updated": n, "blocked": int(blocked or 0)}


def _taobao_upsert(body):
    """Додає/оновлює лоти (дедуп за посиланням)."""
    game = str(body.get("game") or "")[:40]
    query = str(body.get("query") or "")[:80]
    items = body.get("items") or []
    manual = bool(body.get("manual"))
    if not isinstance(items, list):
        return {"ok": False, "error": "items має бути списком"}
    now = int(time.time())
    added = updated = 0
    with _taobao_lock:
        by_href = {x.get("href"): x for x in _taobao["items"]}
        for it in items[:60]:
            href = str(it.get("href") or "").strip()
            if "item.taobao.com" not in href and "detail.tmall.com" not in href:
                continue
            if "id=" not in href:
                continue
            try:
                price = float(it.get("price") or 0)
            except (TypeError, ValueError):
                continue
            if price <= 0 or price > 100000:
                continue
            title_raw = str(it.get("title") or "")
            if not manual and _taobao_is_ad(title_raw):
                continue          # «вибери акаунт на сайті» — реклама
            # поріг: за копійки продають не акаунти, а приманки
            try:
                _min_cny = float((_read_json(SETTINGS_FILE, {}) or {}).get("taobao_min_cny") or 5)
            except (TypeError, ValueError):
                _min_cny = 5.0
            if not manual and price < _min_cny:
                continue
            title = str(it.get("title") or "")[:200]
            if "终末地" in title:
                game_i = "Arknights Endfield"
            else:
                game_i = game or (by_href.get(href) or {}).get("game") or ""
            if game_i in TAOBAO_SKIP_GAMES:
                continue
            rec = by_href.get(href)
            if rec is None:
                rec = {"href": href, "created": now}
                _taobao["items"].append(rec)
                by_href[href] = rec
                added += 1
            else:
                updated += 1
            rec.update({
                "title_cn": title,
                "title_en": _taobao_en(title),
                "region": _taobao_region(title),
                "price_cny": round(price, 2),
                "price_usd": round(price / USD_CNY, 2),
                "sold": str(it.get("sold") or "")[:12],
                "segment": _taobao_segment(title),
                "game": game or rec.get("game") or "",
                "query": query or rec.get("query") or "",
                "ts": now,
            })
        # тримаємо максимум 1500 лотів (найсвіжіші)
        if len(_taobao["items"]) > 1500:
            _taobao["items"] = sorted(_taobao["items"], key=lambda x: x.get("ts") or 0)[-1500:]
        _taobao["runs"] = ([{"ts": now, "game": game, "query": query,
                             "found": len(items)}] + _taobao["runs"])[:50]
        _taobao["ts"] = now
        _taobao["request"] = 0
        _taobao["last_run"] = now
    _taobao_save()
    print(f"  🇨🇳 Taobao: {game or query} — нових {added}, оновлено {updated}", flush=True)
    try:
        cfg = _tg_cfg()
        st = _read_json(SETTINGS_FILE, {}) or {}
        minx = float(st.get("deal_x") or 5)
        if (bool(st.get("notify_deal", False))
                and cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")):
            idx = _taobao_sup_index()
            sent = set(st.get("deal_sent") or [])
            deals = []
            for x in _taobao["items"]:
                if x.get("href") in sent or not x.get("price_usd"):
                    continue
                sup = idx.get(x.get("game") or "")
                if not sup or not sup.get("min"):
                    continue
                landed = float(x["price_usd"]) * (1 + LANDED_PCT)
                if landed > 0 and sup["min"] / landed >= minx:
                    deals.append((sup["min"] / landed, x))
            if deals:
                deals.sort(key=lambda t: -t[0])
                lines = ["🔥 <b>Вигідні лоти Taobao</b> · ≥%.0fx" % minx]
                for ratio, x in deals[:5]:
                    title = _html_mod.escape((x.get("title_en") or x.get("title_cn") or "")[:45])
                    url = _html_mod.escape(str(x.get("href") or ""), quote=True)
                    link = '<a href="%s">%s</a>' % (url, title) if url else title
                    lines.append("• %s — <b>×%.1f</b>" % (link, ratio))
                    sent.add(x.get("href"))
                if len(deals) > 5:
                    lines.append("…і ще %d" % (len(deals) - 5))
                _tg_send("\n".join(lines))
                with _WRITE_LOCK:
                    st2 = _read_json(SETTINGS_FILE, {}) or {}
                    st2["deal_sent"] = list(sent)[-500:]
                    _atomic_dump(SETTINGS_FILE, st2)
                print(f"  🔥 Алерт: {len(deals[:5])} вигідних лотів", flush=True)
    except Exception as e:
        print(f"  ⚠ deal alert: {e}", flush=True)
    return {"ok": True, "added": added, "updated": updated,
            "total": len(_taobao["items"])}


# гра Taobao → як шукати її у каталозі постачальників
_taobao_sup_cache = {"ts": 0, "data": None}



def _taobao_sup_index():
    """Мін/медіана цін постачальників по кожній грі (кеш 10 хв)."""
    if _taobao_sup_cache["data"] is not None and time.time() - _taobao_sup_cache["ts"] < 600:
        return _taobao_sup_cache["data"]
    out = {}
    for game, pat in _TAOBAO_GAME_PATTERNS.items():
        try:
            prs = [float(p.get("price") or 0) for p in _sup()
                   if p.get("price") and re.search(pat, str(p.get("title") or ""), re.I)]
        except Exception:
            prs = []
        prs = [x for x in prs if 0 < x < 100000]
        if prs:
            out[game] = {"min": round(min(prs), 2),
                         "median": round(statistics.median(prs), 2), "n": len(prs)}
    _taobao_sup_cache.update({"ts": time.time(), "data": out})
    return out



def taobao_data():
    items = sorted(_taobao["items"], key=lambda x: (x.get("game") or "", x.get("price_cny") or 0))
    idx = _taobao_sup_index()
    # додаємо ціну постачальника + різницю до кожного лота
    for x in items:
        usd = float(x.get("price_usd") or 0)
        x["landed_usd"] = round(usd * (1 + LANDED_PCT), 2) if usd else 0
        sup = idx.get(x.get("game") or "")
        if not sup:
            x.pop("sup", None)
            continue
        x["sup"] = {"min": sup["min"], "median": sup["median"], "n": sup["n"]}
        x["diff_usd"] = round(sup["min"] - usd, 2)
        x["diff_x"] = round(sup["min"] / usd, 1) if usd > 0 else None
    summary = []
    for game, sup in idx.items():
        tb = [float(x["price_usd"]) for x in items if x.get("game") == game and x.get("price_usd")]
        if not tb:
            continue
        summary.append({"game": game, "tb_min": round(min(tb), 2),
                        "tb_median": round(statistics.median(tb), 2),
                        "sup_min": sup["min"], "sup_median": sup["median"],
                        "n_tb": len(tb), "n_sup": sup["n"]})
    summary.sort(key=lambda r: -(r["sup_min"] / r["tb_min"] if r["tb_min"] else 0))
    now = time.time()
    last = int(_taobao.get("last_run") or 0)
    stt = _read_json(SETTINGS_FILE, {}) or {}
    try:
        usd_cny = float(stt.get("usd_cny") or USD_CNY)
    except (TypeError, ValueError):
        usd_cny = USD_CNY
    cart = [x for x in items if x.get("cart")]
    cart_cny = round(sum(float(x.get("price_cny") or 0) for x in cart), 2)
    cart_usd = round(cart_cny / usd_cny, 2) if usd_cny else 0
    cart_landed = round(cart_usd * (1 + LANDED_PCT), 2)

    pg = dict(_taobao.get("progress") or {})
    # якщо збір «завис» назавжди — ховаємо смугу й кажемо правду
    if pg.get("total") and not pg.get("finished") and now - int(pg.get("ts") or 0) > 900:
        pg["finished"] = True
        pg["current"] = "збір не вдався (таймаут 15 хв)"

    seen = int(_taobao.get("agent_seen") or 0)
    agent_online = bool(seen and (now - seen) < 45)
    return {"ok": True, "ts": _taobao.get("ts") or 0, "count": len(items),
            "agent_seen": seen, "agent_online": agent_online,
            "agent_ago": (int(now - seen) if seen else None),
            "progress": pg,
            "items": items, "runs": _taobao["runs"][:20], "usd_cny": USD_CNY,
            "landed_pct": LANDED_PCT,
            "min_cny": float(stt.get("taobao_min_cny") or 5),
            "usd_cny": usd_cny,
            "usd_cny_ts": stt.get("usd_cny_ts") or 0,
            "cart": {"count": len(cart), "cny": cart_cny, "usd": cart_usd,
                     "landed": cart_landed},
            "enrich_request": int(_taobao.get("enrich_request") or 0),
            "enrich_last": _taobao.get("enrich_last") or {},
            "request": int(_taobao.get("request") or 0), "last_run": last,
            "next_in": max(0, int(last + TAOBAO_COOLDOWN - now)),
            "summary": summary}


