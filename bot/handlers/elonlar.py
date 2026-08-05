from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards.inline import get_regions_keyboard, get_elon_pagination_keyboard
from bot.states import ElonState
from bot.database import get_elons_by_region

router = Router()

def format_region_name(region: str) -> str:
    """Viloyat va hudud nomlarini to'g'ri shakllantirish"""
    region_clean = region.strip()
    region_lower = region_clean.lower()
    
    if region_lower in ["toshkent", "tashkent"]:
        return "Toshkent shahri"
    
    if "qoraqalpog" in region_lower or "karakalpak" in region_lower:
        if "respublikas" in region_lower:
            return region_clean
        return "Qoraqalpog'iston Respublikasi"
    
    if any(word in region_lower for word in ["viloyat", "shahr", "respublika"]):
        return region_clean
        
    return f"{region_clean} viloyati"


def fetch_and_format_elons(region: str, page: int = 1):
    limit = 5
    elons, total_pages, total_items = get_elons_by_region(region, page=page, limit=limit)
    display_region = format_region_name(region)
    
    if not elons:
        text = f"📌 <b>{display_region}</b> bo'yicha hech qanday e'lon topilmadi."
        return text, 1

    text = f"📌 <b>{display_region}</b> bo'yicha e'lonlar (Sahifa {page}/{total_pages}:\n\n"
    
    for idx, elon in enumerate(elons, start=1):
        # sqlite3.Row orqali ushlab olinadi
        msg_text = elon['message'] if elon['message'] else "Matn mavjud emas"
        reg_a = elon['region_a'] if elon['region_a'] else "---"
        reg_b = elon['region_b'] if elon['region_b'] else "---"
        date_str = elon['created_at'] if elon['created_at'] else ""

        text += f"{msg_text}\n"
        if date_str:
            text += f"🕒 <i>{date_str}</i>\n"
        text += "───────────────────\n"
        
    return text, total_pages


# 1. Viloyat tanlanganda
@router.callback_query(F.data.startswith("region:"))
async def process_region_selection(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split(":")[1]
    await state.update_data(selected_region=region)
    await state.set_state(ElonState.viewing_elons)
    
    text, total_pages = fetch_and_format_elons(region, page=1)
    
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_elon_pagination_keyboard(region, page=1, total_pages=total_pages)
    )
    await callback.answer()

# 2. Sahifalarni o'tkazish (Oldingi / Keyingi)
@router.callback_query(F.data.startswith("page:"))
async def process_pagination(callback: CallbackQuery):
    _, region, page = callback.data.split(":")
    page = int(page)
    
    text, total_pages = fetch_and_format_elons(region, page=page)
    
    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=get_elon_pagination_keyboard(region, page=page, total_pages=total_pages)
    )
    await callback.answer()

# 3. Yangilash tugmasi
@router.callback_query(F.data.startswith("refresh:"))
async def process_refresh(callback: CallbackQuery):
    # Callback ma'lumotidan viloyatni ajratib olamiz
    # Eslatma: 'page' ajratib olinsa ham, baribir 1-sahifaga o'tamiz
    _, region, _ = callback.data.split(":")
    
    # Har doim 1-sahifa e'lonlarini olamiz
    new_page = 1
    text, total_pages = fetch_and_format_elons(region, page=new_page)
    
    try:
        # Xabarni 1-sahifa matni va 1-sahifa tugmalari bilan yangilaymiz
        await callback.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=get_elon_pagination_keyboard(region, page=new_page, total_pages=total_pages)
        )
        await callback.answer("🔄 Yangilandi")
    except Exception:
        # Agar matn va sahifa o'zgarmagan bo'lsa (allaqachon 1-sahifada bo'lsangiz va yangi e'lon qo'shilmagan bo'lsa)
        await callback.answer("Yangi e'lonlar yo'q")

# 4. Boshqa viloyatni tanlash tugmasi
@router.callback_query(F.data == "change_region")
async def process_change_region(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ElonState.choosing_region)
    await callback.message.edit_text(
        "Kerakli viloyatni tanlang:",
        reply_markup=get_regions_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "noop")
async def process_noop(callback: CallbackQuery):
    await callback.answer()