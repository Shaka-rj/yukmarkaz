import asyncio
import logging
from telethon import TelegramClient, events

from config import API_ID, API_HASH, SESSION_NAME
from data.group import GROUPS
from send import send_message
from writer import save_message
from utils.filter import filter_message

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=GROUPS))
async def new_message(event):
    try:
        sender = await event.get_sender()

        # 1. Botlardan kelgan xabarlarni o'tkazib yuborish
        if sender and sender.bot:
            return
        
        text = event.raw_text

        # 2. Xabar uzunligini tekshirish (bo'shliqlarsiz 15 va 150 belgi orasida)
        if not (15 <= len(text.replace(" ", "")) <= 150):
            return

        # 3. Filtrdan o'tkazish
        if not filter_message(text):
            return

        # 4. Yuborish, bazaga yozish va o'qildi belgisini qo'yish (Parallel)
        await asyncio.gather(
            send_message(text),
            save_message(text),
            client.send_read_acknowledge(event.chat_id)
        )

    except Exception as e:
        print("Xabar qayta ishlashda xatolik:", e)


async def start_reading():
    """Internet uzilsa ham avtomatik qayta ulanuvchi xavfsiz sikl"""
    while True:
        try:
            await client.start()
            print("Bot ishga tushdi va xabarlarni tinglamoqda...")
            
            # Client uzilmaguncha shu yerda kutib turadi
            await client.run_until_disconnected()

        except (ConnectionError, OSError, TimeoutError, asyncio.TimeoutError) as e:
            print(f"Internet aloqasi uzildi: {e}")
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"Kutilmagan xatolik yuz berdi: {e}")
            await asyncio.sleep(10)