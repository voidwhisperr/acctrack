# Cookie-кабінети — підключення FunPay, ZeusX та Eldorado

Блок **Cookie-кабінети** підключає твої канали продажів до Ledger.

## Що він робить

- підключає FunPay, ZeusX та Eldorado
- показує баланси, замовлення/продажі та лоти
- імпортує нові замовлення в **Orders**
- вмикає **Always online** для кожного каналу

## Як підключити

1. Відкрий кабінет каналу та скопіюй значення:
   - FunPay: F12 → Application → Cookies → `golden_key`
   - ZeusX: F12 → Application → Cookies → `access_token`
   - Eldorado: Dashboard → Seller API → Client ID + Client Secret
2. Встав у відповідне поле в Ledger.
3. Натисни **Save cookie**.
4. Ledger оновлює кабінет не частіше ніж раз на 2 хвилини.

Нікому не передавай ці значення. Вони зберігаються на твоєму сервері й не надсилаються в Ledger.

## Повний гайд

- [EN](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-en.md)
- [RU](https://github.com/voidwhisperr/ledger/blob/main/docs/cookie-cabinets-ru.md)
