# 🎌 Anime Telegram Bot

## O'rnatish

### 1. Python va kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 2. config.py ni sozlang
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # @BotFather dan oling
ADMIN_ID = 123456789                 # O'z Telegram ID ingiz (userinfobot dan bilib oling)
```

### 3. Botni ishga tushiring
```bash
python bot.py
```

---

## Funksiyalar

### 👤 Oddiy Foydalanuvchi
- `/start` — Ro'yxatdan o'tish (telefon raqam orqali)
- 🔍 Anime qidirish — Nomi yoki kodi bo'yicha
- ⭐ Premium animelar — Premium animeler ro'yxati
- 👤 Mening profilim — O'z profil ma'lumotlari

### 🛡 Manager
- Barcha user imkoniyatlari
- ➕ Anime qo'shish — Nom, kod, bio, rasm, premium belgi
- Qism qo'shish — Video fayl yuklash

### 👑 Admin (faqat siz)
- Barcha manager imkoniyatlari
- 👥 Foydalanuvchilar — Ro'yxat va boshqaruv
- User → Manager / Manager → User rol o'zgartirish
- Premium berish / olib tashlash

---

## Fayl tuzilmasi
```
anime_bot/
├── bot.py           # Asosiy fayl
├── config.py        # Token va Admin ID
├── database.py      # SQLite ma'lumotlar bazasi
├── keyboards.py     # Tugmalar
├── requirements.txt
└── handlers/
    ├── common.py    # Start, profil, ro'yxatdan o'tish
    ├── anime.py     # Qidirish, ko'rish
    ├── manager.py   # Anime va qism qo'shish
    └── admin.py     # Foydalanuvchi boshqaruvi
```
