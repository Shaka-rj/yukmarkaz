import re
import httpx
from config import BOT_TOKEN, MAIN_GROUP_ID
from utils.region_detector import find_regions
from utils.filter import remove_phone, get_phone


_client = httpx.AsyncClient(timeout=10)

topic_id = {
    "Toshkent": 109539,
    "Toshkent viloyati": 109729,    
    "Andijon": 109540,
    "Buxoro": 109555,
    "Farg'ona": 109730,
    "Jizzax": 109731,
    "Xorazm": 109732,
    "Namangan": 109735,
    "Navoiy": 109736,
    "Qashqadaryo": 109737,
    "Qoraqalpog'iston": 109740,
    "Samarqand": 109741,
    "Sirdaryo": 109742,
    "Surxondaryo": 109743
}

topic_id2 = {
    "Toshkent": 14,
    "Toshkent viloyati": 15,    
    "Andijon": 2,
    "Buxoro": 3,
    "Farg'ona": 4,
    "Jizzax": 5,
    "Xorazm": 6,
    "Namangan": 7,
    "Navoiy": 8,
    "Qashqadaryo": 9,
    "Qoraqalpog'iston": 10,
    "Samarqand": 11,
    "Sirdaryo": 12,
    "Surxondaryo": 13
}


def gettopic(text: str) -> list[int]:
    regions = find_regions(text) or []

    # Takrorlarni olib tashlash
    regions = list(dict.fromkeys(regions))

    # Viloyat topilmasa → General topic
    if not regions:
        return [1]

    topics = []

    for region in regions[:2]:
        topic = topic_id.get(region)

        if topic is not None and topic not in topics:
            topics.append(topic)

    if not topics:
        return [1]

    return topics


async def send_message(
    text: str,
    load_id: int,
    chat_id: int | str = MAIN_GROUP_ID
) -> bool:

    message_thread_ids = gettopic(text)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    all_success = True

    for message_thread_id in message_thread_ids:
        payload = {
            "chat_id": chat_id,
            "text": remove_phone(text),
            "reply_markup": {
                "inline_keyboard": [[
                    {
                        "text": "📞 Nomer ko'rish 📞",
                        "url": f"https://t.me/Operator_yuk_markazi_bot?start={load_id}"
                    }
                ]]
            }
        }

        if message_thread_id != 1:
            payload["message_thread_id"] = message_thread_id

        try:
            response = await _client.post(url, json=payload)
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            print(
                f"❌ Telegram API xatoligi "
                f"(topic={message_thread_id}, "
                f"{e.response.status_code}): "
                f"{e.response.text}"
            )
            all_success = False

        except Exception as e:
            print(
                f"❌ Xabar yuborishda xatolik "
                f"(topic={message_thread_id}): {e}"
            )
            all_success = False

    return all_success

async def send_message2(text: str, chat_id: int | str = MAIN_GROUP_ID) -> bool:
    message_thread_ids = gettopic(text)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    all_success = True

    if chat_id != MAIN_GROUP_ID:
        message_thread_ids = [1]

    for message_thread_id in message_thread_ids:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "message_thread_id": message_thread_id
        }

        if message_thread_id == 1:
            payload = {
                "chat_id": chat_id,
                "text": text
            }    

        try:
            response = await _client.post(url, data=payload)
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            print(
                f"❌ Telegram API xatoligi "
                f"(topic={message_thread_id}, "
                f"{e.response.status_code}): "
                f"{e.response.text}"
            )
            all_success = False

        except Exception as e:
            print(
                f"❌ Xabar yuborishda xatolik "
                f"(topic={message_thread_id}): {e}"
            )
            all_success = False

    return all_success

async def close_send_client():
    await _client.aclose()