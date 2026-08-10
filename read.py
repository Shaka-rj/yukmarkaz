import asyncio
import logging
from telethon import TelegramClient, events

from config import API_ID, API_HASH, SESSION_NAME, MAIN_GROUP_ID
from send import send_message
from writer import save_message
from utils.filter import filter_message

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

pending_reads = set()

@client.on(events.NewMessage())
async def new_message(event):
    try:
        if not event.is_group or event.chat_id == MAIN_GROUP_ID:
            return

        text = event.raw_text or ""

        if not filter_message(text):
            return

        sender = event.sender
        if sender is None:
            sender = await event.get_sender()

        if sender.bot:
            return

        # Guruhni o'qilishi kerak deb belgilaymiz
        pending_reads.add(event.chat_id)

        await asyncio.gather(
            send_message(text),
            save_message(text)
        )

    except Exception as e:
        print("Xabar qayta ishlashda xatolik:", e)


async def read_worker():
    while True:
        await asyncio.sleep(10)

        if not pending_reads:
            continue

        chats = list(pending_reads)
        pending_reads.clear()

        await asyncio.gather(
            *(client.send_read_acknowledge(chat_id) for chat_id in chats),
            return_exceptions=True
        )

async def start_reading():
    """Internet uzilsa avtomatik qayta ulanadi."""

    worker_task = None

    while True:
        try:
            print("Telegram'ga ulanmoqda...")

            await client.connect()

            if not await client.is_user_authorized():
                print("Telegram sessiyasi avtorizatsiyadan o'tmagan!")
                return

            print("Bot ishga tushdi va xabarlarni tinglamoqda...")

            # Worker faqat bir marta ishga tushadi
            if worker_task is None or worker_task.done():
                worker_task = asyncio.create_task(read_worker())

            # Ulanish uzilguncha kutadi
            await client.disconnected

            print("Telegram ulanishi uzildi.")

        except (ConnectionError, OSError, TimeoutError, asyncio.TimeoutError) as e:
            print(f"Internet/ulanish xatosi: {e}")

        except Exception as e:
            print(f"Kutilmagan xatolik: {e}")

        finally:
            if client.is_connected():
                await client.disconnect()

        print("10 soniyadan keyin qayta ulanadi...")
        await asyncio.sleep(10)