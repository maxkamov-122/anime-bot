from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb
from config import ADMIN_ID

router = Router()

class Registration(StatesGroup):
    waiting_contact = State()

# ─── /start ──────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    
    if not user:
        # Admin avtomatik ro'yxatdan o'tadi
        if message.from_user.id == ADMIN_ID:
            await db.create_user(
                telegram_id=message.from_user.id,
                username=message.from_user.username or "",
                full_name=message.from_user.full_name,
                phone="Admin"
            )
            await db.set_user_role(message.from_user.id, "admin")
            user = await db.get_user(message.from_user.id)
            await message.answer(
                "👑 Salom Admin! Xush kelibsiz!",
                reply_markup=kb.main_menu("admin")
            )
        else:
            await message.answer(
                "🎌 Anime Botga xush kelibsiz!\n\n"
                "Botdan foydalanish uchun profilingizni ulashing 👇",
                reply_markup=kb.share_contact_kb()
            )
            await state.set_state(Registration.waiting_contact)
    else:
        role = user["role"]
        await message.answer(
            f"🎌 Xush kelibsiz, {user['full_name']}!",
            reply_markup=kb.main_menu(role)
        )

# ─── KONTAKT YUBORISH ─────────────────────────────────────────────────────────

@router.message(Registration.waiting_contact, F.contact)
async def get_contact(message: Message, state: FSMContext):
    contact = message.contact
    if contact.user_id != message.from_user.id:
        await message.answer("❗ Iltimos, o'z profilingizni ulashing!")
        return
    
    await db.create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name,
        phone=contact.phone_number
    )
    await state.clear()
    
    await message.answer(
        "✅ Muvaffaqiyatli ro'yxatdan o'tdingiz!\n\n"
        "🎌 Anime botga xush kelibsiz!",
        reply_markup=kb.main_menu("user")
    )

# ─── PROFIL ──────────────────────────────────────────────────────────────────

@router.message(F.text == "👤 Mening profilim")
async def my_profile(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Avval ro'yxatdan o'ting!", reply_markup=kb.share_contact_kb())
        return
    
    role_emoji = {"admin": "👑 Admin", "manager": "🛡 Manager", "user": "👤 User"}.get(user["role"], "👤 User")
    premium_text = "⭐ Premium" if user["is_premium"] else "🆓 Oddiy"
    
    text = (
        f"👤 <b>Profil</b>\n\n"
        f"🆔 ID: <code>{user['telegram_id']}</code>\n"
        f"📛 Ism: {user['full_name']}\n"
        f"📱 Telefon: {user['phone']}\n"
        f"🎭 Rol: {role_emoji}\n"
        f"💎 Status: {premium_text}\n"
    )
    await message.answer(text, parse_mode="HTML")
