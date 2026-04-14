from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database as db
import keyboards as kb

router = Router()

class AddAnime(StatesGroup):
    title = State()
    code = State()
    bio = State()
    photo = State()
    premium = State()

class AddEpisode(StatesGroup):
    anime_id = State()
    ep_number = State()
    ep_title = State()
    ep_file = State()

# ─── ANIME QO'SHISH ──────────────────────────────────────────────────────────

@router.message(F.text == "➕ Anime qo'shish")
async def start_add_anime(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user or user["role"] not in ("admin", "manager"):
        await message.answer("❌ Sizda bu huquq yo'q!")
        return
    
    await message.answer("🎌 Anime nomini yozing:")
    await state.set_state(AddAnime.title)

@router.message(AddAnime.title)
async def add_anime_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("🔢 Anime uchun unikal kod yozing (maslan: AOT, NRT, DBZ):")
    await state.set_state(AddAnime.code)

@router.message(AddAnime.code)
async def add_anime_code(message: Message, state: FSMContext):
    code = message.text.strip().upper()
    existing = await db.get_anime_by_code(code)
    if existing:
        await message.answer("❗ Bu kod allaqachon mavjud! Boshqa kod yozing:")
        return
    await state.update_data(code=code)
    await message.answer("📖 Anime haqida qisqacha bio yozing:")
    await state.set_state(AddAnime.bio)

@router.message(AddAnime.bio)
async def add_anime_bio(message: Message, state: FSMContext):
    await state.update_data(bio=message.text.strip())
    await message.answer("🖼 Anime rasmini yuboring (o'tkazish uchun — yozing: skip):")
    await state.set_state(AddAnime.photo)

@router.message(AddAnime.photo)
async def add_anime_photo(message: Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
    else:
        photo_id = None
    
    await state.update_data(photo_id=photo_id)
    await message.answer(
        "⭐ Bu anime premium bo'lsinmi?",
        reply_markup=kb.add_anime_premium_kb()
    )
    await state.set_state(AddAnime.premium)

@router.callback_query(F.data.in_({"anime_premium_yes", "anime_premium_no"}), AddAnime.premium)
async def add_anime_finish(call: CallbackQuery, state: FSMContext):
    is_premium = call.data == "anime_premium_yes"
    data = await state.get_data()
    await state.clear()
    
    await db.add_anime(
        title=data["title"],
        code=data["code"],
        bio=data["bio"],
        photo_id=data.get("photo_id"),
        is_premium=is_premium,
        added_by=call.from_user.id
    )
    
    anime = await db.get_anime_by_code(data["code"])
    premium_text = "⭐ Premium" if is_premium else "🆓 Bepul"
    
    await call.message.edit_text(
        f"✅ Anime qo'shildi!\n\n"
        f"🎌 {data['title']}\n"
        f"🔢 Kod: {data['code']}\n"
        f"💎 {premium_text}",
        reply_markup=kb.after_add_anime_kb(anime["id"])
    )
    await call.answer()

# ─── QISM QO'SHISH ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("addep_"))
async def start_add_episode(call: CallbackQuery, state: FSMContext):
    anime_id = int(call.data.split("_")[1])
    await state.update_data(anime_id=anime_id)
    await call.message.answer("📺 Qism raqamini yozing (maslan: 1):")
    await state.set_state(AddEpisode.ep_number)
    await call.answer()

@router.message(AddEpisode.ep_number)
async def add_ep_number(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗ Raqam kiriting!")
        return
    await state.update_data(ep_number=int(message.text))
    await message.answer("📝 Qism nomini yozing (maslan: Birinchi jang):")
    await state.set_state(AddEpisode.ep_title)

@router.message(AddEpisode.ep_title)
async def add_ep_title(message: Message, state: FSMContext):
    await state.update_data(ep_title=message.text.strip())
    await message.answer("🎬 Qism videosini yuboring:")
    await state.set_state(AddEpisode.ep_file)

@router.message(AddEpisode.ep_file)
async def add_ep_file(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗ Video yuboring!")
        return
    
    data = await state.get_data()
    await state.clear()
    
    await db.add_episode(
        anime_id=data["anime_id"],
        episode_number=data["ep_number"],
        title=data["ep_title"],
        file_id=message.video.file_id
    )
    
    user = await db.get_user(message.from_user.id)
    await message.answer(
        f"✅ {data['ep_number']}-qism qo'shildi!",
        reply_markup=kb.after_add_anime_kb(data["anime_id"])
    )

@router.callback_query(F.data == "done_adding")
async def done_adding(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_text("✅ Bajarildi!")
    await call.message.answer("Asosiy menyu:", reply_markup=kb.main_menu(user["role"] if user else "user"))
    await call.answer()
