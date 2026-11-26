#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ledger OS Telegram helper bot.

Token is read from (first found):
  $LEDGER_OS_BOT_TOKEN
  ./ledger-os-bot.token
  %USERPROFILE%/Downloads/Ledger-Desktop/ledger-os-bot.token

Never commit the token file.

Usage:
  python ledger_os_bot.py --poll
  python ledger_os_bot.py --post "text"
  python ledger_os_bot.py --post-file post.txt
  python ledger_os_bot.py --chat @ledger_os --post "text"
"""
import json
import os
import pathlib
import sys
import time
import urllib.request

API = "https://api.telegram.org/bot%s/%s"
CHANNEL = "@ledger_os"
SITE = "https://ledger.70-34-243-50.sslip.io"


def _token():
    tok = (os.environ.get("LEDGER_OS_BOT_TOKEN") or "").strip()
    if tok:
        return tok
    here = pathlib.Path(__file__).resolve().parent
    for p in (here / "ledger-os-bot.token",
              pathlib.Path.home() / "Downloads" / "Ledger-Desktop" / "ledger-os-bot.token",
              pathlib.Path.home() / "ledger-os-bot.token"):
        try:
            if p.is_file():
                return p.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    raise SystemExit("No bot token: set LEDGER_OS_BOT_TOKEN or save ledger-os-bot.token next to this script.")


def api(method, payload=None, timeout=30):
    req = urllib.request.Request(
        API % (_token(), method),
        data=json.dumps(payload or {}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def health():
    try:
        with urllib.request.urlopen(SITE + "/api/health", timeout=10) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}


def help_text():
    return ("Ledger OS - reseller OS for game accounts.\n\n"
            "Commands:\n"
            "/status - Ledger server status\n"
            "/pricing - free vs Ledger+\n"
            "/channel - Telegram channel\n"
            "/github - latest release\n"
            "/id - your Telegram id\n\n"
            "Channel: https://t.me/ledger_os")


def reply(chat_id, text, preview=False):
    return api("sendMessage", {"chat_id": chat_id, "text": text,
                               "disable_web_page_preview": not preview})


def handle(msg):
    chat = msg.get("chat") or {}
    cid = chat.get("id")
    text = (msg.get("text") or "").strip()
    if not cid or not text.startswith("/"):
        return
    cmd = text.split()[0].split("@")[0].lower()
    if cmd in ("/start", "/help"):
        reply(cid, "👋 " + help_text())
    elif cmd == "/status":
        h = health()
        if h.get("ok"):
            reply(cid, "✅ Ledger online · v%s · uptime %ss" % (h.get("version", "?"), h.get("uptime", "?")))
        else:
            reply(cid, "⚠️ Ledger unavailable: %s" % h.get("error", "unknown"))
    elif cmd == "/pricing":
        reply(cid, "Ledger free · Ledger+ Solo $7/mo · Team $29/mo\n" + SITE + "/pricing", preview=True)
    elif cmd == "/channel":
        reply(cid, "Telegram channel: https://t.me/ledger_os", preview=True)
    elif cmd == "/github":
        reply(cid, "Latest release: https://github.com/voidwhisperr/ledger/releases/latest", preview=True)
    elif cmd == "/id":
        reply(cid, "chat_id: %s" % cid)


def poll():
    offset = 0
    print("polling as", api("getMe").get("result", {}).get("username"))
    while True:
        try:
            data = api("getUpdates", {"offset": offset, "timeout": 25}, timeout=35)
            for upd in data.get("result", []):
                offset = max(offset, int(upd.get("update_id", 0)) + 1)
                msg = upd.get("message") or upd.get("channel_post")
                if msg:
                    handle(msg)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print("poll error:", e, file=sys.stderr)
            time.sleep(3)


def _val(args, name):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            return args[i + 1]
    return ""


def _compose(parts):
    blocks = []
    labels = {"en": "🇬🇧 English", "uk": "🇺🇦 Українська", "ru": "🇷🇺 Русский"}
    for lang in ("en", "uk", "ru"):
        txt = (parts.get(lang) or "").strip()
        if txt:
            blocks.append(labels[lang] + "\n" + txt)
    return "\n\n──────────\n\n".join(blocks)


def main():
    args = sys.argv[1:]
    chat = _val(args, "--chat") or CHANNEL
    split = "--split" in args
    dry = "--dry-run" in args
    parts = {}

    if "--post-json" in args:
        raw = pathlib.Path(_val(args, "--post-json")).read_text(encoding="utf-8")
        data = json.loads(raw)
        parts = {k: str(data.get(k) or "") for k in ("en", "uk", "ru")}
    elif any(k in args for k in ("--en", "--uk", "--ru")):
        parts = {"en": _val(args, "--en"), "uk": _val(args, "--uk"), "ru": _val(args, "--ru")}
    elif "--post" in args:
        parts = {"en": _val(args, "--post")}
    elif "--post-file" in args:
        parts = {"en": pathlib.Path(_val(args, "--post-file")).read_text(encoding="utf-8")}

    body = _compose(parts) if parts else ""
    if not body:
        poll()
        return
    if dry:
        print(body)
        return
    messages = ([parts["en"] or "", parts["uk"] or "", parts["ru"] or ""]
                if split else [body])
    results = []
    for text in messages:
        if not text.strip():
            continue
        r = api("sendMessage", {"chat_id": chat, "text": text, "disable_web_page_preview": False})
        results.append({"ok": r.get("ok"), "message_id": (r.get("result") or {}).get("message_id"),
                        "error": r.get("description")})
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
