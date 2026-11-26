# Trilingual channel post template

Fill the three blocks, save as post.json, then run on the VPS:

```json
{
  "en": "Ledger vX.Y.Z is live.\n\n• change 1\n• change 2\n\nGitHub: https://github.com/voidwhisperr/ledger/releases/latest",
  "uk": "Ledger vX.Y.Z уже доступний.\n\n• зміна 1\n• зміна 2\n\nGitHub: https://github.com/voidwhisperr/ledger/releases/latest",
  "ru": "Ledger vX.Y.Z уже доступен.\n\n• изменение 1\n• изменение 2\n\nGitHub: https://github.com/voidwhisperr/ledger/releases/latest"
}
```

```bash
python3 ledger_os_bot.py --post-json post.json
python3 ledger_os_bot.py --split --post-json post.json   # three separate messages
```

If you write only English, `--auto` translates to UK/RU via DeepL:

```bash
python3 ledger_os_bot.py --auto --en "Ledger vX.Y.Z is live. ..."
```

Brand names are protected from translation; manual `--uk`/`--ru` override auto output.
