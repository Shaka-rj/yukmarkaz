
import asyncio
import json
import re
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR.parent / ".env")

BOT_TOKEN = os.getenv("INSPECTOR_TOKEN")
GROUP_ID = int(os.getenv("MAIN_GROUP_ID"))


from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ChatPermissions
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

MUTE_SECONDS = 60

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


# QOIDALARNI YUKLASH
def load_rules():
    with open(BASE_DIR / "rules.json", "r", encoding="utf-8") as f:
        return json.load(f)


RULES = load_rules()


# KIRILL -> LOTIN
def normalize(text):
    text = text.lower()

    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g",
        "д": "d", "е": "e", "ё": "yo", "ж": "j",
        "з": "z", "и": "i", "й": "y", "к": "k",
        "л": "l", "м": "m", "н": "n", "о": "o",
        "п": "p", "р": "r", "с": "s", "т": "t",
        "у": "u", "ф": "f", "х": "x", "ц": "ts",
        "ч": "ch", "ш": "sh", "щ": "shch",
        "ъ": "'", "ы": "i", "ь": "", "э": "e",
        "ю": "yu", "я": "ya", "ў": "o'", "қ": "q",
        "ғ": "g", "ҳ": "h"
    }

    return "".join(mapping.get(char, char) for char in text)


# TAQIQLANGAN SO'ZLARNI TEKSHIRISH
def check_message(text):
    normalized = normalize(text)

    # "/" bilan boshlanuvchi buyruqlar taqiqlanadi
    if normalized.lstrip().startswith("/"):
        return "Bu ishlamaydi"

    for category, data in RULES.items():
        for word in data["words"]:
            keyword = normalize(word)

            pattern = (
                r"(?<!\w)" +
                re.escape(keyword) +
                r"(?!\w)"
            )

            if re.search(pattern, normalized):
                return data["reason"]

    return None


# OGOHLANTIRISHNI KEYINCHALIK O'CHIRISH
async def delete_warning(chat_id, message_id):
    await asyncio.sleep(MUTE_SECONDS)

    try:
        await bot.delete_message(chat_id, message_id)
    except TelegramBadRequest:
        pass


# XABARNI TEKSHIRISH
async def moderate(message: Message):

    if message.chat.id != GROUP_ID:
        return

    text = message.text or message.caption

    if not text:
        return

    reason = check_message(text)

    if not reason:
        return

    user = message.from_user

    if not user:
        return

    # ASL XABARNI O'CHIRISH
    try:
        await message.delete()
    except TelegramBadRequest:
        return

    # FOYDALANUVCHINI 1 DAQIQA MUTE QILISH
    try:
        await bot.restrict_chat_member(
            chat_id=GROUP_ID,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=False
            ),
            until_date=datetime.now(timezone.utc)
            + timedelta(seconds=MUTE_SECONDS)
        )
    except TelegramBadRequest:
        pass

    # OGOHLANTIRISH
    warning = await bot.send_message(
        chat_id=message.chat.id,
        message_thread_id=message.message_thread_id,
        text=(
            f"⚠️ {user.mention_html()}\n\n"
            f"Sabab: <b>{reason}</b>\n"
        )
    )

    # 1 DAQIQADAN KEYIN O'CHIRISH
    asyncio.create_task(
        delete_warning(GROUP_ID, warning.message_id)
    )


# YANGI XABARLAR
dp.message.register(
    moderate,
    F.chat.id == GROUP_ID,
    F.text | F.caption
)

# TAHRIRLANGAN XABARLAR
dp.edited_message.register(
    moderate,
    F.chat.id == GROUP_ID,
    F.text | F.caption
)


async def run_inspector_bot():
    print("Inspektor bot ishga tushdi...")
    await dp.start_polling(bot)