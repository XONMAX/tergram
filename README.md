# Tergram

Telegram uchun terminal mijozi. Suhbatlarni ko'rish, xabarlarga javob berish va yangi xabarlar haqida bildirishnoma olish mumkin.

## O'rnatish

```bash
python3 -m pip install telethon
```

Telegram API ma'lumotlarini muhit o'zgaruvchilarida sozlang:

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
```

So'ng ishga tushiring:

```bash
python3 terminal_tg.py
```

Telegram sessiyasi mahalliy `.session` faylida saqlanadi. Uni yoki API ma'lumotlarini GitHub'ga yuklamang.
