import asyncio
import sqlite3
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest
from keyboards.reply import get_main_keyboard

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bazaga yo'l
DB_PATH = "../storage/bot_users.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_all_user_ids():
    """SQLite bazasidan barcha chat_id larni oladi."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows if row[0]]
    except Exception as e:
        logging.error(f"Baza bilan bog'lanishda xatolik: {e}")
        return []


async def send_message_to_user(bot: Bot, chat_id: int, text: str, reply_markup=None) -> bool:
    """Bitta foydalanuvchiga xabar va tugmani yuborish funksiyasi."""
    try:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=reply_markup)
        return True
    except TelegramRetryAfter as e:
        logging.warning(f"Flood limit! {e.retry_after} soniya kutilmoqda...")
        await asyncio.sleep(e.retry_after)
        return await send_message_to_user(bot, chat_id, text, reply_markup)
    except TelegramForbiddenError:
        logging.warning(f"User {chat_id} botni bloklagan.")
        return False
    except TelegramBadRequest as e:
        logging.warning(f"User {chat_id} uchun xatolik: {e}")
        return False
    except Exception as e:
        logging.error(f"Xabar yuborishda kutilmagan xatolik ({chat_id}): {e}")
        return False


async def main():
    bot = Bot(token=BOT_TOKEN)
    
    # 1. Yuboriladigan xabar matni
    broadcast_text = (
        "📢 <b>Diqqat, e'lon!</b>\n\n"
        "Botimizga yangi imkoniyatlar va yo'nalishlar qo'shildi. "
        "2 ta viloyatni tanlab yuklarni qidiring. Misol: Toshkent-Qashqadaryo"
    )
    
    user_ids = get_all_user_ids()
    total_users = len(user_ids)
    logging.info(f"Jami {total_users} ta foydalanuvchi topildi. Xabar yuborish boshlanmoqda...")

    success_count = 0
    fail_count = 0

    for idx, chat_id in enumerate(user_ids, start=1):
        # send_message_to_user funksiyasiga reply_markup argumentini berib yuboramiz
        is_sent = await send_message_to_user(bot, chat_id, broadcast_text, reply_markup=get_main_keyboard())
        
        if is_sent:
            success_count += 1
        else:
            fail_count += 1

        await asyncio.sleep(0.05)

        if idx % 20 == 0 or idx == total_users:
            logging.info(f"Jarayon: {idx}/{total_users} ({success_count} muvaffaqiyatli, {fail_count} xato)")

    logging.info(f"✅ Xabarnoma yakunlandi!\nMuvaffaqiyatli: {success_count}\nYuborilmadi: {fail_count}")

    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())