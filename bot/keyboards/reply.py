from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📦 E'lonlarni ko'rish")],
            [KeyboardButton(text="🔀 Yunalishni tanlash")],
            [KeyboardButton(text="💳 Balans")]
        ],
        resize_keyboard=True
    )
    return keyboard
