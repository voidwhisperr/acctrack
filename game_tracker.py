#!/usr/bin/env python3
"""
Game Account Tracker v4.6
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ПРОДАЖІ   : ручний облік (P&L) + ELDORADO
  ЗАКУПІВЛЯ : 4 Shopify-постачальники (нове / що зникло)
  БЕКАП     : P&L + ELDORADO + ціль · gt_backups/ + хмара + відновлення
  ПОШТА     : Gmail IMAP → Telegram (нові замовлення/повідомлення)

ЩО ЗМІНЕНО В v4.6 (відносно v4.4):
  • прибрано 326 демо-записів, які автоматично засівались у P&L
  • сервер валідовує всі записи: порожній/битий POST більше не стирає дані
  • битий JSON не читається як «0 записів»: 500 + карантин файлу
  • атомарний запис з блокуванням і унікальним tmp (без torn-файлів)
  • сервер піднімається ДО скрапінгу постачальників
  • Gmail-сповіщення повернено (стан перевірок зберігається на диску)
  • UTF-8 stdout (Windows cp1251 більше не вбиває фоновий бекап)
  • auth: не-ASCII логін не валить запит; rate limit на 401
  • security-заголовки, Host allowlist, ліміт тіла запиту
  • ЗАКУПІВЛЯ: gzip+ETag (947 КБ → 95 КБ, повторно 0 байт), пагінація по 50
  • ⚖ порівняння цін між 4 магазинами (та сама гра/регіон/схожа ціна)
  • 🗑 «що зникло»: товари, які зникли з полиць, помічаються на 14 днів
  • ⬇⬆ експорт/імпорт усіх даних одним zip з sha256-перевіркою
  • PWA: service worker зареєстровано (без кешу — UI завжди свіжий)

НАЛАШТУВАННЯ:
  1. python game_tracker.py
  2. http://localhost:8765 — логін/пароль з .gt_secrets.json
  3. З телефона по Wi-Fi: http://<IP-ПК>:8765
  4. ⚙️ → Gmail: адреса + App Password (Google Account → Security → App passwords)
  5. Одноразово (якщо у P&L були демо-записи): python cleanup_demo.py --apply

ХОСТИНГ (Vultr та інші VPS):
  • GT_BIND=127.0.0.1 — слухати лише локально, назовні через nginx з TLS
  • пароль мусить бути ≥8 символів і не дефолтний, інакше на 0.0.0.0 старт
    блокується (обхід: GT_ALLOW_WEAK_PASS=1)
  • POST захищений CSRF-токеном (cookie gt_csrf + заголовок X-GT-CSRF),
    тому працює за будь-яким доменом/проксі; після оновлення — Ctrl+F5
  • деталі: VULTR_DEPLOY.md поруч
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ╔══════════════════════════════════════════════╗
# ║  ⚙️  НАЛАШТУВАННЯ                           ║
# ╚══════════════════════════════════════════════╝
SCRAPER_API_KEY  = ""   # ← .gt_secrets.json -> "scraper_api_key" (обхід блокування Shopify)
# ════════════════════════════════════════════════

import os, sys, json, time, threading, urllib.request, urllib.parse, shutil, datetime
import http.server, webbrowser, pathlib, base64, hmac, subprocess, socket
import gzip, hashlib, io, zipfile, tarfile, html as _html_mod, re, random, statistics, csv

try:
    import ui                     # HTML-шаблон дашборда
except Exception:                 # модуль відсутній — без UI
    ui = None

try:
    import taobao_core          # чисті функції Taobao (без стану)
except Exception:
    taobao_core = None

# Windows-консоль часто в cp1251/cp866: будь-який print з емодзі валив фоновий
# потік бекапу (UnicodeEncodeError). Перемикаємо stdout/stderr на UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PORT = int(os.environ.get("PORT") or os.environ.get("GT_PORT") or "8766")
# GT_BIND=127.0.0.1 — слухати лише локально (рекомендовано за nginx/Cloudflare)
BIND = (os.environ.get("GT_BIND") or "127.0.0.1").strip() or "127.0.0.1"
# GT_AUTH=off — не вимагати пароль (коли застосунок стоїть за Cloudflare Access
# і слухає лише 127.0.0.1). GT_REQUIRE_ACCESS=1 — додатково вимагати заголовок
# від Cloudflare, щоб навіть локальний обхід тунелю не працював.
AUTH_MODE = (os.environ.get("GT_AUTH") or "").strip().lower()  # "" = вирішуємо після налаштувань
REQUIRE_ACCESS = (os.environ.get("GT_REQUIRE_ACCESS") or "").strip() == "1"
_SESSION_SECRET = base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")
_BASE_DIR   = pathlib.Path(os.environ.get("GT_DATA_DIR") or pathlib.Path(__file__).parent)
try:
    _BASE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass
PL_FILE       = str(_BASE_DIR / ".gt_pl.json")
ED_FILE       = str(_BASE_DIR / ".gt_eldorado.json")
GOAL_FILE     = str(_BASE_DIR / ".gt_goal.json")
BACKUP_DIR    = str(_BASE_DIR / "gt_backups")
SUP_TS_FILE   = str(_BASE_DIR / ".gt_sup_ts.json")
SCRAPER_STATE_FILE = str(_BASE_DIR / ".gt_scraper.json")
NEWS_STATE_FILE = str(_BASE_DIR / ".gt_sitemap.json")
TAOBAO_FILE = str(_BASE_DIR / ".gt_taobao.json")
INVENTORY_FILE = str(_BASE_DIR / ".gt_inventory.json")
SETTINGS_FILE = str(_BASE_DIR / ".gt_settings.json")
TG_FILE       = str(_BASE_DIR / ".gt_tg.json")
GMAIL_STATE_FILE = str(_BASE_DIR / ".gt_gmail_state.json")
MAIL_QUEUE_FILE  = str(_BASE_DIR / ".gt_mail_queue.json")
_START_TS = time.time()
UA   = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 OPR/127.0.0.0"

# 🔐 АВТОРИЗАЦІЯ (браузер спитає логін/пароль при відкритті дашборду)
AUTH_USER = os.environ.get("GT_AUTH_USER", "admin")
AUTH_PASS = os.environ.get("GT_AUTH_PASS", "gametracker2026")

SECRETS_FILE = str(_BASE_DIR / ".gt_secrets.json")

_WRITE_LOCK = threading.RLock()

def _atomic_write(path, text):
    """Атомарний запис: унікальний tmp + fsync + os.replace під блокуванням.

    Унікальний tmp потрібен, бо два потоки (напр. /api/settings/save і
    оновлення курсу) писали один і той самий path.tmp і псували файл.
    """
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    with _WRITE_LOCK:
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except OSError:
                pass

_SNAP_LAST = {}
SNAP_KEEP = 20          # скільки знімків тримати на файл
SNAP_MIN_GAP = 180      # не частіше ніж раз на 3 хв на файл
SNAP_TOTAL_MB = 60      # загальний ліміт папки знімків


def _snapshot_before_save(path, tag):
    """Копія файлу перед перезаписом: не частіше 3 хв, максимум 20 на файл."""
    try:
        if not os.path.exists(path) or os.path.getsize(path) < 3:
            return
        now = time.time()
        if now - float(_SNAP_LAST.get(tag) or 0) < SNAP_MIN_GAP:
            return
        _SNAP_LAST[tag] = now
        os.makedirs(BACKUP_DIR, exist_ok=True)
        nm = "%s_%s.json" % (tag, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(path, os.path.join(BACKUP_DIR, nm))
        olds = sorted(f for f in os.listdir(BACKUP_DIR) if f.startswith(tag + "_2"))
        for f in olds[:-SNAP_KEEP]:
            try:
                os.remove(os.path.join(BACKUP_DIR, f))
            except OSError:
                pass
        # загальний ліміт папки
        files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR)
                 if "_2" in f and f.endswith(".json")]
        total = sum(os.path.getsize(x) for x in files if os.path.exists(x))
        if total > SNAP_TOTAL_MB * 1024 * 1024:
            for x in sorted(files, key=lambda z: os.path.getmtime(z))[:-SNAP_KEEP]:
                try:
                    os.remove(x)
                except OSError:
                    pass
    except Exception as e:
        print(f"  ⚠ snapshot {tag}: {e}", flush=True)


_SNAP_TAGS = None


def _atomic_dump(path, obj):
    global _SNAP_TAGS
    if _SNAP_TAGS is None:
        _SNAP_TAGS = {PL_FILE: "snap_pl", ED_FILE: "snap_ed",
                      INVENTORY_FILE: "snap_inv", SETTINGS_FILE: "snap_settings",
                      MAIL_QUEUE_FILE: "snap_mail"}
    _tag = _SNAP_TAGS.get(path)
    if _tag:
        _snapshot_before_save(path, _tag)
    _atomic_write(path, json.dumps(obj, ensure_ascii=False, indent=2))

def _quarantine(path):
    """Копіює пошкоджений файл поруч як .corrupt-<ts>, щоб його не втратити."""
    try:
        dst = f"{path}.corrupt-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(path, dst)
        print(f"  ⚠ Corrupted file saved as {os.path.basename(dst)}", flush=True)
        return dst
    except Exception:
        return ""

def _read_json_strict(path, default):
    """Як _read_json, але НЕ ховає помилку: битий файл → виняток, а не «0 записів»."""
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────
# 💵 КОМІСІЇ — єдине джерело істини (віддаються в JS через __FEE_CONFIG__)
#   fees   — комісія майданчика, яку рахує P&L
#   payout — додаткові витрати на вивід грошей, які враховує калькулятор ціни
#   ed     — комісія ELDORADO
# ─────────────────────────────────────────────────
PLATFORM_FEES = {"zeusx": 0.10, "funpay": 0.10, "eldorado": 0.10, "other": 0.0}
PAYOUT_FEES   = {"zeusx": 0.015, "funpay": 0.055}
ED_FEE        = 0.10

DEFAULT_PLATFORM_FEES = dict(PLATFORM_FEES)


def _apply_fee_profiles(st):
    """Застосовує збережені дефолтні комісії до PLATFORM_FEES."""
    fp = (st or {}).get("fee_profiles") or {}
    for k in ("funpay", "eldorado", "other"):
        try:
            v = float(fp.get(k))
            if 0.0 <= v <= 1.0:
                PLATFORM_FEES[k] = v
        except (TypeError, ValueError):
            pass


# ZeusX: комісія залежить від рангу продавця (5–10%).
# Точну ставку продавець бачить у кабінеті; це стартові пресети,
# які можна перебити полем «Комісія %».
ZEUSX_TIERS = [
    {"id": "iron",      "name": "Iron",      "fee": 0.10, "criteria": "Default"},
    {"id": "bronze",    "name": "Bronze",    "fee": 0.09, "criteria": ">$300 total successful sales"},
    {"id": "silver",    "name": "Silver",    "fee": 0.08, "criteria": ">$1,000 total successful sales"},
    {"id": "gold",      "name": "Gold",      "fee": 0.07, "criteria": ">$10,000 total successful sales"},
    {"id": "platinum",  "name": "Platinum",  "fee": 0.06, "criteria": ">$100,000 total successful sales"},
    {"id": "vibranium", "name": "Vibranium", "fee": 0.05, "criteria": "Invitation / admin approval only"},
]

# Майданчики для калькулятора «де вигідніше продавати» (комісії орієнтовні!)
MARKETPLACES = [
    {"id": "funpay",   "name": "FunPay",           "emoji": "🔵", "fee": 0.10,  "payout": 0.055, "note": "залежить від розділу; для акаунтів зазвичай 10%"},
    {"id": "ggsel",    "name": "GGsel",            "emoji": "🔴", "fee": 0.05,  "payout": 0.0,   "note": ""},
    {"id": "own",      "name": "Своя вітрина",     "emoji": "🏠", "fee": 0.05,  "payout": 0.03,  "note": ""},
    {"id": "z2u",      "name": "Z2U",              "emoji": "🟣", "fee": 0.07,  "payout": 0.02,  "note": ""},
    {"id": "g2g",      "name": "G2G",              "emoji": "🟢", "fee": 0.08,  "payout": 0.02,  "note": ""},
    {"id": "zeusx",    "name": "ZeusX",            "emoji": "⚡", "fee": 0.10,  "payout": 0.005, "note": "5–10% залежно від рангу продавця"},
    {"id": "eldorado", "name": "Eldorado",         "emoji": "🟡", "fee": 0.10,  "payout": 0.0,   "note": "10% для акаунтів; окремі ігри 15–30%"},
    {"id": "pa",       "name": "PlayerAuctions",   "emoji": "🅿️", "fee": 0.13,  "payout": 0.02,  "note": ""},
    {"id": "tg",       "name": "Telegram (прямо)", "emoji": "✈️", "fee": 0.0,   "payout": 0.0,   "note": ""},
]

MAX_RECORDS = 20000
_DATE_RE = None


def _is_date(s, allow_empty=False):
    """YYYY-MM-DD. Порожній рядок — лише якщо явно дозволено."""
    global _DATE_RE
    if not s:
        return bool(allow_empty)
    if _DATE_RE is None:
        import re
        _DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    try:
        datetime.date.fromisoformat(s)
    except Exception:
        return False
    return bool(_DATE_RE.match(s))


def _fnum(value, field, minimum=0.0, maximum=1e9, default=0.0):
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        raise ValueError(f"{field}: очікується число")
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field}: очікується число")
    if num != num or num in (float("inf"), float("-inf")):
        raise ValueError(f"{field}: некоректне число")
    if num < minimum or num > maximum:
        raise ValueError(f"{field}: поза межами ({minimum}…{maximum})")
    return num


def _fee_pct_of(rec, default=None):
    """Частка комісії для запису P&L (0…1).

    Нові записи зберігають feePct. Для старих записів без feePct
    відновлюємо частку з afterFee, щоб історія не змінювалася після
    зміни дефолтних ставок. Якщо нічого не відомо — беремо default.
    """
    if not isinstance(rec, dict):
        return 0.0 if default is None else default
    raw = rec.get("feePct")
    if raw not in (None, ""):
        try:
            v = float(raw)
            if 1.0 < v <= 100.0:
                v /= 100.0
            if 0.0 <= v <= 1.0:
                return v
        except (TypeError, ValueError):
            pass
    src = str(rec.get("src") or "")
    base = PLATFORM_FEES.get(src, 0.0) if default is None else default
    after = rec.get("afterFee")
    if after in (None, ""):
        return base
    try:
        sell = float(rec.get("sell") or 0)
        buy = float(rec.get("buy") or 0)
        aft = float(after)
    except (TypeError, ValueError):
        return base
    if sell <= 0:
        return base
    v = (sell - buy - aft) / sell
    if 0.0 <= v <= 1.0:
        return v
    return base


_EMOJI_RE = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]+\s*")


def _strip_emoji(t):
    """Прибирає емодзі з назв платформ («🔵 FunPay» → «FunPay»)."""
    return _EMOJI_RE.sub("", str(t or "")).strip()


def _clean_pl(data):
    """Валідація/нормалізація P&L. Кидає ValueError з людським текстом."""
    if not isinstance(data, list):
        raise ValueError("purchases має бути списком")
    if len(data) > MAX_RECORDS:
        raise ValueError(f"забагато записів (>{MAX_RECORDS})")
    out, now_ms = [], int(time.time() * 1000)
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            raise ValueError(f"запис #{i + 1}: очікується об'єкт")
        rid = rec.get("id")
        if not isinstance(rid, (int, str)) or isinstance(rid, bool) or rid == "":
            rid = now_ms + i
        buy  = _fnum(rec.get("buy"), f"запис #{i + 1} buy")
        sell = _fnum(rec.get("sell"), f"запис #{i + 1} sell")
        expenses = _fnum(rec.get("expenses"), f"запис #{i + 1} expenses")
        src  = str(rec.get("src") or "other")[:32]
        date = str(rec.get("date") or "")[:10]
        if not _is_date(date):
            raise ValueError(f"запис #{i + 1}: дата має бути YYYY-MM-DD")
        fee_pct = _fee_pct_of({**rec, "src": src, "sell": sell, "buy": buy},
                              PLATFORM_FEES.get(src, 0.0))
        after = round(sell * (1 - fee_pct) - buy, 6)
        out.append({
            **{k: v for k, v in rec.items() if k not in
               ("id", "title", "src", "srcName", "buy", "sell", "afterFee", "feePct", "expenses", "qty", "date", "platform")},
            "id": rid,
            "title": str(rec.get("title") or "")[:500],
            "src": src,
            "srcName": _strip_emoji(str(rec.get("srcName") or src))[:64],
            "buy": round(buy, 6),
            "sell": round(sell, 6),
            "feePct": round(fee_pct, 6),
            "afterFee": after,
            "expenses": round(expenses, 6),
            "qty": int(_fnum(rec.get("qty"), "qty", 0, 1e6, 1) or 1),
            "date": date,
            "platform": str(rec.get("platform") or src)[:32],
        })
    return out


def _clean_ed(data):
    if not isinstance(data, list):
        raise ValueError("sales має бути списком")
    if len(data) > MAX_RECORDS:
        raise ValueError(f"забагато записів (>{MAX_RECORDS})")
    out, now_ms = [], int(time.time() * 1000)
    for i, rec in enumerate(data):
        if not isinstance(rec, dict):
            raise ValueError(f"запис #{i + 1}: очікується об'єкт")
        rid = rec.get("id")
        if not isinstance(rid, (int, str)) or isinstance(rid, bool) or rid == "":
            rid = now_ms + i
        if rec.get("price") in (None, ""):
            raise ValueError(f"запис #{i + 1}: price обовʼязковий")
        price = _fnum(rec.get("price"), f"запис #{i + 1} price")
        if price <= 0:
            raise ValueError(f"запис #{i + 1}: price має бути > 0")
        buy   = _fnum(rec.get("buy"), f"запис #{i + 1} buy")
        fee   = rec.get("fee")
        fee   = round(price * ED_FEE, 6) if fee is None else _fnum(fee, "fee")
        profit = rec.get("profit")
        profit = (round(price - fee - buy, 6) if profit is None
                  else _fnum(profit, "profit", -1e9))
        date = str(rec.get("date") or "")[:10]
        if not _is_date(date):
            raise ValueError(f"запис #{i + 1}: дата обовʼязкова, формат YYYY-MM-DD")
        out.append({
            **{k: v for k, v in rec.items() if k not in
               ("id", "date", "title", "price", "buy", "fee", "profit", "orderId", "category")},
            "id": rid,
            "date": date,
            "title": str(rec.get("title") or "")[:500],
            "price": round(price, 6),
            "buy": round(buy, 6),
            "fee": round(fee, 6),
            "profit": profit,
            "orderId": str(rec.get("orderId") or "")[:120],
            "category": str(rec.get("category") or "")[:80],
        })
    # нові записи — зверху (імпорт історичних даних ішов за спаданням дат)
    out.sort(key=lambda r: (str(r.get("date") or ""),
                            int(str(r.get("id") or 0)[:18] or 0)), reverse=True)
    return out


# ─────────────────────────────────────────────────
# 💼 ПЛАТФОРМИ: ZeusX / FunPay / Eldorado
#   Дані з кабінетів за збереженими cookie. Нові продажі → у чергу 📥.
# ─────────────────────────────────────────────────
# ─────────────────────────────────────────────────



# ─────────────────────────────────────────────────
# 🇨🇳 TAOBAO: ціни постачальників з Китаю (збирає колектор на ПК)
# ─────────────────────────────────────────────────
# ─────────────────────────────────────────────────

def _taobao_en(title):
    """Переклад на англійську (taobao_core)."""
    return taobao_core.translate(title) if taobao_core else str(title or "")[:160]




def _taobao_region(title):
    """Регіон сервера (taobao_core)."""
    return taobao_core.region(title) if taobao_core else ""


def _taobao_segment(title):
    """Тип лота (taobao_core)."""
    return taobao_core.segment(title) if taobao_core else "other"


_TAOBAO_GAME_PATTERNS = (taobao_core.GAME_PATTERNS if taobao_core else {})


def _load_secrets():
    """Пароль дашборда і ключ ScraperAPI — поза кодом: .gt_secrets.json."""
    global AUTH_USER, AUTH_PASS, SCRAPER_API_KEY
    if not os.path.exists(SECRETS_FILE):
        return
    try:
        s = json.loads(open(SECRETS_FILE, encoding="utf-8").read())
    except Exception as e:
        print(f"⚠ .gt_secrets.json: {e}")
        return
    AUTH_USER       = s.get("auth_user")       or AUTH_USER
    AUTH_PASS       = s.get("auth_pass")       or AUTH_PASS
    SCRAPER_API_KEY = s.get("scraper_api_key") or SCRAPER_API_KEY
    print("🔐 Secrets loaded from .gt_secrets.json")

_load_secrets()

def _save_secrets(updates):
    """Оновлює .gt_secrets.json, не втрачаючи інші ключі."""
    s = {}
    if os.path.exists(SECRETS_FILE):
        try:
            s = json.loads(open(SECRETS_FILE, encoding="utf-8").read())
        except Exception:
            s = {}
    s.update(updates)
    _atomic_dump(SECRETS_FILE, s)
    try:
        os.chmod(SECRETS_FILE, 0o600)      # на Linux — тільки власнику
    except OSError:
        pass


# ─────────────────────────────────────────────────
# ПОСТАЧАЛЬНИКИ (Shopify — де закуповувати)
# ─────────────────────────────────────────────────
def _load_extra_suppliers():
    """Додає постачальників, яких користувач вписав у налаштуваннях."""
    try:
        _st = _read_json(SETTINGS_FILE, {}) or {}
        for x in (_st.get("suppliers_extra") or []):
            _k = str(x.get("key") or "")[:16]
            if not _k or not x.get("base"):
                continue
            SUPPLIERS.setdefault(_k, {"name": str(x.get("name") or _k)[:40],
                                      "base": str(x.get("base"))[:200],
                                      "color": x.get("color") or "#7c8f6a",
                                      "emoji": x.get("emoji") or "\u25cf"})
    except Exception as e:
        print(f"  ⚠ suppliers_extra: {e}", flush=True)


SUPPLIERS = {
  # Додайте свої Shopify-магазини тут (або через ⚙ → Постачальники).
  # Приклад:
  # "demo": {"name": "Demo Shop", "base": "https://example-shop.com",
  #          "color": "#7c8f6a", "emoji": "\u25cf"},
  }
_supplier_cache = []
_supplier_seen  = {}   # {product_id: {"seen_at","updated_at","price","available","history"}}
_price_drops    = []   # зниження цін за поточне оновлення (для алерту в TG)
_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gt_cache.json")
SUP_CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gt_suppliers.json")



# ── пароль входу: увімкнений лише якщо користувач сам попросив ────
def _auth_from_settings():
    """Вирішує режим входу: env GT_AUTH > налаштування auth_enabled > без пароля."""
    global AUTH_MODE
    env = (os.environ.get("GT_AUTH") or "").strip().lower()
    if env in ("off", "basic", "cloudflare"):
        AUTH_MODE = env
        return
    try:
        _st = _read_json(SETTINGS_FILE, {}) or {}
    except Exception:
        _st = {}
    AUTH_MODE = "basic" if _st.get("auth_enabled") else "off"


_auth_from_settings()


def _load_file_cache():
    global _supplier_seen
    try:
        if os.path.exists(_CACHE_FILE):
            d = json.loads(open(_CACHE_FILE, encoding="utf-8").read())
            _supplier_seen = d.get("sup_seen", {}) or {}
            if _supplier_seen:
                print(f"  📦 Supplier cache: {len(_supplier_seen)} products", flush=True)
    except Exception as e:
        print(f"  ⚠ Cache read failed: {e}")

def _save_file_cache():
    try:
        _atomic_dump(_CACHE_FILE, {"sup_seen": _supplier_seen})
    except Exception as e:
        print(f"  ⚠ Cache save failed: {e}")

def _load_sup_cache():
    """Кеш products постачальників на диску — щоб перезапуск не обнуляв вкладку."""
    global _supplier_cache
    try:
        if os.path.exists(SUP_CACHE_FILE):
            d = json.loads(open(SUP_CACHE_FILE, encoding="utf-8").read())
            if isinstance(d, list) and d:
                _supplier_cache = d
                print(f"  📦 Product cache: {len(_supplier_cache)}", flush=True)
    except Exception as e:
        print(f"  ⚠ Product cache read failed: {e}")

def _save_sup_cache():
    try:
        _atomic_dump(SUP_CACHE_FILE, _supplier_cache)
    except Exception as e:
        print(f"  ⚠ Product cache save failed: {e}")


def _read_json(path, default):
    """Безпечне читання JSON: будь-яка помилка → default."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ─────────────────────────────────────────────────
# НАЛАШТУВАННЯ: курс, Telegram, хмарний бекап
# ─────────────────────────────────────────────────
_DEFAULT_TG = {"token": "", "chat_id": "", "enabled": False,
               "notify_mail": True, "notify_price": True, "notify_new": True}

def _tg_cfg():
    cfg = dict(_DEFAULT_TG)
    cfg.update(_read_json(TG_FILE, {}) or {})
    # Сумісність зі старими .gt_secrets.json (tg_token / tg_chat_id)
    if not cfg.get("token") or not cfg.get("chat_id"):
        s = _read_json(SECRETS_FILE, {}) or {}
        if not cfg.get("token"):
            cfg["token"] = s.get("tg_token") or ""
        if not cfg.get("chat_id"):
            cfg["chat_id"] = str(s.get("tg_chat_id") or "")
    return cfg

_TG_DEFAULTS = {
    "order": True, "message": True, "watchdog": True,
    "agent": False, "digest": False, "new": False,
    "price": False, "restock": False, "deal": False,
}


def _tg_flag(kind):
    """Чи надсилати цей тип сповіщень (перемикачі в ⚙️ Налаштування)."""
    try:
        st = _read_json(SETTINGS_FILE, {}) or {}
        key = "notify_" + kind
        return bool(st.get(key, _TG_DEFAULTS.get(kind, False)))
    except Exception:
        return bool(_TG_DEFAULTS.get(kind, False))


def _tg_send(text, force=False):
    """Надсилає повідомлення в Telegram. Ніколи не кидає виняток.

    force=True — для кнопки «Тест»: ігнорує enabled, але токен/chat_id все одно
    мусять бути задані.
    """
    cfg = _tg_cfg()
    token = (cfg.get("token") or "").strip()
    chat  = str(cfg.get("chat_id") or "").strip()
    if not cfg.get("enabled") and not force:
        return {"ok": False, "error": "Сповіщення вимкнені"}
    if not token or not chat:
        return {"ok": False, "error": "Не вказано токен або chat_id"}
    try:
        payload = urllib.parse.urlencode({
            "chat_id": chat,
            "text": text[:3900],
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=12) as r:
            res = json.loads(r.read().decode("utf-8", "replace"))
        return {"ok": bool(res.get("ok")),
                "error": None if res.get("ok") else res.get("description", "Telegram error")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ─────────────────────────────────────────────────
# 📧 GMAIL → TELEGRAM
#   Скрапінг пошти: нові замовлення / повідомлення FunPay, ZeusX, Eldorado.
#   Налаштування: ⚙️ → Gmail (адреса + App Password), або .gt_secrets.json:
#     {"gmail_user": "...@gmail.com", "gmail_pass": "xxxx xxxx xxxx xxxx"}
# ─────────────────────────────────────────────────
GMAIL_CHECK_INTERVAL = 120          # кожні 2 хвилини
_MAIL_SENDERS = ("funpay", "zeusx", "eldorado.gg", "eldorado", "talkjs.com")
_MAIL_FOLDER_HINTS = ("inbox", "updates", "promotions", "all mail",
                      "онов", "уведом", "промо", "важлив")

_gmail_lock = threading.Lock()
_gmail_state = {"seen": [], "last_check": 0, "last_ok": 0, "last_error": "",
                "last_found": 0, "last_sent": 0, "runs": 0}
_gmail_last_log = {"error": "", "at": 0.0}


def _gmail_cfg():
    """(user, app_password) з .gt_secrets.json. Пробіли в App Password прибираємо."""
    s = _read_json(SECRETS_FILE, {}) or {}
    user = str(s.get("gmail_user") or "").strip()
    pwd = "".join(str(s.get("gmail_pass") or "").split())
    return user, pwd


def _gmail_configured():
    user, pwd = _gmail_cfg()
    return bool(user and pwd)


def _load_gmail_state():
    d = _read_json(GMAIL_STATE_FILE, {}) or {}
    if isinstance(d, dict):
        for k in list(_gmail_state):
            if k in d and d[k] is not None:
                _gmail_state[k] = d[k]
    if not isinstance(_gmail_state.get("seen"), list):
        _gmail_state["seen"] = []


def _save_gmail_state():
    _gmail_state["seen"] = [str(x) for x in (_gmail_state.get("seen") or [])][-3000:]
    try:
        _atomic_dump(GMAIL_STATE_FILE, _gmail_state)
    except Exception as e:
        print(f"  ⚠ Gmail state save failed: {e}", flush=True)


def _mail_hdr(value):
    """Декодує заголовок листа (RFC 2047) у звичайний текст."""
    try:
        import email.header
        out = []
        for part, enc in email.header.decode_header(value or ""):
            out.append(part.decode(enc or "utf-8", "replace") if isinstance(part, bytes)
                       else str(part))
        return " ".join(" ".join(out).split())
    except Exception:
        return " ".join(str(value or "").split())


def _html_to_text(s):
    import re as _re, html as _html
    s = _re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s or "")
    s = _re.sub(r"(?is)<br\s*/?>", "\n", s)
    s = _re.sub(r"(?is)</(p|div|tr|li|h[1-6]|table)>", "\n", s)
    s = _re.sub(r"(?is)<[^>]+>", " ", s)
    s = _html.unescape(s)
    return "\n".join(line.strip() for line in s.splitlines() if line.strip())


def _mail_body(msg, limit=1400):
    """Текст листа: спершу text/plain, інакше HTML без тегів. Обрізає до limit."""
    chunks, html_chunks = [], []
    try:
        parts = msg.walk() if msg.is_multipart() else [msg]
        for part in parts:
            if part.get_content_disposition() == "attachment":
                continue
            ctype = part.get_content_type()
            if ctype not in ("text/plain", "text/html"):
                continue
            try:
                raw = part.get_payload(decode=True) or b""
            except Exception:
                continue
            text = raw.decode(part.get_content_charset() or "utf-8", "replace")
            (chunks if ctype == "text/plain" else html_chunks).append(text)
    except Exception:
        pass
    text = "\n".join(chunks).strip()
    html_text = _html_to_text("\n".join(html_chunks)) if html_chunks else ""
    # Eldorado: у plain лише трекінгове посилання — сума/гра є тільки в HTML.
    # Тягнемо з HTML тільки змістовні рядки, а не весь документ.
    frag = ""
    if html_text:
        keep = []
        for line in html_text.splitlines():
            low = line.lower()
            if any(k in low for k in ("order price", "order total", "total:", "amount",
                                      "game:", "category:", "order id", "order#")):
                line = " ".join(line.split())
                if line and line not in keep:
                    keep.append(line[:420])   # «Order ID: <uuid> … Game: … Order price: …»
        frag = "\n".join(keep)[:700]
    if not text and html_text:
        text = html_text
    elif frag:
        text = text + "\n" + frag
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text[:limit]


def _classify_mail(sender, subject, body):
    """('order'|'message'|'other', платформа).

    Тема листа — сильніший сигнал, ніж текст: у листах про повідомлення майже
    завжди згадується «order», і раніше вони приходили як «НОВЕ ЗАМОВЛЕННЯ».
    """
    s = (sender or "").lower()
    subj = (subject or "").lower()
    text = f"{subject or ''}\n{body or ''}".lower()
    if "funpay" in s:
        platform = "FunPay"
    elif "zeusx" in s:
        platform = "ZeusX"
    elif "eldorado" in s or "talkjs" in s:
        platform = "Eldorado"
    else:
        platform = "?"

    order_words = ("new order", "new sale", "you have a new order", "order #",
                   "order id", "you sold", "sold your", "has been purchased",
                   "item has been purchased", "замовлення", "продано",
                   "оплачено", "purchased", "paid")
    msg_words = ("new message", "message from", "you received a message",
                 "sent you a message", "new chat", "повідомлення", "написав",
                 "написала", "новое сообщение", "chat")

    # статусні листи ("order marked as Received", "funds released", "payout")
    # — це НЕ нова покупка і НЕ повідомлення: не сповіщаємо взагалі
    status_words = ("marked as", "is now", "has been marked", "status changed",
                    "payment received", "funds released", "funds have been",
                    "payout", "payouts", "completed", "shipped", "delivered",
                    "cancelled", "canceled", "refund", "dispute", "on hold",
                    "отримано", "позначено", "завершено", "виконано", "виплат",
                    "зараховано", "зараховані", "кошти", "withdrawal", "withdrew")
    new_order_markers = ("new order", "new sale", "you have a new order", "you sold",
                         "order placed", "has been purchased", "item has been purchased",
                         "нове замовлення", "продано", "куплено")
    subj_status = any(w in subj for w in status_words)
    subj_new = any(w in subj for w in new_order_markers)
    if subj_status and not subj_new:
        return "status", platform
    if not subj_new and any(w in text[:600] for w in ("marked as received",
                                                      "funds released", "payout processed")):
        return "status", platform

    subj_msg = any(w in subj for w in msg_words)
    subj_order = any(w in subj for w in order_words)
    if subj_msg and not subj_order:
        return "message", platform
    if any(w in text for w in order_words):
        return "order", platform
    if subj_msg or any(w in text for w in msg_words):
        return "message", platform
    return "other", platform


def _parse_order_fields(body):
    """Order ID / сума / гра з тексту листа (структуровано)."""
    import re as _re
    out = {"orderId": "", "price": None, "game": ""}
    m = _re.search(r"(?:\border\s*(?:id|#)|номер\s*замовлення|замовлення)\s*[:#№]?\s*"
                   r"([A-Za-z0-9][A-Za-z0-9\-]{5,40})", body or "", _re.I)
    if m:
        out["orderId"] = m.group(1)
    body_s = body or ""
    pats = [
        r"(?:order\s*price|order\s*total|total|amount|sum|сума)\s*[:\-]?\s*"
        r"(?:\$|USD|EUR|€)?\s*(\d+(?:[.,]\d{1,2})?)",
        r"(\d+(?:[.,]\d{1,2})?)\s*(?:USD|EUR|€|\$)",
        r"(?:\$|USD\s*)(\d+(?:[.,]\d{1,2})?)",
    ]
    for pat in pats:
        m = _re.search(pat, body_s, _re.I)
        if m:
            try:
                val = float(m.group(1).replace(",", "."))
            except ValueError:
                continue
            if 0 < val < 1e6:
                out["price"] = val
                break
    # \b обов'язковий: без нього «pro_gamer» давав «🎮 r_2026»
    m = _re.search(r"\b(?:game|гра|item|товар|product)\b\s*[:#]?\s*([^\n]{3,60})",
                   body or "", _re.I)
    if m:
        out["game"] = " ".join(m.group(1).split())
    return out


def _mail_details(body):
    """Рядки-деталі для Telegram-сповіщення."""
    f = _parse_order_fields(body)
    out = []
    if f["orderId"]:
        out.append("🆔 " + f["orderId"])
    if f["price"] is not None:
        out.append("💵 $%.2f" % f["price"])
    if f["game"]:
        out.append("🎮 " + f["game"])
    return out


def _gmail_folders(mail):
    """INBOX + локальні Gmail-папки з оновленнями/промо (назви бувають локалізовані)."""
    cand = ["INBOX"]
    try:
        typ, data = mail.list()
        if typ == "OK":
            for raw in data or []:
                line = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
                name = line.split('"')[-2] if line.count('"') >= 2 else ""
                low = name.lower()
                if name and name.upper() != "INBOX" and any(h in low for h in _MAIL_FOLDER_HINTS):
                    if name not in cand:
                        cand.append(name)
    except Exception:
        pass
    return cand[:6]


def _gmail_login_test(user=None, pwd=None):
    """Перевіряє логін/App Password, нічого не надсилає і не змінює стан."""
    if user is None or pwd is None:
        user, pwd = _gmail_cfg()
    if not user or not pwd:
        return {"ok": False, "error": "Не вказано Gmail або App Password"}
    try:
        import imaplib
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=25)
        try:
            mail.login(user, pwd)
            typ, data = mail.select("INBOX", True)
            total = int((data[0] or b"0")) if typ == "OK" and data and data[0] else 0
        finally:
            try:
                mail.logout()
            except Exception:
                pass
        return {"ok": True, "msg": f"✅ Gmail підключено ({user}), листів у INBOX: {total}"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}


