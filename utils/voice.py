
import asyncio
import logging
import subprocess
from io import BytesIO

import httpx
import edge_tts
from openai import AsyncOpenAI

from config import BOT_TOKEN, AI_API_KEY

logger = logging.getLogger(__name__)

_client = httpx.AsyncClient(timeout=60)

_openai = AsyncOpenAI(
    api_key=AI_API_KEY,
    timeout=30
)


async def prepare_text(text: str) -> str:
    """Matnni o'zbekcha TTS uchun tayyorlash."""

    try:
        response = await _openai.responses.create(
            model="gpt-6-luna",
            instructions="""
Sen o'zbek tilidagi TTS matn muharririsan.

Vazifang:
1. Kirill matnini lotin alifbosiga o'tkaz.
2. Raqamlarni talaffuz uchun so'z bilan yoz.
3. Qisqartmalarni talaffuzga moslashtir.
4. Tinish belgilarini to'g'rila.
5. Emoji va keraksiz belgilarni olib tashla.

Muhim:
- Yuk yo'nalishini o'zgartirma.
- Og'irlik va miqdorlarni o'zgartirma.
- Hech qanday ma'lumot qo'shma.
- Faqat ovozda aytiladigan matnni qaytar.
""",
            input=text,
            max_output_tokens=300
        )

        return response.output_text.strip() or text

    except Exception:
        logger.exception("ChatGPT TTS tayyorlash xatosi")
        return text


async def generate_audio(text: str) -> bytes:
    """Edge TTS orqali MP3 yaratish."""

    communicate = edge_tts.Communicate(
        text=text,
        voice="uz-UZ-SardorNeural",
        rate="-5%",
        volume="+0%",
        pitch="+0Hz"
    )

    audio = BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    return audio.getvalue()




async def send_voice(
    chat_id: int | str,
    message_id: int,
    text: str,
    topic_id: int | list[int] | None = None
):
    """Matnni ovozga aylantirib, Telegramga reply qiladi."""

    try:
        # 1. Matnni tayyorlash
        prepared_text = await prepare_text(text)

        if not prepared_text:
            return

        # 2. Ovoz yaratish
        audio_mp3 = await generate_audio(prepared_text)

        if not audio_mp3:
            return

        # 4. Topic ID larni aniqlash
        topics = (
            topic_id if isinstance(topic_id, list)
            else [topic_id]
        )

        # 5. Telegramga yuborish
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVoice"

        for topic in topics:
            payload = {
                "chat_id": chat_id,
                "reply_to_message_id": message_id,
                "allow_sending_without_reply": True
            }

            if topic is not None and topic != 1:
                payload["message_thread_id"] = topic

            try:
                response = await _client.post(
                    url,
                    data=payload,
                    files={
                        "voice": (
                            "voice.mp3",
                            audio_mp3,
                            "audio/mpeg"
                        )
                    }
                )

                response.raise_for_status()

                result = response.json()

                if not result.get("ok"):
                    logger.error("Telegram voice xatosi: %s", result)

            except Exception:
                logger.exception(
                    "Voice yuborilmadi: topic=%s",
                    topic
                )

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception(
            "Voice yaratishda umumiy xatolik"
        )


async def close_voice_client():
    """Dastur to'xtatilganda klientlarni yopish."""

    await _client.aclose()
    await _openai.close()
