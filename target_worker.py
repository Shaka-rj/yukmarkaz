import asyncio
import aiosqlite

from telethon import TelegramClient
from pathlib import Path
from config import API_ID, API_HASH

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "storage" / "yuklar.db"


TARGET_REGION = "Qashqadaryo"
TARGET_CHAT_ID = -1001753572530

client = TelegramClient(
    "target_session",
    API_ID,
    API_HASH
)


async def get_new_loads(last_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT id, message, region_a, region_b, from_id
            FROM loads
            WHERE id > ?
            ORDER BY id ASC
            """,
            (last_id,)
        ) as cursor:

            return await cursor.fetchall()


async def start_target_worker():

    print("Target worker ishga tushdi.")

    await client.start()

    # Eski e'lonlarni o'tkazib yuboramiz
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COALESCE(MAX(id), 0) FROM loads"
        ) as cursor:
            last_id = (await cursor.fetchone())[0]

    print(f"Boshlang'ich ID: {last_id}")

    while True:

        try:
            loads = await get_new_loads(last_id)

            for load in loads:

                load_id = load["id"]
                message = load["message"]
                region_a = load["region_a"]
                from_id = load["from_id"]

                # Faqat Qashqadaryodan chiqadigan yuklar
                if region_a != TARGET_REGION:
                    last_id = load_id
                    continue

                # O'zimiz yuboradigan guruhdan olingan
                # xabarni yana o'sha guruhga yubormaymiz
                if from_id == TARGET_CHAT_ID:
                    print(
                        f"[TARGET] #{load_id} o'tkazib yuborildi: "
                        f"source = target group"
                    )

                    last_id = load_id
                    continue

                try:

                    await client.send_message(
                        TARGET_CHAT_ID,
                        message
                    )

                    print(
                        f"[TARGET] #{load_id} → "
                        f"{TARGET_REGION} guruhiga yuborildi"
                    )

                except Exception as e:

                    print(
                        f"[TARGET] #{load_id} yuborishda xato: {e}"
                    )

                last_id = load_id

        except Exception as e:
            print(f"[TARGET WORKER] Xato: {e}")

        await asyncio.sleep(2)