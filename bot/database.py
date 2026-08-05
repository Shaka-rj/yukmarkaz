import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "yuklar.db")
USERS_DB_PATH = os.path.join(BASE_DIR, "storage", "bot_users.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_elons_by_region(region: str, page: int = 1, limit: int = 5):
    """
    Standartlashtirilgan viloyat nomi bo'yicha e'lonlarni tezkor va aniq olish.
    Mavjud idx_region_a va idx_region_b indekslaridan unumli foydalanadi.
    """
    offset = (page - 1) * limit
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Oxirgi 48 soat ichidagi mos e'lonlar sonini hisoblash
    count_query = """
        SELECT COUNT(*) as count 
        FROM loads 
        WHERE (region_a = ? OR region_b = ?)
          AND created_at >= datetime('now', '-48 hours')
    """
    cursor.execute(count_query, (region, region))
    total_items = cursor.fetchone()['count']
    
    # 2. Indekslangan ustunlar bo'yicha e'lonlarni sahifalab (pagination) olish
    select_query = """
        SELECT id, message, region_a, region_b, created_at 
        FROM loads 
        WHERE (region_a = ? OR region_b = ?)
          AND created_at >= datetime('now', '-48 hours')
        ORDER BY id DESC 
        LIMIT ? OFFSET ?
    """
    cursor.execute(select_query, (region, region, limit, offset))
    elons = cursor.fetchall()
    
    conn.close()
    
    # Jami sahifalar sonini hisoblash
    total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
    
    return elons, total_pages, total_items


def add_user(chat_id: int) -> bool:
    """Yangi foydalanuvchini loyiha/storage/bot_users.db bazasiga saqlaydi."""
    try:
        with sqlite3.connect(USERS_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (chat_id) VALUES (?)",
                (chat_id,)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"⚠️ Foydalanuvchini saqlashda xatolik: {e}")
        return False