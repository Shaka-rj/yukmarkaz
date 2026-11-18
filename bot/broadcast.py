import asyncio
import aiosqlite
import sys
from pathlib import Path

from aiogram import Bot
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import BOT_TOKEN

DB_PATH = str(BASE_DIR / "storage" / "bot_users.db")
MP3_PATH = str(BASE_DIR / "storage" / "announcement2.mp3")

# Yangi guruh havolasi
GROUP_URL = "https://t.me/TEZKOR_YUK_MARKAZ"


async def main():
    bot = Bot(token=BOT_TOKEN)

    # Asosiy menyu
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 E'lonlarni ko'rish")],
            [KeyboardButton(text="🔀 Yunalishni tanlash")],
            [KeyboardButton(text="💳 Balans")]
        ],
        resize_keyboard=True
    )

    # Guruhga o'tish tugmasi
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Guruhga kirish",
                    url=GROUP_URL
                )
            ]
        ]
    )

    voice = FSInputFile(MP3_PATH)

    # Foydalanuvchilarni olish
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            users = await cursor.fetchall()

    success = 0
    failed = 0

    for (chat_id,) in users:
        try:
            # 1. Ovozli xabar
            await bot.send_voice(
                chat_id=chat_id,
                voice=voice,
                reply_markup=keyboard
            )

            # 2. Matnli xabar
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "📢 Yangi guruh: @TEZKOR_YUK_MARKAZ"
                ),
                reply_markup=inline_keyboard
            )

            success += 1

        except Exception as e:
            failed += 1
            print(f"Xatolik ({chat_id}): {e}")

        await asyncio.sleep(0.05)

    print("\nTarqatish yakunlandi!")
    print(f"Jami: {len(users)}")
    print(f"Yuborildi: {success}")
    print(f"Yuborilmadi: {failed}")

    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())