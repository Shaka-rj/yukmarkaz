import sqlite3
import os
import asyncio

# Loyiha ildizi va baza manzilini aniqlash
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "yuklar.db")

def clean_old_loads():
    """48 soatdan eski e'lonlarni bazadan o'chirib tashlash"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # created_at < 48 soat oldingi vaqt bo'lganlarni o'chirish
        cursor.execute(
            """
            DELETE FROM loads 
            WHERE created_at < datetime('now', '-48 hours')
            """
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ [Cleaner Error] Eski e'lonlarni o'chirishda xatolik: {e}")

async def start_cleaner(interval_seconds: int = 3600):
    while True:
        clean_old_loads()
        await asyncio.sleep(interval_seconds)