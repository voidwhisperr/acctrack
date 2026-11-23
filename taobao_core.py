#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чисті функції для Taobao: переклад, тип лота, регіон, шаблони ігор.

Тут НЕМАЄ стану, файлів і мережі — тільки перетворення тексту.
Це дозволяє тестувати їх окремо й безпечно переносити решту логіки.

Імпортується з game_tracker.py як `taobao_core`.
"""
import re

USD_CNY = 7.2          # курс юаня до долара (орієнтовно)
LANDED_PCT = 0.07      # посередник за оплату Alipay + доставка

# ігри, які не продаються — не збираємо і не показуємо
SKIP_GAMES = ("Genshin", "Honkai Star Rail")

# китайські терміни → англійська (порядок важливий: довші — першими)
CN_EN = [
    ("明日方舟终末地", "Arknights Endfield"), ("明日方舟", "Arknights"),
    ("アークナイツ", "Arknights"), ("命运冠位指定", "Fate Grand Order"),
    ("命运冠位", "FGO"), ("fgo", "FGO"), ("FGO", "FGO"),
    ("绝区z零", "Zenless Zone Zero"), ("绝区零", "Zenless Zone Zero"), ("绝区0", "ZZZ"),
    ("鸣潮", "Wuthering Waves"), ("战双帕弥什", "Punishing Gray Raven"),
    ("胜利女神", "Nikke"), ("NIKKE", "Nikke"), ("碧蓝档案", "Blue Archive"),
    ("七龙珠", "Dragon Ball"), ("爆裂大战", "Dokkan Battle"),
    ("初始号", "starter account"), ("自抽号", "self-draw starter"),
    ("自抽", "self-draw"), ("自选", "selectable"), ("开局号", "starter account"),
    ("石头号", "gem account"), ("成品号", "developed account"), ("成品", "developed"),
    ("毕业号", "endgame account"), ("毕业", "endgame"), ("满级", "max level"),
    ("全图鉴", "full collection"), ("六星", "6-star"), ("五星", "5-star"),
    ("官服", "CN server"), ("日服", "JP server"), ("台服", "TW server"),
    ("韩服", "KR server"), ("国际服", "Global server"), ("国际", "Global"),
    ("亚服", "Asia server"), ("欧服", "EU server"), ("美服", "NA server"),
    ("港澳台", "HK/TW"), ("安卓", "Android"), ("苹果", "iOS"), ("ios", "iOS"),
    ("全联动", "all collabs"), ("账号", "account"), ("帳號", "account"),
    ("终末地", "Endfield"), ("国服", "CN server"),
    ("自动发货", "instant delivery"), ("出售", "for sale"), ("盲盒号", "blind-box account"),
    ("非科技", "legit"), ("组合", "bundle"), ("自选号", "selectable"), ("解绑", "unbind"),
    ("换绑", "rebind"), ("空白号", "blank account"), ("资料转移", "data transfer"),
]

# регіон сервера з назви лота
REGION_RULES = [
    ("Global", ("国际服", "国际", "全球", "global")),
    ("Asia", ("亚服", "亚洲")),
    ("EU", ("欧服", "欧洲")),
    ("NA", ("美服", "北美")),
    ("JP", ("日服", "日本")),
    ("TW", ("台服", "港澳台", "繁中")),
    ("KR", ("韩服", "韩国")),
    ("CN", ("官服", "国服", "安卓b服", "b服", "ios官服")),
]

# гра Taobao → як шукати її у каталозі постачальників
GAME_PATTERNS = {
    "Arknights Endfield": r"endfield|终末地",
    "Arknights": r"arknights|方舟",
    "FGO": r"\bfgo\b|\bfate\b|冠位",
    "Zenless Zone Zero": r"zenless|zzz|绝区",
    "Wuthering Waves": r"wuthering|wuwa|鸣潮",
    "Nikke": r"nikke|胜利女神",
    "Blue Archive": r"blue archive|碧蓝档案",
    "Genshin": r"genshin|原神",
    "Honkai Star Rail": r"star rail|honkai|星穹",
    "Dokkan": r"dokkan|七龙珠|爆裂",
}

_CJK = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uff00-\uffef]+")


def translate(title):
    """Переклад ключових термінів: без ієрогліфів і без повторів слів."""
    t = str(title or "")
    for cn, en in CN_EN:
        t = t.replace(cn, " " + en + " ")
    t = _CJK.sub(" ", t)
    t = re.sub(r"[\u3000\s]+", " ", t).strip()
    seen_w, out_w = set(), []
    for w in t.split():
        lw = w.lower().strip(",.;:!?")
        if lw and not lw.isdigit() and lw in seen_w:
            continue
        seen_w.add(lw)
        out_w.append(w)
    t = " ".join(out_w)
    t = re.sub(r"\s*([,;:!?])\s*", r"\1 ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" ,;:!?-")
    return t[:160] or "(без опису)"


def segment(title):
    """Тип лота: starter / developed / endgame / other."""
    t = str(title or "")
    if any(k in t for k in ("毕业", "满级", "全图鉴", "满命", "全角色", "满星")):
        return "endgame"
    if any(k in t for k in ("初始", "自抽", "自选", "开局", "石头号")):
        return "starter"
    if any(k in t for k in ("成品", "图鉴", "号")):
        return "developed"
    return "other"


def region(title):
    """Регіон сервера (Global/JP/TW/KR/CN/Asia/EU/NA) або ''."""
    t = str(title or "").lower()
    for name, keys in REGION_RULES:
        for k in keys:
            if k in t:
                return name
    return ""


def landed(price_usd, pct=None):
    """Ціна з урахуванням посередника й доставки."""
    try:
        return round(float(price_usd) * (1 + (LANDED_PCT if pct is None else pct)), 2)
    except (TypeError, ValueError):
        return 0.0
