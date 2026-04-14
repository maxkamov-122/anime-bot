from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

import database as db
import keyboards as kb
from config import ADMIN_ID

router = Router()

# ─── FOYDALANUVCHILAR RO'YXATI ───────────────────────────────────────────────

@router.message(F.text == "👥 Foydalanuvchilar")
async def show_users(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Faqat admin!")
        return
    
    users = await db.get_all_users()
    if not users:
        await message.answer("😔 Foydalanuvchilar yo'q!")
        return
    
    text = f"👥 <b>Foydalanuvchilar ({len(users)} ta):</b>\n\n"
    buttons = []
    
    for user in users:
        role_emoji = {"admin": "👑", "manager": "🛡", "user": "👤"}.get(user["role"], "👤")
        premium = "⭐" if user["is_premium"] else ""
        text += f"{role_emoji}{premium} {user['full_name']} — <code>{user['telegram_id']}</code>\n"
        if user["telegram_id"] != ADMIN_ID:
            buttons.append([{
                "text": f"{user['full_name']}",
                "id": user["telegram_id"],
                "role": user["role"],
                "premium": user["is_premium"]
            }])
    
    # Inline keyboard yasash
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'👑' if u[0]['role']=='admin' else '🛡' if u[0]['role']=='manager' else '👤'}{'⭐' if u[0]['premium'] else ''} {u[0]['text']}",
            callback_data=f"manageuser_{u[0]['id']}"
        )] for u in buttons
    ])
    
    await message.answer(text, parse_mode="HTML", reply_markup=ikb)

@router.callback_query(F.data == "back_users")
async def back_to_users(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin!", show_alert=True)
        return
    
    users = await db.get_all_users()
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for user in users:
        if user["telegram_id"] != ADMIN_ID:
            role_emoji = {"admin": "👑", "manager": "🛡", "user": "👤"}.get(user["role"], "👤")
            premium = "⭐" if user["is_premium"] else ""
            buttons.append([InlineKeyboardButton(
                text=f"{role_emoji}{premium} {user['full_name']}",
                callback_data=f"manageuser_{user['telegram_id']}"
            )])
    
    ikb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(f"👥 <b>Foydalanuvchilar ({len(users)} ta)</b>", parse_mode="HTML", reply_markup=ikb)
    await call.answer()

# ─── FOYDALANUVCHI BOSHQARUVI ─────────────────────────────────────────────────

@router.callback_query(F.data.startswith("manageuser_"))
async def manage_user(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin!", show_alert=True)
        return
    
    target_id = int(call.data.split("_")[1])
    user = await db.get_user(target_id)
    
    if not user:
        await call.answer("❗ Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    role_emoji = {"admin": "👑 Admin", "manager": "🛡 Manager", "user": "👤 User"}.get(user["role"], "👤 User")
    premium_text = "⭐ Premium" if user["is_premium"] else "🆓 Oddiy"
    
    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"🆔 ID: <code>{user['telegram_id']}</code>\n"
        f"📱 Telefon: {user['phone']}\n"
        f"🎭 Rol: {role_emoji}\n"
        f"💎 Status: {premium_text}"
    )
    
    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.user_manage_kb(target_id, user["role"], user["is_premium"])
    )
    await call.answer()

# ─── ROL O'ZGARTIRISH ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("setrole_"))
async def set_role(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin!", show_alert=True)
        return
    
    parts = call.data.split("_")
    new_role = parts[1]
    target_id = int(parts[2])
    
    await db.set_user_role(target_id, new_role)
    
    role_names = {"user": "👤 User", "manager": "🛡 Manager", "admin": "👑 Admin"}
    await call.answer(f"✅ Rol o'zgartirildi: {role_names.get(new_role, new_role)}", show_alert=True)
    
    # Yangilangan user ma'lumotlarini ko'rsatish
    user = await db.get_user(target_id)
    role_emoji = {"admin": "👑 Admin", "manager": "🛡 Manager", "user": "👤 User"}.get(user["role"], "👤 User")
    premium_text = "⭐ Premium" if user["is_premium"] else "🆓 Oddiy"
    
    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"🆔 ID: <code>{user['telegram_id']}</code>\n"
        f"📱 Telefon: {user['phone']}\n"
        f"🎭 Rol: {role_emoji}\n"
        f"💎 Status: {premium_text}"
    )
    
    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.user_manage_kb(target_id, user["role"], user["is_premium"])
    )

# ─── PREMIUM O'ZGARTIRISH ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("setpremium_"))
async def set_premium(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Faqat admin!", show_alert=True)
        return
    
    target_id = int(call.data.split("_")[1])
    user = await db.get_user(target_id)
    new_premium = not bool(user["is_premium"])
    
    await db.set_user_premium(target_id, new_premium)
    
    status = "✅ Premium berildi!" if new_premium else "❌ Premium olib tashlandi!"
    await call.answer(status, show_alert=True)
    
    user = await db.get_user(target_id)
    role_emoji = {"admin": "👑 Admin", "manager": "🛡 Manager", "user": "👤 User"}.get(user["role"], "👤 User")
    premium_text = "⭐ Premium" if user["is_premium"] else "🆓 Oddiy"
    
    text = (
        f"👤 <b>{user['full_name']}</b>\n\n"
        f"🆔 ID: <code>{user['telegram_id']}</code>\n"
        f"📱 Telefon: {user['phone']}\n"
        f"🎭 Rol: {role_emoji}\n"
        f"💎 Status: {premium_text}"
    )
    
    await call.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=kb.user_manage_kb(target_id, user["role"], user["is_premium"])
    )
