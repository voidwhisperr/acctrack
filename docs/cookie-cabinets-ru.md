# Cookie-кабинеты — подключение FunPay, ZeusX и Eldorado

Блок **Cookie-кабинеты** подключает твои каналы продаж к Ledger.

## Что он делает

- подключает FunPay, ZeusX и Eldorado
- показывает балансы, заказы/продажи и лоты
- импортирует новые заказы в **Orders**
- включает **Always online** для каждого канала

## Как подключить

1. Открой кабинет канала и скопируй значение:
   - FunPay: F12 → Application → Cookies → `golden_key`
   - ZeusX: F12 → Application → Cookies → `access_token`
   - Eldorado: Dashboard → Seller API → Client ID + Client Secret
2. Вставь в соответствующее поле в Ledger.
3. Нажми **Save cookie**.
4. Ledger обновляет кабинет не чаще раза в 2 минуты.

Никому не передавай эти значения. Они хранятся на твоём сервере и не отправляются в Ledger.

## Полный гайд

- [EN](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-en.md)
- [UA](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-ua.md)