def _mail_key(msg, subject, sender, body):
    """Стабільний ключ листа: Message-ID, інакше хеш вмісту.

    Ключ folder:uid не годиться — Gmail показує той самий лист у кількох
    папках (INBOX + Updates + All Mail), і без цього були дублі в Telegram.
    """
    import hashlib
    mid = str(msg.get("Message-ID") or "").strip()
    if mid:
        return "mid:" + mid[:200]
    raw = "|".join([subject or "", sender or "", str(msg.get("Date") or ""), (body or "")[:200]])
    return "sha:" + hashlib.sha1(raw.encode("utf-8", "replace")).hexdigest()


_URL_RE = re.compile(r"https?://\S+")


def _strip_urls(text):
    """Прибирає посилання (трекінгові редиректи) з тексту листа."""
    t = _URL_RE.sub("", str(text or ""))
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def _tg_short(text, limit=160):
    """Перший змістовний рядок: без картинок, таблиць, посилань і сміття."""
    raw = str(text or "")
    raw = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", raw)          # ![alt](url)
    raw = re.sub(r"\[[^\]]{0,40}\]\([^)]*\)", " ", raw)       # [text](url) — геть
    raw = re.sub(r"https?://\S+", " ", raw)
    best = ""
    for line in raw.splitlines():
        t = re.sub(r"[|_*`>#~\[\]()]+", " ", line)
        t = re.sub(r"\s+", " ", t).strip(" -·•:;,.")
        if len(re.findall(r"[A-Za-zА-Яа-яІіЇїЄєґҐ0-9]", t)) < 6:
            continue
        if t.lower().startswith(("eldorado", "zeusx", "funpay", "reply now")):
            continue
        if len(t) > len(best):
            best = t
        if len(best) >= limit:
            break
    return (best or "")[:limit]


def _mail_who(subject):
    """Імʼя співрозмовника з теми листа («X wants to chat…»)."""
    m = re.search(r"^(.{2,40}?)\s+(?:wants to chat|sent you|is asking|написав|пише)",
                  subject or "", re.I)
    return m.group(1).strip() if m else ""


def _mail_notification(kind, platform, subject, body, test=False):
    """Короткий Telegram-текст листа: хто, про що, без сміття й посилань."""
    prefix = "🧪 <b>СИМУЛЯЦІЯ</b>\n" if test else ""
    raw_body = body
    clean_subj = _strip_urls(subject)[:140]
    clean_body = _strip_urls(body)

    if kind == "message":
        who = _mail_who(clean_subj)
        lines = ["%s💬 <b>%s</b> · %s" % (prefix, _html_mod.escape(who or "Повідомлення"), platform)]
        snippet = _tg_short(raw_body, 160)
        if snippet:
            lines.append("> " + _html_mod.escape(snippet))
        return "\n".join(lines)

    details = _mail_details(body)
    lines = ["%s💰 <b>НОВЕ ЗАМОВЛЕННЯ</b> · %s" % (prefix, platform),
             "📌 " + _html_mod.escape(clean_subj or "(без теми)")]
    lines += details
    if not details:
        short = _tg_short(clean_body, 200)
        if short:
            lines.append("<i>" + _html_mod.escape(short) + "</i>")
    return "\n".join(lines)


