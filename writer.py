import hashlib
import aiosqlite
from pathlib import Path
from utils.region_detector import find_regions
from config import ABBOS_GROUP_ID
from send import send_message
import re
from utils.filter import mini_cars
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "storage" / "yuklar.db"

UZB_TZ = timezone(timedelta(hours=5))


def get_md5(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode('utf-8')).hexdigest()


async def is_duplicate(db: aiosqlite.Connection, message_hash: str) -> bool:
    async with db.execute("""
        SELECT 1 FROM loads 
        WHERE created_at >= DATETIME('now', '-2 hours') 
          AND message_hash = ? 
        LIMIT 1
    """, (message_hash,)) as cursor:
        row = await cursor.fetchone()
        return row is not None


async def save_load_message(text: str, region_a: str = None, region_b: str = None, chat_id: int = 0) -> bool:
    msg_hash = get_md5(text)
    now_uzb = datetime.now(UZB_TZ)
    today_uzb = now_uzb.strftime("%Y-%m-%d")

    async with aiosqlite.connect(DB_PATH) as db:
        if await is_duplicate(db, msg_hash):
            return False

        async with db.execute(
            """
            SELECT COUNT(*) 
            FROM loads 
            WHERE DATE(created_at, '+5 hours') = DATE(?)
            """,
            (today_uzb,),
        ) as cursor:
            count = (await cursor.fetchone())[0]

        yid = count + 1

        # 2. Yangi xabar bo'lsa bazaga yozamiz
        await db.execute("""
            INSERT INTO loads (message, message_hash, region_a, region_b, yid, from_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, msg_hash, region_a, region_b, yid, chat_id))
        await db.commit()
        return True

async def save_message(text: str, chat_id: int) -> bool:
    regions = find_regions(text)  # ["Toshkent"], ["Qashqadaryo", "Samarqand"] va hokazo

    region_a = regions[0] if len(regions) >= 1 else None
    region_b = regions[1] if len(regions) >= 2 else None

    # Agar regionlardan kamida biri Qashqadaryo yoki Samarqand bo'lsa
    target_regions = {"Qashqadaryo", "Samarqand"}
    if any(region in target_regions for region in regions):
        await abbos_group(text)

    saved = await save_load_message(
        text=text, 
        region_a=region_a, 
        region_b=region_b,
        chat_id=chat_id
    )
    
    return saved


async def abbos_group(text: str) -> bool:
    if mini_cars(text):
        return False
        
    return await send_message(text, chat_id=ABBOS_GROUP_ID)
