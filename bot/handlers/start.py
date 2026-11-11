from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.database import add_user
from bot.billing import require_access
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_regions_keyboard, get_regions_for_route_keyboard
from bot.states import ElonState
from aiogram.filters import CommandObject
from bot.database import get_load_by_id

router = Router()

@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    command: CommandObject
):
    await state.clear()
    add_user(chat_id=message.chat.id)

    if not await require_access(message):
        await message.answer(
            '💳 Balansni ko‘rish yoki to‘ldirish uchun «Balans» tugmasini bosing.',
            reply_markup=get_main_keyboard()
        )
        return

    # Start orqali kelgan yuk ID
    if command.args:
        try:
            load_id = int(command.args)
            load = get_load_by_id(load_id)

            if load:
                await message.answer(
                    f"{load['message']}",
                    reply_markup=get_main_keyboard()
                )
            else:
                await message.answer(
                    "❌ Ushbu e'lon topilmadi.",
                    reply_markup=get_main_keyboard()
                )

        except ValueError:
            await message.answer("❌ E'lon ID noto‘g‘ri.")

        return

@router.message(F.text == "📦 E'lonlarni ko'rish")
async def show_regions(message: Message, state: FSMContext):
    if not await require_access(message):
        return
    await state.set_state(ElonState.choosing_region)
    await message.answer(
        "E'lonlar viloyatini tanlang",
        reply_markup=get_regions_keyboard()
    )

@router.message(F.text == "🔀 Yunalishni tanlash")
async def show_regions(message: Message, state: FSMContext):
    if not await require_access(message):
        return
    await state.set_state(ElonState.select_route)
    await message.answer(
        "1-nuqtani tanlang",
        reply_markup=get_regions_for_route_keyboard()
    )

@router.message(F.text == "/izlash")
async def show_regions(message: Message, state: FSMContext):
    if not await require_access(message):
        return
    await state.set_state(ElonState.choosing_region)
    await message.answer(
        "Viloyat buyicha yuklarni ko'rish",
        reply_markup=get_regions_keyboard()
    )