# ─────────────────────────────────────────────────
# 🔑 СТОРІНКА ВХОДУ (замість браузерного Basic-діалогу)
# ─────────────────────────────────────────────────
LOGIN_HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sign in · AccTrack</title>
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<style>
:root{--bg:#0b0c0e;--card:#111214;--brd:#26282c;--tx:#edeef0;--mu:#8a8f98;--a1:#edeef0}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;display:flex;align-items:center;justify-content:center;background:var(--bg);
color:var(--tx);font-family:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
-webkit-font-smoothing:antialiased;
background-image:radial-gradient(900px 420px at 50% -20%,rgba(255,255,255,.045),transparent 70%)}
.box{width:100%;max-width:352px;background:var(--card);border:1px solid var(--brd);
border-radius:14px;padding:28px 26px 24px;box-shadow:0 24px 70px rgba(0,0,0,.55)}
.brand{display:flex;align-items:center;gap:9px;margin-bottom:22px}
.brand svg{width:18px;height:18px;flex:none}
.brand b{font-size:15px;font-weight:600;letter-spacing:-.01em}
h1{font-size:17px;font-weight:600;margin:0 0 6px;letter-spacing:-.01em}
p{color:var(--mu);font-size:12.5px;line-height:1.5;margin:0 0 18px}
input{width:100%;padding:11px 13px;border-radius:9px;border:1px solid var(--brd);
background:#0d0e10;color:var(--tx);font-size:15px;margin-bottom:10px;font-family:inherit}
input:focus{outline:none;border-color:#4a4d54}
button{width:100%;padding:11px;border-radius:9px;border:1px solid #2c2f34;background:var(--a1);
color:#0b0c0e;font-weight:600;font-size:14px;cursor:pointer;font-family:inherit}
button:hover{filter:brightness(.94)}
button:disabled{opacity:.55;cursor:default}
.err{color:#ef6b6b;font-size:12.5px;min-height:16px;margin-top:10px}
.ok{color:#5fbf7f;font-size:12.5px;margin-top:10px}
.lang{display:flex;gap:10px;justify-content:center;margin-top:16px;font-size:11.5px}
.lang a{color:var(--mu);text-decoration:none;cursor:pointer}
.lang a.on{color:var(--tx)}
</style></head><body>
<form class="box" onsubmit="return go(event)">
  <div class="brand">
    <svg viewBox="0 0 24 24" fill="none"><path d="M12 3.6 21 20.4H3L12 3.6Z" fill="#edeef0"/></svg>
    <b>AccTrack</b>
  </div>
  <h1 id="t1">Sign in</h1>
  <p id="t2">Enter the password. This device stays signed in for a year.</p>
  <input id="pw" type="password" placeholder="Password" autofocus autocomplete="current-password">
  <button id="btn" type="submit">Continue</button>
  <div class="err" id="err"></div>
  <div class="lang">
    <a onclick="setL('uk')" id="l-uk">UA</a>
    <a onclick="setL('en')" id="l-en" class="on">EN</a>
    <a onclick="setL('ru')" id="l-ru">RU</a>
  </div>
</form>
<script>
var L = {
  uk:{t1:'Вхід',t2:'Введіть пароль. Цей пристрій запам’ятається на рік.',ph:'Пароль',btn:'Увійти',err:'Введіть пароль',wrong:'Невірний пароль',net:'Помилка мережі: ',ok:'Входимо…'},
  en:{t1:'Sign in',t2:'Enter the password. This device stays signed in for a year.',ph:'Password',btn:'Continue',err:'Enter the password',wrong:'Wrong password',net:'Network error: ',ok:'Signing in…'},
  ru:{t1:'Вход',t2:'Введите пароль. Это устройство запомнится на год.',ph:'Пароль',btn:'Войти',err:'Введите пароль',wrong:'Неверный пароль',net:'Ошибка сети: ',ok:'Входим…'}
};
var cur = 'en';
function setL(l){
  cur = l;
  var x = L[l];
  document.getElementById('t1').textContent = x.t1;
  document.getElementById('t2').textContent = x.t2;
  document.getElementById('pw').placeholder = x.ph;
  document.getElementById('btn').textContent = x.btn;
  ['uk','en','ru'].forEach(function(k){
    var a = document.getElementById('l-'+k);
    if(a){ a.className = (k===l ? 'on' : ''); }
  });
  try{ localStorage.setItem('gt_lang', l); }catch(e){}
}
try{ var s = localStorage.getItem('gt_lang'); if(s && L[s]) setL(s); }catch(e){}
async function go(e){
  e.preventDefault();
  var pw = document.getElementById('pw').value;
  var err = document.getElementById('err'), btn = document.getElementById('btn');
  var x = L[cur];
  if(!pw){ err.textContent = x.err; return false; }
  btn.disabled = true; err.textContent = '';
  try{
    var r = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({password: pw})});
    var d = await r.json().catch(function(){ return {}; });
    if(r.ok && d.ok){ err.className = 'ok'; err.textContent = x.ok; location.href = '/'; }
    else { err.className = 'err'; err.textContent = (r.status === 401 ? x.wrong : (d.error || (x.wrong + ' (' + r.status + ')'))); btn.disabled = false; }
  }catch(ex){ err.className = 'err'; err.textContent = x.net + ex.message; btn.disabled = false; }
  return false;
}
</script></body></html>"""


# ─────────────────────────────────────────────────
# 🤖 TELEGRAM-БОТ (команди): /stats /balance /new /taobao /help
# ─────────────────────────────────────────────────
def _tg_api(method, payload, timeout=40):
    """Виклик Telegram Bot API."""
    cfg = _tg_cfg()
    token = cfg.get("token") or ""
    if not token:
        raise RuntimeError("немає токена Telegram")
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _bot_stats():
    today = datetime.date.today().isoformat()
    mon = today[:7]
    pl = _read_json(PL_FILE, []) or []
    ed = _read_json(ED_FILE, []) or []
    def agg(rows, date_key, sell_key, profit_key=None):
        n, sell, prof = 0, 0.0, 0.0
        for r in rows:
            n += 1
            sell += float(r.get(sell_key) or 0)
            if profit_key:
                prof += float(r.get(profit_key) or 0)
            else:
                after = r.get("afterFee")
                if after not in (None, ""):
                    prof += float(after)
                else:
                    sell = float(r.get("sell") or 0)
                    prof += sell * (1 - _fee_pct_of(r)) - float(r.get("buy") or 0)
        return n, sell, prof
    def block(label, pred):
        rows_pl = [r for r in pl if pred(str(r.get("date") or ""))]
        rows_ed = [r for r in ed if pred(str(r.get("date") or ""))]
        n1, s1, p1 = agg(rows_pl, "date", "sell")
        n2, s2, p2 = agg(rows_ed, "date", "price", "profit")
        return ("<b>%s</b>: %d продажів · виторг <b>$%.2f</b> · прибуток <b>$%.2f</b>"
                % (label, n1 + n2, s1 + s2, p1 + p2))
    lines = ["📊 <b>Статистика</b>",
             block("Сьогодні", lambda d: d == today),
             block("Цей місяць", lambda d: d.startswith(mon))]
    try:
        an = _analytics()
        top = (an.get("games") or [{}])[0]
        lines.append("Топ-гра: <b>%s</b> — $%.2f" % (_html_mod.escape(str(top.get("game", "—"))),
                                                     float(top.get("profit") or 0)))
        lines.append("Мертвих лотів: %s" % (an.get("dead_total") or 0))
    except Exception:
        pass
    return "\n".join(lines)


def _bot_balance():
    try:
        d = platforms_data()
    except Exception as e:
        return "⚠ не вдалось прочитати платформи: %s" % str(e)[:80]
    z = d.get("zeusx") or {}
    f = d.get("funpay") or {}
    e = d.get("eldorado") or {}
    lines = ["💼 <b>Платформи</b>"]
    if z.get("ok"):
        lines.append("⚡ ZeusX: баланс <b>$%.2f</b> · в обробці $%.2f · виведено $%.2f"
                     % (float(z.get("balance") or 0), float(z.get("on_going") or 0),
                        float(z.get("withdraw") or 0)))
        lines.append("   замовлень: %s (✅%s · ⏳%s · ↩%s)" % (
            z.get("orders_all"), z.get("orders_good"), z.get("orders_pending"),
            z.get("orders_refunded")))
    else:
        lines.append("⚡ ZeusX: %s" % (z.get("error") or "немає даних"))
    if f.get("ok"):
        lines.append("🔵 FunPay: замовлень у списку %s" % f.get("orders_count"))
    else:
        lines.append("🔵 FunPay: %s" % (f.get("error") or "немає даних"))
    if e.get("ok"):
        lines.append("🟡 Eldorado: %s продажів · прибуток <b>$%.2f</b>"
                     % (e.get("count"), float(e.get("profit") or 0)))
    return "\n".join(lines)


def _bot_new():
    _mailq_load()
    items = list(_mail_queue)[-5:]
    if not items:
        return "📥 Черга порожня — нових замовлень немає"
    lines = ["📥 <b>Останні в черзі</b> (%d)" % len(items)]
    for x in reversed(items):
        price = x.get("price")
        lines.append("• %s · %s%s — %s" % (
            _html_mod.escape(str(x.get("platform") or "?")),
            ("$%.2f · " % float(price)) if price else "",
            _html_mod.escape((x.get("subject") or "")[:50]),
            _html_mod.escape(str(x.get("status") or "new"))))
    return "\n".join(lines)


def _bot_taobao():
    try:
        idx = taobao_sup_index() if "taobao_sup_index" in globals() else _taobao_sup_index()
    except Exception:
        idx = {}
    deals = []
    for x in (_taobao.get("items") or []):
        sup = idx.get(x.get("game") or "")
        if not sup or not x.get("price_usd"):
            continue
        landed = float(x["price_usd"]) * (1 + LANDED_PCT)
        if landed > 0:
            deals.append((sup["min"] / landed, landed, x))
    if not deals:
        return "🏮 Taobao: база порожня або немає порівняння"
    deals.sort(key=lambda t: -t[0])
    lines = ["🏮 <b>Вигідні лоти Taobao</b> · ≥%.0fx" % float((_read_json(SETTINGS_FILE, {}) or {}).get("deal_x") or 5)]
    for ratio, landed, x in deals[:5]:
        title = _html_mod.escape((x.get("title_en") or x.get("title_cn") or "")[:45])
        url = _html_mod.escape(str(x.get("href") or ""), quote=True)
        link = '<a href="%s">%s</a>' % (url, title) if url else title
        lines.append("• %s — <b>×%.1f</b> · $%.2f" % (link, ratio, landed))
    if len(deals) > 5:
        lines.append("…і ще %d" % (len(deals) - 5))
    return "\n".join(lines)


_TG_KEYBOARD = {
    "keyboard": [[{"text": "📊 Статистика"}, {"text": "💼 Баланс"}],
                 [{"text": "📥 Замовлення"}, {"text": "🏮 Taobao"}]],
    "resize_keyboard": True,
    "is_persistent": True,
}

_LABEL_CMDS = (("статистика", "stats"), ("баланс", "balance"),
               ("замовлення", "new"), ("taobao", "taobao"), ("склад", "stock"))


def _tg_bot_cmd(text):
    raw = (text or "").strip()
    low = raw.lower()
    # натиснута плашка меню → відповідна команда
    for label, cmd_name in _LABEL_CMDS:
        if label in low and not raw.startswith("/"):
            return _tg_bot_cmd("/" + cmd_name)
    cmd = raw.split()[0].lower().lstrip("/").split("@")[0] if raw else ""
    if cmd in ("start", "help", ""):
        return ("🤖 <b>Game Tracker</b>\n"
                "/stats — продажі сьогодні й за місяць\n"
                "/balance — баланс ZeusX / FunPay / Eldorado\n"
                "/new — останні замовлення з черги\n"
                "/taobao — топ вигідних лотів\n"
                "/stock — склад (що є в наявності)")
    if cmd == "stats":
        return _bot_stats()
    if cmd == "balance":
        return _bot_balance()
    if cmd == "new":
        return _bot_new()
    if cmd == "taobao":
        return _bot_taobao()
    if cmd == "stock":
        d = inventory_data()
        lines = ["📦 <b>Склад</b>",
                 "на складі: <b>%s</b> · заморожено <b>$%.2f</b>"
                 % (d.get("in_stock"), float(d.get("frozen") or 0)),
                 "продано: %s · витрачено всього $%.2f"
                 % (d.get("sold"), float(d.get("cost_total") or 0))]
        for x in [i for i in d.get("items") or [] if i.get("status") == "in_stock"][-5:]:
            lines.append("• %s · $%.2f · %s"
                         % (_html_mod.escape(str(x.get("game") or "—")),
                            float(x.get("cost") or 0),
                            _html_mod.escape(str(x.get("account_hint") or x.get("title") or ""))))
        return "\n".join(lines)
    return "Невідома команда. /help — список"


def _tg_bot_handle(update, allowed_chat):
    """Одна update → текст відповіді або None (чужий чат/не команда)."""
    msg = update.get("message") or {}
    chat = str((msg.get("chat") or {}).get("id") or "")
    text = (msg.get("text") or "").strip()
    low = text.lower()
    is_cmd = text.startswith("/") or any(lbl in low for lbl, _ in _LABEL_CMDS)
    if not is_cmd:
        return None
    if allowed_chat and chat != str(allowed_chat):
        return None
    return _tg_bot_cmd(text)


_wd_state = {"fails": 0, "down": False}


def _funpay_orders_loop():
    """Кожні 10 хв: нові замовлення FunPay → у чергу 📥 (якщо є cookie)."""
    while True:
        try:
            ck = str((_read_json(SECRETS_FILE, {}) or {}).get("funpay_cookie") or "")
            if ck:
                n = _platforms_mod._platform_funpay_orders(ck)
                if n:
                    print(f"  🛒 FunPay: +{n} orders queued", flush=True)
        except Exception as e:
            msg = str(e)[:80]
            if "cookie" in msg.lower() or "кабінет" in msg:
                print(f"  ⚠ FunPay cookie expired: {msg}", flush=True)
            else:
                print(f"  ⚠ FunPay orders: {msg}", flush=True)
        time.sleep(600)


def _fx_usd_cny_loop():
    """Курс USD/CNY раз на 6 год (frankfurter.app, без ключа)."""
    while True:
        try:
            st = _read_json(SETTINGS_FILE, {}) or {}
            if time.time() - float(st.get("usd_cny_ts") or 0) > 6 * 3600:
                with urllib.request.urlopen(
                        "https://api.frankfurter.app/latest?from=USD&to=CNY",
                        timeout=15) as r:
                    d = json.loads(r.read().decode("utf-8", "replace"))
                rate = float((d.get("rates") or {}).get("CNY") or 0)
                if 4 < rate < 12:
                    st["usd_cny"] = round(rate, 4)
                    st["usd_cny_ts"] = time.time()
                    with _WRITE_LOCK:
                        _atomic_dump(SETTINGS_FILE, st)
                    print(f"  💱 FX ¥/$ = {rate:.3f}", flush=True)
        except Exception as e:
            print(f"  ⚠ fx: {e}", flush=True)
        time.sleep(6 * 3600)


def _agent_watchdog_loop():
    """Пильнує Taobao-агента: офлайн > 2 год або збір завис > 30 хв → Telegram."""
    while True:
        try:
            now = time.time()
            seen = int(_taobao.get("agent_seen") or 0)
            st = _read_json(SETTINGS_FILE, {}) or {}
            alert = dict(st.get("agent_alert") or {})

            def mark(key, val):
                st2 = _read_json(SETTINGS_FILE, {}) or {}
                a = dict(st2.get("agent_alert") or {})
                a[key] = val
                st2["agent_alert"] = a
                with _WRITE_LOCK:
                    _atomic_dump(SETTINGS_FILE, st2)

            if seen and (now - seen) > 2 * 3600:
                if now - float(alert.get("offline_ts") or 0) > 6 * 3600:
                    if _tg_flag("agent"):
                        _tg_send("⚠️ <b>Taobao-агент не працює</b>\n"
                             "Останній звʼязок: %d хв тому.\n"
                             "Запустіть taobao_agent.bat (він є в автозапуску Windows)."
                             % int((now - seen) // 60))
                    mark("offline_ts", now)
                    print("  ⚠ agent watchdog: agent offline, alert", flush=True)
            elif seen and alert.get("offline_ts"):
                if _tg_flag("agent"):
                    _tg_send("✅ <b>Taobao-агент знову онлайн</b>")
                mark("offline_ts", 0)
                print("  ✅ agent watchdog: agent is back", flush=True)

            pg = _taobao.get("progress") or {}
            if pg.get("total") and not pg.get("finished"):
                if now - int(pg.get("ts") or 0) > 1800:
                    if now - float(alert.get("stall_ts") or 0) > 3600:
                        if _tg_flag("agent"):
                            _tg_send("⏳ <b>Збір Taobao завис</b>\n"
                                 "Прогрес: %s/%s · %s. Пройдіть капчу у вікні браузера або перезапустіть агента."
                                 % (pg.get("done"), pg.get("total"), pg.get("current") or ""))
                        mark("stall_ts", now)
                        print("  ⏳ agent watchdog: collection stuck", flush=True)
        except Exception as e:
            print(f"  ⚠ agent watchdog: {e}", flush=True)
        time.sleep(600)


def _watchdog_check(url=None):
    """Чи відповідає сайт через Caddy (локально, без перевірки сертифіката)."""
    import ssl
    url = (url or os.environ.get("GT_WATCHDOG_URL")
           or os.environ.get("GT_HEALTH_URL", "http://127.0.0.1:8766/api/health"))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, timeout=8, context=ctx) as r:
            return r.status == 200
    except Exception:
        return False


def _watchdog_loop():
    """Пильнує доступність: 2 збої поспіль → алерт у Telegram, відновлення → ✅."""
    while True:
        try:
            if _watchdog_check():
                if _wd_state["down"]:
                    _wd_state["down"] = False
                    _wd_state["fails"] = 0
                    if _tg_flag("watchdog"):
                        _tg_send("✅ <b>Трекер знову працює</b>")
                    print("  ✅ watchdog: site is back", flush=True)
            else:
                _wd_state["fails"] = int(_wd_state.get("fails") or 0) + 1
                if _wd_state["fails"] >= 2 and not _wd_state["down"]:
                    _wd_state["down"] = True
                    if not _tg_flag("watchdog"):
                        continue
                    _tg_send("⚠️ <b>Трекер недоступний</b>\n"
                             "health не відповідає через Caddy. Перевір gametracker/caddy.")
                    print("  ⚠ watchdog: site unreachable", flush=True)
        except Exception as e:
            print(f"  ⚠ watchdog: {e}", flush=True)
        time.sleep(180)


def _tg_bot_loop():
    """Long-poll getUpdates — відповідає лише власнику чату."""
    cfg = _tg_cfg()
    if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")):
        return
    allowed = str(cfg.get("chat_id"))
    offset = 0
    try:
        _tg_api("setMyCommands", {"commands": [
            {"command": "stats", "description": "Продажі сьогодні й за місяць"},
            {"command": "balance", "description": "Баланс ZeusX / FunPay / Eldorado"},
            {"command": "new", "description": "Останні замовлення"},
            {"command": "taobao", "description": "Топ вигідних лотів"},
            {"command": "stock", "description": "Склад: що є в наявності"},
            {"command": "help", "description": "Довідка"},
        ]})
    except Exception:
        pass
    print("  🤖 Telegram bot: listening for commands", flush=True)
    while True:
        try:
            resp = _tg_api("getUpdates", {"offset": offset, "timeout": 25,
                                          "allowed_updates": ["message"]}, timeout=40)
            for upd in (resp.get("result") or []):
                offset = max(offset, int(upd.get("update_id") or 0) + 1)
                reply = _tg_bot_handle(upd, allowed)
                if reply:
                    try:
                        _txt = ((upd.get("message") or {}).get("text") or "")[:40]
                        print(f"  🤖 bot: «{_txt}» → replied", flush=True)
                    except Exception:
                        pass
                    try:
                        _tg_api("sendMessage", {"chat_id": allowed, "text": reply,
                                                "parse_mode": "HTML",
                                                "disable_web_page_preview": True,
                                                "reply_markup": _TG_KEYBOARD})
                    except Exception as e:
                        print(f"  ⚠ bot send: {e}", flush=True)
        except Exception as e:
            print(f"  ⚠ bot poll: {str(e)[:100]}", flush=True)
            time.sleep(10)
        time.sleep(2)


# ─────────────────────────────────────────────────
# 📦 СКЛАД: куплені акаунти → продаж (реальна маржа)
# ─────────────────────────────────────────────────
_inventory = []
_inv_lock = threading.Lock()
INV_STATUSES = ("in_stock", "sold", "written_off")


def _inv_load():
    global _inventory
    d = _read_json(INVENTORY_FILE, [])
    _inventory = d if isinstance(d, list) else []


def _inv_save():
    try:
        with _inv_lock:
            _atomic_dump(INVENTORY_FILE, _inventory[-2000:])
    except Exception as e:
        print(f"  ⚠ Stock: {e}", flush=True)


def _inv_clean(items):
    """Валідація списку закупівель."""
    if not isinstance(items, list):
        raise ValueError("items має бути списком")
    if len(items) > 5000:
        raise ValueError("забагато записів (>5000)")
    out = []
    for i, r in enumerate(items):
        if not isinstance(r, dict):
            raise ValueError(f"запис #{i + 1}: очікується об'єкт")
        rid = r.get("id") or f"inv-{int(time.time() * 1000)}-{i}"
        title = str(r.get("title") or "").strip()[:200]
        if not title:
            raise ValueError(f"запис #{i + 1}: порожня назва")
        try:
            cost = round(float(r.get("cost") or 0), 2)
        except (TypeError, ValueError):
            raise ValueError(f"запис #{i + 1}: собівартість не число")
        if cost < 0 or cost > 1e6:
            raise ValueError(f"запис #{i + 1}: собівартість поза межами")
        status = str(r.get("status") or "in_stock")
        if status not in INV_STATUSES:
            status = "in_stock"
        out.append({
            "id": str(rid)[:64], "date": str(r.get("date") or datetime.date.today().isoformat())[:10],
            "title": title, "game": str(r.get("game") or "")[:60],
            "cost": cost, "source": str(r.get("source") or "")[:60],
            "status": status, "sale_id": r.get("sale_id") or "",
            "note": str(r.get("note") or "")[:300],
            "account": str(r.get("account") or "")[:4000],
            "ts": int(r.get("ts") or time.time()),
        })
    return out


def _inv_public(x):
    """Запис без паролів: тільки підказка (перший рядок) і прапорець."""
    out = {k: v for k, v in x.items() if k != "account"}
    acc = str(x.get("account") or "")
    hint = acc.strip().splitlines()[0][:40] if acc.strip() else ""
    out["has_account"] = bool(acc.strip())
    out["account_hint"] = hint
    return out


def inventory_data():
    _inv_load()
    items = [_inv_public(x) for x in _inventory]
    stock = [x for x in items if x.get("status") == "in_stock"]
    sold = [x for x in items if x.get("status") == "sold"]
    total_cost = round(sum(float(x.get("cost") or 0) for x in items), 2)
    frozen = round(sum(float(x.get("cost") or 0) for x in stock), 2)
    # «мертвий» склад: куплено давно, досі не продано
    today = datetime.date.today()
    old_days, old_value, oldest = 0, 0.0, 0
    for x in stock:
        try:
            d0 = datetime.date.fromisoformat(str(x.get("date") or "")[:10])
        except ValueError:
            continue
        age = (today - d0).days
        oldest = max(oldest, age)
        if age >= 30:
            old_days += 1
            old_value += float(x.get("cost") or 0)
    return {"ok": True, "items": items, "count": len(items),
            "in_stock": len(stock), "sold": len(sold),
            "cost_total": total_cost, "frozen": frozen,
            "old_count": old_days, "old_value": round(old_value, 2),
            "oldest_days": oldest,
            "sources": sorted({x.get("source") for x in items if x.get("source")})}


def _inv_match(title, limit=3):
    """Схожі позиції на складі (для підказки при продажу)."""
    import difflib
    _inv_load()
    t = str(title or "").lower()
    scored = []
    for x in _inventory:
        if x.get("status") != "in_stock":
            continue
        ratio = difflib.SequenceMatcher(None, t, str(x.get("title") or "").lower()).ratio()
        if ratio >= 0.45:
            scored.append((round(ratio, 2), x))
    scored.sort(key=lambda p: -p[0])
    return [{"match": r, **x} for r, x in scored[:limit]]


_inv_load()


# ─────────────────────────────────────────────────
# 📥 ЧЕРГА ЗАМОВЛЕНЬ З ПОШТИ
#   Лист нічого не додає у P&L сам — він лягає в чергу, а ви одним кліком
#   переносите його в ELDORADO/P&L або ігноруєте.
# ─────────────────────────────────────────────────
_mail_queue = []
_mail_q_lock = threading.Lock()


def _mailq_load():
    global _mail_queue
    d = _read_json(MAIL_QUEUE_FILE, [])
    _mail_queue = d if isinstance(d, list) else []


def _mailq_save():
    try:
        with _mail_q_lock:
            _atomic_dump(MAIL_QUEUE_FILE, _mail_queue[-200:])
    except Exception as e:
        print(f"  ⚠ Mail queue: {e}", flush=True)


IMPORTED_FILE = str(_BASE_DIR / ".gt_imported.json")
_imported_ids = set()
_imported_lock = threading.Lock()


def _imported_load():
    d = _read_json(IMPORTED_FILE, {}) or {}
    ids = d.get("ids") if isinstance(d, dict) else (d if isinstance(d, list) else [])
    if isinstance(ids, list):
        _imported_ids.update(str(x) for x in ids if x)


def _imported_save():
    try:
        _atomic_dump(IMPORTED_FILE,
                     {"ids": sorted(_imported_ids)[-3000:], "ts": int(time.time())})
    except Exception:
        pass


def _imported_mark(ids):
    ids = [str(x) for x in ids if x]
    with _imported_lock:
        if not ids or all(i in _imported_ids for i in ids):
            return
        _imported_ids.update(ids)
        _imported_save()


def _imported_seed():
    """Усе, що вже в черзі, вважаємо імпортованим: видалене не повертається."""
    _mailq_load()
    _imported_load()
    _imported_mark([x.get("id") for x in (_mail_queue or []) if x.get("id")])


def _mailq_add(item):
    with _mail_q_lock:
        if not _mail_queue:
            _mailq_load()
        if any(x.get("id") == item.get("id") for x in _mail_queue):
            return False
        _mail_queue.append(item)
        del _mail_queue[:-200]
        _atomic_dump(MAIL_QUEUE_FILE, _mail_queue[-200:])
    return True


def _mailq_get(qid):
    if not _mail_queue:
        _mailq_load()
    item = next((x for x in _mail_queue if x.get("id") == qid), None)
    if item is None:
        # можливо, запис додав інший процес (CLI/колектор) — перечитаємо під локом
        with _mail_q_lock:
            _mailq_load()
        item = next((x for x in _mail_queue if x.get("id") == qid), None)
    return item


def check_gmail(dry=False):
    """Один прохід по Gmail. Повертає {ok, found, sent, error}. Ніколи не кидає."""
    user, pwd = _gmail_cfg()
    if not user or not pwd:
        return {"ok": False, "found": 0, "sent": 0,
                "error": "Gmail не налаштовано (⚙️ → Gmail)"}
    tg = _tg_cfg()
    can_notify = bool(tg.get("enabled") and tg.get("token") and tg.get("chat_id")
                      and tg.get("notify_mail", True))
    if not can_notify and not dry:
        return {"ok": False, "skipped": True, "found": 0, "sent": 0,
                "error": "Поштові сповіщення вимкнено: увімкни Telegram і галочку «📧 Пошта»"}
    if not _gmail_lock.acquire(blocking=False):
        return {"ok": False, "found": 0, "sent": 0, "error": "перевірка вже виконується"}
    found = sent = skipped = 0
    try:
        import imaplib, email as _email
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=30)
        try:
            mail.login(user, pwd)
            now = time.time()
            since_ts = int(_gmail_state.get("last_check") or 0)
            if not since_ts or since_ts > now:
                since_ts = now - 3 * 86400
            # запас 1 година, але не глибше 3 діб; last_check міг відстати після простою
            since_ts = max(min(since_ts - 3600, now), now - 3 * 86400)
            since = time.strftime("%d-%b-%Y", time.gmtime(since_ts))
            seen = set(str(x) for x in (_gmail_state.get("seen") or []))
            folders = _gmail_folders(mail)

            for folder in folders:
                try:
                    if mail.select('"' + folder.replace('"', '') + '"', True)[0] != "OK":
                        continue
                except Exception:
                    continue
                ids = set()
                for sender in _MAIL_SENDERS:
                    try:
                        typ, data = mail.search(None, "SINCE", since, "FROM", f'"{sender}"')
                        if typ == "OK" and data and data[0]:
                            ids.update(data[0].split())
                    except Exception:
                        continue
                for uid in ids:
                    uid_s = uid.decode() if isinstance(uid, bytes) else str(uid)
                    key = f"{folder}:{uid_s}"
                    if key in seen:
                        continue
                    try:
                        ftyp, fdata = mail.fetch(uid, "(RFC822)")
                        raw = fdata[0][1]
                    except Exception:
                        continue
                    msg = _email.message_from_bytes(raw)
                    subject = _mail_hdr(msg.get("Subject"))
                    sender_hdr = _mail_hdr(msg.get("From"))
                    body = _mail_body(msg)
                    mid = _mail_key(msg, subject, sender_hdr, body)
                    if mid in seen:
                        seen.add(key)      # той самий лист в іншій папці
                        skipped += 1
                        continue
                    found += 1
                    kind, platform = _classify_mail(sender_hdr, subject, body)
                    if kind in ("other", "status"):
                        seen.update({key, mid})
                        skipped += 1
                        continue

                    text = _mail_notification(kind, platform, subject, body)
                    if dry:
                        seen.update({key, mid})
                        continue
                    # у чергу — ЛИШЕ замовлення; повідомлення йдуть тільки в Telegram
                    fld = _parse_order_fields(body)
                    if kind == "order":
                        _mailq_add({"id": mid, "ts": int(time.time()), "platform": platform,
                                    "kind": kind, "subject": subject[:200],
                                    "body": _strip_urls(body)[:800],
                                    "orderId": fld["orderId"], "price": fld["price"],
                                    "game": fld["game"], "status": "new"})
                    if not _tg_flag("order" if kind == "order" else "message"):
                        seen.update({key, mid})
                        continue
                    res = _tg_send(text)
                    if res.get("ok"):
                        seen.update({key, mid})
                        sent += 1
                        print(f"  📧 Gmail → TG: [{platform}] {subject[:60]}", flush=True)
                    else:
                        # не позначаємо як оброблений — спробуємо наступного разу
                        skipped += 1
                        print(f"  ⚠ Gmail → TG not sent: {res.get('error')}", flush=True)

            _gmail_state.update({"seen": list(seen), "last_check": int(now),
                                 "last_ok": int(now), "last_error": "",
                                 "last_found": found, "last_sent": sent,
                                 "runs": int(_gmail_state.get("runs") or 0) + 1})
            return {"ok": True, "found": found, "sent": sent, "skipped": skipped,
                    "error": None, "folders": folders}
        finally:
            try:
                mail.logout()
            except Exception:
                pass
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        _gmail_state["last_error"] = err
        # друкуємо помилку не частіше ніж раз на 30 хв
        if _gmail_last_log["error"] != err or time.time() - _gmail_last_log["at"] > 1800:
            print(f"  ⚠ Gmail: {err}", flush=True)
            _gmail_last_log.update({"error": err, "at": time.time()})
        return {"ok": False, "found": found, "sent": sent, "error": err}
    finally:
        _save_gmail_state()
        _gmail_lock.release()


def _gmail_loop():
    """Фон: перевірка пошти кожні 2 хв (тільки якщо налаштована)."""
    time.sleep(15)
    while True:
        try:
            if _gmail_configured():
                check_gmail()
        except Exception as e:
            print(f"  ⚠ Gmail loop: {e}", flush=True)
        time.sleep(GMAIL_CHECK_INTERVAL)


_load_gmail_state()
_mailq_load()
_imported_seed()      # усе, що вже в черзі, не імпортуємо повторно

# 🇨🇳 TAOBAO — стан і логіка в taobao.py (залежності ін'єктуються)
# ─────────────────────────────────────────────────
import taobao as _taobao_mod

_taobao_mod.configure(read_json=_read_json, atomic_dump=_atomic_dump,
                      settings_file=SETTINGS_FILE, secrets_file=SECRETS_FILE,
                      data_file=TAOBAO_FILE, write_lock=_WRITE_LOCK,
                      supplier_cache=lambda: _supplier_cache,
                      tg_cfg=_tg_cfg, tg_send=_tg_send, html_mod=_html_mod)

_taobao = _taobao_mod._taobao
_taobao_load = _taobao_mod._taobao_load
_taobao_save = _taobao_mod._taobao_save
_taobao_upsert = _taobao_mod._taobao_upsert
_taobao_sup_index = _taobao_mod._taobao_sup_index
taobao_data = _taobao_mod.taobao_data
_TAOBAO_GAME_PATTERNS = _taobao_mod._TAOBAO_GAME_PATTERNS
USD_CNY = _taobao_mod.USD_CNY
LANDED_PCT = _taobao_mod.LANDED_PCT
TAOBAO_SKIP_GAMES = _taobao_mod.TAOBAO_SKIP_GAMES
TAOBAO_COOLDOWN = _taobao_mod.TAOBAO_COOLDOWN

# 💼 ПЛАТФОРМИ — логіка в platforms.py (залежності ін'єктуються)
# ─────────────────────────────────────────────────
import platforms as _platforms_mod

_platforms_mod.configure(ua=UA, secrets_file=SECRETS_FILE, ed_file=ED_FILE,
                         game_of=lambda t: _game_of(t),
                         read_json=_read_json, mailq_add=_mailq_add,
                         imported_ids=lambda: _imported_ids,
                         imported_mark=_imported_mark,
                         mail_queue=lambda: _mail_queue,
                         supplier_cache=lambda: _supplier_cache)

_platform_cache = _platforms_mod._platform_cache
PLATFORM_TTL = _platforms_mod.PLATFORM_TTL
_offers_cache = _platforms_mod._offers_cache
_sec_get = _platforms_mod._sec_get
_cookie_parse = _platforms_mod._cookie_parse
_zx_call = _platforms_mod._zx_call
_platform_zeusx = _platforms_mod._platform_zeusx
_platform_funpay = _platforms_mod._platform_funpay
_platform_eldorado = _platforms_mod._platform_eldorado
platforms_data = _platforms_mod.platforms_data
my_offers = _platforms_mod.my_offers
_supplier_match = _platforms_mod._supplier_match
_title_tokens = _platforms_mod._title_tokens


_taobao_load()

RATE_TTL = 6 * 3600

def _get_rate(force=False):
    """Курс USD→UAH: кеш у .gt_settings.json, оновлення з НБУ раз на 6 годин."""
    force = bool(force)
    st   = _read_json(SETTINGS_FILE, {}) or {}
    rate = float(st.get("usd_uah") or 0)
    ts   = float(st.get("rate_ts") or 0)
    if rate and not force and (time.time() - ts) < RATE_TTL:
        return rate, ts, "cache"
    try:
        _st0 = _read_json(SETTINGS_FILE, {}) or {}
        cur = str(_st0.get("currency") or "USD").upper()[:3]
        if cur == "USD":
            return 1.0, time.time(), "base"
        if cur == "UAH":
            url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode=USD&json"
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            rate = float(data[0]["rate"])
            src = "nbu"
        else:
            url = ("https://api.frankfurter.app/latest?from=USD&to=" + cur)
            with urllib.request.urlopen(url, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
            rate = float((data.get("rates") or {}).get(cur) or 0)
            src = "frankfurter"
            if not rate:
                return rate or 0.0, time.time(), "manual"
        ts = time.time()
        with _WRITE_LOCK:
            st = _read_json(SETTINGS_FILE, {}) or {}
            st["usd_uah"] = rate
            st["rate_ts"] = ts
            st["rate_source"] = src
            _atomic_dump(SETTINGS_FILE, st)
        return rate, ts, src
    except Exception:
        return rate, ts, ("manual" if rate else "none")

def _cloud_dir():
    """Папка хмарного бекапу: своя з налаштувань, інакше OneDrive\\GameTrackerBackups."""
    st = _read_json(SETTINGS_FILE, {}) or {}
    custom = (st.get("cloud_dir") or "").strip()
    if custom:
        return custom
    for env in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        base = os.environ.get(env)
        if base:
            return os.path.join(base, "GameTrackerBackups")
    return ""


def _tunnel_log_path():
    """Лог cloudflared (щоб показати актуальний URL тунелю в інтерфейсі)."""
    st = _read_json(SETTINGS_FILE, {}) or {}
    p = (st.get("tunnel_log") or "").strip()
    if p:
        return p
    for cand in ("/root/cf_quick.log", str(_BASE_DIR / "cf_quick.log")):
        if os.path.exists(cand):
            return cand
    return ""


def _tunnel_url():
    """Останній trycloudflare-URL зі логу (quick tunnel змінює адресу при рестарті)."""
    p = _tunnel_log_path()
    if not p or not os.path.exists(p):
        return ""
    try:
        import re as _re
        with open(p, encoding="utf-8", errors="replace") as f:
            txt = f.read()[-200000:]
        found = _re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", txt)
        return found[-1] if found else ""
    except Exception:
        return ""


def _archive_backup():
    """Щоденний tar.gz усіх даних (14 днів) — на випадок втрати окремих файлів."""
    try:
        adir = os.path.join(BACKUP_DIR, "archive")
        os.makedirs(adir, exist_ok=True)
        name = f"gt_data_{datetime.datetime.now().strftime('%Y-%m-%d')}.tar.gz"
        path = os.path.join(adir, name)
        files = [f for f in (PL_FILE, ED_FILE, GOAL_FILE, SETTINGS_FILE) if os.path.exists(f)]
        with tarfile.open(path, "w:gz") as tar:
            for f in files:
                tar.add(f, arcname=os.path.basename(f))
        keep = sorted(f for f in os.listdir(adir) if f.startswith("gt_data_"))
        for old in keep[:-14]:
            try:
                os.remove(os.path.join(adir, old))
            except OSError:
                pass
        return path
    except Exception as e:
        print(f"  ⚠ Backup archive: {e}", flush=True)
        return ""

def _copy_cloud(files):
    """Копіює бекапи в хмару. Повертає статус для UI."""
    dst = _cloud_dir()
    if not dst:
        return {"dir": "", "copied": [], "error": "Хмару не знайдено"}
    if not files:
        return {"dir": dst, "copied": [], "error": None}
    try:
        os.makedirs(dst, exist_ok=True)
        copied = []
        for name in files:
            src = os.path.join(BACKUP_DIR, name)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(dst, name))
                copied.append(name)
        for prefix in ("gt_pl_", "gt_eldorado_", "gt_goal_"):
            keep = sorted(f for f in os.listdir(dst) if f.startswith(prefix))
            for old in keep[:-30]:
                try: os.remove(os.path.join(dst, old))
                except OSError: pass
        return {"dir": dst, "copied": copied, "error": None}
    except Exception as e:
        return {"dir": dst, "copied": [], "error": str(e)}


def _https_opts():
    """Повертає (cert, key), якщо HTTPS увімкнено і файли існують."""
    st = _read_json(SETTINGS_FILE, {}) or {}
    if not st.get("https_enabled"):
        return None
    cert = (st.get("https_cert") or "").strip()
    key  = (st.get("https_key") or "").strip()
    if cert and key and os.path.isfile(cert) and os.path.isfile(key):
        return (cert, key)
    return None

def _https_gen():
    """Генерує self-signed сертифікат через openssl (якщо встановлено)."""
    cert_dir = os.path.join(_BASE_DIR, "certs")
    cert = os.path.join(cert_dir, "server.crt")
    key  = os.path.join(cert_dir, "server.key")
    exe = shutil.which("openssl")
    if not exe:
        return {"ok": False, "error": "openssl не знайдено. Встанови OpenSSL або вкажи cert/key manual (на хостингу HTTPS зазвичай дає проксі)."}
    try:
        os.makedirs(cert_dir, exist_ok=True)
        subprocess.run(
            [exe, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
             "-keyout", key, "-out", cert, "-days", "825",
             "-subj", "/CN=localhost"],
            check=True, capture_output=True, timeout=60)
        return {"ok": True, "cert": cert, "key": key}
    except Exception as e:
        msg = str(e)
        try:
            msg = e.stderr.decode("utf-8", "replace") if getattr(e, "stderr", None) else msg
        except Exception:
            pass
        return {"ok": False, "error": msg[:500]}


def do_backup():
    """Бекап P&L + ELDORADO + цілі у gt_backups/ і, якщо є, у хмару."""
    made = []
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        for src, prefix in ((PL_FILE, "gt_pl"), (ED_FILE, "gt_eldorado"), (GOAL_FILE, "gt_goal")):
            if not os.path.exists(src):
                continue
            name = f"{prefix}_{date_str}.json"
            shutil.copy2(src, os.path.join(BACKUP_DIR, name))
            made.append(name)
            keep = sorted(f for f in os.listdir(BACKUP_DIR) if f.startswith(prefix + "_"))
            for old in keep[:-30]:
                try: os.remove(os.path.join(BACKUP_DIR, old))
                except OSError: pass
        if made:
            print(f"  💾 Backup: {', '.join(made)}", flush=True)
    except Exception as e:
        print(f"  ⚠ Backup: {e}", flush=True)
    _archive_backup()
    cloud = _copy_cloud(made)
    if cloud.get("copied"):
        print(f"  ☁ Cloud: {len(cloud['copied'])} file(s) → {cloud['dir']}", flush=True)
    elif cloud.get("error") and cloud.get("dir"):
        print(f"  ⚠ Cloud: {cloud['error']}", flush=True)
    return {"ok": True, "files": made, "cloud": cloud}

def _backup_loop():
    last = ""
    while True:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today != last:
            try:
                do_backup()
            except Exception as e:
                print(f"  ⚠ Backup loop: {e}", flush=True)
            last = today
        time.sleep(3600)


def _refresh_suppliers(reason=""):
    """Оновлює кеш постачальників. Збій одного не стирає дані інших.

    Раніше `_supplier_cache = new_cache` затирав усе, навіть якщо 1 з 4 сайтів
    відповів помилкою — товари цього постачальника зникали з UI і з кешу.
    """
    global _supplier_cache
    if not _refresh_lock.acquire(blocking=False):
        print("  ⏳ Refresh already running — skipped", flush=True)
        return {"count": len(_supplier_cache), "failed": {}, "sale": 0, "gone": 0,
                "busy": True}
    try:
        return _refresh_suppliers_inner(reason)
    finally:
        _refresh_lock.release()


def _refresh_suppliers_inner(reason=""):
    global _supplier_cache
    if reason:
        print(f"\n  📦 Supplier refresh ({reason})...", flush=True)
    _price_drops.clear()
    _new_products.clear()
    fresh, ok_keys, failed = [], set(), {}
    for key in SUPPLIERS:
        try:
            fresh.extend(fetch_supplier(key, is_first_run=False))
            ok_keys.add(key)
        except Exception as ex:
            failed[key] = str(ex)
            print(f"  ⚠ {key}: {ex}", flush=True)
        time.sleep(4)      # не бити по всіх сайтах одночасно
    merged = _merge_supplier_cache(fresh, ok_keys)
    _sup_mark(bool(ok_keys))
    try:
        if merged:
            _save_sup_cache()
        _save_file_cache()
    except Exception as e:
        print(f"  ⚠ Supplier cache: {e}", flush=True)
    _notify_new_products()
    print(f"  💳 ScraperAPI today: {_scraper_state.get('used', 0)}"
          f"/{_scraper_state.get('limit', 30)}", flush=True)
    sale = sum(1 for p in _supplier_cache if p.get("isOnSale") and not p.get("gone"))
    gone = sum(1 for p in _supplier_cache if p.get("gone"))
    _notify_price_drops()
    tail = f" | ⚠ не оновлено: {', '.join(failed)}" if failed else ""
    print(f"  ✅ Suppliers: {len(_supplier_cache)} products | Sale: {sale}"
          f" | gone: {gone}{tail}", flush=True)
    return {"count": len(_supplier_cache), "failed": failed, "sale": sale, "gone": gone}


def _digest_due():
    st = _read_json(SETTINGS_FILE, {}) or {}
    try:
        hour = int(st.get("digest_hour") if st.get("digest_hour") is not None else 9)
    except Exception:
        hour = 9
    now = datetime.datetime.now()
    return now.hour >= hour and str(st.get("digest_last") or "") != now.date().isoformat()


def _digest_send():
    if not _tg_flag("digest"):
        return 0
    cfg = _tg_cfg()
    if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")
            and cfg.get("notify_digest", True)):
        return False
    today = datetime.date.today().isoformat()
    pl_t = [r for r in (_read_json(PL_FILE, []) or []) if str(r.get("date") or "") == today]
    ed_t = [r for r in (_read_json(ED_FILE, []) or []) if str(r.get("date") or "") == today]
    an = _analytics()
    top = (an.get("games") or [{}])[0]
    sales = len(pl_t) + len(ed_t)
    revenue = sum(float(r.get("sell") or 0) for r in pl_t) + sum(float(r.get("price") or 0) for r in ed_t)
    profit = sum(float(r.get("profit") or 0) for r in pl_t) + sum(float(r.get("profit") or 0) for r in ed_t)
    lines = ["📊 <b>Дайджест за %s</b>" % today,
             "Продажів: <b>%d</b> · виторг <b>$%.2f</b> · прибуток <b>$%.2f</b>" % (sales, revenue, profit),
             "Taobao: %d лотів · постачальники: %d products" % (len(_taobao.get("items") or []), len(_supplier_cache)),
             "Топ-гра: <b>%s</b> ($%.2f прибутку)" % (top.get("game", "—"), float(top.get("profit") or 0)),
             "Кредити ScraperAPI: %s/%s" % (_scraper_state.get("used", 0), _scraper_state.get("limit", 30))]
    try:
        _tg_send("\n".join(lines))
    except Exception as e:
        print(f"  ⚠ digest: {e}", flush=True)
        return False
    with _WRITE_LOCK:
        st = _read_json(SETTINGS_FILE, {}) or {}
        st["digest_last"] = today
        _atomic_dump(SETTINGS_FILE, st)
    print("  📊 Digest sent", flush=True)
    return True


def _probe_direct():
    """Один безкоштовний запит: чи IP уже не в 429 (тоді знімаємо блокування)."""
    blocked = _scraper_state.get("blocked") or {}
    if not any(int(v or 0) > time.time() for v in blocked.values()):
        return False
    for key, src in SUPPLIERS.items():
        try:
            req = urllib.request.Request(
                src["base"] + "/products.json?limit=1&page=1",
                headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                if r.status == 200:
                    _scraper_state["blocked"] = {}
                    _scraper_save()
                    print("  ✅ Direct access restored", flush=True)
                    return True
        except Exception:
            continue
    return False


def _bg_loop():
    """Фон: перевіряє, чи час оновити постачальників (інтервал sup_hours)."""
    while True:
        try:
            if _digest_due():
                _digest_send()
            _probe_direct()
            if _news_due():
                news_check()
            if _sup_due():
                _refresh_suppliers("scheduled")
        except Exception as e:
            print(f"  ⚠ Background: {e}", flush=True)
        time.sleep(300)


# ─────────────────────────────────────────────────
# 💳 БЮДЖЕТ ScraperAPI + стан оновлення постачальників
# ─────────────────────────────────────────────────
_scraper_state = {"day": "", "used": 0, "limit": 30, "blocked": {}}
_scraper_lock = threading.Lock()
_refresh_lock = threading.Lock()
_direct_pace_lock = threading.Lock()
_last_direct_ts = [0.0]
DIRECT_PACE = 13.0        # Shopify пускає ~4-5 запитів/хв з IP


def _pace_direct():
    """Тримає безпечний інтервал між прямими запитами (0 кредитів)."""
    with _direct_pace_lock:
        wait = _last_direct_ts[0] + DIRECT_PACE - time.time()
        if wait > 0:
            time.sleep(min(wait, DIRECT_PACE))
        _last_direct_ts[0] = time.time()


def _scraper_load():
    d = _read_json(SCRAPER_STATE_FILE, {})
    if isinstance(d, dict):
        for k in ("day", "used", "limit", "blocked", "keys"):
            if k in d:
                _scraper_state[k] = d[k]
    if not isinstance(_scraper_state.get("blocked"), dict):
        _scraper_state["blocked"] = {}
    if not isinstance(_scraper_state.get("keys"), dict):
        _scraper_state["keys"] = {}


def _scraper_save():
    try:
        _atomic_dump(SCRAPER_STATE_FILE, _scraper_state)
    except Exception:
        pass


def _scraper_allow():
    """Денний ліміт кредитів (за замовч. 120)."""
    today = datetime.date.today().isoformat()
    with _scraper_lock:
        if _scraper_state.get("day") != today:
            _scraper_state["day"] = today
            _scraper_state["used"] = 0
            _scraper_save()
        st = _read_json(SETTINGS_FILE, {}) or {}
        try:
            limit = int(st.get("scraper_limit") or _scraper_state.get("limit") or 30)
        except Exception:
            limit = int(_scraper_state.get("limit") or 30)
        _scraper_state["limit"] = limit
        return int(_scraper_state.get("used") or 0) < limit


def _scraper_take():
    with _scraper_lock:
        _scraper_state["used"] = int(_scraper_state.get("used") or 0) + 1
    _scraper_save()


def _direct_blocked(key):
    return int((_scraper_state.get("blocked") or {}).get(key) or 0) > time.time()


def _mark_direct_blocked(key, secs=1800):
    _scraper_state.setdefault("blocked", {})[key] = int(time.time()) + secs
    _scraper_save()


def _sup_status():
    d = _read_json(SUP_TS_FILE, {}) or {}
    return {"ts": int(d.get("ts") or 0),
            "attempt": int(d.get("attempt") or d.get("ts") or 0)}


def _sup_hours():
    st = _read_json(SETTINGS_FILE, {}) or {}
    try:
        return max(1.0, float(st.get("sup_hours") or 8))
    except Exception:
        return 8.0


def _sup_due():
    s = _sup_status()
    return (time.time() - s["attempt"]) >= _sup_hours() * 3600 or not _supplier_cache


_quota_cache = {}       # tail -> {"ts": ..., "data": {...}}


def _scraper_keys():
    """Усі ключі: список scraper_api_keys + одиничний scraper_api_key."""
    s = _read_json(SECRETS_FILE, {}) or {}
    keys = s.get("scraper_api_keys") or []
    if isinstance(keys, str):
        keys = [keys]
    one = s.get("scraper_api_key")
    out = []
    for k in list(keys) + ([one] if one else []):
        k = str(k or "").strip()
        if k and k not in out:
            out.append(k)
    return out


def _scraper_quota(key):
    """Квота конкретного ключа (кеш 10 хв)."""
    tail = key[-6:]
    c = _quota_cache.get(tail)
    if c and time.time() - c["ts"] < 600:
        return c["data"]
    out = {}
    try:
        u = "https://api.scraperapi.com/account?api_key=" + key
        with urllib.request.urlopen(u, timeout=12) as r:
            d = json.loads(r.read().decode("utf-8", "replace"))
        out = {"used": d.get("requestCount"), "limit": d.get("requestLimit"),
               "left": d.get("creditsLeft"),
               "renews": str(d.get("nextBillingDate") or "")[:10]}
    except Exception as e:
        out = {"error": str(e)[:80]}
    _quota_cache[tail] = {"ts": time.time(), "data": out}
    return out


def _ban_key(key, secs=3600, why=""):
    st = _scraper_state.setdefault("keys", {})
    st.setdefault(key[-6:], {})["until"] = int(time.time()) + secs
    st[key[-6:]]["err"] = str(why)[:80]
    _scraper_save()


def _scraper_key():
    """Ключ із найбільшим залишком; вичерпані/забанені пропускаємо."""
    keys = _scraper_keys()
    if not keys:
        return None
    now = time.time()
    st = _scraper_state.setdefault("keys", {})
    best, best_left = None, -1
    for k in keys:
        info = st.get(k[-6:]) or {}
        if int(info.get("until") or 0) > now:
            continue
        q = _scraper_quota(k)
        if q.get("error"):
            left = 1                       # не змогли перевірити — пробуємо
        else:
            left = q.get("left")
            left = 10 ** 9 if left is None else int(left)
        if left <= 5:
            _ban_key(k, 1800, "квота вичерпана")
            continue
        if left > best_left:
            best, best_left = k, left
    return best


def _sup_mark(ok):
    d = _read_json(SUP_TS_FILE, {}) or {}
    now = int(time.time())
    if ok:
        d["ts"] = now
    d["attempt"] = now
    d["ok"] = bool(ok)
    try:
        _atomic_dump(SUP_TS_FILE, d)
    except Exception:
        pass


_scraper_load()



# ─────────────────────────────────────────────────
# 🆕 ДЕТЕКТОР НОВИНОК (sitemap) + Telegram-алерти
# ─────────────────────────────────────────────────
_news_state = {"by_supplier": {}, "checked": 0, "last_new": 0}
_news_cache = {}
_new_products = []
_news_lock = threading.Lock()


def _news_load():
    d = _read_json(NEWS_STATE_FILE, {})
    if isinstance(d, dict):
        for k in ("by_supplier", "checked", "last_new"):
            if k in d:
                _news_state[k] = d[k]
    if not isinstance(_news_state.get("by_supplier"), dict):
        _news_state["by_supplier"] = {}


def _news_save():
    try:
        _atomic_dump(NEWS_STATE_FILE, _news_state)
    except Exception:
        pass


def _smart_get(url, timeout=40, allow_scraper=True):
    """GET: спершу напряму (безкоштовно), інакше через ScraperAPI з ротацією ключів.

    Для новинок викликаємо з allow_scraper=False — перевірка має бути безкоштовною.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        if not allow_scraper:
            raise
    if not _scraper_allow():
        raise RuntimeError("денний ліміт ScraperAPI")
    key = _scraper_key()
    if not key:
        raise RuntimeError("немає ключів з квотою")
    _scraper_take()
    u = ("https://api.scraperapi.com?api_key=%s&url=%s"
         % (key, urllib.parse.quote(url, safe="")))
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}),
                                    timeout=90) as r:
            return r.read()
    except Exception:
        _ban_key(key, 900, "news")
        raise


