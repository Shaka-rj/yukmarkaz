from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Viloyatlar ro'yxati
VILOYATLAR = [
    "Toshkent", "Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm", "Namangan", "Navoiy", "Qashqadaryo", "Qoraqalpog'iston", "Samarqand", "Sirdaryo", "Surxondaryo", "Toshkent viloyati"
]

def get_regions_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for viloyat in VILOYATLAR:
        # Callback format: "region:<viloyat_nomi>"
        builder.button(text=viloyat, callback_data=f"region:{viloyat}")
    builder.adjust(2)  # Qatorda 2 tadan tugma
    return builder.as_markup()

def get_elon_pagination_keyboard(region: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1-qator: Navigation (Oldingi / Sahifa / Keyingi)
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page:{region}:{page - 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="⛔️", callback_data="noop"))
        
    nav_buttons.append(InlineKeyboardButton(text=f"📄 {page}/{total_pages}", callback_data="noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page:{region}:{page + 1}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="⛔️", callback_data="noop"))
        
    builder.row(*nav_buttons)
    
    # 2-qator: Yangilash
    builder.row(InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"refresh:{region}:{page}"))
    
    # 3-qator: Boshqa viloyatni tanlash
    builder.row(InlineKeyboardButton(text="🗺 Boshqa viloyatni tanlash", callback_data="change_region"))
    
    return builder.as_markup()