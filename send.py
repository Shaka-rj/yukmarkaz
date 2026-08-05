import httpx
from config import BOT_TOKEN, MAIN_GROUP_ID

# Bitta umumiy mijoz (session) - ulanishni qayta-qayta ishlatib tezlikni oshiradi
_client = httpx.AsyncClient(timeout=10)



async def send_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": MAIN_GROUP_ID,
        "text": text
    }

    try:
        response = await _client.post(url, data=payload)
        response.raise_for_status()
        return True

    except httpx.HTTPStatusError as e:
        print(f"❌ Telegram API xatoligi ({e.response.status_code}): {e.response.text}")
        return False
    except Exception as e:
        print("❌ Xabar yuborishda tarmoq xatoligi:", e)
        return False


async def close_send_client():
    await _client.aclose()