def _sitemap_handles(base):
    """{handle: lastmod} із sitemap_products_*.xml (1–2 запити на магазин)."""
    xml = _smart_get(base.rstrip("/") + "/sitemap.xml",
                     allow_scraper=False).decode("utf-8", "replace")
    subs = re.findall(r"<loc>\s*([^<]*sitemap_products[^<]*)</loc>", xml)
    if not subs:
        subs = [base.rstrip("/") + "/sitemap_products_1.xml"]
    out = {}
    for sm in subs[:3]:
        try:
            body = _smart_get(sm, allow_scraper=False).decode("utf-8", "replace")
        except Exception:
            continue
        for m in re.finditer(r"<loc>\s*[^<]*/products/([^<]+?)\s*</loc>"
                             r"(?:\s*<lastmod>([^<]+)</lastmod>)?", body):
            out[m.group(1)] = m.group(2) or ""
    return out


def _notify_news(new_items):
    if not _tg_flag("new"):
        return 0
    """Одне повідомлення: що нового з'явилось у магазинах."""
    if not new_items:
        return 0
    cfg = _tg_cfg()
    if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")
            and cfg.get("notify_new", True)):
        return 0
    lines = ["🆕 <b>Нові акаунти у постачальників</b> (%d)" % len(new_items)]
    for it in new_items[:10]:
        lines.append("• <b>%s</b> — %s\n  %s"
                     % (_html_mod.escape(it["title"][:70]),
                        _html_mod.escape(it["source"]),
                        it["url"]))
    _tg_send("\n".join(lines))
    return min(len(new_items), 10)


def _notify_new_products():
    if not _tg_flag("new"):
        return 0
    """Алерт про новинки, знайдені під час повного оновлення."""
    global _new_products
    items, _new_products = _new_products, []
    if not items:
        return 0
    st0 = _read_json(SETTINGS_FILE, {}) or {}
    if st0.get("alerts_only_my_games", True):
        allowed = _my_games()
        items = [x for x in items if _alert_relevant(x.get("title"), allowed)]
        if not items:
            return 0
    items.sort(key=lambda x: x.get("price") or 0)
    cfg = _tg_cfg()
    if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")
            and cfg.get("notify_new", True)):
        return 0
    lines = ["🆕 <b>Нові акаунти</b> (%d)" % len(items)]
    for it in items[:10]:
        lines.append("• <b>%s</b> — $%.2f · %s\n  %s"
                     % (_html_mod.escape(it["title"][:60]), float(it.get("price") or 0),
                        _html_mod.escape(it["source"]), it["url"]))
    _tg_send("\n".join(lines))
    return min(len(items), 10)


def news_check(force=False):
    """Швидка перевірка новинок: sitemap кожного магазину замість повного скану."""
    if not _news_lock.acquire(blocking=False):
        return {"ok": False, "error": "перевірка вже виконується"}
    try:
        found = []
        known_all = _news_state.get("by_supplier") or {}
        first_run = not known_all
        for key, src in SUPPLIERS.items():
            try:
                handles = _sitemap_handles(src["base"])
            except Exception as e:
                print(f"  ⚠ sitemap {key}: {e}", flush=True)
                continue
            known = set(known_all.get(key) or [])
            if not first_run:
                for h in handles:
                    if h not in known:
                        found.append({"title": h.replace("-", " ")[:70],
                                      "source": src["name"],
                                      "url": f"{src['base']}/products/{h}"})
            known_all[key] = sorted(handles)
        _news_state["by_supplier"] = known_all
        _news_state["checked"] = int(time.time())
        _news_state["last_new"] = len(found)
        _news_save()
        sent = 0 if first_run else _notify_news(found)
        print(f"  🆕 News: checked {len(known_all)} shops, new {len(found)}"
              + (" (перший запуск — без алерту)" if first_run else ""), flush=True)
        return {"ok": True, "new": len(found), "notified": sent, "baseline": first_run}
    finally:
        _news_lock.release()


def _news_due():
    st = _read_json(SETTINGS_FILE, {}) or {}
    try:
        hrs = max(0.25, float(st.get("news_hours") or 2))
    except Exception:
        hrs = 2.0
    return (time.time() - int(_news_state.get("checked") or 0)) >= hrs * 3600


_news_load()


def fetch_supplier(key, is_first_run=False):
    src = SUPPLIERS[key]; products = []; page = 1
    blocked = _direct_blocked(key)
    print(f"  {src['emoji']} {src['name']}...{' (blocked directly)' if blocked else ''}",
          end="", flush=True)
    while True:
        raw_url = f"{src['base']}/products.json?limit=250&page={page}"
        items = None
        modes = []
        if not blocked:
            modes.append("direct")
        modes.append("scraper")
        for mode in modes:
            is_scraper = mode == "scraper"
            if mode == "direct":
                _pace_direct()
            url = raw_url
            used_key = None
            if is_scraper:
                if not _scraper_allow():
                    print(" ⛔ ScraperAPI daily limit", end="", flush=True)
                    if page == 1:
                        raise RuntimeError(f"{src['name']}: денний ліміт ScraperAPI")
                    break
                used_key = _scraper_key()
                if not used_key:
                    print(" ⛔ no keys with quota left", end="", flush=True)
                    if page == 1:
                        raise RuntimeError(f"{src['name']}: усі ключі ScraperAPI вичерпані")
                    break
                _scraper_take()
                url = ("https://api.scraperapi.com?api_key=%s&url=%s"
                       % (used_key, urllib.parse.quote(raw_url, safe="")))
            try:
                headers = {"User-Agent": UA, "Accept": "application/json"}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode())
                    items = data.get("products", [])
                if is_scraper:
                    try:
                        st = _scraper_state.setdefault("keys", {})
                        if not isinstance(st, dict):
                            st = _scraper_state["keys"] = {}
                        info = st.setdefault(used_key[-6:], {})
                        info["used"] = int(info.get("used") or 0) + 1
                        _scraper_save()
                    except Exception as _e:
                        print(f" [key-stat {_e}]", end="", flush=True)
                break
            except urllib.error.HTTPError as ex:
                if not is_scraper and ex.code == 429:
                    # 429 тримається довше за Retry-After — не чекаємо, а
                    # блокуємо сайт на 20 хв і йдемо через ScraperAPI.
                    # Повернення на прямий доступ робить _probe_direct() кожні 5 хв.
                    _mark_direct_blocked(key, 1200)
                    blocked = True
                if is_scraper and ex.code in (401, 403, 429):
                    _ban_key(used_key, 1800, "HTTP %s" % ex.code)
                print(f" ⚠{'[ScraperAPI]' if is_scraper else '[direct]'}HTTP {ex.code}",
                      end="", flush=True)
            except Exception as ex:
                # бан лише за мережеві збої, не за помилки обліку
                if is_scraper and isinstance(ex, (urllib.error.URLError, TimeoutError,
                                                  ConnectionError, OSError)):
                    _ban_key(used_key, 900, str(ex)[:40])
                print(f" ⚠{'[ScraperAPI]' if is_scraper else '[direct]'}{str(ex)[:40]}",
                      end="", flush=True)
        if items is None:
            print(f" ❌ both attempts failed", end="", flush=True)
            if page == 1:
                # перша сторінка не завантажилась — це збій сайту, а не «0 products»
                raise RuntimeError(f"{src['name']}: не вдалось завантажити (блок/ScraperAPI)")
            break
        if not items: break
        for p in items:
            v = (p.get("variants") or [{}])[0]
            try: price = round(float(str(v.get("price","0")).replace(",",".")), 2)
            except Exception: price = 0.0
            try: comp = round(float(str(v.get("compare_at_price","0") or "0").replace(",",".")), 2)
            except Exception: comp = 0.0
            sale  = comp > 0 and comp > price
            avail = any(x.get("available") for x in p.get("variants", []))
            raw_id = p.get("id") or p.get("handle") or p.get("title") or "?"
            pid = f"{key}_{raw_id}"
            now_ts = int(time.time())
            prev = _supplier_seen.get(pid)
            if not prev:
                if not is_first_run:
                    _new_products.append({
                        "title": (p.get("title") or "")[:70], "price": price,
                        "source": src["name"],
                        "url": f"{src['base']}/products/{p.get('handle','')}"})
                # Новий товар: якщо перший запуск — seen_at=0 (не показуємо як нове)
                _supplier_seen[pid] = {
                    "seen_at": now_ts if not is_first_run else 0,
                    "updated_at": 0,
                    "price": price, "available": avail
                }
            else:
                if prev.get("price") != price or prev.get("available") != avail:
                    prev["updated_at"] = now_ts
                    old_price = float(prev.get("price") or 0)
                    if old_price and price != old_price:
                        hist = prev.get("history") or []
                        hist.append([now_ts, price])
                        prev["history"] = hist[-20:]
                        if price < old_price * 0.9:       # падіння ≥10%
                            _price_drops.append({
                                "id": pid, "title": p.get("title", "")[:70],
                                "old": round(old_price, 2), "new": round(price, 2),
                                "pct": (price / old_price - 1) * 100,
                                "source": src["name"], "url": f"{src['base']}/products/{p.get('handle','')}",
                            })
                    prev["price"] = price
                    prev["available"] = avail
            seen_info = _supplier_seen[pid]
            products.append({
                "id": pid, "title": p.get("title",""),
                "url": f"{src['base']}/products/{p.get('handle','')}",
                "source": key, "sourceName": src["name"],
                "sourceColor": src["color"], "sourceEmoji": src["emoji"],
                "price": price, "comparePrice": comp,
                "isOnSale": sale,
                "discount": max(0, min(99, round((1-price/comp)*100))) if sale and comp else 0,
                "available": avail,
                "seen_at": seen_info["seen_at"],
                "updated_at": seen_info["updated_at"],
                "last_seen": now_ts,
                "gone": False,
            })
        print(".", end="", flush=True)
        if len(items) < 250: break
        page += 1
        if page > 15: break
        time.sleep(1.6 + random.uniform(0, 0.6))   # повільніше = менше 429
    print(f" ✓{len(products)}")
    return products


# ─────────────────────────────────────────────────
# HTTP SERVER
# ─────────────────────────────────────────────────
GONE_TTL = 14 * 86400            # скільки днів показуємо «товар зник»
_TITLE_STOP = {
    "account", "accounts", "acc", "accs", "global", "region", "server", "fresh",
    "stacked", "starter", "starters", "new", "the", "and", "for", "with", "game",
    "gaming", "shop", "store", "best", "cheap", "buy", "sale", "top", "full",
    "ready", "instant", "delivery", "custom", "selective", "official", "fast",
    "auto", "gift", "code", "key", "pack", "bonus", "item", "items", "sell",
    "selling", "available", "stock", "limited", "premium", "secure", "safe",
    "trusted", "cheapest", "price", "off", "all", "any", "your", "you", "our",
    "from", "that", "this", "are", "was", "will", "can", "not", "has", "have",
}
_REGION_WORDS = {"global", "eu", "na", "asia", "jp", "kr", "europe", "america",
                 "sea", "ru", "tr", "cn"}


def _supplier_counts():
    """Кількість products по джерелах (без «зниклих»)."""
    return {k: sum(1 for x in _supplier_cache
                   if x.get("source") == k and not x.get("gone")) for k in SUPPLIERS}


def _supplier_sort(items, sort):
    if sort == "pa":
        return sorted(items, key=lambda p: p.get("price") or 0)
    if sort == "pd":
        return sorted(items, key=lambda p: -(p.get("price") or 0))
    if sort == "sale":
        return sorted(items, key=lambda p: -(1 if p.get("isOnSale") else 0))
    if sort == "new":
        return sorted(items, key=lambda p: -(p.get("seen_at") or 0))
    if sort == "updated":
        return sorted(items, key=lambda p: -(p.get("updated_at") or 0))
    return items


def _title_parts(title):
    """(регіон, змістовні слова) — для порівняння products між магазинами."""
    import re as _re
    t = (title or "").lower()
    t = _re.sub(r"[^0-9a-zа-яіїєґё]+", " ", t)
    words = [w for w in t.split() if w]
    region = next((w for w in words if w in _REGION_WORDS), "")
    core = [w for w in words if w not in _TITLE_STOP and w not in _REGION_WORDS]
    return region, core


_cheaper_map = {}
_cmp_index = {}
_cmp_parts = {}


def _cmp_core(pid):
    """(регіон, змістовні слова) товару — з індексу, інакше рахуємо на місці."""
    info = _cmp_parts.get(pid)
    if info:
        return info
    p = next((x for x in (_supplier_cache or []) if x.get("id") == pid), None)
    return _title_parts(p.get("title")) if p else ("", [])


def _build_compare_index():
    """Індекс «та сама гра» + карта «де дешевше» — після кожного оновлення.

    Без індексу порівняння 1571 товару було б O(n²) на кожен запит; з індексом
    по першому слову назви — кілька тисяч порівнянь.
    """
    global _cheaper_map, _cmp_index, _cmp_parts
    index, parts = {}, {}
    for p in (_supplier_cache or []):
        if p.get("gone"):
            continue
        r, core = _title_parts(p.get("title"))
        if len(core) < 2:
            continue
        parts[p.get("id")] = (r, core)
        index.setdefault(core[0], []).append(p)
    cheaper = {}
    for p in (_supplier_cache or []):
        pid = p.get("id")
        info = parts.get(pid)
        if not info or p.get("gone"):
            continue
        r_me, core_me = info
        p_me = float(p.get("price") or 0)
        if p_me <= 0:
            continue
        best = None
        for q in index.get(core_me[0], []):
            if q is p or q.get("source") == p.get("source"):
                continue
            info_q = parts.get(q.get("id"))
            if not info_q:
                continue
            r_q, core_q = info_q
            if r_me and r_q and r_me != r_q:
                continue
            inter = len(set(core_me) & set(core_q))
            score = inter / max(1, len(set(core_me) | set(core_q)))
            if inter < 3 or score < 0.5:
                continue
            p_q = float(q.get("price") or 0)
            if p_q <= 0 or max(p_me, p_q) / min(p_me, p_q) > 1.8:
                continue
            if best is None or p_q < best[0]:
                best = (p_q, q.get("sourceName"), q.get("id"))
        if best and best[0] < p_me - 0.01:
            cheaper[pid] = {"price": round(best[0], 2), "sourceName": best[1] or "",
                            "id": best[2], "diff": round(best[0] - p_me, 2)}
    _cmp_index, _cmp_parts, _cheaper_map = index, parts, cheaper
    return len(cheaper)


def _my_game_tokens(min_sales=None, max_catalog_pct=0.05):
    """Унікальні слова ігор, які ви продаєте.

    Беремо слова з назв ваших продажів/складу, які:
      • зустрічаються щонайменше у min_sales ваших записах (не випадковість),
      • рідко зустрічаються в каталозі постачальників (не «america»/«starter»).
    """
    from collections import Counter
    pl_all = _read_json(PL_FILE, []) or []
    ed_all = _read_json(ED_FILE, []) or []
    if min_sales is None:
        # на малих даних (нова інсталяція) вистачить одного згадування
        min_sales = 2 if (len(pl_all) + len(ed_all)) >= 30 else 1
    mine = Counter()
    for src in (PL_FILE, ED_FILE):
        for r in (_read_json(src, []) or []):
            for t in set(_title_tokens(r.get("title"))):
                mine[t] += 1
    for r in (_read_json(INVENTORY_FILE, []) or []):
        for t in (set(_title_tokens(r.get("title"))) | set(_title_tokens(r.get("game")))):
            mine[t] += 1
    cat = Counter()
    for p in (_supplier_cache or []):
        for t in set(_title_tokens(p.get("title"))):
            cat[t] += 1
    limit = max(3, int(len(_supplier_cache or []) * max_catalog_pct))
    return {t for t, c in mine.items() if c >= min_sales and cat.get(t, 0) <= limit}


def _my_games():
    """Ігри, які ви реально продаєте (за назвами P&L / ELDORADO / складу)."""
    games = set()
    for src in (PL_FILE, ED_FILE):
        for r in (_read_json(src, []) or []):
            g = _game_of(r.get("title"))
            if g and g != "Other":
                games.add(g)
    for r in (_read_json(INVENTORY_FILE, []) or []):
        g = _game_of(r.get("title")) or _game_of(r.get("game"))
        if g and g != "Other":
            games.add(g)
    return games


def _alert_relevant(text, allowed):
    """Чи стосується алерт ваших ігор (якщо список порожній — усе)."""
    if not allowed:
        return True
    return _game_of(text) in allowed


def _notify_price_drops():
    if not _tg_flag("price"):
        return 0
    """Одне агреговане повідомлення про зниження цін після оновлення."""
    global _price_drops
    drops, _price_drops = _price_drops, []
    if not drops:
        return 0
    cfg = _tg_cfg()
    if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")
            and cfg.get("notify_price", True)):
        return 0
    st = _read_json(SETTINGS_FILE, {}) or {}
    if st.get("alerts_only_my_games", True):
        allowed = _my_games()
        before = len(drops)
        drops = [d for d in drops if _alert_relevant(d.get("title"), allowed)]
        if before != len(drops):
            print(f"  💸 price drops: {before} → {len(drops)} (my games filter)", flush=True)
    if not drops:
        return 0
    top = sorted(drops, key=lambda d: d.get("pct", 0))[:10]
    lines = [f"💸 <b>Ціна впала</b> ({len(drops)} шт.)"]
    for d in top:
        lines.append("• %s: $%.2f → $%.2f (%+.0f%%) — %s"
                     % (_html_mod.escape(d.get("title", "")[:60]), d.get("old", 0),
                        d.get("new", 0), d.get("pct", 0),
                        _html_mod.escape(d.get("source", ""))))
    res = _tg_send("\n".join(lines))
    if res.get("ok"):
        print(f"  📉 TG: {len(top)} price drops", flush=True)
    return len(top)


def _compare_products(pid, limit=12):
    """Той самий товар в інших магазинах: та сама гра, регіон і схожа ціна.

    Поріг підібрано на реальному каталозі (2116 products): без нього 95%
    «збігів» були різними іграми через спільні слова-маркетинг.
    """
    me = next((p for p in (_supplier_cache or []) if p.get("id") == pid), None)
    if not me:
        return {"ok": False, "error": "товар не знайдено"}
    r_me, core_me = _cmp_core(pid)
    if len(core_me) < 2:
        return {"ok": True, "product": _cmp_product(me), "matches": [], "best": None}
    p_me = float(me.get("price") or 0)
    candidates = _cmp_index.get(core_me[0]) if _cmp_index else (_supplier_cache or [])
    scored = []
    for p in candidates or []:
        if p.get("id") == me.get("id") or p.get("gone"):
            continue
        if p.get("source") == me.get("source"):
            continue                       # шукаємо саме в інших магазинах
        r_p, core_p = _cmp_core(p.get("id"))
        if len(core_p) < 2:
            continue
        if r_me and r_p and r_me != r_p:
            continue
        if not (core_me[0] == core_p[0] or core_me[0] in " ".join(core_p[:2])
                or core_p[0] in " ".join(core_me[:2])):
            continue
        inter = len(set(core_me) & set(core_p))
        score = inter / max(1, len(set(core_me) | set(core_p)))
        if inter < 3 or score < 0.5:
            continue
        p_p = float(p.get("price") or 0)
        if p_me > 0 and p_p > 0 and max(p_me, p_p) / min(p_me, p_p) > 1.8:
            continue                       # $1 і $50 — це різні товари
        scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], x[1].get("price") or 0))
    matches = []
    for score, p in scored[:limit]:
        m = _cmp_product(p)
        m["match"] = round(score * 100)
        m["diff"] = round((p.get("price") or 0) - p_me, 2)
        matches.append(m)
    best = min(matches, key=lambda m: m.get("price") or 0) if matches else None
    return {"ok": True, "product": _cmp_product(me), "matches": matches, "best": best}


def _cmp_product(p):
    return {"id": p.get("id"), "title": p.get("title"), "price": p.get("price"),
            "url": p.get("url"), "source": p.get("source"),
            "sourceName": p.get("sourceName"), "sourceColor": p.get("sourceColor"),
            "sourceEmoji": p.get("sourceEmoji"), "available": p.get("available")}


def _notify_restock(items, limit=5):
    if not _tg_flag("restock"):
        return 0
    """«Знову в наявності» — товар, який ви продавали, повернувся в каталог."""
    try:
        cfg = _tg_cfg()
        if not (cfg.get("enabled") and cfg.get("token") and cfg.get("chat_id")
                and cfg.get("notify_new", True)):
            return 0
        my = _my_games() if "_my_games" in globals() else set()
        rows = [p for p in items
                if not my or _game_of(p.get("title")) in my]
        if not rows:
            return 0
        rows.sort(key=lambda p: float(p.get("price") or 0))
        lines = ["🔄 <b>Знову в наявності</b> (%d)" % len(rows)]
        for p in rows[:limit]:
            lines.append("• %s — $%.2f · %s" % (
                _html_mod.escape(str(p.get("title") or "")[:46]),
                float(p.get("price") or 0),
                _html_mod.escape(str(p.get("sourceName") or p.get("source") or ""))))
        if len(rows) > limit:
            lines.append("…і ще %d" % (len(rows) - limit))
        _tg_send("\n".join(lines))
        print("  🔄 restock: %d products, alert" % len(rows), flush=True)
        return len(rows)
    except Exception as e:
        print(f"  ⚠ restock: {e}", flush=True)
        return 0


def _merge_supplier_cache(fresh, ok_keys):
    """Свіжі дані + старі для тих сайтів, що не відповіли, + маркери зниклих."""
    global _supplier_cache
    now = int(time.time())
    old = _supplier_cache or []
    old_by_key = {k: [p for p in old if p.get("source") == k] for k in SUPPLIERS}
    fresh_ids = {p.get("id") for p in fresh}
    restocked = [p for k in SUPPLIERS for p in old_by_key.get(k) or []
                 if p.get("gone") and p.get("id") in fresh_ids]
    merged = list(fresh)
    for key in SUPPLIERS:
        for p in old_by_key.get(key) or []:
            if p.get("id") in fresh_ids:
                continue
            if key not in ok_keys:
                merged.append(p)              # сайт не відповів — не вважаємо зниклим
                continue
            if p.get("gone"):
                if now - int(p.get("gone_at") or now) <= GONE_TTL:
                    merged.append(p)          # ще показуємо як «зникло»
                continue
            last_seen = int(p.get("last_seen") or p.get("seen_at") or 0)
            if last_seen and now - last_seen > 30 * 86400:
                continue                      # давно не бачили — не маркуємо
            merged.append({**p, "gone": True, "gone_at": now, "available": False,
                           "was_price": p.get("price"), "last_seen": last_seen or now})
    _supplier_cache = merged
    if restocked:
        _notify_restock(restocked)
    try:
        _build_compare_index()
    except Exception as e:
        print(f"  ⚠ Compare index: {e}", flush=True)
    return merged


_AN_GAMES = [
    # порядок важливий: специфічні ігри — раніше, «fate» — останнім і з \b,
    # інакше «Primogems Fates Genshin Impact» розпізнавалось як FGO
    ("Arknights", r"arknights|方舟"),
    ("ZZZ", r"zenless|\bzzz\b|绝区"),
    ("Wuthering Waves", r"wuthering|\bwuwa\b|鸣潮"),
    ("Nikke", r"nikke|胜利女神"),
    ("Blue Archive", r"blue archive|碧蓝档案"),
    ("Cookie Run", r"cookie run|姜饼人"),
    ("Epic Seven", r"epic seven|第七史诗"),
    ("DB Legends", r"dragon ball legends|龙珠激斗"),
    ("Dokkan", r"dokkan|爆裂"),
    ("One Piece", r"one piece|海贼"),
    ("Genshin", r"genshin|primogem|原神"),
    ("Star Rail", r"star rail|honkai|星穹"),
    ("FGO", r"\bfgo\b|\bfate\b|冠位"),
    ("Identity V", r"identity\s*v|第五人格"),
    ("Genshin", r"\bgenshin\b"),
    ("Honkai", r"honkai"),
    ("Clash of Clans", r"clash of clans|\bcoc\b"),
    ("Brawl Stars", r"brawl stars"),
    ("Free Fire", r"free fire"),
    ("PUBG", r"\bpubg\b"),
    ("Valorant", r"valorant"),
    ("Roblox", r"roblox"),
    ("Minecraft", r"minecraft"),
    ("Fortnite", r"fortnite"),
    ("Steam", r"\bsteam\b"),
]


def _game_of(title):
    t = str(title or "")
    for name, pat in _AN_GAMES:
        if re.search(pat, t, re.I):
            return name
    return "Other"


