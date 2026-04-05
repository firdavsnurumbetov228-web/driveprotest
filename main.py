import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command

TOKEN = "8291260233:AAFBXv_1is_ulavf_cPY7D3tUhxZeSdCXUM"  # xavfsizlik uchun tokenni yashir!

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}

# Default keyboard
def get_default_keyboard(user_id: int):
    lang = user_lang.get(user_id, "uz")

    if lang == "uz":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📚 Terminlar",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    ),
                    KeyboardButton(
                        text="📝 Bot haqida qisqacha",
                        web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/")
                    )
                ],
                [
                    KeyboardButton(text="💳 Aktivatsiya / Подписка"),
                    KeyboardButton(text="🌐 Tilni o‘zgartirish")
                ]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(
                        text="📚 Термины",
                        web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")
                    ),
                    KeyboardButton(
                        text="📝 коротко о боте",
                        web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/")
                    )
                ],
                [
                    KeyboardButton(text="💳 Активация / Подписка"),
                    KeyboardButton(text="🌐 Сменить язык")
                ]
            ],
            resize_keyboard=True
        )


# START (IMAGE + TEXT)
@dp.message(Command("start"))
async def start(message: types.Message):
    user_lang[message.from_user.id] = "uz"
    keyboard = get_default_keyboard(message.from_user.id)

    photo_url = "https://i.imgur.com/3ZQ3Z4L.png"  # 🔥 shu yerga o‘zingni logo URL qo‘y

    await message.answer_photo(
        photo=photo_url,
        caption=(
            "🚗 AVTOTEST 911 botga xush kelibsiz!\n\n"
            "📚 Terminlarni o‘rganing\n"
            "📝 Bot haqida ma'lumot oling\n"
            "💳 Aktivatsiya qilib test ishlang\n\n"
            "👇 Pastdagi tugmalardan foydalaning"
        ),
        reply_markup=keyboard
    )


# HAMMA MESSAGE HANDLER (BITTA QILDIM)
@dp.message()
async def handle_all(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")

    # WebApp data
    if message.web_app_data:
        data = message.web_app_data.data
        await message.answer(f"📊 Natijangiz: {data}")
        return

    # UZ
    if lang == "uz":
        if message.text == "💳 Aktivatsiya / Подписка":
            await message.answer("💳 Aktivatsiya bo‘limi: tez kunda qo‘shiladi...")
        elif message.text == "🌐 Tilni o‘zgartirish":
            user_lang[user_id] = "ru"
            await message.answer(
                "🇷🇺 Til rus tiliga o‘zgartirildi!",
                reply_markup=get_default_keyboard(user_id)
            )
        elif message.text not in ["📚 Terminlar", "📝 Bot haqida qisqacha"]:
            await message.answer("⚠️ Iltimos, tugmalardan foydalaning 👇")

    # RU
    else:
        if message.text == "💳 Активация / Подписка":
            await message.answer("💳 Раздел активации скоро будет доступен...")
        elif message.text == "🌐 Сменить язык":
            user_lang[user_id] = "uz"
            await message.answer(
                "🇺🇿 Til o‘zbek tiliga o‘zgartirildi!",
                reply_markup=get_default_keyboard(user_id)
            )
        elif message.text not in ["📚 Термины", "📝 коротко о боте"]:
            await message.answer("⚠️ Пожалуйста, используйте кнопки 👇")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())