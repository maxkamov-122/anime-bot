import aiosqlite

DB_PATH = "anime_bot.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                role TEXT DEFAULT 'user',
                is_premium INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS animes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                bio TEXT,
                photo_id TEXT,
                is_premium INTEGER DEFAULT 0,
                added_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anime_id INTEGER,
                episode_number INTEGER,
                title TEXT,
                file_id TEXT,
                FOREIGN KEY (anime_id) REFERENCES animes(id)
            )
        """)
        await db.commit()

# ─── USER ───────────────────────────────────────────────────────────────────

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,)) as cur:
            return await cur.fetchone()

async def create_user(telegram_id, username, full_name, phone):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, username, full_name, phone) VALUES (?,?,?,?)",
            (telegram_id, username, full_name, phone)
        )
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY joined_at DESC") as cur:
            return await cur.fetchall()

async def set_user_role(telegram_id, role):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET role=? WHERE telegram_id=?", (role, telegram_id))
        await db.commit()

async def set_user_premium(telegram_id, is_premium: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET is_premium=? WHERE telegram_id=?", (int(is_premium), telegram_id))
        await db.commit()

# ─── ANIME ───────────────────────────────────────────────────────────────────

async def add_anime(title, code, bio, photo_id, is_premium, added_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO animes (title, code, bio, photo_id, is_premium, added_by) VALUES (?,?,?,?,?,?)",
            (title, code, bio, photo_id, int(is_premium), added_by)
        )
        await db.commit()

async def get_anime_by_code(code):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE code=?", (code,)) as cur:
            return await cur.fetchone()

async def search_anime(query):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM animes WHERE title LIKE ? OR code LIKE ?",
            (f"%{query}%", f"%{query}%")
        ) as cur:
            return await cur.fetchall()

async def get_all_animes():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes ORDER BY created_at DESC") as cur:
            return await cur.fetchall()

async def get_premium_animes():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE is_premium=1") as cur:
            return await cur.fetchall()

# ─── EPISODE ─────────────────────────────────────────────────────────────────

async def add_episode(anime_id, episode_number, title, file_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO episodes (anime_id, episode_number, title, file_id) VALUES (?,?,?,?)",
            (anime_id, episode_number, title, file_id)
        )
        await db.commit()

async def get_episodes(anime_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM episodes WHERE anime_id=? ORDER BY episode_number",
            (anime_id,)
        ) as cur:
            return await cur.fetchall()

async def get_anime_by_id(anime_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM animes WHERE id=?", (anime_id,)) as cur:
            return await cur.fetchone()
