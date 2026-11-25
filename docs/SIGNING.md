# Code signing

Ledger.exe and LedgerPlus.exe are Authenticode-signed (SHA-256, RFC 3161 timestamp).

## Status of this build

- Subject: `CN=Ledger, O=Ledger contributors, C=UA`
- Type: **self-signed** code-signing certificate (valid 2026-11-25 → 2029-11-25)
- Thumbprint: `0F3F7898E3CE20A5411D179CAF65B4A57C14AF72`
- Public certificate: [ledger-codesign.cer](ledger-codesign.cer)
- Signing time is timestamped by DigiCert, so the signature stays valid after the certificate expires.

Self-signed means: the binary is signed and the signature is intact, but Windows only shows it as
trusted after the public certificate is installed in `Trusted Root Certification Authorities` and
`Trusted Publishers`. On the build machine this was done for the current user, so
`Get-AuthenticodeSignature` returns `Valid`.

To trust it on another PC (current user, no admin):

```powershell
certutil -user -addstore Root ledger-codesign.cer
certutil -user -addstore TrustedPublisher ledger-codesign.cer
```

## For public distribution

A self-signed certificate does **not** remove the SmartScreen warning for other people. For a clean
reputation buy an OV or EV code-signing certificate from a public CA and sign with it:

```powershell
$env:LEDGER_SIGN_PFX  = 'C:\secure\codesign.pfx'
$env:LEDGER_SIGN_PASS = '...'
powershell -ExecutionPolicy Bypass -File scripts\sign_windows.ps1 -Files dist\Ledger.exe,dist\LedgerPlus.exe
```

The private key (`.pfx`) and its password are never committed. The script verifies every signature
and exits non-zero if any file stays unsigned or untrusted.

## Verify a release

```powershell
Get-AuthenticodeSignature .\Ledger.exe | Format-List Status, StatusMessage, SignerCertificate
Get-FileHash .\Ledger.exe -Algorithm SHA256
```

Compare the hash with `SHA256SUMS.txt` attached to the GitHub release.
