import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from bot.billing import admin_add_balance
from aiogram.filters.command import CommandObject

from bot.billing import (
    get_account, create_receipt, review_receipt, format_money,
    DAILY_PRICE, DEBT_LIMIT
)

router = Router()

ADMIN_IDS = {
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
}
CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "KARTA_RAQAMINI_ENV_FAYLGA_KIRITING")
CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "Karta egasi")


class BillingState(StatesGroup):
    waiting_amount = State()
    waiting_receipt = State()


def balance_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➕ Balansni to‘ldirish", callback_data="billing:topup")
    ]])


def admin_receipt_keyboard(receipt_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"billing:approve:{receipt_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"billing:reject:{receipt_id}")
    ]])


async def show_balance(message: Message):
    account = get_account(message.chat.id)
    balance = account["balance"]
    await message.answer(
        "💳 <b>Balansingiz</b>\n\n"
        f"Hisob raqam: <code>{message.chat.id}</code>\n"
        f"Joriy balans: <b>{format_money(balance)} so‘m</b>\n"
        f"Kunlik tarif: {format_money(DAILY_PRICE)} so‘m\n"
        f"Qarzdorlik limiti: {format_money(DEBT_LIMIT)} so‘m",
        parse_mode="HTML",
        reply_markup=balance_keyboard()
    )


@router.message(Command("balans"))
@router.message(F.text == "💳 Balans")
async def balance_command(message: Message):
    await show_balance(message)


@router.callback_query(F.data == "billing:topup")
async def start_topup(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BillingState.waiting_amount)
    await callback.message.answer(
        "Qancha summa to‘ldirmoqchisiz? Summani so‘mda yuboring.",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(BillingState.waiting_amount, F.text)
async def receive_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text.replace(" ", "").replace(",", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Summani faqat musbat butun son ko‘rinishida yuboring. Masalan: 50000")
        return

    await state.update_data(payment_amount=amount)
    await state.set_state(BillingState.waiting_receipt)
    await message.answer(
        "💳 <b>To‘lov uchun karta ma’lumotlari</b>\n\n"
        f"Karta: <code>{CARD_NUMBER}</code>\n"
        f"Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To‘lov summasi: <b>{format_money(amount)} so‘m</b>\n\n"
        "Endi to‘lov chekini rasm ko‘rinishida yuboring.",
        parse_mode="HTML"
    )


@router.message(BillingState.waiting_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("payment_amount")
    if not amount:
        await state.clear()
        await message.answer("To‘lov summasi topilmadi. Iltimos, qaytadan boshlang: 💳 Balans")
        return

    receipt_id, temporary_access = create_receipt(
        chat_id=message.chat.id,
        amount=int(amount),
        file_id=message.photo[-1].file_id
    )
    await state.clear()

    if temporary_access:
        await message.answer(
            "✅ Chekingiz qabul qilindi.\n"
            "Balansingizdan 1 000 so‘m yechildi.\n"
            "Admin tekshirguncha 24 soat foydalanishingiz mumkin. Muammo bo'lsa: @Rajabov_Shamshod, 919481922"
        )
    else:
        await message.answer(
            "⚠️ Chekingiz qabul qilindi.\n"
            "Balansingizdan 1 000 so‘m yechildi.\n"
            "Qarzdorlik limiti oshgani sababli vaqtinchalik foydalanish berilmadi.\n"
            "Admin tasdiqlashini kuting. Muammo bo'lsa: @Rajabov_Shamshod, 919481922"
        )

    caption = (
        f"🧾 <b>Yangi to‘lov cheki</b>\n\n"
        f"Chek ID: <code>{receipt_id}</code>\n"
        f"Foydalanuvchi: <code>{message.chat.id}</code>\n"
        f"Summa: <b>{format_money(int(amount))} so‘m</b>\n"
        f"Username: @{message.from_user.username or 'mavjud emas'}"
    )

    if not ADMIN_IDS:
        await message.answer("⚠️ Admin sozlanmagan. Chek adminlarga yuborilmadi.")
        return

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_photo(
                chat_id=admin_id,
                photo=message.photo[-1].file_id,
                caption=caption,
                parse_mode="HTML",
                reply_markup=admin_receipt_keyboard(receipt_id)
            )
        except Exception as e:
            print(f"Admin {admin_id} ga chek yuborilmadi: {e}")


@router.message(BillingState.waiting_receipt)
async def receipt_must_be_photo(message: Message):
    await message.answer("Iltimos, chekni rasm (photo) ko‘rinishida yuboring.")


@router.callback_query(F.data.startswith("billing:approve:"))
@router.callback_query(F.data.startswith("billing:reject:"))
async def review_payment(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Sizda admin huquqi yo‘q.", show_alert=True)
        return

    _, action, receipt_id_text = callback.data.split(":")
    result = review_receipt(
        receipt_id=int(receipt_id_text),
        admin_id=callback.from_user.id,
        approve=(action == "approve")
    )

    if result is None:
        await callback.answer("Bu chek avval ko‘rib chiqilgan yoki topilmadi.", show_alert=True)
        return

    user_id = result["chat_id"]
    if result["status"] == "approved":
        user_text = (
            "✅ To‘lovingiz tasdiqlandi!\n\n"
            f"To‘lov: {format_money(result['amount'])} so‘m\n"
            "Bonus: 1 000 so‘m\n"
            f"Joriy balans: {format_money(result['balance'])} so‘m"
        )
        admin_text = f"✅ Chek #{receipt_id_text} tasdiqlandi."
    else:
        user_text = (
            "❌ To‘lov chekingiz admin tomonidan rad etildi.\n"
            "Botdan foydalanish vaqtincha to‘xtatildi. Qayta to‘lov yuborishingiz mumkin."
        )
        admin_text = f"❌ Chek #{receipt_id_text} rad etildi."

    try:
        await callback.bot.send_message(user_id, user_text)
    except Exception as e:
        print(f"Foydalanuvchiga billing xabari yuborilmadi: {e}")

    await callback.message.edit_caption(
        caption=(callback.message.caption or "") + f"\n\n{admin_text}",
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("Amal bajarildi.")

@router.message(Command("add"))
async def add_balance_command(
    message: Message,
    command: CommandObject
):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not command.args:
        await message.answer(
            "Foydalanish:\n"
            "/add chat_id amount\n\n"
            "Misol:\n"
            "/add 123456789 50000"
        )
        return

    try:
        chat_id, amount = map(int, command.args.split())

        if chat_id <= 0 or amount <= 0:
            raise ValueError

    except ValueError:
        await message.answer(
            "❌ Buyruq noto‘g‘ri.\n"
            "Misol: /add 123456789 50000"
        )
        return

    balance = admin_add_balance(
        chat_id=chat_id,
        amount=amount,
        admin_id=message.from_user.id
    )

    if balance is None:
        await message.answer("❌ Balansni to‘ldirish amalga oshmadi.")
        return

    await message.answer(
        "✅ Balans muvaffaqiyatli to‘ldirildi!\n\n"
        f"Foydalanuvchi: <code>{chat_id}</code>\n"
        f"Qo‘shildi: <b>{format_money(amount)} so‘m</b>\n"
        f"Joriy balans: <b>{format_money(balance)} so‘m</b>",
        parse_mode="HTML"
    )

    try:
        await message.bot.send_message(
            chat_id,
            "💳 <b>Balansingiz admin tomonidan to‘ldirildi!</b>\n\n"
            f"Qo‘shilgan summa: {format_money(amount)} so‘m\n"
            f"Joriy balans: {format_money(balance)} so‘m",
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Foydalanuvchiga xabar yuborilmadi: {e}")