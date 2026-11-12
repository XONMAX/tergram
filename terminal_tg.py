import asyncio
import itertools
import os
import sys
from telethon import TelegramClient, events

# Telegram API ma'lumotlari
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
if not API_ID or not API_HASH:
    raise RuntimeError(
        "TELEGRAM_API_ID va TELEGRAM_API_HASH muhit o'zgaruvchilarini sozlang."
    )

try:
    API_ID = int(API_ID)
except ValueError as error:
    raise ValueError("TELEGRAM_API_ID butun son bo'lishi kerak.") from error

# Telethon mijoz sessiyasini ishga tushirish
client = TelegramClient('my_terminal_session', API_ID, API_HASH)
settings = {"animations": True}


async def settings_menu():
    while True:
        animation_status = "Yoqilgan" if settings["animations"] else "O'chirilgan"
        print("\n--- Sozlamalar ---")
        print(f"[1] Yuklanish animatsiyalari: {animation_status}")
        print("[/back] Ortga qaytish")
        choice = (await asyncio.to_thread(input, "Tanlov: ")).strip().lower()
        if choice == "/back":
            return
        if choice == "1":
            settings["animations"] = not settings["animations"]
        else:
            print("Noto'g'ri tanlov. Qayta urinib ko'ring.")


@client.on(events.NewMessage(incoming=True))
async def show_new_message(event):
    sender = await event.get_sender()
    sender_name = (
        getattr(sender, "first_name", None)
        or getattr(sender, "title", None)
        or "Noma'lum"
    )
    text = event.message.text or "[Media/Stiker]"
    message_time = event.message.date.astimezone().strftime("%H:%M")
    print(f"{sender_name} [{message_time}]: {text}", flush=True)


async def animate(message):
    frames = itertools.cycle(("◐", "◓", "◑", "◒"))
    dots = itertools.cycle(("", ".", "..", "..."))
    while True:
        print(f"\r{next(frames)} {message}{next(dots)}", end="", flush=True)
        await asyncio.sleep(0.1)


async def with_animation(operation, message):
    if not sys.stdout.isatty() or not settings["animations"]:
        print(f"{message}...")
        return await operation

    animation = asyncio.create_task(animate(message))
    try:
        return await operation
    finally:
        animation.cancel()
        try:
            await animation
        except asyncio.CancelledError:
            pass
        print("\r\033[K", end="", flush=True)


async def main():
    await with_animation(client.start(), "Telegramga ulanmoqda")

    me = await client.get_me()
    username = f"@{me.username}" if me.username else "Foydalanuvchi nomi yo'q"
    print(f"\nTelegramga muvaffaqiyatli kirdingiz: {me.first_name} ({username})\n")

    while True:
        dialogs = await with_animation(
            client.get_dialogs(limit=10), "Yaqin suhbatlar yuklanmoqda"
        )

        print("\n--- Yaqin suhbatlar ---")
        for i, dialog in enumerate(dialogs):
            print(f"[{i}] {dialog.name} (O'qilmagan: {dialog.unread_count})")
        print("[q] Chiqish  |  /settings Sozlamalar")

        choice = (await asyncio.to_thread(
            input, "\nSuhbat indeksini tanlang, /settings yozing yoki 'q' bilan chiqing: "
        )).strip()
        if choice.lower() == 'q':
            break
        if choice.lower() == "/settings":
            await settings_menu()
            continue

        try:
            selected_dialog = dialogs[int(choice)]
        except (ValueError, IndexError):
            print("Noto'g'ri tanlov. Qayta urinib ko'ring.")
            continue

        print(f"\n--- Ochilgan suhbat: {selected_dialog.name} ---")

        messages = await with_animation(
            client.get_messages(selected_dialog.entity, limit=15),
            "Oxirgi 15 ta xabar yuklanmoqda",
        )
        for msg in reversed(messages):
            sender_name = msg.sender.first_name if msg.sender else "Noma'lum"
            text = msg.text or "[Media/Stiker]"
            print(f"[{sender_name}]: {text}")

        print("\nJavob yozing (suhbatlar ro'yxatiga qaytish uchun 'orqaga' deb yozing):")
        while True:
            reply_text = (await asyncio.to_thread(input, ">> ")).strip()
            command = reply_text.lower()
            if command in ("/back", "orqaga"):
                break
            if command == "/settings":
                await settings_menu()
                continue
            if reply_text:
                await with_animation(
                    client.send_message(selected_dialog.entity, reply_text),
                    "Xabar yuborilmoqda",
                )
                print("-> Xabar yuborildi!")

with client:
    client.loop.run_until_complete(main())