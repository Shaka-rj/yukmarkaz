import hashlib
import aiosqlite
from pathlib import Path
from utils.region_detector import find_regions
from config import ABBOS_GROUP_ID
from send import send_message
import re

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
        region_b=region_b
    )
    
    return saved



def extract_max_weight(text: str) -> float | None:
    pattern = r'(\d+(?:[\.,]\d+)?)(?:\s*-\s*(\d+(?:[\.,]\d+)?))?\s*(?:tonna|tona|tn|тн|тонна|[tт])\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if not matches:
        return None
    
    max_weight = 0.0
    for match in matches:
        val1 = float(match[0].replace(',', '.'))
        val2 = float(match[1].replace(',', '.')) if match[1] else val1
        
        current_max = max(val1, val2)
        if current_max > max_weight:
            max_weight = current_max
            
    return max_weight


async def abbos_group(text: str) -> bool:
    # 1. Isuzu/Исузу tekshiruvi
    if re.search(r'\b(isuzu|исузу)\b', text, re.IGNORECASE):
        print("⛔ Filtirdan o'tmadi: Matnda Isuzu/Исузу bor")
        return False

    # 2. Tonna tekshiruvi (3 tonnadan ko'p bo'lsa)
    weight = extract_max_weight(text)
    if weight is not None and weight > 3:
        print(f"⛔ Filtirdan o'tmadi: {weight} tonna (3 t-dan ko'p)")
        return False

    return await send_message(text, chat_id=ABBOS_GROUP_ID)
