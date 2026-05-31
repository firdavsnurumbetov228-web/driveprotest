import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}


# 🔘 KEYBOARD
def get_keyboard(lang: str):
    if lang == "uz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📝 Mavzuni tanlash",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    )
                ],
                [
                    KeyboardButton(
                        text="📚 Imtihon topshirish",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    )
                ],
                [KeyboardButton(text="💳 Aktivatsiya")],
                [
                    KeyboardButton(
                        text="🎥 Video qo‘llanma",
                    ),
                    KeyboardButton(
                        text="ℹ️ Bot haqida qisqacha",
                        web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/")
                    )
                ],
                [KeyboardButton(text="🌐 Tilni o‘zgartirish")]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📝 ВЫБИРАЕМ ТЕМУ",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    )
                ],
                [
                    KeyboardButton(
                        text="📚 Сдавать экзамен",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    )
                ],
                [KeyboardButton(text="💳 Активация подписки")],
                [
                    KeyboardButton(
                        text="🎥 Видео инструкция",
                    ),
                    KeyboardButton(
                        text="ℹ️ Коротко о Боте",
                        web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/")
                    )
                ],
                [KeyboardButton(text="🌐 Сменить язык")]
            ],
            resize_keyboard=True
        )

# 🚀 START
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_lang[user_id] = "uz"

    await message.answer_photo(
        photo=types.FSInputFile("test.jpg"),
        caption=(
            "🚗 AVTOTEST 911\n"
            "📘 Haydovchilik imtihoniga tayyorlov\n\n"
            "📚 Terminlarni o‘rganing\n"
            "📝 Bot haqida ma'lumot oling\n"
            "💳 Aktivatsiya qilib test ishlang\n\n"
            "📞 Aloqa: +998940907300"
        ),
        reply_markup=get_keyboard("uz")
    )


# 💳 AKTIVATSIYA (UZ)
@dp.message(F.text == "💳 Aktivatsiya")
async def aktiv_uz(message: types.Message):
    await message.answer("💳 Aktivatsiya uchun @sariyev_u bilan bog‘laning")


# 💳 АКТИВАЦИЯ (RU)
@dp.message(F.text == "💳 Активация")
async def aktiv_ru(message: types.Message):
    await message.answer("💳 Раздел активации скоро будет доступен...")


# 🌐 TILNI O‘ZGARTIRISH (UZ -> RU)
@dp.message(F.text == "🌐 Tilni o‘zgartirish")
async def lang_ru(message: types.Message):
    user_lang[message.from_user.id] = "ru"
    await message.answer(
        "🇷🇺 Til rus tiliga o‘zgartirildi!",
        reply_markup=get_keyboard("ru")
    )


# 🌐 СМЕНИТЬ ЯЗЫК (RU -> UZ)
@dp.message(F.text == "🌐 Сменить язык")
async def lang_uz(message: types.Message):
    user_lang[message.from_user.id] = "uz"
    await message.answer(
        "🇺🇿 Til o‘zbek tiliga o‘zgartirildi!",
        reply_markup=get_keyboard("uz")
    )
@dp.message(F.text == "🎥 Video qo‘llanma")
async def video_uz(message: types.Message):
    await message.answer("🎥 Video qo‘llanma")

# 📊 WEB APP DATA
@dp.message(F.web_app_data)
async def webapp_data(message: types.Message):
    await message.answer(f"📊 Natijangiz: {message.web_app_data.data}")


# ⚠️ DEFAULT (XATO BOSSA)
@dp.message()
async def fallback(message: types.Message):
    lang = user_lang.get(message.from_user.id, "uz")

    if lang == "uz":
        await message.answer("⚠️ Iltimos, tugmalardan foydalaning 👇")
    else:
        await message.answer("⚠️ Пожалуйста, используйте кнопки 👇")


# ▶️ MAIN
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())