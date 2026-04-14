from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ─── ASOSIY MENYU ─────────────────────────────────────────────────────────────

def main_menu(role="user"):
    buttons = [
        [KeyboardButton(text="🔍 Anime qidirish"), KeyboardButton(text="⭐ Premium animelar")],
        [KeyboardButton(text="👤 Mening profilim")],
    ]
    if role in ("admin", "manager"):
        buttons.append([KeyboardButton(text="➕ Anime qo'shish")])
    if role == "admin":
        buttons.append([KeyboardButton(text="👥 Foydalanuvchilar")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ─── PROFIL YO'Q ─────────────────────────────────────────────────────────────

def share_contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Profilimni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ─── ANIME QIDIRISH USULI ─────────────────────────────────────────────────────

def search_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Nomi bo'yicha", callback_data="search_by_name")],
        [InlineKeyboardButton(text="🔢 Kodi bo'yicha", callback_data="search_by_code")],
    ])

# ─── ANIME NATIJASI ──────────────────────────────────────────────────────────

def anime_result_kb(anime_id, is_premium_anime, user_is_premium):
    buttons = []
    if not is_premium_anime or user_is_premium:
        buttons.append([InlineKeyboardButton(text="▶️ Qismlarni ko'rish", callback_data=f"episodes_{anime_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="🔒 Premium kerak", callback_data="need_premium")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── ADMIN: FOYDALANUVCHI BOSHQARUVI ─────────────────────────────────────────

def user_manage_kb(telegram_id, current_role, is_premium):
    premium_text = "❌ Premiumni olib tashlash" if is_premium else "✅ Premium berish"
    role_buttons = []
    if current_role != "user":
        role_buttons.append(InlineKeyboardButton(text="👤 User qilish", callback_data=f"setrole_user_{telegram_id}"))
    if current_role != "manager":
        role_buttons.append(InlineKeyboardButton(text="🛡 Manager qilish", callback_data=f"setrole_manager_{telegram_id}"))
    
    buttons = []
    if role_buttons:
        buttons.append(role_buttons)
    buttons.append([InlineKeyboardButton(text=premium_text, callback_data=f"setpremium_{telegram_id}")])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_users")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── PREMIUM ANIME BELGISI ────────────────────────────────────────────────────

def add_anime_premium_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Ha, Premium", callback_data="anime_premium_yes")],
        [InlineKeyboardButton(text="🆓 Yo'q, Bepul", callback_data="anime_premium_no")],
    ])

# ─── QISMLAR ─────────────────────────────────────────────────────────────────

def episodes_kb(episodes, anime_id):
    buttons = []
    for ep in episodes:
        buttons.append([InlineKeyboardButton(
            text=f"📺 {ep['episode_number']}-qism: {ep['title']}",
            callback_data=f"watch_{ep['id']}"
        )])
    buttons.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"anime_{anime_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ─── ANIME QO'SHISH: QISM QO'SHISH ─────────────────────────────────────────

def after_add_anime_kb(anime_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Qism qo'shish", callback_data=f"addep_{anime_id}")],
        [InlineKeyboardButton(text="✅ Tayyor", callback_data="done_adding")],
    ])
