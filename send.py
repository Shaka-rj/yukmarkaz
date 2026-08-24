import httpx
from config import BOT_TOKEN, MAIN_GROUP_ID
from utils.region_detector import find_regions

_client = httpx.AsyncClient(timeout=10)

topic_id = {
    "Toshkent": 109539,
    "Andijon": 109540,
    "Buxoro": 109555,
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

    # Viloyat topildi, lekin topic_id jadvalida yo'q
    if not topics:
        return [1]

    return topics


async def send_message(
    text: str,
    chat_id: int | str = MAIN_GROUP_ID
) -> bool:

    message_thread_ids = gettopic(text)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    all_success = True

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

            print(
                f"✅ Yuborildi: "
                f"topic={message_thread_id}"
            )

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