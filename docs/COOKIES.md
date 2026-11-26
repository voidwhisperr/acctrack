# Як додати cookie та токени платформ

Ledger не просить пароль від FunPay/ZeusX. Потрібні лише значення cookie або API-ключі, які ви копіюєте зі свого браузера/кабінету.

## FunPay (golden_key)
1. Увійдіть на https://funpay.com у Chrome/Edge.
2. F12 → **Application** → **Cookies** → `https://funpay.com`.
3. Знайдіть `golden_key`, скопіюйте **Value** (без `golden_key=`).
4. Ledger → Канали → Баланси → поле FunPay → вставте → Зберегти cookie.

## ZeusX (access_token)
1. Увійдіть на https://zeusx.com.
2. F12 → **Application** → **Cookies** → `https://zeusx.com`.
3. Знайдіть `access_token`, скопіюйте **Value**.
4. Вставте в поле ZeusX → Зберегти cookie.

## Eldorado (Seller API)
1. Увійдіть на https://www.eldorado.gg.
2. Dashboard → **Seller API** → **Generate credentials**.
3. Скопіюйте **Client ID** і **Client Secret** (секрет показується один раз).
4. Вставте обидва значення в поля Eldorado → Зберегти cookie.

## Безпека
- Ніколи не надсилайте ці значення в чат/третім особам.
- Вони зберігаються лише на вашому сервері (`.gt_secrets.json`, права 600).
- Cookie прострочуються — якщо канал показує помилку, просто оновіть значення.
- Після зміни пароля на платформі cookie може стати недійсним.

## English (short)
FunPay: F12 → Application → Cookies → `golden_key` → copy Value. ZeusX: `access_token` → copy Value. Eldorado: Dashboard → Seller API → Client ID + Secret. Never share them; they are stored only on your server.

## Русский (кратко)
FunPay: F12 → Application → Cookies → `golden_key` → скопируйте Value. ZeusX: `access_token` → Value. Eldorado: Dashboard → Seller API → Client ID + Secret. Никому не передавайте; значения хранятся только на вашем сервере.