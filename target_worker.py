import asyncio
import aiosqlite

from telethon import TelegramClient
from pathlib import Path
from config import API_ID, API_HASH
from data.target_group import target_regions

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "storage" / "yuklar.db"


client = TelegramClient("target_session", API_ID, API_HASH)


async def get_new_loads(last_id):
    async with aiosqlite.connect(DB_PATH) as db:

        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT
                id,
                message,
                region_a,
                region_b,
                from_id
            FROM loads
            WHERE id > ?
            ORDER BY id ASC
            """,
            (last_id,)
        ) as cursor:

            return await cursor.fetchall()


async def start_target_worker():

    print("Target worker ishga tushmoqda...")

    await client.start()

    print("Target session ishga tushdi.")

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

                # Shu e'lon qaysi viloyat uchun target qilingan?
                target_chats = target_regions.get(region_a)

                if not target_chats:

                    last_id = load_id
                    continue

                # E'lonni viloyatning barcha target guruhlariga yuborish
                for target_chat_id in target_chats:

                    # E'lon aynan shu guruhdan olingan bo'lsa,
                    # qaytadan o'sha guruhga yubormaymiz
                    if from_id == target_chat_id:

                        print(
                            f"[SKIP] #{load_id} | "
                            f"{region_a} | "
                            f"source target guruhning o'zi"
                        )

                        continue

                    try:

                        await client.send_message(
                            target_chat_id,
                            message
                        )

                        print(
                            f"[SEND] #{load_id} | "
                            f"{region_a} → {target_chat_id}"
                        )

                    except Exception as e:

                        print(
                            f"[ERROR] #{load_id} | "
                            f"{target_chat_id} | {e}"
                        )

                last_id = load_id

        except Exception as e:

            print(f"[TARGET WORKER] Xato: {e}")

        await asyncio.sleep(2)