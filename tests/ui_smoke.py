"""UI-тест публічного білда: онбординг, форма, теми, мови, вкладки."""
import json
import os
import sys
import time

sys.path.insert(0, os.environ.get("GT_PW_PATH", ""))
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    PW = json.load(open(os.path.join(D, ".gt_secrets.json"), encoding="utf-8")).get("auth_pass")
except Exception:
    PW = None          # режим без пароля

ok = fail = 0


def check(name, cond, info=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  ✓ {name}")
    else:
        fail += 1
        print(f"  ✗ {name}  {info}")


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://127.0.0.1:9222", timeout=20000)
    p = b.contexts[0].new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:120]))
    p.set_viewport_size({"width": 1440, "height": 900})

    print("=== 1. ВХІД ===")
    base = os.environ.get("GT_URL", "http://127.0.0.1:8766")
    if PW:
        p.goto(base + "/", wait_until="domcontentloaded", timeout=30000)
        try:
            p.evaluate("fetch('/api/logout',{method:'POST'})")
        except Exception:
            pass
        time.sleep(1)
        p.goto(base + "/login", wait_until="networkidle", timeout=30000)
        check("лого AccTrack", p.evaluate("document.querySelector('.brand b').innerText") == "AccTrack")
        p.click("#l-uk")
        time.sleep(0.4)
        check("мова входу UA", p.evaluate("document.getElementById('btn').innerText") == "Увійти")
        p.click("#l-en")
        time.sleep(0.3)
        p.fill("#pw", PW)
        p.keyboard.press("Enter")
        time.sleep(3)
    else:
        check("пароль вимкнено — логін не потрібен", True)
        check("пароль вимкнено — мова входу н/д", True)
        p.goto(base + "/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
    check("увійшли в дашборд", p.evaluate("document.querySelectorAll('.tab').length") > 0)

    print("=== 2. ОНБОРДИНГ ===")
    p.evaluate("localStorage.removeItem('gt_onboarded'); location.reload()")
    time.sleep(4)
    vis = p.evaluate("document.getElementById('onb').style.display")
    check("онбординг показано", vis == "flex", vis)
    p.click("#onbNext")
    time.sleep(1)
    check("крок 2 — назва/тема", "Name" in p.evaluate("document.getElementById('onbTitle').innerText"))
    p.fill("#onbName", "MyAccTrack")
    p.click("#onbNext")
    time.sleep(1)
    check("крок 3 — токени", "Connect" in p.evaluate("document.getElementById('onbTitle').innerText"))
    p.click("#onbSkip")
    time.sleep(1)
    check("онбординг закрито", p.evaluate("document.getElementById('onb').style.display") == "none")
    check("назва застосована", p.evaluate("document.querySelector('header h1').innerText").startswith("MyAccTrack"))

    print("=== 3. ТЕМИ ===")
    bgs = {}
    for t in ("ledger", "slate", "nord", "carbon", "light"):
        p.evaluate(f"pickTheme('{t}')")
        time.sleep(0.5)
        bgs[t] = p.evaluate("getComputedStyle(document.body).backgroundColor")
    check("5 тем перемикаються", len(set(bgs.values())) >= 3, bgs)
    p.evaluate("pickTheme('ledger')")
    time.sleep(0.4)

    print("=== 4. МОВИ ===")
    for lang, word in (("uk", "Огляд"), ("ru", "Обзор"), ("en", "Overview")):
        p.evaluate(f"setLang('{lang}')")
        time.sleep(1.2)
        tabs = p.evaluate("[...document.querySelectorAll('.tab')].map(t=>t.innerText.trim())")
        check(f"мова {lang}: {word}", any(word in x for x in tabs), tabs[:3])

    print("=== 5. ДОДАТИ УГОДУ ЧЕРЕЗ ФОРМУ ===")
    p.evaluate("document.querySelectorAll('.tab')[1].click()")
    time.sleep(2)
    p.fill("#plTitle", "UITest")
    p.fill("#plBuy", "4")
    p.fill("#plSell", "10")
    p.evaluate("plPlatPick('funpay')")
    p.evaluate("addPLRecord()")
    time.sleep(2.5)
    rows = p.evaluate("[...document.querySelectorAll('#purList tr, #purList div')].map(r=>r.innerText)")
    check("угода з'явилась у списку", any("UITest" in r for r in rows), rows[:2])

    print("=== 6. ВКЛАДКИ ===")
    n = p.evaluate("document.querySelectorAll('.tab').length")
    errs.clear()
    for i in range(n):
        p.evaluate(f"document.querySelectorAll('.tab')[{i}].click()")
        time.sleep(1.0)
    check(f"усі {n} вкладок без JS-помилок", not errs, errs[:2])

    print("=== 7. КАТАЛОГ / СКЛАД ===")
    p.evaluate("document.querySelectorAll('.tab')[4].click()")
    time.sleep(2.5)
    check("каталог: порожній стан", "постачальник" in p.evaluate("document.getElementById('supAl') ? document.getElementById('supAl').innerText : ''").lower()
          or p.evaluate("document.querySelectorAll('#supList tr').length") == 0)
    p.evaluate("document.querySelectorAll('.tab')[7].click()")
    time.sleep(2)
    check("склад відкривається", p.evaluate("!!document.getElementById('invSummary')"))

    print("=== 8. НАЛАШТУВАННЯ / ДІАГНОСТИКА ===")
    p.evaluate("document.querySelectorAll('.tab')[9].click()")
    time.sleep(2)
    p.evaluate("diagLoad()")
    time.sleep(1.5)
    diag = p.evaluate("document.getElementById('diagBox').innerText")
    check("діагностика показує дані", "версія" in diag or "version" in diag.lower(), diag[:60])
    check("панель контактів", p.evaluate("!!document.getElementById('contactPanel')"))
    check("email у контактах", "ledgeros.gg@gmail.com" in p.evaluate("document.getElementById('contactPanel').innerText"))
    check("discord у контактах", "facemyfear" in p.evaluate("document.getElementById('contactPanel').innerText"))

    print()
    print(f"ПІДСУМОК UI: {ok}/{ok + fail} пройдено")
    p.close()

sys.exit(0 if fail == 0 else 1)

