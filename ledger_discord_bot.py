#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ledger OS Discord bot + REST poster.

Token lookup: $DISCORD_BOT_TOKEN, /root/discord-bot.token, or Downloads/Ledger-Desktop/discord-bot.token
Channel lookup: $DISCORD_CHANNEL_ID, /root/discord-channel.id, or first text channel of the first guild.

Run:
  python ledger_discord_bot.py --run
  python ledger_discord_bot.py --post-json post.json
"""
import json
import os
import pathlib
import sys
import urllib.request

import discord
from discord import app_commands

API = "https://discord.com/api/v10"
SITE = "https://ledger.70-34-243-50.sslip.io"


def token():
    t = (os.environ.get("DISCORD_BOT_TOKEN") or "").strip()
    if t:
        return t
    here = pathlib.Path(__file__).resolve().parent
    for p in (pathlib.Path("/root/discord-bot.token"), here / "discord-bot.token",
              pathlib.Path.home() / "Downloads" / "Ledger-Desktop" / "discord-bot.token"):
        try:
            if p.is_file():
                return p.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    raise SystemExit("no Discord bot token")


def rest(method, path, payload=None):
    import urllib.error, time
    last = None
    for attempt in range(4):
        req = urllib.request.Request(API + path,
                                     data=json.dumps(payload or {}).encode("utf-8") if payload is not None else None,
                                     headers={"Authorization": "Bot " + token(),
                                              "Content-Type": "application/json",
                                              "User-Agent": "LedgerOSBot/1.0"},
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", "replace")
            try:
                data = json.loads(raw)
            except Exception:
                data = {}
            if e.code == 429:
                time.sleep(min(float(data.get("retry_after") or 2), 30))
                last = e
                continue
            if e.code >= 500 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                last = e
                continue
            raise RuntimeError("Discord %s: %s" % (e.code, raw[:300]))
    raise RuntimeError("Discord failed after retries: %s" % last)


def channel_id():
    cid = (os.environ.get("DISCORD_CHANNEL_ID") or "").strip()
    if cid:
        return cid
    for p in (pathlib.Path("/root/discord-channel.id"),
              pathlib.Path.home() / "Downloads" / "Ledger-Desktop" / "discord-channel.id"):
        try:
            if p.is_file():
                v = p.read_text(encoding="utf-8").strip()
                if v:
                    return v
        except OSError:
            pass
    guilds = rest("GET", "/users/@me/guilds")
    if guilds:
        chans = rest("GET", "/guilds/%s/channels" % guilds[0]["id"])
        text = [c for c in chans if c.get("type") == 0]
        for c in text:
            if c.get("name", "").lower() in ("general", "загальний"):
                return c["id"]
        if text:
            return text[0]["id"]
    return ""


def send_text(cid, text):
    text = (text or "").strip()
    while text:
        chunk, text = text[:1900], text[1900:]
        cut = chunk.rfind("\n")
        if cut > 200 and len(text) > 0:
            text = chunk[cut + 1:] + text
            chunk = chunk[:cut]
        rest("POST", "/channels/%s/messages" % cid, {"content": chunk, "allowed_mentions": {"parse": []}})
    return True


def health():
    try:
        with urllib.request.urlopen(SITE + "/api/health", timeout=10) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        return {"ok": False, "error": str(e)[:80]}


def compose(parts):
    labels = {"en": "English", "uk": "Українська", "ru": "Русский"}
    blocks = []
    for lang in ("en", "uk", "ru"):
        txt = (parts.get(lang) or "").strip()
        if txt:
            blocks.append(labels[lang] + "\n" + txt)
    return "\n\n──────────\n\n".join(blocks)


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    try:
        synced = await tree.sync()
        print("discord ready as", client.user, "commands:", len(synced), flush=True)
    except Exception as e:
        print("sync error:", e, flush=True)


@tree.command(name="status", description="Ledger server status")
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    h = health()
    if h.get("ok"):
        await interaction.followup.send("✅ Ledger online · v%s · uptime %ss" % (h.get("version", "?"), h.get("uptime", "?")), ephemeral=True)
    else:
        await interaction.followup.send("⚠️ Ledger unavailable: %s" % h.get("error", "unknown"), ephemeral=True)


@tree.command(name="pricing", description="Free vs Ledger+ pricing")
async def pricing_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("Ledger free · Ledger+ Solo $7/mo · Team $29/mo\n%s/pricing" % SITE, ephemeral=True)


@tree.command(name="channel", description="Telegram channel")
async def channel_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("Telegram: https://t.me/ledger_os", ephemeral=True)


@tree.command(name="discord", description="Discord community invite")
async def discord_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("Discord: https://discord.gg/eMBXnKA3Pa", ephemeral=True)


@tree.command(name="github", description="Latest Ledger release")
async def github_cmd(interaction: discord.Interaction):
    await interaction.response.send_message("https://github.com/voidwhisperr/ledger/releases/latest", ephemeral=True)


@tree.command(name="faq", description="Common Ledger questions")
async def faq_cmd(interaction: discord.Interaction):
    txt = ("FAQ\n\n"
           "• Is Ledger free? Yes, local bookkeeping is free.\n"
           "• What is Ledger+? Hosting, Taobao agent, auto-import, team roles.\n"
           "• Can I move my key? Deactivate on the old device, activate on the new one.\n"
           "• Where is my data? Locally; Ledger+ runs on your VPS.\n\n"
           "More: https://t.me/ledger_os")
    await interaction.response.send_message(txt, ephemeral=True)


def main():
    args = sys.argv[1:]
    if "--post-json" in args:
        i = args.index("--post-json")
        data = json.loads(pathlib.Path(args[i + 1]).read_text(encoding="utf-8"))
        parts = data if "en" in data else {"en": data.get("content", "")}
        text = compose(parts)
        cid = channel_id()
        if "--dry-run" in args:
            print(text)
            return
        if not cid:
            raise SystemExit("no channel id")
        send_text(cid, text)
        print("posted")
        return
    if "--post" in args:
        i = args.index("--post")
        text = args[i + 1]
        cid = channel_id()
        if not cid:
            raise SystemExit("no channel id")
        send_text(cid, text)
        print("posted")
        return
    client.run(token())


if __name__ == "__main__":
    main()
