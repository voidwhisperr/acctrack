# Commit conventions

History should read like a release log, not a tool log. One commit = one logical change.

## Format

```
type(scope): imperative summary

Why this change is needed and what users get.

Verified: <tests/manual checks>
```

Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `build`, `ci`, `chore`.
Scopes: `app`, `desktop`, `community`, `billing`, `auth`, `hosting`, `telegram`, `discord`, `docs`.

## Rules

- Summary ≤ 72 chars, imperative mood ("add", "fix", not "added").
- Body explains **why** and user impact, not which tool was used.
- Batch related edits: UI + translation + changelog for one feature = one commit.
- Do not commit after every agent step, build or verification run.
- Tests/verification line is required for functional changes.
- No `wip`, `test`, `update`, `fixes` as bare messages.

## Examples

Good:
```
feat(community): add Telegram and Discord links to app UI

Branded buttons in the header and contact panel; login and pricing also
link both communities. Mobile shows icon-only buttons.

Verified: Playwright header/contact checks, /login and /pricing 200,
release v1.66.21 installed and signed.
```
```
fix(telegram): prevent empty posts from starting a second poller
```

Bad:
```
discord: automod, mention permissions, pinned channel guide
update docs
test
```

## Release commits

Group each release into one commit `release: vX.Y.Z` with a short changelog
summary, then tag it. Bot/documentation-only changes go in one `chore(community)`
commit per batch, not one commit per file.