def _analytics():
    """Прибуток/виторг по іграх і місяцях + «мертві» лоти."""
    pl = _read_json(PL_FILE, []) or []
    ed = _read_json(ED_FILE, []) or []
    games, months = {}, {}

    def add(g, m, sell, prof):
        a = games.setdefault(g, {"n": 0, "sell": 0.0, "profit": 0.0})
        a["n"] += 1; a["sell"] += sell; a["profit"] += prof
        b = months.setdefault(m, {"n": 0, "sell": 0.0, "profit": 0.0})
        b["n"] += 1; b["sell"] += sell; b["profit"] += prof

    for r in (pl if isinstance(pl, list) else []):
        try:
            sell = float(r.get("sell") or 0); buy = float(r.get("buy") or 0)
        except Exception:
            sell = buy = 0.0
        fee = round(sell * _fee_pct_of(r), 2)
        exp = round(float(r.get("expenses") or 0), 2)
        add(_game_of(r.get("title")), str(r.get("date") or "")[:7] or "?",
            sell, round(sell - buy - fee - exp, 2))
    for r in (ed if isinstance(ed, list) else []):
        try:
            price = float(r.get("price") or 0); prof = float(r.get("profit") or 0)
        except Exception:
            price = prof = 0.0
        add(_game_of(r.get("title")), str(r.get("date") or "")[:7] or "?", price, prof)
    for d in (games, months):
        for v in d.values():
            v["sell"] = round(v["sell"], 2)
            v["profit"] = round(v["profit"], 2)
            v["avg"] = round(v["sell"] / v["n"], 2) if v["n"] else 0
    now = time.time()
    dead = []
    for x in _supplier_cache:
        seen = int((_supplier_seen.get(x.get("id")) or {}).get("seen_at") or 0)
        if seen and (now - seen) > 14 * 86400:
            dead.append({"title": (x.get("title") or "")[:60], "price": x.get("price"),
                         "sourceName": x.get("sourceName"),
                         "age": int((now - seen) // 86400)})
    dead.sort(key=lambda r: -r["age"])
    gl = sorted(games.items(), key=lambda kv: -kv[1]["profit"])
    return {"ok": True, "games": [{"game": k, **v} for k, v in gl],
            "months": [{"month": k, **v} for k, v in sorted(months.items())],
            "dead": dead[:30], "dead_total": len(dead)}


def _game_stats(days=90):
    """Статистика продажів по іграх за останні N днів (для «що купити»)."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    stats = {}
    for src, field in ((PL_FILE, "sell"), (ED_FILE, "price")):
        for r in (_read_json(src, []) or []):
            if str(r.get("date") or "") < since:
                continue
            g = _game_of(r.get("title"))
            st = stats.setdefault(g, {"sells": [], "n": 0})
            st["n"] += 1
            try:
                v = float(r.get(field) or 0)
            except (TypeError, ValueError):
                v = 0.0
            if v > 0:
                st["sells"].append(v)
    for g, st in stats.items():
        st["median_sell"] = round(statistics.median(st["sells"]), 2) if st["sells"] else 0
        st["max_sell"] = round(max(st["sells"]), 2) if st["sells"] else 0
    return stats


def _sales_tokens(days=180):
    """[(токени назви, ціна продажу)] — щоб порівнювати схожі лоти, а не всю гру."""
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    out = []
    for src, field in ((PL_FILE, "sell"), (ED_FILE, "price")):
        for r in (_read_json(src, []) or []):
            if str(r.get("date") or "") < since:
                continue
            try:
                price = float(r.get(field) or 0)
            except (TypeError, ValueError):
                continue
            if price <= 0:
                continue
            out.append((_game_of(r.get("title")), set(_title_tokens(r.get("title"))), price))
    return out


_CUSTOM_RE = re.compile(r"custom|selective|choose|choice|build your|pick your", re.I)


def _buy_list(limit=20, days=180, fee=0.095):
    """«Що купити сьогодні»: постачальник vs схожі ваші продажі.

    Порівнюємо не «гру в цілому», а лоти зі спільними словами назви, і
    відсікаємо нісенітницю (різниця понад 8× — це різні товари).
    """
    sales = _sales_tokens(days)
    stats = _game_stats(days)
    rows = []
    for p in (_supplier_cache or []):
        if p.get("gone"):
            continue
        try:
            price = float(p.get("price") or 0)
        except (TypeError, ValueError):
            continue
        if price <= 0:
            continue
        title = str(p.get("title") or "")
        # «Custom / Selective» — ціна залежить від вибору героя в каталозі,
        # це не фіксований товар, тому в порівняння не беремо
        if _CUSTOM_RE.search(title):
            continue
        g = _game_of(title)
        if not g or g == "Other":
            continue           # невідома гра — порівнювати нема з чим
        toks = set(_title_tokens(p.get("title")))
        if not toks:
            continue
        prices = [v for (sg, st, v) in sales if sg == g and (toks & st)]
        if not prices:
            continue
        expected = round(statistics.median(prices), 2)
        # 1.1× … 8× — інакше це різні за класом товари, а не вигідна ціна
        if not (price * 1.1 <= expected <= price * 8):
            continue
        net = round(expected * (1 - fee), 2)
        margin = round(net - price, 2)
        if margin <= 0:
            continue
        rows.append({
            "title": str(p.get("title") or "")[:160],
            "game": g,
            "source": str(p.get("sourceName") or p.get("source") or ""),
            "price": price,
            "expected": expected,
            "margin": margin,
            "roi": round(margin / price, 3),
            "demand": len(prices),
            "url": str(p.get("url") or ""),
        })
    rows.sort(key=lambda r: (-r["roi"], -r["margin"]))
    return {"ok": True, "items": rows[:max(1, min(100, int(limit or 20)))],
            "games": len(stats), "days": days, "fee": fee}


def _lots_csv(markup=30.0, source="inventory", limit=50, game=""):
    """CSV для заливки лотів: назва, ціна з націнкою, опис, джерело.

    Дані акаунтів (логін/пароль) у файл НЕ потрапляють.
    """
    try:
        markup = max(0.0, min(500.0, float(markup)))
    except (TypeError, ValueError):
        markup = 30.0
    game_l = str(game or "").lower().strip()
    rows = []
    if source == "inventory":
        for r in (_read_json(INVENTORY_FILE, []) or []):
            if r.get("status") != "in_stock":
                continue
            if game_l and game_l not in (str(r.get("game") or "") + str(r.get("title") or "")).lower():
                continue
            cost = float(r.get("cost") or 0)
            rows.append({
                "title": str(r.get("title") or "")[:180],
                "price": round(cost * (1 + markup / 100), 2),
                "game": str(r.get("game") or ""),
                "description": ("Server: see title. Instant delivery. "
                                "Fast response. Cost basis not included."),
                "source": "inventory",
                "cost": cost,
                "url": "",
            })
    elif source == "suppliers":
        for p in (_supplier_cache or []):
            if p.get("gone"):
                continue
            title = str(p.get("title") or "")
            if game_l and game_l not in title.lower():
                continue
            try:
                price = float(p.get("price") or 0)
            except (TypeError, ValueError):
                continue
            rows.append({
                "title": title[:180],
                "price": round(price * (1 + markup / 100), 2),
                "game": str(p.get("sourceName") or ""),
                "description": ("Instant delivery. Fast response. Source: %s"
                                % (p.get("sourceName") or "")),
                "source": str(p.get("sourceName") or ""),
                "cost": price,
                "url": str(p.get("url") or ""),
            })
    else:
        for x in (_taobao.get("items") or []):
            title = str(x.get("title_en") or x.get("title_cn") or "")
            if game_l and game_l not in title.lower():
                continue
            try:
                price = float(x.get("price_usd") or 0)
            except (TypeError, ValueError):
                continue
            rows.append({
                "title": title[:180],
                "price": round(price * (1 + markup / 100), 2),
                "game": str(x.get("game") or ""),
                "description": "Instant delivery. Fast response.",
                "source": "taobao",
                "cost": price,
                "url": str(x.get("href") or ""),
            })
    rows.sort(key=lambda r: r["price"])
    rows = rows[:max(1, min(500, int(limit or 50)))]
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["title", "price", "game", "description", "source", "cost", "url"])
    for r in rows:
        w.writerow([r["title"], r["price"], r["game"], r["description"],
                    r["source"], r["cost"], r["url"]])
    return "\ufeff" + buf.getvalue(), len(rows)


def _month_report(month=""):
    """Місячний звіт: продажі, закупівлі, комісії, касовий потік, прибуток."""
    month = (month or datetime.date.today().strftime("%Y-%m"))[:7]
    pl = [r for r in (_read_json(PL_FILE, []) or [])
          if str(r.get("date") or "").startswith(month)]
    ed = [r for r in (_read_json(ED_FILE, []) or [])
          if str(r.get("date") or "").startswith(month)]
    inv = [r for r in (_read_json(INVENTORY_FILE, []) or [])
           if str(r.get("date") or "").startswith(month)]

    def num(x):
        try:
            return float(x or 0)
        except (TypeError, ValueError):
            return 0.0

    pl_sell = round(sum(num(r.get("sell")) for r in pl), 2)
    pl_after = round(sum(num(r.get("afterFee")) for r in pl), 2)
    pl_buy = round(sum(num(r.get("buy")) for r in pl), 2)
    # afterFee вже = sell - fee - buy, тому комісію НЕ можна рахувати як sell - afterFee
    # (інакше в комісії опиняється закупівля, а прибуток зменшується вдвічі).
    pl_fee = round(sum(num(r.get("sell")) * _fee_pct_of(r) for r in pl), 2)
    pl_expenses = round(sum(num(r.get("expenses")) for r in pl), 2)
    pl_profit = round(pl_after - pl_expenses, 2)

    ed_rev = round(sum(num(r.get("price")) for r in ed), 2)
    ed_fee = round(sum(num(r.get("fee")) for r in ed), 2)
    ed_buy = round(sum(num(r.get("buy")) for r in ed), 2)
    ed_profit = round(sum(num(r.get("profit")) for r in ed), 2)

    purchases = round(sum(num(r.get("cost")) for r in inv), 2)
    sold_inv = [r for r in (_read_json(INVENTORY_FILE, []) or [])
                if r.get("status") == "sold"]
    inv_value = round(sum(num(r.get("cost")) for r in
                         (_read_json(INVENTORY_FILE, []) or [])
                         if r.get("status") == "in_stock"), 2)

    revenue = round(pl_sell + ed_rev, 2)
    fees = round(pl_fee + ed_fee, 2)
    cogs = round(pl_buy + ed_buy, 2)
    profit = round(pl_profit + ed_profit, 2)
    cash = round(revenue - fees - purchases, 2)

    by_day = {}
    for r in pl:
        d = str(r.get("date") or "")[:10]
        if d:
            by_day[d] = round(by_day.get(d, 0) + num(r.get("sell")), 2)
    for r in ed:
        d = str(r.get("date") or "")[:10]
        if d:
            by_day[d] = round(by_day.get(d, 0) + num(r.get("price")), 2)

    return {
        "ok": True, "month": month,
        "sales": {"pl_count": len(pl), "ed_count": len(ed), "count": len(pl) + len(ed),
                  "revenue": revenue, "fees": fees, "cogs": cogs, "profit": profit},
        "pl": {"count": len(pl), "sell": pl_sell, "after_fee": pl_after,
               "buy": pl_buy, "fee": pl_fee, "expenses": pl_expenses, "profit": pl_profit},
        "ed": {"count": len(ed), "revenue": ed_rev, "fee": ed_fee,
               "buy": ed_buy, "profit": ed_profit},
        "purchases": {"count": len(inv), "cost": purchases},
        "stock": {"in_stock_value": inv_value, "sold_total": len(sold_inv)},
        "cash": cash,
        "by_day": [{"date": k, "revenue": v} for k, v in sorted(by_day.items())],
    }


def _report_csv(rep, lang="uk"):
    """CSV місячного звіту (Excel: BOM + ;). lang = uk/en/ru."""
    T = {
        "uk": {
            "month": "Місяць", "metric": "Показник", "value": "Значення",
            "sales": "Продажів усього", "revenue": "Виторг",
            "fees": "Комісії майданчиків", "cogs": "Собівартість проданого",
            "profit": "Прибуток", "purchases": "Закупівлі цього місяця",
            "cash": "Касовий потік (виторг-комісії-закупівлі)",
            "plcols": ["P&L", "продажів", "виторг", "після комісії",
                       "собівартість", "комісія", "прибуток"],
            "edcols": ["ELDORADO", "продажів", "виторг", "комісія",
                       "собівартість", "прибуток"],
            "day": "День", "dayrev": "Виторг",
        },
        "en": {
            "month": "Month", "metric": "Metric", "value": "Value",
            "sales": "Total sales", "revenue": "Revenue",
            "fees": "Marketplace fees", "cogs": "Cost of goods sold",
            "profit": "Profit", "purchases": "Purchases this month",
            "cash": "Cash flow (revenue-fees-purchases)",
            "plcols": ["P&L", "deals", "revenue", "after fee",
                       "cost", "fee", "profit"],
            "edcols": ["ELDORADO", "deals", "revenue", "fee",
                       "cost", "profit"],
            "day": "Day", "dayrev": "Revenue",
        },
        "ru": {
            "month": "Месяц", "metric": "Показатель", "value": "Значение",
            "sales": "Продаж всего", "revenue": "Выручка",
            "fees": "Комиссии площадок", "cogs": "Себестоимость проданного",
            "profit": "Прибыль", "purchases": "Закупки за месяц",
            "cash": "Денежный поток (выручка-комиссии-закупки)",
            "plcols": ["P&L", "продаж", "выручка", "после комиссии",
                       "себестоимость", "комиссия", "прибыль"],
            "edcols": ["ELDORADO", "продаж", "выручка", "комиссия",
                       "себестоимость", "прибыль"],
            "day": "День", "dayrev": "Выручка",
        },
    }
    t = T.get(str(lang or "uk")[:2], T["uk"])
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow([t["month"], rep.get("month")])
    w.writerow([])
    w.writerow([t["metric"], t["value"]])
    for name, key in ((t["sales"], ("sales", "count")),
                      (t["revenue"], ("sales", "revenue")),
                      (t["fees"], ("sales", "fees")),
                      (t["cogs"], ("sales", "cogs")),
                      (t["profit"], ("sales", "profit")),
                      (t["purchases"], ("purchases", "cost")),
                      (t["cash"], ("cash",))):
        v = rep
        for k in key:
            v = (v or {}).get(k) if isinstance(v, dict) else v
        w.writerow([name, v])
    w.writerow([])
    w.writerow(t["plcols"])
    p = rep.get("pl") or {}
    w.writerow(["", p.get("count"), p.get("sell"), p.get("after_fee"),
                p.get("buy"), p.get("fee"), p.get("profit")])
    w.writerow(t["edcols"])
    e = rep.get("ed") or {}
    w.writerow(["", e.get("count"), e.get("revenue"), e.get("fee"),
                e.get("buy"), e.get("profit")])
    w.writerow([])
    w.writerow([t["day"], t["dayrev"]])
    for d in rep.get("by_day") or []:
        w.writerow([d.get("date"), d.get("revenue")])
    return "\ufeff" + buf.getvalue()


def _build_backup_zip():
    """zip з P&L + ELDORADO + ціль + налаштування + manifest sha256.

    Секрети (.gt_secrets.json) і токен Telegram НЕ включаються.
    """
    files = ((".gt_pl.json", PL_FILE), (".gt_eldorado.json", ED_FILE),
             (".gt_settings.json", SETTINGS_FILE),
             # важливі дані, які раніше не потрапляли в бекап:
             (".gt_taobao.json", TAOBAO_FILE),
             (".gt_imported.json", IMPORTED_FILE),
             (".gt_sitemap.json", NEWS_STATE_FILE),
             (".gt_scraper.json", SCRAPER_STATE_FILE),
             (".gt_mail_queue.json", MAIL_QUEUE_FILE))
    manifest = {"app": "GameTracker", "version": "4.5",
                "created": datetime.datetime.now().isoformat(timespec="seconds"),
                "files": {}}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, path in files:
            if not os.path.exists(path):
                continue
            with open(path, "rb") as f:
                data = f.read()
            z.writestr(name, data)
            manifest["files"][name] = {"size": len(data),
                                       "sha256": hashlib.sha256(data).hexdigest()}
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return buf.getvalue(), manifest


def _import_backup_zip(raw):
    """Відновлення з zip: перевіряє manifest/sha256, робить бекап поточного стану."""
    if not raw:
        raise ValueError("порожній файл")
    if len(raw) > 50 * 1024 * 1024:
        raise ValueError("файл завеликий (>50 МБ)")
    allowed = {".gt_pl.json": ("pl", PL_FILE), ".gt_eldorado.json": ("ed", ED_FILE),
               ".gt_goal.json": ("goal", GOAL_FILE), ".gt_settings.json": ("settings", SETTINGS_FILE)}
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except Exception as e:
        raise ValueError(f"це не zip-бекап: {e}")
    names = set(zf.namelist())
    if not names:
        raise ValueError("zip порожній")
    manifest = {}
    if "manifest.json" in names:
        try:
            manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
        except Exception:
            manifest = {}
    total_unpacked = sum(i.file_size for i in zf.infolist())
    if total_unpacked > 80 * 1024 * 1024:
        raise ValueError("zip розпаковується занадто сильно (>80 МБ)")

    loaded = {}
    for name in names:
        if name not in allowed:
            continue
        data = zf.read(name)
        want = ((manifest.get("files") or {}).get(name) or {}).get("sha256")
        if want and hashlib.sha256(data).hexdigest() != want:
            raise ValueError(f"{name}: sha256 не збігається — файл пошкоджено")
        loaded[name] = data
    if not loaded:
        raise ValueError("у zip немає файлів трекера")

    # бекап поточного стану перед імпортом
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for name, (pref, path) in allowed.items():
        if name in loaded and os.path.exists(path):
            shutil.copy2(path, os.path.join(BACKUP_DIR, f"{pref}_before_import_{ts}.json"))

    written = {}
    for name, data in loaded.items():
        kind, path = allowed[name]
        obj = json.loads(data.decode("utf-8"))
        if kind == "pl":
            obj = _clean_pl(obj)
        elif kind == "ed":
            obj = _clean_ed(obj)
        elif kind == "goal":
            if not isinstance(obj, dict):
                raise ValueError("ціль у бекапі має бути об'єктом")
        elif kind == "settings":
            if not isinstance(obj, dict):
                raise ValueError("налаштування у бекапі мають бути об'єктом")
            obj = {k: v for k, v in obj.items()
                   if k in ("usd_uah", "rate_ts", "rate_source", "cloud_dir", "currency",
                            "https_enabled", "https_cert", "https_key")}
        _atomic_dump(path, obj)
        written[name] = len(obj) if isinstance(obj, list) else None
    return {"ok": True, "files": sorted(written), "counts": written}
def _local_ip():
    """IP цієї машини (для підказки «з телефона» / публічної адреси)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        return ""


_LOCAL_IP = _local_ip()
_SCHEME = "http"          # ставиться в main() після можливого TLS-обгортання
_access_seen = set()      # унікальні email-и з Cloudflare Access (для логу/перевірки)


def _is_private_ip(ip):
    """192.168.x / 10.x / 172.16–31.x — домашня мережа, а не публічний VPS."""
    parts = (ip or "").split(".")
    if len(parts) != 4:
        return False
    try:
        a, b = int(parts[0]), int(parts[1])
    except ValueError:
        return False
    return a == 10 or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31)


def _csrf_key():
    """Ключ підпису CSRF: пароль, а в режимі GT_AUTH=off — секрет процесу."""
    return (AUTH_PASS or _SESSION_SECRET).encode("utf-8")


def _csrf_token():
    """Токен CSRF: випадкове значення + HMAC-підпис.

    Підпис робить cookie неспроможним до підробки без ключа
    (захист від cookie-injection із сусіднього піддомену).
    """
    raw = base64.urlsafe_b64encode(os.urandom(18)).decode("ascii").rstrip("=")
    sig = hmac.new(_csrf_key(), raw.encode("utf-8"), "sha256").hexdigest()[:16]
    return f"{raw}.{sig}"


# ─────────────────────────────────────────────────
# 🎨 ІКОНКИ (favicon / PWA / iOS) — вшиті в один файл
# ─────────────────────────────────────────────────
_LOGOS = {
    "zeusx": "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAArP0lEQVR42tW7eZDdV3Xv+9m/3+/Mc/c5PajnVrfUmgdrsGTLkjzItjxDZDBwKRJeTHIDFwpuitwXbsm+1E3IzSOGF/IIBApsw/WNBRiwPKPZkiyrNbSkbvU8T6fP6T7z+Bv2++PIwoEKAermVb1f1akz/X5777X2Wt+19l7fDf/e14svqu99lKDU/e3ftvi6ux/09Pd/y3X16nXXO+8Mubq7n7Vfv/7B4OHDLeL9zx48qP17D0/8u7UspYIQFoBLygZzcHB7+cSJZo4fD7G0tIxIZDVVVR0YhsLCwhjR6DW83gkOHEg4H3kk5QiFTqWEGP3Vtv53X/9+Gr5wQQUsDh5UjGMn77Zy6b8RpWIthQLK8DDiwgUUrxdcLmQqFbYMY6vsWA65HGb/dQpe3xeQ8ms3BK+09f+xAsQvLfd3mvnKc089ZSKlxuuvr9R//tIOkslan17CX8hR3dpKi89LQ3Mzan09c4kE44ODLCaWSL71Bqnu81BTc6vv8Q9trZXy8jDoCAGWJRBC/v/DAp5+2uKpp7xaOLzLnJvfaj961GytXWY0dK02Ii2N9u3r1iorly9X8i4nY0tLVmN9ozV/+YoxcvJtpX92ksKBP1hXsmv3LsAQQixx8KDyO0/GLyfyX31O+U1zCQh279ZudP67dPie9fgUm+0O4fet9RXKapOnxlFbt9xl81XZnN4q1ad4hDKfEsrMghowFduy+nZnS3OHozYYttlqalaUC8Xb08l5vwBYs0b8Tph18KDCgQPqDfcRv58F7N6tBBoafM6RkXIUcr+NRgE4frwyW5OTTjNf6LJCQXvRMkxplkU8uaRMxCbBsAgZdpwOD9PjC5zuPoNbswmZz1p5LGkoQmVmpon+AZcE6O0VHDggfytQlxIef9wBqOzeXeTEid/TBVauFHoi4ZCVhnO/tfb37DEByZEjAUsSJJWSJUUwn4xKc8rGZDEH8QXc83EaGtqYGuxnorcHBLikJU0V1JlpaZ7vdoJWh5QDCGHw1FPit5gAiRBw9912QiE7UPx9XQASCSu/sFBMj48LWlqcN+6XvzHmC2EhhIxI6WVwcJ08dtTl6Lsu/HaHSGbTQpRzrI74sGcXOPnmj/j5//w6+vh5bmsJELQrlCWiobpGhIZHBKdP+3Bq2+uhsTK/QvLii/+W2wIQ0HXhKRb/TddVfqM5HTpkEYvlWbfOYX/88Rb+5m88N1H+vfeDB5V/gRFSisCf/mkoefToY7jdHxbd3V5n7zUzEg6LQKhGuOwaPneZsK9IlS2DrTBL2ZjDdBWwO+0E/WERCgaEc3TEEsPDHpzOR5beeecBnnwycLPP98b3q2ORUuEb3/Dy13/dWl671u1Op3Ps2WP9JgxQfgOIVEytr6/saGpyml5vI8mk+9fC0NNPWzz9dCVGHzggEUKWrlzxmanUw3g898lEwuvOZsxwY4Pw1dQLm6rgUYu0Rtzs2LSaO2/fTn1LPYtGnrKQuD1+oTjsQubzhjR0J7p+qzE8vJfr1/0IId+HA/LXxiKERSzmVU1zpVlb64mdOJHl6aetG7L8Hi5w4yoZhmnm8zqHDlnv6+zXXeG112yAKJ4+nVAWFw2h66AqeKtrpDdSx1Qhg5FPs7t6GWuCDXiDNSxf0cWd67Zwe9MKnJrFYimNxA6hsMTjRiwuIq4PWpw6lX9fggVCgKpWZv/9Y/nJT0paJqOLUsn4bWT71xXw1FPypnllsyny+Rntz/6sw/6973UhpXLjJerBze7dXqRU2L+/hKZJ2/XrrebMjENeumTYNLuUbr8SnZ1ncmqUlKHjDraSEREuTGU4NxwjqYQJLt+M7vUyHZ9hIbaIFqhRXHa3lOfeNY2FuSq1t3cjUips2aLf6NuOaSoIIW98V51HjrS4n3yyzV4oTDmXlpLvS8rk7x4FKloVgMLXv57iW98q09S031IUOHt2gh07Sv7vfCeU+qu/2ua029NFeAfAoett5atXPy5nZ7bYL17W6jUfRqGoDFzsxtLzZBobOJ2DRLJM7+gsl/vGGFY8BFetIOMMkk9fZzxboiHcqDbiEhMDg2p5xfId0jT/xAZRHa5x6JDgC1/oIJNxUl8/DGQ5e9YuDONBuXy5ksnnv88Xv5hl714FMH9T9qj8q+lsBdwEhw5V/O3JJ4silysSi5UP7NxZRgirYFkN+oc//GfWgw9uRwjLIWV7+ciR/ygPHfqguHxpWSRXkh2NK7C7/Eo+lyLgcKGU4OyZ8yyOD7Gpxs1t7RHU+CzXT55GS5Xxq06yiQWymYxS66+hLVArfSPjXuu7371Lf/WV/+iXsoPHHzf57Gf3iIMHn2b58rUIYbFzZ9EslYImhHjggRIgiUQqclQsQfw2FiDeBy7yX6D88eOKbWrqggnhl154Ybt948ZFotH7rUjkHul2J5mebjLfeOOAvHDh4+pbb9W0FEusXLPe8nojIlcuirp8C06bDWdJRxQLOB0GkWonkWo/9kyJ+EyUchlqAtVUefzYXT6EU6Nr3QbpnB6R1954I2S6XU8ULTlHMvlDEQjsEfCgbGvro7t7SRsb80pdn7WkTDE5WYkQhw7JGyD9r65v1H8h/rFjGp/5jEp9PZw4UXGBr35V4yMfUWhrM/X9+5fMlSubrA0b/kTYbB/C6VxlmaaK14uSTO4wDx9+iKNHm6rn5rhtwybaV6wUk1OTuF0+VndtYGkpjmaDjZs2U7bg4sAww7E0rnAjkYY2puenCVZV88D+P0BRYGFxiuaWJuGqCrKUSYrCyKjTNIwV7NixU/F6lzE1pQtNCwif7x7q6lbLZPJdU9OOc//9BUClr0/l0CF5I0KpPPecyhNPCJ591vpVC6jM/N69N5GzUUrXJ6H0tBD6DbdQEaLE6dNQKnVZlpXR7PZXuHRJEaXSLjMWe5T+fod3YsJatmmTTDudSvTyBTE50E9n5yYi4VXUNzSQyyew2x34axqoszRQFExXCB2FZTVhIpFl2OxObJpCIbXAlcvdeNevo27zZiv/2utkBgYaGB5uIJXqlmNjPxDt7XEKhUekpm0XVVXPs3Nn+sZYjQqUCaRlKQhhcuiQ+avWrv5KDm2jtjbMihXrcq+/vu7U0aN11qc/XeRHPyoiROXhT34yKLJZu4zFvmfu2PEDrbOzIF2ubdbAwHoOH5aufN7wbd1q6798WfS/fRKHQ8MTCGLoBlV1NRiWyeTYGHU1ddx37wNs27KN2elpenousqKri0hNHee73yVTzCAtnatXekgoivC0tIrM5IRRisUUFAWkHJWK8hN5223fUx5/fEYK4bWcznP84z/O8PTTFlKqrFkTorFxHS++2Mn27V4+9SmDn//cuJG3iAoIdnfbAImUgkLhcW7Z9A1qa79m9fZ+WZme/L+8K1f+vQ/23dTbunVT8qc//SoPPHAUwP7f/tsKzTKbte5uiEZJzcyI3h/9mGRPD/XVflbt3InldjE6Noji9qD6A4yNj5DP5ejoWMWmTdvwODSmZyfIBKrJ+EKMjY+QUwQ16zdSX1NFpq+P6z/6MemZOUEmg3bpkrAZRsD1yCN1KArmnj1vyb6+g9TUjL4nmAf2uNrbv66m019XJib+Fo/nmzQ2/j+kUgcQooIDx45p2s0U8itfaaap6TGWEh9kaBi5uETZMCm/9NMtRGOqY26uWKyrOy6EiCNli/qf/tMG+eaba3L/9N0HOPP2co4es+ylklITqVadZhHdpqC43GRNwUI0SmkhhhWKIIFEapFyoYA/UIU/WIVNVSiWS6QVOzbFTjqToBx1ontcWKpGvQIeq0g5HFJihYIoXL4sqamtp1x+RPnyl51i585L5p49wwgxhxBolnVr7ucv/x+8++6HWVyEfB5mZuD6dcik7PZnnjlf/uxnxzh+HO1GYmFXM5mV1iuvtMvJKRgcpKq+RmqZlFh45hmLePxhsybc5ZmZ+Q/OJ5+Mly5c+FtrenofAwN2cfy4TV65IjAMZVlthNs3r1Xa6iP0Xh/izLV+Bs+cJp1M4vcHwRdAFguYlommKtjsLnTdwrBAVVSUXAlsRUrlAqn+XjILc5BJcHtXB7duXMt8OqecvHSV/vFpwU9+UiWu990lu7p2y3C4hMv1Bp///H+2/fmf+82Rkb/j9de2ihf+J+F1a9AVrOS77yrE4yhNjZ10dG6IwFxs796sdsNkTLJZy+Zw2Mtuj0UwaH1k1zZ9d0PYduznZX5++oQ2LZTVxpNPPuX47/89L/7pnx6wLvW4mZqgwSzTtWk1fpuNsoSFRIJiJknYpfKBTStYTKQ4nV0kViqiz8xgTydQFQUdSSqZRi+WSabTlIo51OQSCIGUFjWKyZYaN5HOWlRNY2R0jKJqY0VTPc2RKopCVcekwtTgkEYq5RRjYw+pn/pjqccX7Tz73I7IO2e4r63W2r9vu9VdVvRvHDtnK5XKijI/r5lV1YUIlGMgNI4dUxHCUD//+Qlt795YuX9wDemUsqo6IP7g7tvUdQ0RCn/1NePF578nCvfe85AsF7FefBFHb2+5dvMG9t26Wd3T1aZ4SmVxpfc67167Tj6nc8valaxtqmVsfIrhhTjT0Sy9J4/gFBKvO4ip2JiYmcTvC2KgoCoqcyMDzDlclAp5wtUutne2sKK5kfH4EpeGJ1FtBmvammlrbcEIVsmLc3Hr9YtXzblfvEVxeNgl7rzzQ0omi/3578s7gk7z05/5I23bhtWKfvaqUBxOlaYmlHD1XHl+fqBPiDIHD2oakYgCUP7AB+bU5cuHmJ7ZxsCA+4xTKrev65LLGxrEQ/vuUKdePy66n/0umXgaLl+m66H7bQ9+/EPsLaZFi14gXbKRr/bTvPMWWttbCQaDzMUWiU7EUbxVOBaLXLt8BpfLQ22kAUsKrg5fpypSh+bxUxNexvBwH6VSEQCnv4qM5qbs9rP7jjXcs1swMjREqVSkPRygOuAVqxtq1dYtG5SX/F7eeeMo1lf+BpfLziq7FI/uvlVd27WCoYWUPHX4TaV0rgc+85m88oefGOLixQV+8AM4cEDRKBYrEcBmywhdf0n4vPXKrtvvPzUxpja+csT8rx97TNlw61ZR231V6odfNUzdlI7mJm3Hnbcp96/qwD80RKJvjLl0khGh0L6ii+3rVqIAlmZnvalQW1fP5OQk717p4frUAovJGNemxljSBEGHm/mJcXKFHNXkWNEWZu2qVXR2Lqc+EqamKsjq9mZ8Xg+zQmGw7zpydBxqa2jesJEPNjWK+P67uTAbs/STbxtFo4Rveb2tc22XsKSQh46cto5MR1W5epWl1NZctK9efby4enWWj31McOGC1BgdtdiyRSKl0P/u72aVQGDU2rbNnByfVN9487h86JY1hKpCBEPVIqRptrzmRFu5An8mje3dcySKJcbHxumdHKe7dQ15V4B7dYOwXaVzWQ2rGuvRsFiMRjm/vI7Dp9/lSP8EU3PDxDOLOHIFZDpBxCm5b2MHD922hQ23bCFcX4eFimFZeJAsZXP0h2o4JUepOd9NaVUHVY2NKEuLOAoF3GtWKemJKXtoMUYoFCQvoftaP6+9dUyOWgrcstkSHs+8PHIkydKS4PHHLQ4elCpf/KLGt79tce6c3/rABz4nJyf3861vhxnoN+czOdWwLBEM+FhW5Ucp5IguLpLPl5CLS4SNAk0elZmxCX4xMEE0sozVHW1s97lwKYKSZSGkhanrICVun48VtdWs8NvIpFIMjc9SyqTZXuvhY1tXcvetW2nvXEkgGECoKhKBCdhNgzxwyRPg9PAk8++8w+11fpbXVvGz0928cvYyxZkZ6nMp7uho4I6tm8Dh4M3uq+JnZy4IM5EwmZxW5abNfr22Vq36whdOFJaWSjz1lKLyxBNKy/e/b0/NzGxieua/OBKJjrrpSdHe0mi6nQ61Z2CEsM/Lw7dvpbnaT24xztLYBEMTMyQLRVxmmZGJGU7PJijWNdDVsozbA048LgcIFcPQyRWKFA0DqdlojlTRXuUnmUozNB1FVeC+DSv4yJ5baW5fTsnuwZRgSomiqNhsGjabQklKThYtzlwbJHnpMnUqzOfyPPv2ZS5cuU5jZonbWmt44t472LJpA7+42MuLx87ijYRFa1en6fS41XJVKKDHYuHyrl1Xwm+8MZ8/f17X2LvXMKWsVYLBHdbXvq4Fl7dy15e+yO0Bp9L/wiF+eOhlpuZjqHY72zauRxaLuBTJS1dGOd0/xsx8DJnLMa1LmF/k8vAYvWaaNZEwKc2FaRg4NRWv2wXZHAUJuj9MXVMLq5pnmV1K4YvU4GpoQTjd2EwLl8tJXjdIJFJomkpQWAyms/RMxIkOjyJzJX5wcRSrf4ZEtkhAE6xqquHereu4/ZYN5B0+BiZmWIwv8dGP7Gbrxz+qXkxk+fnf/yPT8VTAPPhfHzNgiscf731vMeSSitZIIuF2D+u0zk2xzAzgrA1i27uNvCU4eXWQvRtWcdvObXjtGrGy5Mc9IwzFkr9cXrxzjl+MDbPgsxP2+rDsLoJuB9tWLueBHZsJe5woSEzVwu7xEolEkJodfyCAsDkRmg2HDTLFEj99+zynrw6QzJcQps5iLselZA7m4yANYgDpPKqA3ava+MRdt7Jz2y0khINTPf34NIWP3LaRXW0NNJWyxKPTOPt6LTzBID7feglVldWglKIIOaFq/fLWHQuFhZnQ4AsvKnmXDVfAw7Kgl4lEhiuDI6xrb6a1oZ3mFV3suy2NM1jFQqHMUr5EIp1BKRQwigWm83misSTZXI6cIZmcmqOzthpfVwd+jxOtVEIIgc3hxO01cdhsIC2EomAaJpNTs/z4yGlO9w7iFODzeTAtaNUU1GofpsNBOBigxuui2uNgZ1crGzZvorqlnUvDU/RcH8SGxbJwiNGBYYav9DI8FyW3bJnC6g1R7PaLOiSRUmh8+9ta/MknY7gdh7U//dQt8ePHGl5//nl/OJNSfNVB6cASNUEvuzato8HnYjqZ5XQsTfu6dey/azd6SWeibBDPl3AmllAKBVKWRVDo9PT18/dvvkM2m2V2Zo6m6hA2NYxuWRiWRVnXKZTKFHUT3bIolsssxBOMjk8yG0ugAZ+9Zws7Nq6jYPMQ1DSKikLK5WFZyEen341NURjK5OkuSwqLacJ2lZXVXg4PDXGsd5iSJaWVy4u0qpL9/Bdg/wNnKBS+noNJLlzQNEIhQWXNP6VIOVi+cjWVzOb9yUxe1ISqrE6vS+zauI6Hd27BKQSH+4Y5El3iwPoVNK7rAkugXB8kVihQ2riB+oCfmokxlOkxVAucDgdKfS2l1ka8dklNLsG8brIQi9M3MU0qV+SW1mV4ShmCVp6CXeJoXoa3vgZfNo3TptEQ8kNDK0ZLGyNLCYrjkzRWBWld1wWmyUDPAMevDTE1OceDyxt4YNc2NJuDxLFzXIjGSWfzAs0Ore2ILVtmpBCDAAwOOrT37QM65ey0n3RKEYZOdVsLW+7ezYMhN3cub8IXCHB5cIy3J6JMBkLEdRMrGkdakpOnzvLc+R6yt++mra0Z/7vvkurv50L/CKNLGeo7nExqdsbicYzkEkMFg3N9Q/SMTSMl9I5OcOFKgDqHRiIcIe4OgtdNIl/if52/znC6jGf5HKlNZQamZ1HOn0dsXcvKcBApBIlSiZlimfnxcaqKee65bQv7d27BVV3Fj6fjHP/xyzKayQq5uIiSTAZNKT1AnqEhbqbCgKrABkKhekolOjesNfZ99IC2eXqUwctXODs2xWIswVzdMpyt7UhNIxONoutl5pYWGRwZJzodZ8DjQVuI4nS5SLs8QJq5gWFefjbF2047olAkk0wxn84ib+zMHeufYGAujs/rRfF5yEnJ6MQcALMlg+Njc5Sm4pjnr5LJ5vAYOrHmalLjw1gON2WnG3tjA7P9g7z4+lG6B0e4fU0nDau6uGvDZrEwOq5Hj71tQ9dRpqfrzfl5ha4uOH1aaDQ0/LLS4vZnhd2ek6rqLRSKpIpFFhH0zMzx1ulzOApFRLgGuayBgsNkfrCXC1OzHOkfY2opiywuUrrRWGTrZlprQpSFyexUlIlUiolAALdNRSaWUBC4bSqWlOjFIuOlIjbdJLuYhkQKBxYr6qrwr13FbK5MvKcX8pMApGx2jlwdohmDW9saMLbsItXRiX7mHKN9g/SOTaApgp0dncyUdJkt60JaEqHrRez2BH6/hRCSV1+VGun0exuEhgz6z4lcbg0u15qr75zXiv/ksaKdrYql2PHY7YhkkqlkmoVkjo3mEq7z3bx4eYTjGQPp9YOeANPA1dxIw7pVbGsK0+A0edOucbqscntbHXfXetFTaYbmFumLLlEoGXRFAqxvrcdeHeJoosip8RjLM3Hu37gC7d59XJpbIrsQIz0yXqkIOewcG5hCn5/Dvqmd4UgzPf5mgsUCfgGaw0ZJVTk/MsmPxs/JifM9mlBVFJuWsjo6hlGUyt5nc7PUGB2t7AeOjyum3V4lLSuIEMJMJGX/idNEp+fxFAs4UjkCNhv5sTEyz/2Qn1kFuqdHiSdybLx1M6GuLq4eP8v8xDSuQIA1LU3s7GrBZROciGaxFS023Lmbj25fizozzekLV3BeGSBbKHLnupXsv30rtmXL0C8P0lM4je4QBDtX0raqi3Joid7mS2QnZ6gJh9i4eTVLUzNMXBvimTO9RGfLzDoDlGMzaA47lhCcHZ0hMZNgbHxSkM2YwudTZSDgkPF4DTU1FbefnBQauVzli9OpinR6g3S7m0ilaAAr4NbEfHSW+VQGLVNg0a7hmJsnPDpFFMjaFPavaOLW/buJNrYxcrkXa1hHX1wiPzxGIeTDE67HUVuH3j/GfCJLSvPQ3tpB9XwC18gMhqJS1dBAVXM7cxbEoktYyST+SASttp6FmQUWRqcopTNYuo7b72XTru0sS8XpFgYvD82Rv9xLBChqChM2DVu+jJiZxeGw00VZLAmshVJJlS5PUEmnV8j3ygEul/hlFKirk6rdrhuKCpZlNtjgtpWNCqbBYMzGJSGYXUpS73Wxa1Ud8+k8oaCPT9y/G6uzk1NTS8SzBQBy81GOvvom+sI8B+7ZRXt9BO3dy7zx3Assm53mob23MbSYom96nnShxMr5Rd7tHeCVsxd58c0TSCHYtX45DXaFfz5+mjPvXiYzNgZA3FK4btq5ddUa1loWrtBlkskkLgRHxxaYyBSw2WzsDrnZ1liNgeBkLC4WymWLQlFRfb60VVMjf1kXKJff2yvXNSFeKhtmI/fdt33x+hX0bME4sOdWNZorCvHGKZRMkkKpxHBepzYY4IHt67nnzl28mSrSfewMqcUkiteLZVmkUllO9w0T8vtY5rJzV0MVvxgp8krvIAEMZqMLjMzMkS+b9Fy8TDG+wC/mkhT8fnYHXERKBXov93L52giJ6VkwLRS/n3Qyw/mjp3ni0b3cf+stpEyLNy5fZ2g+Tr5UxGuZNHi9fGj3Dm5prZM/OfmutRSu1mhoh8TiFaVUehmo1Dp8PlPjyScNPvUpEEL/z/DCX33zm05z//6ukUze+4vrV6wdez1quK2RTRvitDTXc3F0mgvjc5TDIUp2FwM6XOrpY+r0WSQK2oYNyOpqiMfJLixwcWSShmVB9rTU0ResoSRBM4p4Snn8Ng27UPBYBqomUDqWs7ytje1mlkwiwZmlWfKGhVizGrxeVCmxeq8zc+Qol+r9LA/dwbypcHV6iSuTs7SGgyyvraYmUkPDqtXM6ibHB+eswWVtirjrzpxEPmf/0pcOlZ5/vgzAyy+bKk8/Xan/nTghT4B0PPNMzEqnpRweqk1HFyLD8zFlwe01G+/aq+y4ezdd4SDOWJT5uQX6cgYXcyXOXbjC1OAIoq4e5ZGHYf9+RLmMe36WTS21dATcxKJxTk9GaW9u5jMP3EVtKEh0MUHI6+bR/few7a69vD0+y3D3JRr1PC6/h4Tbx5TmoLx6LezdA+3tyFgcJsZJWSZXy5ILl/tITE6wrr6K//CB/dz5oQ9C50re7h+xfvzKL5Se0UlRXrM2Jh55+E3b7bu+X3jyyfGbdJ5Pf9rSbtbPn34arl2za4ZRMMPh8+oTH95bXtGpXPrBDxg+fkbm6+opqzbs/hCeFZ3kZuL0XRvkwmIKLZ8DhwNZE8ZwuZCFAsTiWKkkphFiLK3TPzxBdiJGyunk4uo2sokc6ZJBtlDgeixBYmyapb4BUv1DXK710263k9ck5cUkViqNqmlIRYFIGMXn49p0lKvZM4jYIvUOhfb2NlK1yxixVHqmY7xy7IwVG51QePBBRbv/voy1fkOP2t6e1o8d09i713iPaVIpG1dIBgB221//9Rpr584PWitWfEj29nbwX/5PxMULpt3lUrXqKmhsxHK70YeGMScnkUKAokAggFi5AmrrIJ1G9vahJZeI1EYI2VWKsRizqRwlKXDYbQhANwwsy0Kz2VAUlbJeRrMswj4XnkiEnG4Sm41i1tbChg1Ijwc5Pw/Dw7C0BIYBUiKWLUNbuQJN0xAzMxgTk5TzeZO1a1UOHkRs2TJNNPozee3aD/jDP7wIlBGCymoQ3k9BNXVdb6G7+zHOnq0X164ZYm5WtUxTKWWzlLJZmJj8daaaaeKQkvLYOPJ6P6JYxKEbuFwuhCVIF000t5+WqlpKhslcLE4xX2HdhSI1OBxO8tksmqKQzeeZTReo8xoE/H5ytiVSMzOVyk4wiHC7kIYBpdLNUcj4IroYQU8kIJu+yX1QFxakdeiQKaenqwkE9lEsHrnJOa7IjAZIDh1SARMwaW9XxPx8u/zZz5zy7NmyBNVfXS1CPh8Omw1ZLmPpOsJuQ3U4sdntpJIJSvkCDVVV1NXX4w0ECISChIIh3G43Q4ODTE5Ns279OhobGhgcGOCtt94iFovR2drCPffcg91h561fHOHa1Wu0t7exfft22tramItG6b12jeH+fmZnZiilUuD3IzZuBKcTMTsLMzOIqQlURUBNDZbTiVUqCXNuTvLCCxazsy4+9rE6WltNoJIFHjqkAGbFAiKRm+wJ5+OPx43z50eNt99eDahVTqfYt3+/fPDee8Wy+nr0chlFgD8Ywma3Mz8/z3PPPce1q1f5xCc/yaOPPIIE3B4PVdXVSEvyv/75nzn8ymEefughtm3bxqFDh3j3/Hnm5ueRUrJn717WrV1LLBYnEAjwF3/xF6zq6iIUCmGaJslkknffeYcvfelLXL5yBWw21E9+EuPee6G7G555Bnn+PHJ5B3zsY9DSjDx5yuLZZxVM04bDYdDaeoWdO6M3rfaGzNqv8msVmy2ltbdPGorS5XY41Lv27eOP/uiPuOuOO5BSks5mCQUCNx95/fXXyWQyNLW0sPfuu2lua+PCxYuMXbyI0+HA4XRy9WoPmVQKn89HVVUVdru9UreXklK5jNfrpbaujpaWFsLhMLffdhvZbIZXX32VUqnEtm3b2LR1Ky2dnVy+ehWKReTwMNx/PzzxBExOwvg4srkZ7r4bNmyA6ZkKi0xRBFVVUFOTxe0uc/CgcpPW92sKePppS/7lX9rN69c9LCzgMgzZ0dEhbKrK+fPnSaVSeDwe1q1bh8vloqenh2984xtcunSJRx55hOqqKsbGxvjaM89w6tQpNE3D6XQyPT1NbW0t8XicmZkZ5ufnKRQqWWO5XGZpaQnDMLDZbPj9fkzT5MqVq3znO99hZGSEXbt2sWrVKpJLSxUecDaL9c1vQjIJ/+N/wN69MDAAwSB4vRVQXlwUlMsAJoqiEY22MjXle7/wv1RALHYzJJS///1aa2mpA9MUBSmNEydPaie7u0U2lWLVqlV84AMfoKmpiQsXLvC9732PkydP4vf7aWpqwmazMTo6yuzsLE6nk1AoRDwev6k4v99PKBS6gUHWDfw00TQNTdPIZrPk83lUVWX9+vV88pOf5PTp01y5coUjR44wPTPDDfSGchneegueew727YM//3PIZMDphKlJiMffw0iTYlFlbKyGeNx3U/IbMmuAwuOPWwjB5ulp96Uvf7lDLi7WKum0yFuWPNPdDYDb7Wb79u243W56enp4/fXXOXz4MJlMhuXLlxMKhUgmk6iqysMPP0xTUxPFYpFvfetbjI6OEgqFqK6uxul0UiqVMAwDRVEwTZNEIkEsFsM0TXp7ezl06BD79u3joYceYvPmzbzwwgtkMhnm5+dRFKWiPFWF+Xl49llwOOFPPgU2GwwNwfETFYt47xoeBqfTo9TUtIZiMd9iOJx97zSLcvMggmWpvaXSFuFwbObKFUuZmkIIoQC0L1/O5z73OT760Y+iKAovv/wyr776KslkZUu8qqqKYDBIIpHAsix27tzJY489xpo1a0ilUliWxbJly3C5XGSzWXK5HLpeScdVVWVhYYHJyUm8Xi8zMzN85Stf4fnnn2dhYYFyucz+/fs5ePAgH/zgB6mJRCrhz7JQLAv6+uDNN+DatYqwNhuMjUE0WrEWIRSuX4ejRxXFMHYWYStQIVju2aNoHDig3KCh20su12PKmjW7tR/8QDHSaRNQN2zcKB599FF27thBLBbj8OHDvPTSS6RSqZsKDgQC1NXVoes6x44do7u7m9raWtLpNIODgzctSFEUVFXF6XSSyWSwLAshBOFwmNraWrxeLy6Xi/n5ef7hH/6Bn/zkJ7S1tfHAAw+wZs0a7rvvPubn53nrrbcwTLNCXbcsZLkMuWzFBXxe2LwJ3n4bJiYEoKLrFktLCk1NdxhSTgJvI6VFb6+iYbdXkqBvfcsutm7dYknZLLNZHDab3tzZqT744IPcc/fd6LrO2bNnOXv2LJZlEYlE0HWdXC6Hy+WiqqoKwzCYnZ3lzTffpFAoUFdXR1tbG7FYjMXFxZvusmbNGjZu3Mj4+Di33HILW7dupbGxkXg8TiQS4b777uPkyZOcOnWKubk5Wlpa6OjoYOfOnYyNjXHs2DEMw0CoKvh80NYCpg49lysWsKIT9t0DCwswOirQdQubTbUcjkZrbGwDZ844ePTRMq++KjR++MPKcvjUqYiaTmv6xYtQKrFxzRrx6Cc+wca1a3G73SwsLGCz2di8eTN79uzB7XYzMjLClStXcLvdlZRW07j11lupra0lm80SDoepqqrixRdfpLe3l76+PjZu3Mj69ev54z/+Y1KpFK2trTQ2NhKNRjl37hyWZfHEE0/w4Q9/mNdee41UKkVnZyf19fVEIhGWd3SgqDf40k4XtLdDXR3Mz8LV65BIwsb1cMsm0FT47vdgeFii61jXrkGpFODatXogw7lzpsqJE1RL6TXm5u6w3nxzn+3q1XBrVZV47OGH5UOPPaYsq69Hs9lwulxUh8PcvmsXu/fsQQrB5NQUbo+HW7ZuZWVXF6qm4fX7Wb12LV2rV7O8s5Oq6mqu9vVxvrtbFstlHE4nTpeLpuZmmltb8QUCzEWjvPnWW7z4ox8hheD2O+6grb1dBKuqqG9ooKa2FqfbTXRhgVNnznDi5MmKC4QjWI8fgI9/DMJhOHocXnsdpqZh/Tq4cw9Uh2FpSRKLKSQSknw+x5YtQ7z11iR795Y0wDJguWxufshcWGjwLy4qm++6i9auLpFOJEjE45imidPhwG23E/R6MYpF+np66OvpoaGhAT2f5+rFixiGQT6XQ7PZsEwTXddZWlpibmICs1wWh3/2Mxbn59mzZw9tbW2VHd5UioGBAS5cuMDs1BTFTIb/+6tfpaOjA6/XS8Dvx+fzcalcZnh4mOOnTqHn82BZWIaO9HnB7YFMrjL7ExOVV0szNDbAbTthfl4wMQFDQ4Kqqno6O+8H+oAeDSlFPpVaYdrt+7DZPGo2mzfKZdv1wUF5tadHRGdmZD6TQQNZLBQwTZNiscjE8LCMptNEr11j7Nw57HY7lmVhvQ+cLMsShXJZJIpFcYOYLbrPnRNTV64Iv9+PAErlMslkkqSsLEeTyaR8/Uc/kl5VtVx2u3TabJaqaeiGQSqTISEl721hWdEofO1r8JOXBKVSJQS+R/z8+csVDOjogHwBamsF0aiO3e6hqupe4KcVBQghzR/+sEbG4zUkkxR13Xa9v5+RaJR0KkU8naaoKFg2G1Y+D9lsJbxUV0NbGzkpmS+XwbIqv2sV+iuq+sukRVVRVBVVCPRSielstpLISAkuF9TWgtMpFE3DsiyRNk3SUqooCjdYoTdKN+p76W2lkKHrEItBf3/lnmCw0pZlQToNb5+BnqsQCVe4gmAjHoerV2uIRhsBVavats2ffOcdH/E4pFLkQA7GYoJCAalpyHC4AjLhcEU4ISrpZnU1VFWBx/PeyY3KwJzOym9OZ2Uqcjmp6npO6HreNM0SUpaxrDJSWu+d8BKgIoQmFUVVQFOEcFqa5rVcLjdeb6XPUgmKxcrrPeXpeiUdTqUqITCXq9yXz1cUkExW3hOJyudKBgivvYaoqws7/vIvG7Xs5z63TxSLdSwu9ovq6iU5OTkl8/kCllXGbtex2wuEwyUCgbKmaSXFZiupwaCuBwLSikQsAgFTdbksRdMkNpvE6ayEJo8HYbNZarlsUCrperGoC8Mw7U6nqdntJpomUVWpGQaGaSpGuayUTVMoQihOITTpdNrQNLvpdKqKZSlmLoeVz2MmkxVLLJUUSiWNYFAlkxGkUiixmEIm47R8Pg/BoJ1wWCOXc1AoOAG38Plc1NfXEQ4HlOrqgBkO79Ck37+elpYAVVUzit0+bDfNK2ahsEA+n7MZRqE8P58SMzNZdWgo53711cziwEDuVw8y/y6nmk2g/G/8n/19D6wDDeCa/vznw6xa5aGmxkFtrQ+n04fHUyV8vohU1ZXk803EYna5sND+/wIljj28U9Co5AAAAABJRU5ErkJggg==",
    "funpay": "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",
    "eldorado": "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",
}


_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="112" fill="#0B0C0E"/>
  <path d="M256 96L440 416H72L256 96z" fill="#EDEEF0"/>
</svg>"""

_ICONS_B64 = {
    "favicon.ico": ("image/x-icon", "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"),
    "favicon-32.png": ("image/png", "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAeklEQVR42u2XyxGAMAgFybvq2H99NKIdaD6QPQgNsDsQIO04r9vAkMFRAAWwDODuHMBq8rASrICItA9twlkgkfbhz3AGTKR9yiAaBRRpnzaKR0BF2qcuo15gkfbp67gHXKT9loPkS0Ck/baT7E1EpL2ZWaufUQH8HuABJEk3f3JzN04AAAAASUVORK5CYII="),
    "apple-touch-icon.png": ("image/png", "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"),
    "icon-192.png": ("image/png", "iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAYAAABS3GwHAAACO0lEQVR42u3WsRGEMBAEQYQrivzjUyIiBgwMarpDeG5WP+Z17wOiTj8BAgABgABAACAAEAAIAAQAAgABgABAACAAEAAIAAQAAgABgABAACAAEAAIAAQAAgABgABAACAAEAAIAAQAAgABgABAACAAEAAIAAQAAvihtZYfQQCOHwEIAQE4egQgCATg2BGAMBCAI0cAAkEAjhsBCAUBOGoEIBgE4JgRgHAQgCNGAAJCAI4XAQgJAThaBCAoBOBYEYCwEIAjRQACQwCOUwAITQA4SgEgOAHgGAWA8ASAIxQAAhQAjk8ACFEAODoBIEgBODYEgDAF4MgQAAIVgONCAAhVAI4KASBYATgmBIBwBeCIEAACFoDjQQAIWQCOBgEgaAE4FgSAsAXgSBAAAheA40AACF0AjgIBIHgBOAYEgPAF4AgQAAZAAD4+AsAQCMBHRwAYBAH42AgAwyAAHxkBYCAEYP3xAmAoigFYf7wAGIxiANYfLwCGoxiA9ccLgAEpBmD98QJgSIoBWH+8ABiUYgDWHy8AhqUYgPXHC4CBKQZg/fECYGiKAVh/vAAYnGIA1h8vAIanGID1xwuAASoGYP3xAmCIigFYf7wAGKRiANYfLwCGqRiA9ccLgIEqBmD98QJgqIoBWH++MOZ1bz8D/gKBAEAAIAAQAAgABAACAAGAAEAAIAAQAAgABAACAAGAAEAAIAAQAAgABAACAAGAAEAAIAAQAAgABAACAAGAAEAAIAAQAAgABAACAAHACw8JlCHeazi3LAAAAABJRU5ErkJggg=="),
    "icon-512.png": ("image/png", "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"),
}
_icons_cache = {}


def _icon_bytes(name):
    """Декодує PNG/ICO з base64 один раз."""
    if name not in _icons_cache:
        ct, b64 = _ICONS_B64[name]
        _icons_cache[name] = (ct, base64.b64decode(b64))
    return _icons_cache[name]


_SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com data:; "
        "img-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    ),
}


def _log_error(where, exc):
    print(f"  ⚠ {where}: {type(exc).__name__}: {exc}", flush=True)


class Handler(http.server.BaseHTTPRequestHandler):
    html_bytes = b""

    # Ліміт тіла запиту та таймаут з'єднання (захист від «важких» POST і slowloris)
    MAX_BODY = 20 * 1024 * 1024
    timeout = 60

    _auth_fails = {}          # {ip: [кількість, до_коли_блокувати]}
    _auth_lock = threading.Lock()

    def _cookie(self, name):
        raw = self.headers.get("Cookie") or ""
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k.strip() == name:
                return v.strip()
        return ""

    def _is_https(self):
        if _SCHEME == "https":
            return True
        return (self.headers.get("X-Forwarded-Proto") or "").strip().lower() == "https"

    def _csrf_token_ok(self, token):
        """Чи підписаний токен поточним ключем (пароль/секрет процесу)."""
        token = str(token or "")
        raw, _, sig = token.partition(".")
        if not raw or not sig:
            return False
        want = hmac.new(_csrf_key(), raw.encode("utf-8"), "sha256").hexdigest()[:16]
        return hmac.compare_digest(sig, want)

    def _csrf_check(self):
        """Подвійна відправка токена: cookie + X-GT-CSRF, підпис HMAC на паролі.

        Працює за будь-яким доменом/проксі (на відміну від allowlist Host, який
        ламав усі POST на Vultr за доменом). Підпис не дає підробити cookie.
        """
        cookie = self._cookie("gt_csrf")
        header = (self.headers.get("X-GT-CSRF") or "").strip()
        if not cookie or not header:
            return False
        if not hmac.compare_digest(cookie.encode("utf-8"), header.encode("utf-8")):
            return False
        return self._csrf_token_ok(cookie)

    def _origin_ok(self):
        """CSRF-захист: мутація з браузера мусить нести токен із cookie.

        Запити без Origin (curl, скрипти, старі клієнти з Basic-auth) лишаються
        дозволеними — вони не підпадають під CSRF.
        """
        origin = (self.headers.get("Origin") or "").strip()
        if not origin:
            return True
        if not self._csrf_check():
            return False
        try:
            netloc = urllib.parse.urlsplit(origin).netloc.lower()
        except Exception:
            return False
        host = (self.headers.get("Host") or "").strip().lower()
        return bool(host) and netloc == host

    def _device_token(self):
        """Підписаний токен пристрою (щоб не вводити пароль щоразу)."""
        ts = str(int(time.time()))
        sig = hmac.new(_csrf_key(), ("v1|" + ts).encode("utf-8"), "sha256").hexdigest()[:24]
        return ts + "." + sig

    def _device_ok(self):
        c = (self._cookie("gt_device") or "").strip()
        if not c or "." not in c:
            return False
        ts, _, sig = c.partition(".")
        if not ts.isdigit():
            return False
        try:
            age = time.time() - int(ts)
        except Exception:
            return False
        if age < 0 or age > 365 * 86400:
            return False
        want = hmac.new(_csrf_key(), ("v1|" + ts).encode("utf-8"), "sha256").hexdigest()[:24]
        return hmac.compare_digest(sig, want)

    def _auth_ok(self):
        """Basic-auth: без пароля дашборд не віддається навіть у локальній мережі."""
        if not AUTH_PASS:
            return False          # порожній пароль = застосунок не працює (див. main)
        hdr = self.headers.get("Authorization", "")
        if not hdr.startswith("Basic "):
            return False
        try:
            raw = base64.b64decode(hdr[6:].strip(), validate=True)
            decoded = raw.decode("utf-8", "replace")
            user, _, pwd = decoded.partition(":")
            # compare_digest працює з bytes: str з не-ASCII кидав TypeError
            return (hmac.compare_digest(user.encode("utf-8"), AUTH_USER.encode("utf-8"))
                    and hmac.compare_digest(pwd.encode("utf-8"), AUTH_PASS.encode("utf-8")))
        except Exception:
            return False

    def _rate_limited(self):
        """Блокування IP після багатьох невдалих спроб Basic-auth.

        GT_AUTH_NO_LIMIT=1 — вимкнути (коли браузер надсилає старий пароль
        і людина не може достукатись).
        """
        if os.environ.get("GT_AUTH_NO_LIMIT") == "1":
            return False
        ip = self.client_address[0] if self.client_address else "?"
        now = time.time()
        with Handler._auth_lock:
            fails, until = Handler._auth_fails.get(ip, (0, 0.0))
            if until > now:
                return True
            if fails >= 20 and until <= now:
                Handler._auth_fails[ip] = (0, now + 120)
                return True
            return False

    def _note_auth_fail(self):
        ip = self.client_address[0] if self.client_address else "?"
        with Handler._auth_lock:
            fails, until = Handler._auth_fails.get(ip, (0, 0.0))
            Handler._auth_fails[ip] = (fails + 1, until if until > time.time() else 0.0)

    def _collector_ok(self):
        """Колектор на ПК автентифікується токеном, а не паролем/сесією."""
        try:
            tok = (os.environ.get("GT_COLLECTOR_TOKEN")
                   or (_read_json(SECRETS_FILE, {}) or {}).get("collector_token") or "")
            got = str(self.headers.get("X-GT-TOKEN") or "")
            return bool(tok) and bool(got) and hmac.compare_digest(got, tok)
        except Exception:
            return False

    def _basic_ok_quiet(self):
        """Чи прийшли валідні Basic-дані (без відправки 401)."""
        if AUTH_MODE == "off":
            return False
        if self._device_ok():
            return True
        return self._auth_ok()

    def _require_auth(self):
        if (self.path in ("/manifest.json", "/favicon.ico", "/favicon-32.png",
                          "/apple-touch-icon.png", "/sw.js",
                          "/icon.svg", "/icon.png")
                or self.path.split("?")[0].lstrip("/") in _ICONS_B64
                or self.path.split("?")[0] in ("/icon.svg", "/icon.png")
                or self.path.startswith("/logo/") or self.path == "/demo"
                or self.path.startswith("/docs/")):
            return True      # публічні статичні файли
        if (self.path.startswith("/api/taobao")
                or self.path.startswith("/api/secrets/")) and self._collector_ok():
            return True
        if AUTH_MODE != "off" and self._device_ok():
            return True          # вже входили з цього пристрою
        # Режим «за Cloudflare Access»: пароль не питаємо, але (за бажанням)
        # вимагаємо заголовок, який Cloudflare додає лише після входу в Access.
        if AUTH_MODE == "off":
            if REQUIRE_ACCESS:
                email = (self.headers.get("Cf-Access-Authenticated-User-Email") or "").strip()
                if not email:
                    self._send(403, "text/plain",
                               b"403 Forbidden - only via Cloudflare Access")
                    return False
            email = (self.headers.get("Cf-Access-Authenticated-User-Email") or "").strip()
            if email and email not in _access_seen:
                _access_seen.add(email)
                print(f"  🌐 Cloudflare Access: login {email}", flush=True)
            return True
        if self._rate_limited():
            ip = self.client_address[0] if self.client_address else "?"
            with Handler._auth_lock:
                until = Handler._auth_fails.get(ip, (0, 0.0))[1]
            left = max(1, int(until - time.time()))
            self._send(429, "text/plain",
                       ("429 Too Many Requests — забагато спроб пароля. "
                        "Спробуйте через %d с." % left).encode("utf-8"))
            return False
        if self._auth_ok():
            self._device_cookie = True       # запам'ятати пристрій
            ip = self.client_address[0] if self.client_address else "?"
            with Handler._auth_lock:
                Handler._auth_fails.pop(ip, None)   # успішний вхід скидає лічильник
            return True
        # рахуємо ЛИШЕ реальні спроби з паролем (браузерний запит пароля — ні)
        auth_hdr = (self.headers.get("Authorization") or "").strip()
        if auth_hdr:
            self._note_auth_fail()
            try:
                import base64 as _b64
                _u = _b64.b64decode(auth_hdr[6:] or "").decode("utf-8", "replace").split(":")[0]
                print(f"  🔐 failed login: user «{_u[:32]}» · IP {self.client_address[0]}",
                      flush=True)
            except Exception:
                pass
        self._send(401, "text/plain", b"401 Unauthorized",
                   extra={"WWW-Authenticate": 'Basic realm="Game Tracker"'})
        return False

    def do_GET(self):
        try:
            self._route_get()
        except Exception as e:
            _log_error("GET " + self.path, e)
            try:
                self._json({"ok": False, "error": f"{type(e).__name__}: {e}"}, code=500)
            except Exception:
                pass

    def _route_get(self):
        p = self.path.split("?")[0]
        # health — без пароля: для uptime-моніторингу (жодних даних не віддає)
        if p == "/api/health":
            self._json({"ok": True, "version": "1.1.1", "uptime": int(time.time() - _START_TS)})
            return
        if (p in ("/manifest.json", "/favicon.ico", "/favicon-32.png",
                  "/apple-touch-icon.png", "/sw.js", "/icon.svg", "/icon.png")
                or p.split("?")[0].lstrip("/") in _ICONS_B64
                or p.startswith("/logo/")):
            pass  # публічні статичні файли (без них PWA/іконки ламаються)
        elif (AUTH_MODE != "off"
                and (p.startswith("/api/taobao") or p.startswith("/api/secrets/"))
                and "X-GT-TOKEN" in self.headers and self._collector_ok()):
            pass  # колектор з валідним токеном
        elif AUTH_MODE != "off" and not self._device_ok() and not self._basic_ok_quiet():
            if p == "/login":
                self._send(200, "text/html", LOGIN_HTML.encode("utf-8"))
                return
            if not p.startswith("/api/"):
                self._send(200, "text/html", LOGIN_HTML.encode("utf-8"))
                return
            # API без входу → 401 (JS на сторінці входу його не викликає)
            self._send(401, "application/json", b'{"ok":false,"error":"auth required"}')
            return
        if not self._require_auth():
            return
        if p == "/":
            token = self._cookie("gt_csrf")
            if not token or not self._csrf_token_ok(token):
                token = _csrf_token()
            cookie = f"gt_csrf={token}; Path=/; SameSite=Strict"
            if self._is_https():
                cookie += "; Secure"
            self._send(200, "text/html", Handler.html_bytes, extra={"Set-Cookie": cookie})
        elif p == "/manifest.json":
            manifest = {
                "name": "Game Account Tracker",
                "short_name": "GameTracker",
                "description": "Облік продажів, закупівля акаунтів, сповіщення з пошти",
                "start_url": "/",
                "scope": "/",
                "display": "standalone",
                "background_color": "#0d1017",
                "theme_color": "#0d1017",
                "icons": [
                    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                    {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml"},
                ],
            }
            self._send(200, "application/json", json.dumps(manifest))
        elif p == "/sw.js":
            sw = """
self.addEventListener('install', e => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
// без кешу: локальний трекер має завжди віддавати свіжий UI
self.addEventListener('fetch', e => {});
self.addEventListener('push', e => {
  const d = e.data ? e.data.json() : {};
  e.waitUntil(self.registration.showNotification(d.title||'GameTracker', {
    body: d.body||'', icon: '/icon.svg', badge: '/icon.svg', vibrate: [200,100,200]
  }));
});
self.addEventListener('notificationclick', e => { e.notification.close(); clients.openWindow('/'); });
"""
            self._send(200, "application/javascript", sw)
        elif p.split("?")[0].lstrip("/") in _ICONS_B64:
            _n = p.split("?")[0].lstrip("/")
            ct, data = _icon_bytes(_n)
            # короткий кеш: іконки оновлюються разом з релізом
            self._send(200, ct, data, extra={"Cache-Control": "public, max-age=300"})
        elif p == "/demo" or p.startswith("/docs/"):
            _f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs",
                              "DEMO.html" if p == "/demo" else p[len("/docs/"):])
            if not os.path.exists(_f):
                self._send(404, "text/plain", b"404")
            else:
                with open(_f, "rb") as _fh:
                    _data = _fh.read()
                _ct = "image/png" if _f.endswith(".png") else "text/html; charset=utf-8"
                self._send(200, _ct, _data)
        elif p.startswith("/logo/") and p.endswith(".png"):
            nm = p[6:-4]
            data = _LOGOS.get(nm)
            if not data:
                self._send(404, "text/plain", b"404")
            else:
                self._send(200, "image/png", __import__("base64").b64decode(data),
                           extra={"Cache-Control": "max-age=86400"})
        elif p in ("/icon.png", "/icon.svg"):
            self._send(200, "image/svg+xml", _ICON_SVG,
                       extra={"Cache-Control": "public, max-age=604800"})
        elif p == "/api/backup/run":
            # мутація через GET = CSRF без перевірки Origin → тільки POST
            self._json({"ok": False, "error": "use POST /api/backup/run"}, code=405)
        elif p == "/api/export/csv":
            what = "ed" if "what=ed" in self.path else "pl"
            rows = []
            if what == "pl":
                data = _read_json(PL_FILE, []) or []
                head = ["date", "title", "platform", "buy", "sell", "qty", "afterFee", "profit"]
                for r in (data if isinstance(data, list) else []):
                    try:
                        sell = float(r.get("sell") or 0)
                        buy = float(r.get("buy") or 0)
                        aft = r.get("afterFee")
                        exp = float(r.get("expenses") or 0)
                        pr = ((float(aft) if aft not in (None, "")
                               else round(sell * (1 - _fee_pct_of(r)) - buy, 2)) - exp)
                    except Exception:
                        sell = buy = 0
                        pr = 0
                    rows.append([r.get("date", ""), r.get("title", ""),
                                 r.get("srcName") or r.get("platform") or "",
                                 r.get("buy", 0), r.get("sell", 0), r.get("qty", 1),
                                 r.get("afterFee", 0), round(pr, 2)])
            else:
                data = _read_json(ED_FILE, []) or []
                head = ["date", "title", "price", "buy", "fee", "profit", "orderId"]
                for r in (data if isinstance(data, list) else []):
                    rows.append([r.get("date", ""), r.get("title", ""), r.get("price", 0),
                                 r.get("buy", 0), r.get("fee", 0), r.get("profit", 0),
                                 r.get("orderId", "")])
            buf = io.StringIO()
            w = csv.writer(buf, delimiter=";")
            w.writerow(head)
            w.writerows(rows)
            self._send(200, "text/csv",
                       ("\ufeff" + buf.getvalue()).encode("utf-8"),
                       extra={"Content-Disposition":
                              'attachment; filename="tracker_%s_%s.csv"'
                              % (what, datetime.date.today())})
        elif p == "/api/offers":
            now = time.time()
            if (_offers_cache["data"] is None or now - _offers_cache["ts"] > 300
                    or "refresh=1" in self.path):
                res = my_offers()
                if res.get("ok"):
                    idx = _taobao_sup_index()
                    for o in res.get("items") or []:
                        sup = _supplier_match(o.get("title"), o.get("game")) or {}
                        o["supplier"] = sup or None
                        if sup and o.get("price"):
                            base = sup.get("median") or sup.get("min") or 0
                            o["diff_usd"] = round(o["price"] - base, 2)
                            o["diff_x"] = round(o["price"] / base, 1) if base else None
                    res["supplier_games"] = len(idx)
                _offers_cache.update({"ts": now, "data": res})
            self._json(_offers_cache["data"] or {"ok": False, "error": "немає даних"})
        elif p == "/api/inventory":
            self._json(inventory_data())
        elif p == "/api/inventory/secret":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            iid = (qs.get("id") or [""])[0]
            _inv_load()
            it = next((x for x in _inventory if x.get("id") == iid), None)
            if not it:
                self._json({"ok": False, "error": "запис не знайдено"}, code=404)
                return
            self._json({"ok": True, "id": iid, "title": it.get("title"),
                        "game": it.get("game"), "account": it.get("account") or ""})
        elif p == "/api/inventory/match":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            self._json({"ok": True, "matches": _inv_match((qs.get("title") or [""])[0])})
        elif p == "/api/lots/export":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            data, n = _lots_csv((qs.get("markup") or ["30"])[0],
                                (qs.get("source") or ["inventory"])[0],
                                (qs.get("limit") or ["50"])[0],
                                (qs.get("game") or [""])[0])
            self._send(200, "text/csv", data.encode("utf-8"), extra={
                "Content-Disposition": 'attachment; filename="lots_%s.csv"'
                                       % (qs.get("source") or ["inventory"])[0]})
        elif p == "/api/buy-list":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            self._json(_buy_list((qs.get("limit") or ["20"])[0],
                                 int((qs.get("days") or ["90"])[0] or 90)))
        elif p == "/api/report":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            self._json(_month_report((qs.get("month") or [""])[0]))
        elif p == "/api/report/export":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            rep = _month_report((qs.get("month") or [""])[0])
            data = _report_csv(rep, (qs.get("lang") or ["uk"])[0]).encode("utf-8")
            self._send(200, "text/csv", data, extra={
                "Content-Disposition":
                'attachment; filename="report_%s.csv"' % rep.get("month")})
        elif p == "/api/analytics":
            self._json(_analytics())
        elif p == "/api/backup/export":
            try:
                data, _manifest = _build_backup_zip()
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500); return
            name = f"game_tracker_backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M')}.zip"
            self._send(200, "application/zip", data,
                       extra={"Content-Disposition": f'attachment; filename="{name}"'})
        elif p == "/api/backup/list":
            files = sorted(os.listdir(BACKUP_DIR), reverse=True) if os.path.exists(BACKUP_DIR) else []
            self._json({"ok": True, "files": files[:15]})
        elif p == "/api/pl":
            try:
                data = _read_json_strict(PL_FILE, [])
            except Exception as e:
                _log_error("read " + PL_FILE, e)
                _quarantine(PL_FILE)
                self._json({"ok": False,
                            "error": "Файл P&L пошкоджено — його збережено як .corrupt, "
                                     "дані не перезаписані. Відновіть з gt_backups.",
                            "purchases": [], "corrupt": True}, code=500)
                return
            if not isinstance(data, list):
                self._json({"ok": False, "error": "P&L має бути списком", "purchases": []},
                           code=500)
                return
            self._json({"ok": True, "purchases": data})
        elif p == "/api/eldorado":
            try:
                data = _read_json_strict(ED_FILE, [])
            except Exception as e:
                _log_error("read " + ED_FILE, e)
                _quarantine(ED_FILE)
                self._json({"ok": False, "sales": [], "corrupt": True,
                            "error": "Файл ELDORADO пошкоджено — збережено як .corrupt"}, code=500)
                return
            sales = data if isinstance(data, list) else []
            # нові — зверху (історичний імпорт ішов у зворотному порядку)
            sales = sorted(sales, key=lambda r: (str(r.get("date") or ""),
                                                 str(r.get("id") or "")), reverse=True)
            self._json({"ok": True, "sales": sales})
        elif p == "/api/settings":
            st = _read_json(SETTINGS_FILE, {}) or {}
            tg = _tg_cfg()
            rate = float(st.get("usd_uah") or 0)
            ts   = float(st.get("rate_ts") or 0)
            src  = st.get("rate_source") or ("cache" if rate else "none")
            cloud = _cloud_dir()
            g_user, g_pwd = _gmail_cfg()
            self._json({
                "ok": True,
                "taobao_min_cny": float(st.get("taobao_min_cny") or 5),
                "digest_hour": int(st.get("digest_hour") if st.get("digest_hour") is not None else 9),
                "deal_x": float(st.get("deal_x") or 5),
                "digest_last": str(st.get("digest_last") or ""),
                "alerts_only_my_games": bool(st.get("alerts_only_my_games", True)),
                "notify": {k: bool(st.get("notify_" + k, v))
                           for k, v in _TG_DEFAULTS.items()},
                "lang": str(st.get("lang") or "en")[:2],
                "onboarded": bool(st.get("onboarded")),
                "app_name": str(st.get("app_name") or "AccTrack")[:32],
                "zeusx_tier": str(st.get("zeusx_tier") or "iron")[:16],
                "fee_profiles": {
                    "funpay": round(float(st.get("fee_profiles", {}).get("funpay", PLATFORM_FEES["funpay"])), 6),
                    "eldorado": round(float(st.get("fee_profiles", {}).get("eldorado", PLATFORM_FEES["eldorado"])), 6),
                    "other": round(float(st.get("fee_profiles", {}).get("other", PLATFORM_FEES["other"])), 6),
                    "games": st.get("fee_profiles", {}).get("games", {}) or {},
                },
                "auth_enabled": AUTH_MODE != "off",
                "sup_hours": float(st.get("sup_hours") or _sup_hours()),
                "news_hours": float(st.get("news_hours") or 1),
                "scraper_limit": int(st.get("scraper_limit") or _scraper_state.get("limit") or 30),
                "usd_uah": rate,
                "currency": str((_read_json(SETTINGS_FILE, {}) or {}).get("currency") or "USD").upper()[:3],
                "rate_ts": ts,
                "rate_source": src,
                "cloud_dir": st.get("cloud_dir") or "",
                "cloud_effective": cloud,
                "cloud_exists": bool(cloud) and os.path.isdir(cloud),
                "auth": {"mode": AUTH_MODE, "access_required": REQUIRE_ACCESS,
                         "bind": BIND},
                "https": {
                    "enabled": bool(st.get("https_enabled")),
                    "cert": st.get("https_cert", ""),
                    "key": st.get("https_key", ""),
                    "active": bool(_https_opts()),
                },
                "tg": {
                    "configured": bool(tg.get("token") and tg.get("chat_id")),
                    "has_token": bool(tg.get("token")),
                    "chat_id": tg.get("chat_id", ""),
                    "enabled": bool(tg.get("enabled")),
                    "notify_mail": bool(tg.get("notify_mail", True)),
                    "notify_price": bool(tg.get("notify_price", True)),
                    "notify_new": bool(tg.get("notify_new", True)),
                },
                "gmail": {
                    "configured": bool(g_user and g_pwd),
                    "user": g_user,
                    "has_pass": bool(g_pwd),
                    "last_check": int(_gmail_state.get("last_check") or 0),
                    "last_ok": int(_gmail_state.get("last_ok") or 0),
                    "last_error": _gmail_state.get("last_error") or "",
                    "last_found": int(_gmail_state.get("last_found") or 0),
                    "last_sent": int(_gmail_state.get("last_sent") or 0),
                    "seen": len(_gmail_state.get("seen") or []),
                    "interval": GMAIL_CHECK_INTERVAL,
                },
            })
        elif p == "/api/gmail/status":
            g_user, g_pwd = _gmail_cfg()
            self._json({
                "ok": True,
                "configured": bool(g_user and g_pwd),
                "user": g_user,
                "has_pass": bool(g_pwd),
                "last_check": int(_gmail_state.get("last_check") or 0),
                "last_ok": int(_gmail_state.get("last_ok") or 0),
                "last_error": _gmail_state.get("last_error") or "",
                "last_found": int(_gmail_state.get("last_found") or 0),
                "last_sent": int(_gmail_state.get("last_sent") or 0),
                "seen": len(_gmail_state.get("seen") or []),
                "interval": GMAIL_CHECK_INTERVAL,
            })
        elif p == "/api/rate":
            rate, ts, src = _get_rate("refresh=1" in self.path)
            self._json({"ok": bool(rate), "usd_uah": rate, "rate_ts": ts, "source": src})
        elif p == "/api/suppliers/compare":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            self._json(_compare_products((qs.get("id") or [""])[0]))
        elif p == "/api/suppliers/history":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            pid = (qs.get("id") or [""])[0]
            pr = next((x for x in _supplier_cache if x.get("id") == pid), None)
            if not pr:
                self._json({"ok": False, "error": "товар не знайдено"}, code=404)
            else:
                self._json({"ok": True, "id": pid, "title": pr.get("title"),
                            "price": pr.get("price"), "sourceName": pr.get("sourceName"),
                            "url": pr.get("url"),
                            "history": ((_supplier_seen.get(pid) or {}).get("history") or [])})
        elif p == "/api/diag":
            _sec = _read_json(SECRETS_FILE, {}) or {}
            def fsize(path):
                try:
                    return os.path.getsize(path)
                except Exception:
                    return 0
            self._json({"ok": True, "version": "1.1.1",
                        "uptime": int(time.time() - _START_TS),
                        "counts": {"purchases": len(_read_json(PL_FILE, []) or []),
                                   "eldorado": len(_read_json(ED_FILE, []) or []),
                                   "inventory": len(_read_json(INVENTORY_FILE, []) or []),
                                   "suppliers": len(_supplier_cache),
                                   "suppliers_configured": len(SUPPLIERS)},
                        "files_kb": {"pl": round(fsize(PL_FILE) / 1024, 1),
                                     "ed": round(fsize(ED_FILE) / 1024, 1),
                                     "inv": round(fsize(INVENTORY_FILE) / 1024, 1),
                                     "settings": round(fsize(SETTINGS_FILE) / 1024, 1)},
                        "tokens": {"funpay": bool(_sec.get("funpay_cookie")),
                                   "zeusx": bool(_sec.get("zeusx_cookie")),
                                   "gmail": bool(_sec.get("gmail_user"))},
                        "lang": (_read_json(SETTINGS_FILE, {}) or {}).get("lang", "en"),
                        "theme": "—"})
        elif p == "/api/secrets/status":
            _s = _read_json(SECRETS_FILE, {}) or {}
            self._json({"ok": True,
                        "funpay_cookie": bool(_s.get("funpay_cookie")),
                        "zeusx_cookie": bool(_s.get("zeusx_cookie"))})
        elif p == "/api/mail/queue":
            _mailq_load()
            items = [x for x in _mail_queue if (x.get("kind") or "order") == "order"][-100:]
            out = []
            for x in items:
                y = dict(x)
                if str(y.get("game") or "") in ("", "Other"):
                    g = _game_of((y.get("subject") or "") + " " + (y.get("body") or ""))
                    if g and g != "Other":
                        y["game"] = g
                out.append(y)
            self._json({"ok": True, "items": out,
                        "new": sum(1 for x in out if x.get("status") == "new")})
        elif p == "/api/taobao":
            if "agent=1" in self.path:
                # колектор на ПК смикає цей endpoint — так бачимо, що він живий
                now_ts = time.time()
                if now_ts - int(_taobao.get("agent_seen") or 0) > 10:
                    _taobao["agent_seen"] = now_ts
                    _taobao_save()
            _td = taobao_data()
            _cr = _taobao.get("cookie_request") or {}
            if _cr and time.time() - int(_cr.get("ts") or 0) < 180:
                _td["cookie_request"] = _cr
            elif _cr:
                _taobao.pop("cookie_request", None)
                _taobao_save()
            self._json(_td)
        elif p == "/api/platforms":
            self._json({"ok": True, **platforms_data(force=("refresh=1" in self.path))})
        elif p == "/api/tunnel":
            self._json({"ok": True, "url": _tunnel_url(), "log": _tunnel_log_path()})
        elif p == "/api/suppliers/status":
            st = _sup_status()
            now = time.time()
            hrs = _sup_hours()
            self._json({"ok": True, "count": len(_supplier_cache),
                "suppliers": [{"key": _k, "name": _v["name"],
                  "color": _v.get("color", ""), "emoji": _v.get("emoji", ""),
                  "count": _supplier_counts().get(_k, 0)}
                for _k, _v in SUPPLIERS.items()],
                        "last_ok": st["ts"], "last_attempt": st["attempt"],
                        "next_in": max(0, int(st["attempt"] + hrs * 3600 - now)),
                        "hours": hrs, "busy": _refresh_lock.locked(),
                        "scraper": {"used": int(_scraper_state.get("used") or 0),
                                    "limit": int(_scraper_state.get("limit") or 30),
                                    "day": _scraper_state.get("day") or "",
                                    "keys": [dict({"tail": k[-6:]}, **_scraper_quota(k),
                                                  banned=int((_scraper_state.get("keys", {})
                                                              .get(k[-6:], {}) or {}).get("until") or 0))
                                             for k in _scraper_keys()]},
                        "blocked": [k for k in SUPPLIERS if _direct_blocked(k)],
                        "news": {"checked": int(_news_state.get("checked") or 0),
                                 "last_new": int(_news_state.get("last_new") or 0),
                                 "suppliers": len(_news_state.get("by_supplier") or {})}})
        elif p == "/api/suppliers":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1]) if "?" in self.path else {}
            def q1(k, d=""):
                v = (qs.get(k) or [d])[0]
                return v if isinstance(v, str) else d
            counts = _supplier_counts()
            if not _cmp_index and _supplier_cache:      # кеш із диска — індекс ще не збудовано
                try:
                    _build_compare_index()
                except Exception as e:
                    print(f"  ⚠ Compare index: {e}", flush=True)
            sale = sum(1 for x in _supplier_cache if x.get("isOnSale") and not x.get("gone"))
            gone_total = sum(1 for x in _supplier_cache if x.get("gone"))
            if not q1("page"):
                # legacy: повний список (для скриптів), тепер стиснутий gzip+ETag
                self._json({"products": _supplier_cache, "counts": counts,
                            "sale": sale, "gone": gone_total, "cheaper": len(_cheaper_map)})
                return
            try:
                page = max(1, int(q1("page", "1")))
                per = min(200, max(1, int(q1("per", "50"))))
            except ValueError:
                page, per = 1, 50
            q = q1("q").strip().lower()
            src = q1("src")
            only_avail = q1("avail") in ("1", "true", "on")
            show_gone = q1("gone") in ("1", "true", "on")
            only_cheaper = q1("cheaper") in ("1", "true", "on")
            items = [x for x in _supplier_cache
                     if (not src or x.get("source") == src)
                     and (bool(x.get("gone")) if show_gone else not x.get("gone"))
                     and (not only_avail or x.get("available"))
                     and (not only_cheaper or x.get("id") in _cheaper_map)
                     and (not q or q in (x.get("title") or "").lower())]
            items = _supplier_sort(items, q1("sort"))
            total = len(items)
            start = (page - 1) * per
            page_items = []
            for x in items[start:start + per]:
                y = dict(x)
                c = _cheaper_map.get(x.get("id"))
                if c:
                    y["cheaper"] = c
                page_items.append(y)
            self._json({"ok": True, "items": page_items, "total": total,
                        "page": page, "per": per, "counts": counts,
                        "sale": sale, "gone": gone_total,
                        "cheaper": len(_cheaper_map)})
        else:
            self._send(404, "text/plain", b"404")

    def do_POST(self):
        try:
            self._route_post()
        except Exception as e:
            _log_error("POST " + self.path, e)
            try:
                self._json({"ok": False, "error": f"{type(e).__name__}: {e}"}, code=500)
            except Exception:
                pass

    def _route_post(self):
        global AUTH_PASS
        # вхід/вихід — публічні (без пароля й без CSRF-токена)
        if self.path in ("/api/login", "/api/logout"):
            try:
                n = int(self.headers.get("Content-Length", 0) or 0)
            except Exception:
                n = 0
            raw = self.rfile.read(n) if 0 < n <= 64 * 1024 else b""
            try:
                body = json.loads(raw) if raw else {}
            except Exception:
                body = {}
            if self.path == "/api/logout":
                self._json({"ok": True}, extra={"Set-Cookie":
                           "gt_device=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"})
                return
            pw = str((body or {}).get("password") or "")
            if not (AUTH_PASS and hmac.compare_digest(pw.encode("utf-8"),
                                                      AUTH_PASS.encode("utf-8"))):
                self._note_auth_fail()
                print(f"  🔐 failed login (form) · IP {self.client_address[0]}", flush=True)
                self._json({"ok": False, "error": "Невірний пароль"}, code=401)
                return
            ip = self.client_address[0] if self.client_address else "?"
            with Handler._auth_lock:
                Handler._auth_fails.pop(ip, None)
            cookie = ("gt_device=" + self._device_token()
                      + "; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax")
            if self._is_https():
                cookie += "; Secure"
            self._json({"ok": True}, extra={"Set-Cookie": cookie})
            print(f"  🔑 device login · IP {ip}", flush=True)
            return
        if not self._require_auth():
            return
        if not self._origin_ok():
            self._json({"ok": False,
                        "error": "CSRF: онови сторінку (Ctrl+F5) — браузер не надіслав токен"},
                       code=403); return
        try:
            n = int(self.headers.get("Content-Length", 0) or 0)
        except Exception:
            n = 0
        body_limit = 60 * 1024 * 1024 if self.path == "/api/backup/import" else self.MAX_BODY
        if n < 0 or n > body_limit:
            self._json({"ok": False, "error": "request body too large"}, code=413); return
        raw_body = self.rfile.read(n) if n else b""
        if self.path == "/api/backup/import":
            try:
                self._json(_import_backup_zip(raw_body))
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            except Exception as e:
                self._json({"ok": False, "error": f"{type(e).__name__}: {e}"}, code=500)
            return
        try:
            body = json.loads(raw_body) if raw_body else {}
        except Exception as ex:
            self._json({"ok": False, "error": f"invalid JSON: {ex}"}, code=400); return
        if not isinstance(body, dict):
            self._json({"ok": False, "error": "JSON must be an object"}, code=400); return
        if self.path == "/api/auth/toggle":
            try:
                enabled = bool(body.get("enabled"))
                st = _read_json(SETTINGS_FILE, {}) or {}
                if enabled:
                    new = str(body.get("new") or "")
                    if len(new) < 8:
                        self._json({"ok": False, "error": "Пароль має бути мінімум 8 символів"}, code=400)
                        return
                    _save_secrets({"auth_pass": new})
                    globals()["AUTH_PASS"] = new
                    globals()["AUTH_MODE"] = "basic"
                else:
                    globals()["AUTH_MODE"] = "off"
                st["auth_enabled"] = enabled
                _atomic_dump(SETTINGS_FILE, st)
                self._json({"ok": True, "auth_enabled": enabled})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/auth/password":
            if AUTH_MODE == "off":
                self._json({"ok": False, "reason": "auth_off",
                            "error": "Пароль вимкнено (GT_AUTH=off) — доступ через Cloudflare Access"},
                           code=400)
                return
            old = str(body.get("old") or "")
            new = str(body.get("new") or "")
            if not hmac.compare_digest(old.encode("utf-8"), AUTH_PASS.encode("utf-8")):
                self._json({"ok": False, "error": "Невірний поточний пароль"}); return
            if len(new) < 8:
                self._json({"ok": False, "error": "Новий пароль має бути мінімум 8 символів"}); return
            if new == AUTH_PASS:
                self._json({"ok": False, "error": "Новий пароль збігається з поточним"}); return
            try:
                _save_secrets({"auth_pass": new})
                AUTH_PASS = new
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        if self.path == "/api/https/save":
            try:
                with _WRITE_LOCK:
                    st = _read_json(SETTINGS_FILE, {}) or {}
                    if "enabled" in body:
                        st["https_enabled"] = bool(body.get("enabled"))
                    if "cert" in body:
                        st["https_cert"] = str(body.get("cert") or "").strip()
                    if "key" in body:
                        st["https_key"] = str(body.get("key") or "").strip()
                    _atomic_dump(SETTINGS_FILE, st)
                self._json({"ok": True, "active": bool(_https_opts()), "restart": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        if self.path == "/api/https/generate":
            self._json(_https_gen())
            return
        if self.path == "/api/backup/restore":
            try:
                raw = str(body.get("file") or "")
                name = os.path.basename(raw)
                if not raw or name != raw:
                    raise ValueError("invalid file name")
                prefix_map = (
                    ("gt_pl_", PL_FILE, "pl"), ("gt_eldorado_", ED_FILE, "ed"),
                    ("gt_goal_", GOAL_FILE, "goal"),
                    ("snap_pl_", PL_FILE, "pl"), ("snap_ed_", ED_FILE, "ed"),
                    ("snap_settings_", SETTINGS_FILE, "settings"),
                    ("snap_inv_", INVENTORY_FILE, "inv"),
                    ("snap_mail_", MAIL_QUEUE_FILE, "mail"),
                )
                found = next(((t, k) for pref, t, k in prefix_map
                              if name.startswith(pref)), None)
                if not found:
                    raise ValueError("unknown backup type")
                target, kind = found
                src = os.path.join(BACKUP_DIR, name)
                if not os.path.isfile(src):
                    raise ValueError("backup not found")
                with open(src, encoding="utf-8") as f:
                    data = json.load(f)
                # страховка: копія поточного стану перед відновленням
                if os.path.exists(target):
                    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    pref = {"pl": "gt_pl", "ed": "gt_eldorado", "goal": "gt_goal",
                            "settings": "gt_settings", "inv": "gt_inventory",
                            "mail": "gt_mail"}.get(kind, "gt_backup")
                    shutil.copy2(target, os.path.join(BACKUP_DIR, f"{pref}_before_restore_{ts}.json"))
                if kind == "pl":
                    data = _clean_pl(data)
                elif kind == "ed":
                    data = _clean_ed(data)
                elif kind == "inv":
                    data = _inv_clean(data)
                elif kind in ("goal", "settings"):
                    if not isinstance(data, dict):
                        raise ValueError("backup must be an object")
                elif kind == "mail":
                    if not isinstance(data, list):
                        raise ValueError("mail backup must be a list")
                _atomic_write(target, json.dumps(data, ensure_ascii=False, indent=2))
                self._json({"ok": True, "file": name, "kind": kind,
                            "count": len(data) if isinstance(data, list) else None})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            return
        if self.path == "/api/backup/run":
            res = do_backup()
            files = sorted(os.listdir(BACKUP_DIR)) if os.path.exists(BACKUP_DIR) else []
            self._json({"ok": True, "files": files[-10:], "cloud": res.get("cloud")})
            return
        if self.path == "/api/settings/save":
            try:
                usd = body.get("usd_uah")
                cloud_dir = body.get("cloud_dir")
                with _WRITE_LOCK:
                    st = _read_json(SETTINGS_FILE, {}) or {}
                    if "sup_hours" in body:
                        st["sup_hours"] = max(1, min(48, _fnum(body.get("sup_hours"), "sup_hours", 1, 48)))
                    if "news_hours" in body:
                        st["news_hours"] = max(0.25, min(24, _fnum(body.get("news_hours"), "news_hours", 0.25, 24)))
                    if "digest_hour" in body:
                        st["digest_hour"] = int(_fnum(body.get("digest_hour"), "digest_hour", 0, 23))
                    if "onboarded" in body:
                        st["onboarded"] = bool(body.get("onboarded"))
                    if "currency" in body:
                        _c = str(body.get("currency") or "USD").upper()[:3]
                        if _c.isalpha():
                            st["currency"] = _c
                    if "app_name" in body:
                        st["app_name"] = (str(body.get("app_name") or "").strip()[:32] or "AccTrack")
                    if "zeusx_tier" in body:
                        _zt = str(body.get("zeusx_tier") or "iron").lower()[:16]
                        st["zeusx_tier"] = _zt if _zt in {t["id"] for t in ZEUSX_TIERS} else "iron"
                    if isinstance(body.get("fee_profiles"), dict):
                        _fp = body["fee_profiles"]
                        _clean = {}
                        for _k in ("funpay", "eldorado", "other"):
                            try:
                                _v = float(_fp.get(_k))
                                if 0.0 <= _v <= 1.0:
                                    _clean[_k] = round(_v, 6)
                            except (TypeError, ValueError):
                                pass
                        _games = {}
                        if isinstance(_fp.get("games"), dict):
                            for _g, _pv in list(_fp["games"].items())[:200]:
                                if not isinstance(_pv, dict):
                                    continue
                                _row = {}
                                for _pk in ("funpay", "eldorado", "other"):
                                    try:
                                        _v = float(_pv.get(_pk))
                                        if 0.0 <= _v <= 1.0:
                                            _row[_pk] = round(_v, 6)
                                    except (TypeError, ValueError):
                                        pass
                                if _row:
                                    _games[str(_g)[:80]] = _row
                        if _clean:
                            st["fee_profiles"] = {**_clean, "games": _games}
                            _apply_fee_profiles(st)
                    if "lang" in body:
                        _l = str(body.get("lang")).lower()
                        st["lang"] = "en" if _l.startswith("en") else ("ru" if _l.startswith("ru") else "uk")
                    if isinstance(body.get("notify"), dict):
                        for _k, _v in body["notify"].items():
                            if _k in _TG_DEFAULTS:
                                st["notify_" + _k] = bool(_v)
                    if "taobao_min_cny" in body:
                        st["taobao_min_cny"] = round(_fnum(body.get("taobao_min_cny"), "taobao_min_cny", 0, 10000), 2)
                    if "deal_x" in body:
                        st["deal_x"] = round(_fnum(body.get("deal_x"), "deal_x", 1, 100), 1)
                    if "scraper_limit" in body:
                        st["scraper_limit"] = int(_fnum(body.get("scraper_limit"), "scraper_limit", 1, 5000))
                    if "usd_uah" in body:
                        r = _fnum(usd, "usd_uah", 0, 1e6)
                        st["usd_uah"] = round(r, 4)
                        st["rate_ts"] = time.time() if r else 0
                        st["rate_source"] = "manual" if r else "none"
                    if "cloud_dir" in body:
                        st["cloud_dir"] = str(cloud_dir or "").strip()[:500]
                    _atomic_dump(SETTINGS_FILE, st)
                self._json({"ok": True, "cloud_effective": _cloud_dir()})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            return
        if self.path == "/api/rate/refresh":
            rate, ts, src = _get_rate(True)
            self._json({"ok": bool(rate), "usd_uah": rate, "rate_ts": ts, "source": src})
            return
        if self.path == "/api/tg/save":
            try:
                cfg = _tg_cfg()
                if body.get("clear"):
                    cfg["token"] = ""
                    cfg["chat_id"] = ""
                    cfg["enabled"] = False
                    _atomic_dump(TG_FILE, cfg)
                    self._json({"ok": True, "configured": False, "cleared": True})
                    return
                token = str(body.get("token") or "").strip()
                if token:
                    cfg["token"] = token          # порожнє поле = не змінювати токен
                if "chat_id" in body:
                    cfg["chat_id"] = str(body.get("chat_id") or "").strip()
                for k in ("enabled", "notify_mail", "notify_price", "notify_new"):
                    if k in body:
                        cfg[k] = bool(body.get(k))
                _atomic_dump(TG_FILE, cfg)
                self._json({"ok": True,
                            "configured": bool(cfg.get("token") and cfg.get("chat_id"))})
            except Exception as e:
                self._json({"ok": False, "error": str(e)})
            return
        if self.path == "/api/tg/test":
            self._json(_tg_send("🎮 <b>Game Tracker</b>\nТестове сповіщення — все працює!", force=True))
            return
        if self.path == "/api/gmail/save":
            try:
                if body.get("clear"):
                    _save_secrets({"gmail_user": "", "gmail_pass": ""})
                    self._json({"ok": True, "configured": False, "cleared": True})
                    return
                user = str(body.get("user") or "").strip()
                pwd  = "".join(str(body.get("password") or "").split())
                if user and ("@" not in user or " " in user):
                    self._json({"ok": False, "error": "Невірна Gmail-адреса"}, code=400); return
                if not user and not pwd:
                    self._json({"ok": False, "error": "Нема що зберігати"}, code=400); return
                old_user, old_pwd = _gmail_cfg()
                cand_user = user or old_user
                cand_pwd  = pwd or old_pwd
                if not cand_user or not cand_pwd:
                    self._json({"ok": False,
                                "error": "Введи і адресу, і App Password (16 символів)"},
                               code=400)
                    return
                # перевіряємо кандидата ДО запису, щоб не зберігати «мертвий» пароль
                test = _gmail_login_test(cand_user, cand_pwd)
                if not test.get("ok"):
                    self._json({"ok": False, "test": test,
                                "error": test.get("error") or "Gmail не підключився"},
                               code=400)
                    return
                updates = {}
                if user:
                    updates["gmail_user"] = user
                if pwd:
                    updates["gmail_pass"] = pwd
                _save_secrets(updates)
                self._json({"ok": True, "test": test,
                            "configured": _gmail_configured(), "error": None})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            return
        if self.path == "/api/gmail/test":
            self._json(_gmail_login_test())
            return
        if self.path == "/api/gmail/check":
            self._json(check_gmail())
            return
        if self.path == "/api/suppliers/news":
            self._json({"ok": True, **news_check(force=True)})
            return
        if self.path == "/api/suppliers/refresh":
            if _refresh_lock.locked():
                self._json({"ok": False, "error": "оновлення вже виконується"}, code=409)
                return
            threading.Thread(target=_refresh_suppliers,
                             kwargs={"reason": "manual"}, daemon=True).start()
            self._json({"ok": True, "started": True})
            return
        if self.path == "/api/platforms/refresh":
            self._json({"ok": True, **platforms_data(force=True)})
            return
        if self.path == "/api/taobao/request":
            now = time.time()
            last = int(_taobao.get("last_run") or 0)
            left = int(last + TAOBAO_COOLDOWN - now)
            if left > 0 and not body.get("force"):
                self._json({"ok": False, "error": "зарано", "next_in": left,
                            "message": "наступний збір через %d хв" % (left // 60)},
                           code=429)
                return
            _taobao["request"] = int(now)
            _taobao_save()
            seen = int(_taobao.get("agent_seen") or 0)
            online = bool(seen and (now - seen) < 45)
            if online:
                msg = "запит надіслано — агент онлайн (був на звʼязку %d с тому), почне за ~20 с" % int(now - seen)
            else:
                msg = ("⚠ агент не підключений (немає звʼязку). "
                       "Запустіть taobao_agent.bat і натисніть ще раз")
            self._json({"ok": True, "queued": True, "agent_online": online,
                        "agent_ago": (int(now - seen) if seen else None),
                        "message": msg})
            return
        if self.path == "/api/import/csv":
            try:
                import csv as _csv, io as _io
                raw = str(body.get("csv") or "")
                if not raw.strip():
                    self._json({"ok": False, "error": "порожній файл"}, code=400)
                    return
                rows = list(_csv.DictReader(_io.StringIO(raw)))
                cur = _read_json(PL_FILE, []) or []
                added, skipped, errs = 0, 0, []
                alias = {"date": ("date", "дата", "день"),
                         "title": ("title", "назва", "название", "name", "гра", "игра"),
                         "buy": ("buy", "купів", "купил", "закупка", "cost"),
                         "sell": ("sell", "продав", "продал", "price", "ціна", "цена"),
                         "platform": ("platform", "платформа", "src", "канал"),
                         "feePct": ("feepct", "fee_pct", "fee%", "fee", "комісія", "комиссия", "ставка"),
                         "afterFee": ("afterfee", "after_fee", "після комісії", "после комиссии")}
                def pick(row, key):
                    for k, v in row.items():
                        if not k:
                            continue
                        if str(k).strip().lower() in alias[key]:
                            return (v or "").strip()
                    return ""
                for i, row in enumerate(rows, start=2):
                    try:
                        d_ = pick(row, "date").replace(".", "-").replace("/", "-")
                        parts = [x for x in d_.split("-") if x]
                        if len(parts) == 3 and len(parts[0]) <= 2:
                            d_ = "%s-%02d-%02d" % (parts[2], int(parts[1]), int(parts[0]))
                        if not _is_date(d_):
                            skipped += 1
                            continue
                        buy = float(str(pick(row, "buy")).replace(",", ".").replace("$", "") or 0)
                        sell = float(str(pick(row, "sell")).replace(",", ".").replace("$", "") or 0)
                        if sell <= 0 and buy <= 0:
                            skipped += 1
                            continue
                        plat_raw = pick(row, "platform").lower()
                        plat = ("zeusx" if "zeus" in plat_raw else
                                "funpay" if "fun" in plat_raw else
                                "eldorado" if "eld" in plat_raw or "ель" in plat_raw else "other")
                        src_name = {"zeusx": "ZeusX", "funpay": "FunPay",
                                    "eldorado": "Eldorado", "other": "Інше"}[plat]
                        fee_pct = None
                        fee_raw = pick(row, "feePct").replace("%", "").replace(",", ".").strip()
                        if fee_raw:
                            try:
                                fee_pct = float(fee_raw)
                                if fee_pct > 1:
                                    fee_pct /= 100.0
                                fee_pct = max(0.0, min(1.0, fee_pct))
                            except ValueError:
                                fee_pct = None
                        after_raw = pick(row, "afterFee").replace(",", ".").replace("$", "").strip()
                        after_fee = None
                        if after_raw:
                            try:
                                after_fee = float(after_raw)
                            except ValueError:
                                after_fee = None
                        if fee_pct is None and after_fee is None:
                            fee_pct = PLATFORM_FEES.get(plat, 0.0)
                        cur.append({"id": int(time.time() * 1000) + i, "date": d_,
                                    "title": pick(row, "title")[:120] or "—",
                                    "src": plat, "srcName": src_name, "qty": 1,
                                    "platform": plat, "buy": buy, "sell": sell,
                                    **({"feePct": round(fee_pct, 6)} if fee_pct is not None else {}),
                                    **({"afterFee": round(after_fee, 4)} if after_fee is not None else {})})
                        added += 1
                    except Exception as e:
                        errs.append("рядок %d: %s" % (i, str(e)[:40]))
                _atomic_dump(PL_FILE, _clean_pl(cur))
                self._json({"ok": True, "added": added, "skipped": skipped,
                            "errors": errs[:5], "total": len(cur)})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/suppliers/add":
            try:
                nm = str(body.get("name") or "").strip()[:40]
                base = str(body.get("base") or "").strip()
                if not base.startswith("http"):
                    self._json({"ok": False, "error": "URL має починатися з http(s)://"}, code=400)
                    return
                if not nm:
                    self._json({"ok": False, "error": "вкажіть назву"}, code=400)
                    return
                key = re.sub(r"[^a-z0-9]+", "", nm.lower())[:16] or ("s%d" % int(time.time()))
                st = _read_json(SETTINGS_FILE, {}) or {}
                extra = [x for x in (st.get("suppliers_extra") or []) if x.get("key") != key]
                extra.append({"key": key, "name": nm, "base": base,
                              "color": "#7c8f6a", "emoji": "\u25cf"})
                st["suppliers_extra"] = extra[:20]
                _atomic_dump(SETTINGS_FILE, st)
                SUPPLIERS[key] = {"name": nm, "base": base,
                                  "color": "#7c8f6a", "emoji": "\u25cf"}
                self._json({"ok": True, "key": key, "suppliers": len(SUPPLIERS)})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/demo/load":
            try:
                import random
                today = datetime.date.today()
                games = ["Arknights", "Zenless Zone Zero", "Identity V", "Epic Seven",
                         "Blue Archive", "Nikke", "FGO", "Cookie Run"]
                pl = []
                for i in range(20):
                    d = (today - datetime.timedelta(days=i * 2)).isoformat()
                    sell = round(random.uniform(6, 40), 2)
                    buy = round(sell * random.uniform(0.35, 0.7), 2)
                    src = random.choice(["funpay", "funpay", "zeusx", "eldorado"])
                    fee = {"funpay": 0.015, "zeusx": 0.095, "eldorado": 0.10}[src]
                    pl.append({"id": int(time.time() * 1000) + i, "date": d,
                               "title": random.choice(games), "src": src,
                               "srcName": {"funpay": "FunPay", "zeusx": "ZeusX",
                                           "eldorado": "Eldorado"}[src],
                               "buy": buy, "sell": sell, "qty": 1, "platform": src,
                               "afterFee": round(sell * (1 - fee) - buy, 4)})
                _atomic_dump(PL_FILE, _clean_pl(pl))
                inv = []
                for i in range(4):
                    inv.append({"id": "demo-%d" % (time.time() + i), "date": today.isoformat(),
                                "title": random.choice(games) + " starter", "game": "Demo",
                                "cost": round(random.uniform(3, 15), 2), "source": "Demo",
                                "status": "in_stock", "account": "login: demo\npass: demo"})
                _atomic_dump(INVENTORY_FILE, inv)
                self._json({"ok": True, "purchases": len(pl), "inventory": len(inv)})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/demo/clear":
            try:
                _atomic_dump(PL_FILE, [])
                _atomic_dump(ED_FILE, [])
                _atomic_dump(INVENTORY_FILE, [])
                self._json({"ok": True})
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/secrets/request":
            what = str(body.get("what") or "both")[:10]
            if body.get("clear"):
                _taobao.pop("cookie_request", None)
            else:
                _taobao["cookie_request"] = {"what": what, "ts": int(time.time())}
            _taobao_save()
            self._json({"ok": True, "requested": None if body.get("clear") else what})
            return
        if self.path == "/api/secrets/status":
            _s = _read_json(SECRETS_FILE, {}) or {}
            self._json({"ok": True,
                        "funpay_cookie": bool(_s.get("funpay_cookie")),
                        "zeusx_cookie": bool(_s.get("zeusx_cookie"))})
            return
        if self.path == "/api/secrets/save":
            allowed = ("funpay_cookie", "zeusx_cookie")
            if body.get("clear"):
                keys = body.get("keys") if isinstance(body.get("keys"), list) else list(allowed)
                keys = [k for k in allowed if k in keys]
                _save_secrets({k: "" for k in keys})
                try:
                    _platforms_mod._platform_cache["ts"] = 0
                except Exception:
                    pass
                self._json({"ok": True, "cleared": keys})
                return
            upd = {}
            for _k in allowed:
                if _k in body:
                    _v = str(body.get(_k) or "").strip()
                    if len(_v) > 8000:
                        self._json({"ok": False, "error": "cookie задовгий"}, code=400)
                        return
                    upd[_k] = _v
            if not upd:
                self._json({"ok": False, "error": "немає що зберігати"}, code=400)
                return
            # не даємо затерти робочий cookie токеном без access_token
            _old = _read_json(SECRETS_FILE, {}) or {}
            if ("zeusx_cookie" in upd and "access_token=" not in upd["zeusx_cookie"]
                    and "access_token=" in str(_old.get("zeusx_cookie") or "")):
                self._json({"ok": False, "error":
                            "новий zeusx cookie без access_token — старий робочий не замінено. "
                            "Увійдіть на zeusx.com у вікні агента і натисніть «Взяти з браузера»."},
                           code=409)
                return
            _save_secrets(upd)
            try:
                _platforms_mod._platform_cache["ts"] = 0
            except Exception:
                pass
            self._json({"ok": True, "saved": sorted(upd)})
            return
        if self.path == "/api/taobao/mark":
            self._json(_taobao_mod._taobao_mark(
                str(body.get("href") or ""),
                body.get("card_pay") if "card_pay" in body else None,
                body.get("options") if "options" in body else None,
                body.get("cart") if "cart" in body else None))
            return
        if self.path == "/api/taobao/manual":
            self._json(_taobao_mod._taobao_manual(body))
            return
        if self.path == "/api/taobao/cart-clear":
            for _x in _taobao.get("items") or []:
                _x.pop("cart", None)
            _taobao_save()
            self._json({"ok": True})
            return
        if self.path == "/api/taobao/enrich":
            tok = (os.environ.get("GT_COLLECTOR_TOKEN")
                   or (_read_json(SECRETS_FILE, {}) or {}).get("collector_token") or "")
            got = str(body.get("token") or self.headers.get("X-GT-TOKEN") or "")
            if tok and got != tok:
                self._json({"ok": False, "error": "bad token"}, code=403)
                return
            self._json(_taobao_mod._taobao_enrich(body.get("rows") or [],
                                                 body.get("blocked") or 0,
                                                 body.get("requested") or 0))
            return
        if self.path == "/api/taobao/enrich-request":
            _taobao["enrich_request"] = int(time.time())
            _taobao_save()
            self._json({"ok": True, "message": "запит на перевірку оплати/варіантів надіслано"})
            return
        if self.path == "/api/taobao/progress":
            tok = (os.environ.get("GT_COLLECTOR_TOKEN")
                   or (_read_json(SECRETS_FILE, {}) or {}).get("collector_token") or "")
            got = str(body.get("token") or self.headers.get("X-GT-TOKEN") or "")
            if tok and got != tok:
                self._json({"ok": False, "error": "bad token"}, code=403)
                return
            _taobao["agent_seen"] = time.time()
            _taobao["progress"] = {
                "done": int(body.get("done") or 0),
                "total": int(body.get("total") or 0),
                "found": int(body.get("found") or 0),
                "current": str(body.get("current") or "")[:80],
                "ts": int(time.time()),
                "finished": bool(body.get("finished")),
            }
            _taobao_save()
            self._json({"ok": True})
            return
        if self.path == "/api/taobao/import":
            tok = os.environ.get("GT_COLLECTOR_TOKEN") or \
                  (_read_json(SECRETS_FILE, {}) or {}).get("collector_token") or ""
            got = str(body.get("token") or self.headers.get("X-GT-TOKEN") or "")
            if tok and got != tok:
                self._json({"ok": False, "error": "bad token"}, code=403)
                return
            res = _taobao_upsert(body)
            _taobao["agent_seen"] = time.time()
            pg = dict(_taobao.get("progress") or {})
            if pg.get("total"):          # не скидаємо смугу прогресу, лише оновлюємо «found»
                pg["found"] = int(res.get("total") or pg.get("found") or 0)
                pg["finished"] = False
                pg["ts"] = int(time.time())
                _taobao["progress"] = pg
            _taobao_save()
            self._json(res)
            return
        if self.path == "/api/inventory/save":
            try:
                data = _inv_clean(body.get("items"))
                global _inventory
                with _inv_lock:
                    _inventory = data
                _inv_save()
                self._json({"ok": True, "count": len(data)})
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/inventory/add":
            try:
                rec = _inv_clean([body])[0]
                with _inv_lock:
                    _inventory.append(rec)
                _inv_save()
                self._json({"ok": True, "item": rec})
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            return
        if self.path == "/api/inventory/status":
            iid = str(body.get("id") or "")
            status = str(body.get("status") or "")
            if status not in INV_STATUSES:
                self._json({"ok": False, "error": "невірний статус"}, code=400)
                return
            _inv_load()
            item = next((x for x in _inventory if x.get("id") == iid), None)
            if not item:
                self._json({"ok": False, "error": "запис не знайдено"}, code=404)
                return
            item["status"] = status
            if body.get("sale_id"):
                item["sale_id"] = body.get("sale_id")
            _inv_save()
            self._json({"ok": True, "item": item})
            return
        if self.path == "/api/inventory/delete":
            iid = str(body.get("id") or "")
            with _inv_lock:
                n = len(_inventory)
                _inventory[:] = [x for x in _inventory if x.get("id") != iid]
                removed = n - len(_inventory)
            _inv_save()
            self._json({"ok": True, "removed": removed})
            return
        if self.path == "/api/mail/clear":
            _mailq_load()
            with _mail_q_lock:
                ids = [x.get("id") for x in _mail_queue if x.get("id")]
                n = len(_mail_queue)
                _mail_queue.clear()
            _imported_mark(ids)
            _mailq_save()
            self._json({"ok": True, "removed": n})
            return
        if self.path == "/api/mail/action":
            try:
                qid = str(body.get("id") or "")
                action = str(body.get("action") or "")
                item = _mailq_get(qid)
                if not item:
                    self._json({"ok": False, "error": "запис не знайдено"}, code=404); return
                if action == "ignore":
                    item["status"] = "ignored"
                elif action == "remove":
                    with _mail_q_lock:
                        if item in _mail_queue:
                            _mail_queue.remove(item)
                    _mailq_save()
                    self._json({"ok": True, "removed": True}); return
                elif action in ("add_ed", "add_pl"):
                    if action == "add_ed" and (item.get("platform") or "") in ("FunPay", "ZeusX"):
                        self._json({"ok": False, "error":
                                    "Це замовлення %s — додавайте його в P&L "
                                    "(кнопка ➕ P&L), а не в ELDORADO"
                                    % item.get("platform")}, code=400)
                        return
                    if action == "add_pl" and (item.get("platform") or "") == "Eldorado":
                        self._json({"ok": False, "error":
                                    "Це замовлення Eldorado — додавайте його в "
                                    "вкладку ELDORADO (кнопка ➕ ELDORADO)"}, code=400)
                        return
                    if item.get("status") == "added":
                        self._json({"ok": False, "error": "цей лист уже додано"},
                                   code=400)
                        return
                    price = item.get("price")
                    try:
                        price = float(price) if price is not None else 0.0
                    except (TypeError, ValueError):
                        price = 0.0
                    if price <= 0:
                        # у листі немає суми — беремо введену manual
                        try:
                            price = float(body.get("price") or 0)
                        except (TypeError, ValueError):
                            price = 0.0
                    if price <= 0 and (item.get("platform") or "") == "ZeusX" \
                            and item.get("orderId"):
                        # у листі ZeusX суми немає — беремо з API по коду офера
                        try:
                            d = _zx_call("/v1/earning/ongoing-earning",
                                         _sec_get("zeusx_cookie"), method="POST",
                                         body={"pageIndex": 0})
                            for e in ((d or {}).get("data") or {}).get("earnings") or []:
                                if str(e.get("offer_code") or "") == str(item["orderId"]):
                                    price = round(float(e.get("listed_price") or 0), 2)
                                    print(f"  💰 ZeusX: amount from API ${price}", flush=True)
                                    break
                        except Exception as ex:
                            print(f"  ⚠ ZeusX price: {ex}", flush=True)
                    if price <= 0:
                        self._json({"ok": False,
                                    "error": "у листі не знайдено суму — вкажіть manual"},
                                   code=400)
                        return
                    price = round(price, 2)
                    try:
                        buy = round(float(body.get("buy") or 0), 2)
                    except (TypeError, ValueError):
                        buy = 0.0
                    buy = max(0.0, min(buy, 1e6))
                    today = datetime.date.today().isoformat()
                    _g = str(body.get("game") or "").strip()[:60]
                    if _g:
                        item["game"] = _g
                    title = (item.get("game") or item.get("subject")
                             or item.get("platform") or "Продаж")[:200]
                    if action == "add_ed":
                        fee = round(price * ED_FEE, 2)
                        rec = {"id": int(time.time() * 1000), "date": today, "title": title,
                               "price": price, "buy": buy, "fee": fee,
                               "profit": round(price - fee - buy, 2),
                               "orderId": item.get("orderId") or "",
                               "category": item.get("platform") or ""}
                        data = _read_json_strict(ED_FILE, [])
                        if not isinstance(data, list):
                            data = []
                        data.append(rec)
                        data = _clean_ed(data)
                        _atomic_dump(ED_FILE, data)
                        item["added_to"] = "ELDORADO"
                    else:
                        src = {"ZeusX": "zeusx", "FunPay": "funpay"}.get(
                            item.get("platform"), "other")
                        rec = {"id": int(time.time() * 1000), "date": today, "title": title,
                               "src": src, "srcName": item.get("platform") or "Інше",
                               "buy": buy, "sell": price,
                               "orderId": item.get("orderId") or "",
                               "qty": 1, "platform": src}
                        data = _read_json_strict(PL_FILE, [])
                        if not isinstance(data, list):
                            data = []
                        data.append(rec)
                        data = _clean_pl(data)
                        _atomic_dump(PL_FILE, data)
                        item["added_to"] = "P&L"
                    item["status"] = "added"
                else:
                    self._json({"ok": False, "error": "unknown action"}, code=400); return
                if action in ("add_ed", "add_pl"):
                    with _mail_q_lock:
                        _mail_queue[:] = [x for x in _mail_queue
                                          if x.get("id") != item.get("id")]
                        _atomic_dump(MAIL_QUEUE_FILE, _mail_queue[-200:])
                    _imported_mark([item.get("id")])
                else:
                    with _mail_q_lock:
                        _atomic_dump(MAIL_QUEUE_FILE, _mail_queue[-200:])
                self._json({"ok": True, "item": item})
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/pl/save":
            try:
                data = _clean_pl(body.get("purchases"))
                if not data and not body.get("force"):
                    old = _read_json(PL_FILE, []) or []
                    if isinstance(old, list) and old:
                        self._json({"ok": False, "error":
                                    "порожній список відхилено — дані не стерто. "
                                    "Для навмисного очищення надішліть force:true"},
                                   code=409)
                        return
                _snapshot_before_save(PL_FILE, "gt_pl")
                _atomic_dump(PL_FILE, data)
                self._json({"ok": True, "count": len(data)})
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        if self.path == "/api/eldorado/save":
            try:
                data = _clean_ed(body.get("sales"))
                if not data and not body.get("force"):
                    old = _read_json(ED_FILE, []) or []
                    if isinstance(old, list) and old:
                        self._json({"ok": False, "error":
                                    "порожній список відхилено — дані не стерто. "
                                    "Для навмисного очищення надішліть force:true"},
                                   code=409)
                        return
                _snapshot_before_save(ED_FILE, "gt_eldorado")
                _atomic_dump(ED_FILE, data)
                self._json({"ok": True, "count": len(data)})
            except ValueError as e:
                self._json({"ok": False, "error": str(e)}, code=400)
            except Exception as e:
                self._json({"ok": False, "error": str(e)}, code=500)
            return
        else:
            self._send(404, "text/plain", b"404")

    def _send(self, code, ct, data, extra=None):
        if isinstance(data, str): data = data.encode()
        dev_cookie = None
        if getattr(self, "_device_cookie", False) and code == 200:
            self._device_cookie = False
            dev_cookie = ("gt_device=" + self._device_token()
                          + "; Path=/; Max-Age=31536000; HttpOnly; SameSite=Lax")
            if self._is_https():
                dev_cookie += "; Secure"
        try:
            self.send_response(code)
            if code != 304:
                # для бінарних типів charset не потрібен
                bin_type = ct.startswith(("image/", "font/", "application/zip",
                                          "application/octet-stream", "application/x-icon"))
                self.send_header("Content-Type", ct if bin_type else ct + "; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
            self.send_header("Connection", "close")
            if dev_cookie:
                self.send_header("Set-Cookie", dev_cookie)
            for k, v in _SECURITY_HEADERS.items():
                if k == "Cache-Control" and extra and "Cache-Control" in extra:
                    continue          # іконкам дозволяємо кеш
                self.send_header(k, v)
            if self._is_https():
                self.send_header("Strict-Transport-Security", "max-age=31536000")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if data:
                self.wfile.write(data)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass

    def _json(self, obj, code=200, extra=None):
        """JSON + gzip + ETag: 970 КБ відповіді стискаються в ~8 разів,
        а повторні запити без змін отримують 304."""
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        etag = '"' + hashlib.sha1(raw).hexdigest()[:20] + '"'
        inm = (self.headers.get("If-None-Match") or "").strip()
        if code == 200 and inm and etag in [t.strip() for t in inm.split(",")]:
            self._send(304, "application/json", b"", extra={"ETag": etag})
            return
        extra = dict(extra or {})
        extra.update({"ETag": etag, "Vary": "Accept-Encoding"})
        if len(raw) > 1024 and "gzip" in (self.headers.get("Accept-Encoding") or "").lower():
            raw = gzip.compress(raw, 5)
            extra["Content-Encoding"] = "gzip"
        self._send(code, "application/json", raw, extra=extra)

    def log_message(self, *a): pass

# ─────────────────────────────────────────────────
# HTML DASHBOARD
# ─────────────────────────────────────────────────


def _render_html():
    """HTML + конфіг комісій з Python (єдине джерело істини)."""
    cfg = {"fees": PLATFORM_FEES, "payout": PAYOUT_FEES, "ed": ED_FEE, "zeusx_tiers": ZEUSX_TIERS,
           "marketplaces": MARKETPLACES}
    payload = json.dumps(cfg)
    if ui is None:
        return ("<h1>UI недоступний</h1><p>Не знайдено модуль ui.py — "
                "поклади його поруч із game_tracker.py</p>")
    return ui.render_html(payload)


def _startup_supplier_refresh(allow_network=True):
    """Оновлення постачальників у фоні — вже після старту сервера."""
    global _supplier_cache
    try:
        last_ts = 0
        try:
            with open(SUP_TS_FILE, encoding="utf-8") as f:
                last_ts = int(json.load(f).get("ts", 0) or 0)
        except Exception:
            pass
        now_ts = int(time.time())
        st = _sup_status()
        if not _sup_due() and _supplier_cache:
            print(f"  📦 Suppliers: cache {len(_supplier_cache)} products "
                  f"(оновлено {max(0, (now_ts - st['ts']) // 60)} хв тому, "
                  f"інтервал {int(_sup_hours())} год)", flush=True)
            return
        if not allow_network:
            return
        print("\n  📦 Loading suppliers in background (dashboard is ready)...", flush=True)
        is_first_run = len(_supplier_seen) == 0
        _price_drops.clear()
        fresh, ok_keys = [], set()
        for key in SUPPLIERS:
            try:
                fresh.extend(fetch_supplier(key, is_first_run))
                ok_keys.add(key)
            except Exception as ex:
                print(f"  ⚠ {key}: {ex}", flush=True)
        if ok_keys:
            _merge_supplier_cache(fresh, ok_keys)
            _sup_mark(True)
            _save_file_cache()
            _save_sup_cache()
        else:
            _sup_mark(False)
        _notify_price_drops()
        sale = sum(1 for p in _supplier_cache if p.get("isOnSale") and not p.get("gone"))
        gone = sum(1 for p in _supplier_cache if p.get("gone"))
        print(f"\n  ✅ Suppliers: {len(_supplier_cache)} products | 🔥 Sale: {sale}"
              f" | 🗑 gone: {gone}\n", flush=True)
    except Exception as e:
        print(f"  ⚠ Suppliers: {e}", flush=True)


def main():
    try:
        _apply_fee_profiles(_read_json(SETTINGS_FILE, {}) or {})
    except Exception:
        pass
    _load_extra_suppliers()
    global _SCHEME
    # CLI для cron/обслуговування:
    #   python3 game_tracker.py --backup       (зробити бекап і вийти)
    #   python3 game_tracker.py --check-gmail  (одна перевірка пошти і вийти)
    if "--backup" in sys.argv:
        _load_file_cache()
        _load_sup_cache()
        res = do_backup()
        print(json.dumps({"files": res.get("files"), "cloud": res.get("cloud")},
                         ensure_ascii=False))
        return 0
    if "--check-gmail" in sys.argv:
        print(json.dumps(check_gmail(), ensure_ascii=False))
        return 0

    public_bind = BIND not in ("127.0.0.1", "localhost", "::1")
    if AUTH_MODE == "off" and public_bind:
        # не блокуємо запуск — лише голосно попереджаємо
        print("=" * 60)
        print("  ⚠  No password + listening on " + str(BIND) + " — anyone on your network can open it.")
        print("     For internet access set a password: ⚙ → Password.")
        print("     For local-only access use: GT_BIND=127.0.0.1")
        print("=" * 60)
    elif not AUTH_PASS:
        print("  ❌ Empty password in .gt_secrets.json — that opens the dashboard to everyone.")
        print("     Set auth_pass (min 8 chars) and start again.")
        return 2

    weak_pass = (AUTH_PASS == "gametracker2026") or len(AUTH_PASS) < 8
    if AUTH_MODE != "off" and public_bind and weak_pass and os.environ.get("GT_ALLOW_WEAK_PASS") != "1":
        print("=" * 60)
        print("  ❌ Public access with a weak/default password — stopping.")
        print(f"     Listening on {BIND}:{PORT}, but the password is default or shorter than 8 chars.")
        print('     1) у .gt_secrets.json задай:  "auth_pass": "довгий-унікальний-пароль"')
        print("     2) start it again")
        print("     Temporarily allow: GT_ALLOW_WEAK_PASS=1")
        print("=" * 60)
        return 3

    print("=" * 60)
    print("  ▲  AccTrack v1.1.1")
    print("  📊 Deals · Channels · Stock · Analytics · Backups")
    print("=" * 60 + "\n")

    if AUTH_MODE == "off":
        print("  🔓 No password — open access (set one in ⚙ → Password)"
              + (" · заголовок Access обов'язковий" if REQUIRE_ACCESS else ""))
    else:
        print("  🔓 No password — open access (enable: ⚙ → Login password)")
    print()

    _load_file_cache()
    _load_sup_cache()
    _load_gmail_state()
    try:
        if _supplier_cache:
            n = _build_compare_index()
            print(f"  ⚖ Compare index: {len(_supplier_cache)} products, "
                  f"дешевше в інших: {n}", flush=True)
    except Exception as e:
        print(f"  ⚠ Compare index: {e}", flush=True)

    Handler.html_bytes = _render_html().encode("utf-8")
    try:
        srv = http.server.ThreadingHTTPServer((BIND, PORT), Handler)
    except OSError as e:
        print(f"  ❌ Could not bind {BIND}:{PORT} — {e}")
        print("     Close the other tracker instance or set PORT=8766")
        return 1

    scheme = "http"
    opts = _https_opts()
    if opts:
        try:
            import ssl
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(opts[0], opts[1])
            srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
            scheme = "https"
        except Exception as e:
            print(f"  ⚠ HTTPS did not start: {e}", flush=True)
    elif (_read_json(SETTINGS_FILE, {}) or {}).get("https_enabled"):
        print("  ⚠ HTTPS enabled but cert/key not found — running over HTTP", flush=True)
    _SCHEME = scheme

    threading.Thread(target=srv.serve_forever, daemon=True).start()
    threading.Thread(target=_backup_loop, daemon=True).start()
    threading.Thread(target=_bg_loop, daemon=True).start()
    threading.Thread(target=_gmail_loop, daemon=True).start()
    threading.Thread(target=_tg_bot_loop, daemon=True).start()
    threading.Thread(target=_watchdog_loop, daemon=True).start()
    threading.Thread(target=_agent_watchdog_loop, daemon=True).start()
    threading.Thread(target=_fx_usd_cny_loop, daemon=True).start()
    threading.Thread(target=_funpay_orders_loop, daemon=True).start()
    threading.Thread(target=_startup_supplier_refresh,
                     kwargs={"allow_network": os.environ.get("GT_NO_SUPPLIERS") != "1"},
                     daemon=True).start()

    local_ip = _LOCAL_IP or "localhost"
    url = f"{scheme}://localhost:{PORT}"
    print(f"  🌐  {url}")
    if public_bind:
        print(f"  🌍  Listening on {BIND}:{PORT} — reachable from outside")
        if BIND not in ("127.0.0.1", "localhost", "::1"):
            print(f"  📱  Phone URL: {scheme}://{local_ip}:{PORT}")
    elif _is_private_ip(local_ip):
        if BIND not in ("127.0.0.1", "localhost", "::1"):
            print(f"  📱  Phone (WiFi): {scheme}://{local_ip}:{PORT}")
    else:
        print(f"  🖥  Local: {url} — expose it through nginx/domain")
    if public_bind and scheme == "https":
        print("  🔒  HTTPS enabled")
    elif public_bind:
        print("  ⚠  No HTTPS: password and data travel in clear text.")
        print("      Add nginx/Cloudflare with TLS in front, or enable HTTPS in ⚙ → Security.")
    if _gmail_configured():
        print("  📧  Gmail: enabled (checking every 2 min)")
    else:
        print("  📧  Gmail: not configured (⚙ → Gmail)")
    print("  Ctrl+C — stop\n" + "-" * 60)
    if os.environ.get("GT_NO_BROWSER") != "1" and sys.stdout.isatty():
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Bye!")
        try:
            srv.shutdown()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
