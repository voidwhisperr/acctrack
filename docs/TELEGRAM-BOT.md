# Ledger OS Telegram bot (@LedgerOSHelperBot)

1. BotFather: copy the token. Do NOT paste it into chat or commits.
2. Save the token as one line to:
   `C:/Users/User/Downloads/Ledger-Desktop/ledger-os-bot.token`
   (or set env `LEDGER_OS_BOT_TOKEN`).
3. Add @LedgerOSHelperBot to the channel: Manage Channel -> Administrators -> Add Admin -> Post Messages.
4. Post a test message:
   `python ledger_os_bot.py --post "Ledger OS is live"`
5. Run interactive commands:
   `python ledger_os_bot.py --poll`
   Commands: /start /help /status /pricing /channel /github /id

Token file is ignored by git and never bundled into the exe.

## Trilingual posts (EN + UA + RU)

One combined post:
```
python3 ledger_os_bot.py --en "English text" --uk "Український текст" --ru "Русский текст"
```

Three separate messages:
```
python3 ledger_os_bot.py --split --en "..." --uk "..." --ru "..."
```

From a JSON file:
```
python3 ledger_os_bot.py --post-json post.json
# {"en":"...","uk":"...","ru":"..."}
```

Preview without sending: add `--dry-run`.

Hosted on the VPS as systemd unit `ledger-os-bot.service` (WorkingDirectory /root, token /root/ledger-os-bot.token, 0600).


## Automatic translation (DeepL)

Save the DeepL key locally as `deepl.key` (or env `DEEPL_API_KEY`):
- Windows: `C:/Users/User/Downloads/Ledger-Desktop/deepl.key`
- VPS: `/root/deepl.key` (0600)

One key works for all target languages; the bot makes one request per language.

```
python3 ledger_os_bot.py --auto --en "Ledger OS is live."
python3 ledger_os_bot.py --auto --split --en "..."
```

Brand names (Ledger OS, Reseller OS, Ledger+, FunPay, ZeusX, Eldorado, Taobao, P&L, GitHub, Telegram, Discord) are protected from translation. Any supplied `--uk`/`--ru` overrides the automatic translation.
