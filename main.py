import asyncio
from read import start_reading
from bot.main import run_bot
from utils.database_cleaner import start_cleaner

async def main():
    print("Loyiha ishga tushirilmoqda...")
    
    await asyncio.gather(
        start_reading(),               # 1. Telegram xabarlarini o'qish (INSERT)
        run_bot(),                     # 2. Bot xizmati (SELECT)
        start_cleaner(interval_seconds=3600)  # 3. Har 1 soatda bazani tozalash (DELETE)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLoyiha to'xtatildi.")
