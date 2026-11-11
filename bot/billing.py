import os
import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any, Awaitable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "storage", "bot_users.db")
TZ = ZoneInfo("Asia/Tashkent")

DAILY_PRICE = 1000
DEBT_LIMIT = -20000
TEMP_ACCESS_HOURS = 24


def now():
    return datetime.now(TZ)


def connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 15000")
    return conn


def init_billing_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS billing_accounts (
                chat_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0,
                last_charge_date TEXT,
                pending_until TEXT,
                blocked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS billing_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                file_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewed_by INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS billing_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )
        """)
        db.commit()


def ensure_account(chat_id: int):
    stamp = now().isoformat(timespec="seconds")
    with connect() as db:
        db.execute("""
            INSERT OR IGNORE INTO billing_accounts
                (chat_id, balance, created_at, updated_at)
            VALUES (?, 0, ?, ?)
        """, (chat_id, stamp, stamp))
        db.commit()


def get_account(chat_id: int):
    ensure_account(chat_id)
    with connect() as db:
        return db.execute(
            "SELECT * FROM billing_accounts WHERE chat_id = ?", (chat_id,)
        ).fetchone()


def charge_and_check(chat_id: int):
    """Kuniga bir marta 1000 so'm yechadi. (allowed, balance, reason)."""
    ensure_account(chat_id)
    current = now()
    stamp = current.isoformat(timespec="seconds")
    today = current.date().isoformat()

    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        account = db.execute(
            "SELECT * FROM billing_accounts WHERE chat_id = ?", (chat_id,)
        ).fetchone()

        # Chek tekshirilayotgan davrda 24 soatlik vaqtinchalik ruxsat.
        pending_until = account["pending_until"]
        if pending_until:
            try:
                if datetime.fromisoformat(pending_until) > current:
                    db.commit()
                    return True, account["balance"], "pending"
            except ValueError:
                pass

        if account["blocked"]:
            db.commit()
            return False, account["balance"], "blocked"

        if account["last_charge_date"] != today:
            new_balance = account["balance"] - DAILY_PRICE
            db.execute("""
                UPDATE billing_accounts
                SET balance = ?, last_charge_date = ?, updated_at = ?
                WHERE chat_id = ?
            """, (new_balance, today, stamp, chat_id))
            db.execute("""
                INSERT INTO billing_transactions
                    (chat_id, amount, type, description, created_at)
                VALUES (?, ?, 'daily_charge', 'Kunlik foydalanish', ?)
            """, (chat_id, -DAILY_PRICE, stamp))
            account_balance = new_balance
        else:
            account_balance = account["balance"]

        if account_balance <= DEBT_LIMIT:
            db.commit()
            return False, account_balance, "debt_limit"

        db.commit()
        return True, account_balance, "ok"


