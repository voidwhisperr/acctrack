# Ledger OS Discord bot

Application: Ledger OS (bot user id 1575563676146999430).
Server: Ledger OS (guild 1575546706756640821), channel: #загальний (1575546709185134724).

Token: /root/discord-bot.token (0600); channel id: /root/discord-channel.id.
Service: ledger-discord-bot.service (venv /root/ledger-discord-venv, discord.py 2.7.1).

## Commands
/status /pricing /channel /github /faq

## Posting
```bash
/root/ledger-discord-venv/bin/python /root/ledger_discord_bot.py --post-json post.json
/root/ledger-discord-venv/bin/python /root/ledger_discord_bot.py --post "text"
```
JSON format: {"en":"...","uk":"...","ru":"..."} (labels added automatically, no flags).

Do not enable Discord App Directory verification unless the bot should be public on 100+ servers.
