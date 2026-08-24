from telethon import TelegramClient
from config import API_ID, API_HASH


client = TelegramClient(
    "target_worker",
    API_ID,
    API_HASH
)


async def main():
    await client.start()
    print("target_worker.session muvaffaqiyatli autentifikatsiya qilindi.")

    me = await client.get_me()

    print(f"Account: {me.first_name}")
    print(f"Username: @{me.username}" if me.username else "Username yo'q")

    await client.disconnect()


with client:
    client.loop.run_until_complete(main())