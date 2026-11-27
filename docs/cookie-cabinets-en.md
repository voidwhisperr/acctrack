# Cookie cabinets — connect FunPay, ZeusX and Eldorado

The **Cookie cabinets** block connects your sales channels to Ledger.

## What it does

- connects FunPay, ZeusX and Eldorado
- shows balances, orders/sales and lots
- imports new orders into **Orders**
- enables **Always online** for each channel

## How to connect

1. Open the channel cabinet and copy the value:
   - FunPay: F12 → Application → Cookies → `golden_key`
   - ZeusX: F12 → Application → Cookies → `access_token`
   - Eldorado: Dashboard → Seller API → Client ID + Client Secret
2. Paste it into the matching field in Ledger.
3. Click **Save cookie**.
4. Ledger refreshes the cabinet no more than once every 2 minutes.

Never share these values. They stay on your server and are not sent to Ledger.

## Full guide in your language

- [UA](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-ua.md)
- [RU](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-ru.md)
