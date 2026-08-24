import httpx
from config import BOT_TOKEN, MAIN_GROUP_ID
from utils.region_detector import find_regions

# Bitta umumiy mijoz (session) - ulanishni qayta-qayta ishlatib tezlikni oshiradi
_client = httpx.AsyncClient(timeout=10)

topic_id = {
    "Toshkent": 109539,
    "Andijon": 109540,
    "Buxoro": 109555,
}


def gettopic(text: str) -> list[int]:
    regions = find_regions(text)

    # Takrorlangan viloyatlarni olib tashlash,
    # lekin tartibni saqlash
    regions = list(dict.fromkeys(regions))

    # 0 ta viloyat topilsa
    if len(regions) == 0:
        return [1]

    # 1 ta yoki undan ko'p viloyat
    topics = []

    for region in regions[:2]:
        topic = topic_id.get(region)

        if topic is not None and topic not in topics:
            topics.append(topic)

    # Viloyat topilgan, lekin topic_id jadvalida yo'q bo'lsa
    if not topics:
        return [1]


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

        try:
            response = await _client.post(url, data=payload)
            response.raise_for_status()

            print(f"✅ Xabar yuborildi: topic_id={message_thread_id}")

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
                f"❌ Xabar yuborishda tarmoq xatoligi "
                f"(topic={message_thread_id}): {e}"
            )
            all_success = False

    return all_success

async def close_send_client():
    await _client.aclose()