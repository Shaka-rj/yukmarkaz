import os
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Import handlers
from bot.handlers import start, elonlar

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Routerlarni ulash
dp.include_router(start.router)
dp.include_router(elonlar.router)

async def run_bot() -> None:
    print("Telegram Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)