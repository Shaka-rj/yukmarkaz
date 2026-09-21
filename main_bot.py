import asyncio
from bot.main import run_bot

async def main():
    print("Loyiha ishga tushirilmoqda...")
    
    await asyncio.gather(
        run_bot()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nLoyiha to'xtatildi.")
