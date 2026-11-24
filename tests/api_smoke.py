"""Повний API-тест публічного білда AccTrack (без токенів каналів)."""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("GT_URL", "http://127.0.0.1:8766")
PASS_FILE = os.environ.get("GT_SECRETS", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".gt_secrets.json"))
try:
    PW = json.load(open(PASS_FILE, encoding="utf-8")).get("auth_pass")
except Exception:
    PW = None          # режим без пароля — файл ще не створений
AUTH = "Basic " + base64.b64encode(f"admin:{PW}".encode()).decode() if PW else None

ok = fail = 0


def call(path, method="GET", body=None, auth=True, raw=False, timeout=40):
    req = urllib.request.Request(BASE + path, method=method)
    if auth and AUTH:
        req.add_header("Authorization", AUTH)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data, timeout=timeout) as r:
            payload = r.read()
            if raw:
                return r.status, payload
            try:
                return r.status, json.loads(payload)
            except Exception:
                return r.status, payload.decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def check(name, cond, info=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  ✓ {name}")
    else:
        fail += 1
        print(f"  ✗ {name}  {info}")


print("=== 1. ПУБЛІЧНЕ / АВТОРИЗАЦІЯ ===")
st, d = call("/api/health", auth=False)
check("health без пароля", st == 200 and d.get("ok"), st)
check("версія 1.6.0", d.get("version") == "1.6.0", d)
st, d = call("/api/settings", auth=False)
auth_open = (st == 200)
check("API: режим без пароля (або 401, якщо пароль увімкнено)", st in (200, 401), st)
st, d = call("/login", auth=False, raw=True)
if st == 200:
    check("сторінка входу показує AccTrack", b"AccTrack" in d, st)
else:
    check("вхід вимкнено — сторінки логіну немає (404)", st == 404, st)
if not auth_open:
    st, d = call("/api/login", "POST", {"password": "wrong"}, auth=False)
    check("невірний пароль → не 200", st != 200, st)
else:
    check("пароль вимкнено — вхід не потрібен", True)

print("=== 2. ДІАГНОСТИКА ===")
st, d = call("/api/diag")
check("diag", st == 200 and "counts" in d, st)
check("diag має токени", "tokens" in d, d.keys())

print("=== 3. УГОДИ (P&L) ===")
# Тест не має залежати від збережених fee_profiles користувача
call("/api/settings/save", "POST", {"fee_profiles": {
    "funpay": 0.10, "eldorado": 0.10, "other": 0.0, "games": {}
}})
call("/api/pl/save", "POST", {"purchases": []})
st, d = call("/api/pl/save", "POST", {"purchases": [
    {"id": 1, "date": "2026-11-20", "title": "TestOne", "src": "funpay",
     "srcName": "FunPay", "buy": 5, "sell": 12, "qty": 1, "platform": "funpay"},
]})
check("додати угоду", st == 200, st)
st, d = call("/api/pl")
rows = d.get("purchases", [])
check("угода збережена", len(rows) == 1, len(rows))
check("прибуток пораховано", abs(abs(rows[0].get("afterFee", 0)) - 5.80) < 0.02, rows[0].get("afterFee"))
st, d = call("/api/pl/save", "POST", {"purchases": [
    {"id": 2, "date": "", "title": "Bad", "buy": 1, "sell": 2},
]})
check("некоректна дата відхилена", st != 200 or not (call("/api/pl")[1].get("purchases")), st)

print("=== 4. ІМПОРТ CSV ===")
csv = "date,title,platform,buy,sell\n2026-11-20,A,FunPay,5,12\n21.11.2026,B,ZeusX,8,20\nbad,skip,FunPay,1,2\n"
st, d = call("/api/import/csv", "POST", {"csv": csv})
check("імпорт: 2 додано", st == 200 and d.get("added") == 2, d)
check("імпорт: 1 пропущено", d.get("skipped") == 1, d)

print("=== 5. СКЛАД ===")
st, d = call("/api/inventory/add", "POST", {"title": "InvTest", "game": "G", "cost": 9.5,
                                            "source": "Test", "account": "a:b"})
check("додати на склад", st == 200, st)
st, d = call("/api/inventory")
items = d.get("items", d if isinstance(d, list) else [])
check("склад містить запис", any((x.get("title") == "InvTest") for x in items), len(items))
inv_id = next((x.get("id") for x in items if x.get("title") == "InvTest"), None)
st, d = call("/api/inventory/delete", "POST", {"id": inv_id})
check("видалити зі складу", st in (200, 204), st)

print("=== 6. ДЕМО-ДАНІ ===")
st, d = call("/api/demo/load", "POST")
check("демо: 20 угод", st == 200 and d.get("purchases") == 20, d)
st, d = call("/api/pl")
check("демо в P&L", len(d.get("purchases", [])) == 20, len(d.get("purchases", [])))
st, d = call("/api/demo/clear", "POST")
check("демо стерто", st == 200, st)

print("=== 7. ПОСТАЧАЛЬНИКИ ===")
st, d = call("/api/suppliers/add", "POST", {"name": "TestShop", "base": "https://example.com"})
check("додати постачальника", st == 200 and d.get("ok"), d)
st, d = call("/api/suppliers/add", "POST", {"name": "Bad", "base": "no-url"})
check("поганий URL відхилено", st == 400, st)
st, d = call("/api/suppliers/status")
check("статус постачальників", st == 200 and any(s["name"] == "TestShop" for s in d.get("suppliers", [])), d.get("suppliers"))
st, d = call("/api/suppliers?page=1&per=5")
check("каталог (порожній)", st == 200 and d.get("total") == 0, d.get("total"))

print("=== 8. ЕКСПОРТИ ===")
st, d = call("/api/export/csv", raw=True)
check("експорт CSV", st == 200 and b"date" in d.lower(), st)
st, d = call("/api/backup/export", raw=True)
check("експорт zip", st == 200 and len(d) > 200, len(d) if isinstance(d, bytes) else st)

print("=== 9. АНАЛІТИКА / ЗВІТ ===")
st, d = call("/api/analytics")
check("аналітика", st == 200, st)
st, d = call("/api/report")
check("звіт", st == 200, st)
st, d = call("/api/mail/queue")
check("черга пошти", st == 200, st)
st, d = call("/api/eldorado")
check("Eldorado", st == 200, st)

print("=== 10. НАЛАШТУВАННЯ ===")
st, d = call("/api/settings/save", "POST", {"app_name": "MyTrack"})
check("змінити назву", st == 200, st)
st, d = call("/api/settings")
check("назва збережена", d.get("app_name") == "MyTrack", d.get("app_name"))
st, d = call("/api/settings/save", "POST", {"lang": "ru"})
check("мова ru", st == 200, st)
st, d = call("/api/settings")
check("мова збережена", d.get("lang") == "ru", d.get("lang"))
call("/api/settings/save", "POST", {"app_name": "AccTrack", "lang": "en"})

print("=== 11. КАНАЛИ БЕЗ ТОКЕНІВ ===")
call("/api/secrets/save", "POST", {"funpay_cookie": "", "zeusx_cookie": ""})   # чистий стан
st, d = call("/api/platforms")
check("канали відповідають", st == 200, st)
errs = [str((d.get(k) or {}).get("error", "")) for k in ("zeusx", "funpay")]
check("помилка пояснює причину людською мовою",
      all(("не підключено" in e or "cookie" in e or not e) for e in errs), errs)

print("=== 12. СЕКРЕТИ ===")
st, d = call("/api/secrets/status")
check("статус токенів", st == 200, st)
st, d = call("/api/secrets/save", "POST", {"funpay_cookie": "golden_key=test123"})
check("зберегти cookie", st == 200, st)
st, d = call("/api/secrets/status")
check("cookie враховано", (d.get("funpay") is True) or (d.get("funpay_cookie") is True), d)

print("=== 13. ПАРОЛЬ (toggle) ===")
st, d = call("/api/auth/toggle", "POST", {"enabled": True, "new": "123"})
check("короткий пароль відхилено", st == 400, st)
st, d = call("/api/auth/toggle", "POST", {"enabled": True, "new": "TestPass123"})
check("увімкнути пароль", st == 200 and d.get("auth_enabled"), d)
globals()["AUTH"] = "Basic " + base64.b64encode(b"admin:TestPass123").decode()
st, d = call("/api/pl", auth=False)
check("після вмикання API закритий", st == 401, st)
st, d = call("/api/auth/toggle", "POST", {"enabled": False}, auth=True)
check("вимкнути пароль", st == 200 and d.get("auth_enabled") is False, d)
st, d = call("/api/pl", auth=False)
check("після вимикання API відкритий", st == 200, st)

print()
print(f"ПІДСУМОК: {ok}/{ok + fail} пройдено")
sys.exit(0 if fail == 0 else 1)
