import asyncpg
from typing import Optional
from config import DATABASE_URL

pool: Optional[asyncpg.Pool] = None


# =========================
# POOL & INIT
# =========================
async def init_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)


async def init_db():
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       BIGINT PRIMARY KEY,
                full_name     TEXT,
                phone         TEXT,
                lang          TEXT DEFAULT 'uz',
                is_activated  BOOLEAN DEFAULT FALSE,
                registered_at TIMESTAMP DEFAULT NOW(),
                activated_at  TIMESTAMP
            )
        """)


# =========================
# USER CRUD
# =========================
async def get_user(user_id: int) -> Optional[asyncpg.Record]:
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )


async def create_user(user_id: int, lang: str = "uz"):
    """Faqat yangi user yaratiladi, mavjud bo'lsa hech narsa qilmaydi."""
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (user_id, lang)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO NOTHING
            """,
            user_id, lang
        )


async def update_user_name(user_id: int, full_name: str):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET full_name = $1 WHERE user_id = $2",
            full_name, user_id
        )


async def update_user_phone(user_id: int, phone: str):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET phone = $1 WHERE user_id = $2",
            phone, user_id
        )


async def set_lang(user_id: int, lang: str):
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET lang = $1 WHERE user_id = $2",
            lang, user_id
        )


async def get_lang(user_id: int) -> str:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT lang FROM users WHERE user_id = $1", user_id
        )
        return row["lang"] if row else "uz"


async def is_activated(user_id: int) -> bool:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT is_activated FROM users WHERE user_id = $1", user_id
        )
        return bool(row["is_activated"]) if row else False


async def activate_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET is_activated = TRUE, activated_at = NOW()
            WHERE user_id = $1
            """,
            user_id
        )


async def deactivate_user(user_id: int):
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE users
            SET is_activated = FALSE, activated_at = NULL
            WHERE user_id = $1
            """,
            user_id
        )


# =========================
# ADMIN QUERIES
# =========================
async def get_all_users(limit: int = 30, offset: int = 0):
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM users
            ORDER BY registered_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit, offset
        )


async def get_pending_users():
    """Ro'yxatdan o'tgan lekin aktivlanmagan userlar."""
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM users
            WHERE is_activated = FALSE AND full_name IS NOT NULL
            ORDER BY registered_at DESC
            """
        )


async def get_activated_users():
    """Aktivlangan userlar (deaktivatsiya uchun)."""
    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT * FROM users
            WHERE is_activated = TRUE
            ORDER BY activated_at DESC
            """
        )


async def get_stats() -> tuple:
    """(jami, aktivlangan, kutayotgan) qaytaradi."""
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        activated = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE is_activated = TRUE"
        )
        pending = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE is_activated = FALSE AND full_name IS NOT NULL"
        )
        return total, activated, pending
