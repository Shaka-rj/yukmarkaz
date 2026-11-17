import asyncio
import aiosqlite
import sys
from pathlib import Path

from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import BOT_TOKEN

DB_PATH = str(BASE_DIR / "storage" / "bot_users.db")
MP3_PATH = str(BASE_DIR / "storage" / "announcement.mp3")


async def main():
    bot = Bot(token=BOT_TOKEN)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 E'lonlarni ko'rish")],
            [KeyboardButton(text="🔀 Yunalishni tanlash")],
            [KeyboardButton(text="💳 Balans")]
        ],
        resize_keyboard=True
    )

    voice = FSInputFile(MP3_PATH)

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT chat_id FROM users") as cursor:
            users = await cursor.fetchall()

    success = 0
    failed = 0

    for (chat_id,) in users:
        try:
            await bot.send_voice(
                chat_id=chat_id,
                voice=voice,
                reply_markup=keyboard
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