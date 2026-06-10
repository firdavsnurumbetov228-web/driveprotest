import os
import asyncio
import logging
import aiosqlite
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "users.db"


# =========================
# DATABASE
# =========================
async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                lang TEXT DEFAULT 'uz'
            )
        """)
        await db.commit()


async def get_lang(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT lang FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cursor.fetchone()

    return row[0] if row else "uz"


async def set_lang(user_id: int, lang: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT INTO users(user_id, lang)
            VALUES(?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET lang=excluded.lang
        """, (user_id, lang))
        await db.commit()


# =========================
# CONSTANTS
# =========================
VIDEO_TEXTS = {
    "🎥 Video qo‘llanma",
    "🎥 Video qo'llanma",
    "🎥 Видео инструкция"
}

ACTIVATION_TEXTS = {
    "💳 Aktivatsiya",
    "💳 Активация подписки"
}

LANG_CHANGE_UZ = "🌐 Tilni o‘zgartirish"
LANG_CHANGE_RU = "🌐 Сменить язык"


# =========================
# KEYBOARD
# =========================
def get_keyboard(lang: str):
    if lang == "uz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📝 Mavzuni tanlash",
                        web_app=WebAppInfo(
                            url=f"https://auto-test-911-lg62.vercel.app/?lang={lang}"
                        )
                    )
                ],
                [KeyboardButton(text="💳 Aktivatsiya")],
                [
                    KeyboardButton(text="🎥 Video qo‘llanma"),
                    KeyboardButton(
                        text="ℹ️ Bot haqida qisqacha",
                        web_app=WebAppInfo(
                            url="https://avtot-test-malumotlar.vercel.app/"
                        )
                    )
                ],
                [KeyboardButton(text=LANG_CHANGE_UZ)]
            ],
            resize_keyboard=True
        )

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📝 ВЫБИРАЕМ ТЕМУ",
                    web_app=WebAppInfo(
                        url=f"https://auto-test-911-lg62.vercel.app/?lang={lang}"
                    )
                )
            ],
            [KeyboardButton(text="💳 Активация подписки")],
            [
                KeyboardButton(text="🎥 Видео инструкция"),
                KeyboardButton(
                    text="ℹ️ Коротко о Боте",
                    web_app=WebAppInfo(
                        url="https://avtot-test-malumotlar.vercel.app/"
                    )
                )
            ],
            [KeyboardButton(text=LANG_CHANGE_RU)]
        ],
        resize_keyboard=True
    )


# =========================
# START
# =========================
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    lang = await get_lang(user_id)
    await set_lang(user_id, lang)

    await message.answer_photo(
        photo=types.FSInputFile("testt.jpg"),
        caption=(
            "🚗 Driving pro test\n"
            "📘 Haydovchilik imtihoniga tayyorlov\n\n"
            "📚 Terminlarni o‘rganing\n"
            "📝 Bot haqida ma'lumot oling\n"
            "💳 Aktivatsiya qilib test ishlang\n\n"
            "📞 Aloqa: +998940907300"
        ),
        reply_markup=get_keyboard("uz")
    )


# =========================
# ACTIVATION
# =========================
@dp.message(F.text, F.text.in_(ACTIVATION_TEXTS))
async def activation(message: types.Message):
    await message.answer(
        "💳 Aktivatsiya uchun @sariyev_u bilan bog‘laning"
    )


# =========================
# VIDEO
# =========================
@dp.message(F.text, F.text.in_(VIDEO_TEXTS))
async def video(message: types.Message):
    await message.answer(
        "🎥 Video qo‘llanma hozircha tayyor emas"
    )


# =========================
# LANGUAGE
# =========================
@dp.message(F.text == LANG_CHANGE_UZ)
async def to_ru(message: types.Message):
    await set_lang(message.from_user.id, "ru")

    await message.answer(
        "🇷🇺 Til rus tiliga o‘zgartirildi!",
        reply_markup=get_keyboard("ru")
    )


@dp.message(F.text == LANG_CHANGE_RU)
async def to_uz(message: types.Message):
    await set_lang(message.from_user.id, "uz")

    await message.answer(
        "🇺🇿 Til o‘zbek tiliga o‘zgartirildi!",
        reply_markup=get_keyboard("uz")
    )


# =========================
# WEBAPP DATA
# =========================
@dp.message(F.web_app_data)
async def webapp_data(message: types.Message):
    await message.answer(
        f"📊 Natijangiz: {message.web_app_data.data}"
    )


# =========================
# FALLBACK
# =========================
@dp.message()
async def fallback(message: types.Message):
    lang = await get_lang(message.from_user.id)

    if lang == "uz":
        await message.answer(
            "⚠️ Iltimos, tugmalardan foydalaning 👇"
        )
    else:
        await message.answer(
            "⚠️ Пожалуйста, используйте кнопки 👇"
        )


# =========================
# MAIN
# =========================
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())