import hashlib
import aiosqlite
from pathlib import Path
from utils.region_detector import find_regions

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "storage" / "yuklar.db"


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


async def save_load_message(text: str, region_a: str = None, region_b: str = None) -> bool:
    msg_hash = get_md5(text)

    async with aiosqlite.connect(DB_PATH) as db:
        if await is_duplicate(db, msg_hash):
            return False

        # 2. Yangi xabar bo'lsa bazaga yozamiz
        await db.execute("""
            INSERT INTO loads (message, message_hash, region_a, region_b)
            VALUES (?, ?, ?, ?)
        """, (text, msg_hash, region_a, region_b))
        await db.commit()
        return True

async def save_message(text: str) -> bool:
    regions = find_regions(text)  # Massiv qaytaradi: [], ["Toshkent"] yoki ["Toshkent", "Samarqand"]

    region_a = None
    region_b = None

    if len(regions) == 1:
        region_a = regions[0]
    elif len(regions) >= 2:
        region_a = regions[0]
        region_b = regions[1]

    saved = await save_load_message(
        text=text, 
        region_a=region_a, 
        region_b=region_b
    )
    
    return saved