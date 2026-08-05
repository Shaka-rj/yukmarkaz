from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database import add_user
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_regions_keyboard
from bot.states import ElonState

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # 1. Foydalanuvchini bazaga saqlash
    add_user(chat_id=message.chat.id)
    
    # 2. Xabarlarni yuborish
    await message.answer(
        "Assalomu alaykum. Xush kelibsiz.",
        reply_markup=get_main_keyboard()
    )
    await message.answer(
        "Yuklarni izlash uchun viloyatni tanlang",
        reply_markup=get_regions_keyboard()
    )

@router.message(F.text == "📦 E'lonlarni ko'rish")
async def show_regions(message: Message, state: FSMContext):
    await state.set_state(ElonState.choosing_region)
    await message.answer(
        "E'lonlar viloyatini tanlang",
        reply_markup=get_regions_keyboard()
    )

@router.message(F.text == "🚚 Viloyat tanlash")
async def show_regions(message: Message, state: FSMContext):
    await state.set_state(ElonState.choosing_region)
    await message.answer(
        "Viloyat buyicha yuklarni ko'rish",
        reply_markup=get_regions_keyboard()
    )

@router.message(F.text == "/izlash")
async def show_regions(message: Message, state: FSMContext):
    await state.set_state(ElonState.choosing_region)
    await message.answer(
        "Viloyat buyicha yuklarni ko'rish",
        reply_markup=get_regions_keyboard()
    )