def create_receipt(chat_id: int, amount: int, file_id: str):
    current = now()
    stamp = current.isoformat(timespec="seconds")

    with connect() as db:
        db.execute("BEGIN IMMEDIATE")

        account = db.execute(
            "SELECT * FROM billing_accounts WHERE chat_id = ?",
            (chat_id,)
        ).fetchone()

        if not account:
            db.rollback()
            return None, False

        # Chek yuborish uchun 1000 so'm yechiladi
        new_balance = account["balance"] - DAILY_PRICE

        db.execute("""
            UPDATE billing_accounts
            SET balance = ?, updated_at = ?
            WHERE chat_id = ?
        """, (new_balance, stamp, chat_id))

        db.execute("""
            INSERT INTO billing_transactions
                (chat_id, amount, type, description, created_at)
            VALUES (?, ?, 'receipt_fee', 'Chek yuborish uchun to‘lov', ?)
        """, (chat_id, -DAILY_PRICE, stamp))

        # 31 ming qarzga yetgan bo'lsa vaqtinchalik ruxsat yo'q
        allowed = new_balance > -31000

        pending_until = None

        if allowed:
            pending_until = (
                current + timedelta(hours=TEMP_ACCESS_HOURS)
            ).isoformat(timespec="seconds")

        db.execute("""
            UPDATE billing_accounts
            SET pending_until = ?, blocked = ?, updated_at = ?
            WHERE chat_id = ?
        """, (
            pending_until,
            0 if allowed else 1,
            stamp,
            chat_id
        ))

        cur = db.execute("""
            INSERT INTO billing_receipts
                (chat_id, amount, file_id, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (chat_id, amount, file_id, stamp))

        db.commit()

        return cur.lastrowid, allowed


def review_receipt(receipt_id: int, admin_id: int, approve: bool):
    stamp = now().isoformat(timespec="seconds")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        receipt = db.execute(
            "SELECT * FROM billing_receipts WHERE id = ?", (receipt_id,)
        ).fetchone()
        if not receipt or receipt["status"] != "pending":
            db.rollback()
            return None

        chat_id = receipt["chat_id"]
        account = db.execute(
            "SELECT * FROM billing_accounts WHERE chat_id = ?", (chat_id,)
        ).fetchone()

        if approve:
            bonus = 1000
            new_balance = (
                (account["balance"] if account else 0)
                + receipt["amount"]
                + bonus
            )

            db.execute("""
                UPDATE billing_accounts
                SET balance = ?, pending_until = NULL,
                    blocked = 0, updated_at = ?
                WHERE chat_id = ?
            """, (new_balance, stamp, chat_id))

            db.execute("""
                INSERT INTO billing_transactions
                    (chat_id, amount, type, description, created_at)
                VALUES (?, ?, 'topup', ?, ?)
            """, (
                chat_id,
                receipt["amount"],
                f"Chek #{receipt_id} tasdiqlandi",
                stamp
            ))

            db.execute("""
                INSERT INTO billing_transactions
                    (chat_id, amount, type, description, created_at)
                VALUES (?, ?, 'bonus', ?, ?)
            """, (
                chat_id,
                bonus,
                f"Chek #{receipt_id} uchun bonus",
                stamp
            ))

            status = "approved"
        else:
            db.execute("""
                UPDATE billing_accounts
                SET pending_until = NULL, blocked = 1, updated_at = ?
                WHERE chat_id = ?
            """, (stamp, chat_id))
            status = "rejected"

        db.execute("""
            UPDATE billing_receipts
            SET status = ?, reviewed_at = ?, reviewed_by = ?
            WHERE id = ? AND status = 'pending'
        """, (status, stamp, admin_id, receipt_id))
        db.commit()

        updated = db.execute(
            "SELECT balance FROM billing_accounts WHERE chat_id = ?", (chat_id,)
        ).fetchone()
        return {
            "chat_id": chat_id,
            "amount": receipt["amount"],
            "balance": updated["balance"],
            "status": status,
        }


def format_money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


async def require_access(event):
    """Message yoki callback uchun billing tekshiruvi."""
    user = getattr(event, "from_user", None)
    if not user:
        return True

    allowed, balance, reason = charge_and_check(user.id)
    if allowed:
        return True

    message = getattr(event, "message", None) or event
    if reason == "debt_limit":
        warning = (
            "⛔ Xizmat vaqtincha to‘xtatildi. Qarzdorlik limiti "
            f"{format_money(DEBT_LIMIT)} so‘mga yetdi. Davom etish uchun balansni to‘ldiring."
        )
    else:
        warning = "⛔ Hisobingiz vaqtincha bloklangan. Davom etish uchun yangi chek yuboring."

    try:
        if hasattr(event, "answer") and event.__class__.__name__ == "CallbackQuery":
            await event.answer("Balansni to‘ldirish talab qilinadi.", show_alert=True)
        await message.answer(warning)
    except Exception:
        pass
    return False


def admin_add_balance(chat_id: int, amount: int, admin_id: int):
    if amount <= 0:
        return None

    ensure_account(chat_id)

    stamp = now().isoformat(timespec="seconds")

    with connect() as db:
        db.execute("BEGIN IMMEDIATE")

        db.execute("""
            UPDATE billing_accounts
            SET balance = balance + ?,
                blocked = 0,
                pending_until = NULL,
                updated_at = ?
            WHERE chat_id = ?
        """, (amount, stamp, chat_id))

        db.execute("""
            INSERT INTO billing_transactions
                (chat_id, amount, type, description, created_at)
            VALUES (?, ?, 'admin_topup', ?, ?)
        """, (
            chat_id,
            amount,
            f"Admin {admin_id} tomonidan balans to‘ldirildi",
            stamp
        ))

        balance = db.execute(
            "SELECT balance FROM billing_accounts WHERE chat_id = ?",
            (chat_id,)
        ).fetchone()["balance"]

        db.commit()

    return balance


class BillingCallbackMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:

        if not isinstance(event, CallbackQuery):
            return await handler(event, data)

        # Billing tugmalari doim ishlashi kerak
        if event.data and event.data.startswith("billing:"):
            return await handler(event, data)

        # Adminlar uchun cheklov yo'q
        admin_ids = {
            int(x.strip())
            for x in os.getenv("ADMIN_IDS", "").split(",")
            if x.strip().isdigit()
        }

        if event.from_user.id in admin_ids:
            return await handler(event, data)

        # Qolgan barcha inline tugmalar uchun billing tekshiruvi
        if not await require_access(event):
            return

        return await handler(event, data)