import sqlite3
from pathlib import Path

# 1. Loyiha ildizini to'g'ri aniqlaymiz (loyiha/)
# utils/ papkasidan bir pog'ona yuqoriga chiqamiz
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Storage papkasiga to'g'ri yo'l
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(exist_ok=True)  # Storage papkasi bo'lmasa yaratadi

YUKLAR_DB = STORAGE_DIR / "yuklar.db"
BOT_USERS_DB = STORAGE_DIR / "bot_users.db"


def init_db():
    # --- 1. YUKLAR.DB ---
    with sqlite3.connect(YUKLAR_DB) as conn:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS loads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            message_hash TEXT NOT NULL,
            region_a TEXT,
            region_b TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            yid INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_created_hash ON loads(created_at, message_hash);
        CREATE INDEX IF NOT EXISTS idx_region_a ON loads(region_a);
        CREATE INDEX IF NOT EXISTS idx_region_b ON loads(region_b);
        """)
    print(f"{YUKLAR_DB} tekshirildi.")

    # --- 2. BOT_USERS.DB ---
    with sqlite3.connect(BOT_USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_chat_id ON users(chat_id);
        """)
    print(f"{BOT_USERS_DB} muvaffaqiyatli yaratildi/tekshirildi.")


if __name__ == "__main__":
    init_db()