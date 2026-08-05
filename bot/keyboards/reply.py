from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 E'lonlarni ko'rish")],
            [KeyboardButton(text="🚚 Viloyat tanlash")]
        ],
        resize_keyboard=True
    )
    return keyboard