# Ledger OS Discord bot

Application: Ledger OS (bot user id 1575563676146999430).
Server: Ledger OS (guild 1575546706756640821).

Token: /root/discord-bot.token (0600); channel id: /root/discord-channel.id.
Service: ledger-discord-bot.service (venv /root/ledger-discord-venv, discord.py 2.7.1).

## Channels
Public category `Ledger OS`:
- `#announcements` 1575566227059773460 (read-only; bot posts)
- `#updates` 1575566228364337314
- `#guides` 1575566229815693374
- `#q-and-a` 1575566231472177155
- `#off-topic` 1575566236916654162

Private category `STAFF`:
- `#admin-chat` 1575566240083087400
- `#mod-log` 1575566241450561556
- `#bot-log` 1575566243417825320

## Posting
```bash
/root/ledger-discord-venv/bin/python /root/ledger_discord_bot.py --post-json post.json
/root/ledger-discord-venv/bin/python /root/ledger_discord_bot.py --post "text"
```
JSON: {"en":"...","uk":"...","ru":"..."} (labels added automatically, no flags).

Discord verification is not required for a private bot.
