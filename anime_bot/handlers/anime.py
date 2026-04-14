from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb

router = Router()

class SearchState(StatesGroup):
    waiting_query = State()

# ─── QIDIRISH ─────────────────────────────────────────────────────────────────

@router.message(F.text == "🔍 Anime qidirish")
async def anime_search_menu(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Avval /start bosing!")
        return
    await message.answer("Qidirish usulini tanlang:", reply_markup=kb.search_type_kb())

@router.callback_query(F.data == "search_by_name")
async def search_by_name(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("📝 Anime nomini yozing:")
    await state.set_state(SearchState.waiting_query)
    await state.update_data(search_type="name")
    await call.answer()

@router.callback_query(F.data == "search_by_code")
async def search_by_code(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("🔢 Anime kodini yozing:")
    await state.set_state(SearchState.waiting_query)
    await state.update_data(search_type="code")
    await call.answer()

@router.message(SearchState.waiting_query)
async def process_search(message: Message, state: FSMContext):
    data = await state.get_data()
    query = message.text.strip()
    await state.clear()
    
    user = await db.get_user(message.from_user.id)
    
    if data.get("search_type") == "code":
        anime = await db.get_anime_by_code(query)
        results = [anime] if anime else []
    else:
        results = await db.search_anime(query)
    
    if not results:
        await message.answer(
            "😔 Hech narsa topilmadi!",
            reply_markup=kb.main_menu(user["role"] if user else "user")
        )
        return
    
    for anime in results:
        await send_anime_card(message, anime, user)

async def send_anime_card(message: Message, anime, user):
    is_premium_anime = bool(anime["is_premium"])
    user_is_premium = bool(user["is_premium"]) if user else False
    role = user["role"] if user else "user"
    
    premium_badge = "⭐ PREMIUM" if is_premium_anime else "🆓 Bepul"
    text = (
        f"🎌 <b>{anime['title']}</b>\n"
        f"🔢 Kod: <code>{anime['code']}</code>\n"
        f"💎 {premium_badge}\n\n"
        f"📖 {anime['bio'] or 'Tavsif yo\'q'}"
    )
    
    markup = kb.anime_result_kb(anime["id"], is_premium_anime, user_is_premium or role in ("admin", "manager"))
    
    if anime["photo_id"]:
        await message.answer_photo(anime["photo_id"], caption=text, parse_mode="HTML", reply_markup=markup)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=markup)

# ─── PREMIUM ANIMELAR ────────────────────────────────────────────────────────

@router.message(F.text == "⭐ Premium animelar")
async def premium_animes(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        await message.answer("❗ Avval /start bosing!")
        return
    
    animes = await db.get_premium_animes()
    if not animes:
        await message.answer("😔 Hozircha premium animelar yo'q!")
        return
    
    text = "⭐ <b>Premium Animelar:</b>\n\n"
    for anime in animes:
        text += f"🎌 {anime['title']} — <code>{anime['code']}</code>\n"
    
    if not user["is_premium"] and user["role"] not in ("admin", "manager"):
        text += "\n\n🔒 Premium olish uchun Admin/Manager bilan bog'laning!"
    
    await message.answer(text, parse_mode="HTML")

# ─── QISMLARNI KO'RISH ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("episodes_"))
async def show_episodes(call: CallbackQuery):
    anime_id = int(call.data.split("_")[1])
    user = await db.get_user(call.from_user.id)
    anime = await db.get_anime_by_id(anime_id)
    
    if anime["is_premium"] and not user["is_premium"] and user["role"] not in ("admin", "manager"):
        await call.answer("🔒 Bu anime premium!", show_alert=True)
        return
    
    episodes = await db.get_episodes(anime_id)
    if not episodes:
        await call.answer("😔 Hozircha qismlar yo'q!", show_alert=True)
        return
    
    await call.message.edit_text(
        f"📺 <b>{anime['title']}</b> — qismlar:",
        parse_mode="HTML",
        reply_markup=kb.episodes_kb(episodes, anime_id)
    )
    await call.answer()

@router.callback_query(F.data.startswith("watch_"))
async def watch_episode(call: CallbackQuery):
    ep_id = int(call.data.split("_")[1])
    async with __import__("aiosqlite").connect("anime_bot.db") as db_conn:
        db_conn.row_factory = __import__("aiosqlite").Row
        async with db_conn.execute("SELECT * FROM episodes WHERE id=?", (ep_id,)) as cur:
            ep = await cur.fetchone()
    
    if ep and ep["file_id"]:
        await call.message.answer_video(ep["file_id"], caption=f"📺 {ep['episode_number']}-qism: {ep['title']}")
    else:
        await call.answer("😔 Fayl topilmadi!", show_alert=True)

@router.callback_query(F.data == "need_premium")
async def need_premium_info(call: CallbackQuery):
    await call.answer(
        "🔒 Bu anime premium!\nPremium olish uchun Admin yoki Manager bilan bog'laning.",
        show_alert=True
    )
