import sqlite3

conn = sqlite3.connect("storage/yuklar.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE yuklar ADD COLUMN yid INTEGER;")
    conn.commit()
    print("'yid' ustuni muvaffaqiyatli qo'shildi.")
except sqlite3.OperationalError:
    print("'yid' ustuni allaqachon mavjud yoki jadval topilmadi.")

conn.close()