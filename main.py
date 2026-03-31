import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command

TOKEN = "8291260233:AAGuU7qhz5QXDQvOXPUTQZavvNowd7_5zWU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}

# Default keyboard generator
def get_default_keyboard(user_id: int):
    lang = user_lang.get(user_id, "uz")
    if lang == "uz":
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📚 Terminlar", web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")),
                 KeyboardButton(text="📝 Bot haqida qisqacha", web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/"))],
                [KeyboardButton(text="💳 Aktivatsiya / Подписка"),
                 KeyboardButton(text="🌐 Tilni o‘zgartirish")]
            ],
            resize_keyboard=True
        )
    else:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📚 Термины", web_app=WebAppInfo(url="https://auto-test-911-lg62.vercel.app/")),
                 KeyboardButton(text="📝 коротко о боте", web_app=WebAppInfo(url="https://avtot-test-malumotlar.vercel.app/"))],
                [KeyboardButton(text="💳 Активация / Подписка"),
                 KeyboardButton(text="🌐 Сменить язык")]
            ],
            resize_keyboard=True
        )
    return kb

@dp.message(Command("start"))
async def start(message: types.Message):
    user_lang[message.from_user.id] = "uz"  
    keyboard = get_default_keyboard(message.from_user.id)
    await message.answer("Avtotest botga xush kelibsiz! 👇", reply_markup=keyboard)
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    lang = user_lang.get(user_id, "uz")

    if lang == "uz":
        if message.text == "💳 Aktivatsiya / Подписка":
            await message.answer("💳 Aktivatsiya / Подписка bo‘limi: ...")
        elif message.text == "🌐 Tilni o‘zgartirish":
            user_lang[user_id] = "ru"
            await message.answer("Til rus tiliga o‘zgartirildi!", reply_markup=get_default_keyboard(user_id))
        elif message.text not in ["📚 Terminlar", "📝 Bot haqida qisqacha"]:
            await message.answer("Iltimos, tugmalardan foydalaning 👆")
    else:
        if message.text == "💳 Активация / Подписка":
            await message.answer("💳 Раздел активации: ...")
        elif message.text == "🌐 Сменить язык":
            user_lang[user_id] = "uz"
            await message.answer("Язык изменён на узбекский!", reply_markup=get_default_keyboard(user_id))
        elif message.text not in ["📚 Термины", "📝 коротко о боте"]:
            await message.answer("Пожалуйста, используйте кнопки 👆")

@dp.message()
async def get_webapp_data(message: types.Message):
    if message.web_app_data:
        data = message.web_app_data.data
        await message.answer(f"Natijangiz: {data}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())