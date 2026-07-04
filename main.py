import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
from config import BOT_TOKEN, ADMIN_IDS
from keyboards import (
    get_main_keyboard,
    get_phone_keyboard,
    get_admin_keyboard,
    get_user_select_keyboard,
    remove_keyboard,
    LANG_CHANGE_UZ,
    LANG_CHANGE_RU,
    VIDEO_TEXTS,
    ACTIVATION_TEXTS,
)
from states import Registration

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ─────────────────────────────────────────────
# YORDAMCHI FUNKSIYALAR
# ─────────────────────────────────────────────
def start_caption_uz(activated: bool) -> str:
    if activated:
        return (
            "🚗 *Drive Pro Test*\n"
            "📘 Haydovchilik imtihoniga tayyorlov\n\n"
            "📝 Mavzuni tanlash — test boshlash\n"
            "💳 Aktivatsiya — obuna ma'lumoti\n"
            "🎥 Video qo'llanma — ko'rsatmalar\n\n"
            "📞 Aloqa: +998940907300"
        )
    return (
        "🚗 *Drive Pro Test*\n\n"
        "⚠️ Hisobingiz hali faollashtirilmagan.\n"
        "Admin tasdiqlashini kuting yoki aktivatsiya uchun murojaat qiling.\n\n"
        "📞 Aloqa: +998940907300"
    )


def start_caption_ru(activated: bool) -> str:
    if activated:
        return (
            "🚗 *Drive Pro Test*\n"
            "📘 Подготовка к экзамену по вождению\n\n"
            "📝 Выбрать тему — начать тест\n"
            "💳 Активация — информация о подписке\n"
            "🎥 Видео инструкция — руководство\n\n"
            "📞 Контакт: +998940907300"
        )
    return (
        "🚗 *Drive Pro Test*\n\n"
        "⚠️ Ваш аккаунт ещё не активирован.\n"
        "Ожидайте подтверждения от администратора.\n\n"
        "📞 Контакт: +998940907300"
    )


# ─────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()

    # ── Admin ──
    if user_id in ADMIN_IDS:
        await message.answer(
            "👨‍💼 *Admin paneliga xush kelibsiz!*\n\nQuyidagi amallardan birini tanlang:",
            parse_mode="Markdown",
            reply_markup=get_admin_keyboard(),
        )
        return

    user = await db.get_user(user_id)

    # ── To'liq ro'yxatdan o'tgan user ──
    if user and user["full_name"] and user["phone"]:
        lang = user["lang"]
        activated = bool(user["is_activated"])
        caption = (
            start_caption_uz(activated)
            if lang == "uz"
            else start_caption_ru(activated)
        )
        await message.answer_photo(
            photo=types.FSInputFile("testt.jpg"),
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(lang, activated),
        )
        return

    # ── Yangi user — ro'yxatdan o'tkazish ──
    if not user:
        await db.create_user(user_id, "uz")

    await state.set_state(Registration.waiting_for_name)
    await message.answer(
        "🚗 *Drive Pro Test*ga xush kelibsiz!\n\n"
        "Ro'yxatdan o'tish uchun ism va familiyangizni kiriting:\n"
        "_(Masalan: Abdullayev Jasur)_",
        parse_mode="Markdown",
        reply_markup=remove_keyboard(),
    )


# ─────────────────────────────────────────────
# RO'YXATDAN O'TISH: ISM
# ─────────────────────────────────────────────
@dp.message(Registration.waiting_for_name)
async def reg_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = (message.text or "").strip()
    lang = await db.get_lang(user_id)

    if len(full_name) < 3 or not full_name.replace(" ", "").isalpha():
        err = (
            "❌ Iltimos, to'liq ism va familiyangizni kiriting.\n"
            "_(Faqat harflardan iborat bo'lishi kerak)_"
            if lang == "uz"
            else
            "❌ Пожалуйста, введите полное имя и фамилию.\n"
            "_(Только буквы)_"
        )
        await message.answer(err, parse_mode="Markdown")
        return

    await db.update_user_name(user_id, full_name)
    await state.update_data(full_name=full_name)
    await state.set_state(Registration.waiting_for_phone)

    text = (
        f"✅ Rahmat, *{full_name}*!\n\n"
        "📱 Endi telefon raqamingizni yuboring\n"
        "_(Tugmani bosib yoki qo'lda yozing: +998901234567)_"
        if lang == "uz"
        else
        f"✅ Спасибо, *{full_name}*!\n\n"
        "📱 Теперь отправьте ваш номер телефона\n"
        "_(Нажмите кнопку или введите вручную: +998901234567)_"
    )
    await message.answer(
        text, parse_mode="Markdown", reply_markup=get_phone_keyboard(lang)
    )


# ─────────────────────────────────────────────
# RO'YXATDAN O'TISH: TELEFON (kontakt orqali)
# ─────────────────────────────────────────────
@dp.message(Registration.waiting_for_phone, F.contact)
async def reg_phone_contact(message: types.Message, state: FSMContext):
    await _finish_registration(message, state, message.contact.phone_number)


# ─────────────────────────────────────────────
# RO'YXATDAN O'TISH: TELEFON (matn orqali)
# ─────────────────────────────────────────────
@dp.message(Registration.waiting_for_phone, F.text)
async def reg_phone_text(message: types.Message, state: FSMContext):
    phone = (message.text or "").strip()
    await _finish_registration(message, state, phone)


async def _finish_registration(
    message: types.Message, state: FSMContext, phone: str
):
    user_id = message.from_user.id
    lang = await db.get_lang(user_id)

    await db.update_user_phone(user_id, phone)
    await state.clear()

    user = await db.get_user(user_id)
    name = user["full_name"] if user else "—"

    # ── Adminlarga xabar ──
    admin_msg = (
        f"🆕 *Yangi foydalanuvchi ro'yxatdan o'tdi!*\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n"
        f"🆔 ID: `{user_id}`\n"
        f"🌐 Til: {lang.upper()}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="Markdown")
        except Exception:
            pass

    # ── Userga javob ──
    text = (
        f"✅ *Ro'yxatdan muvaffaqiyatli o'tdingiz!*\n\n"
        f"👤 Ism: {name}\n"
        f"📱 Telefon: {phone}\n\n"
        "⏳ Admin aktivatsiyangizni tasdiqlashini kuting.\n"
        "Tasdiqlangandan so'ng to'liq testdan foydalana olasiz.\n\n"
        "📞 Aloqa: +998940907300"
        if lang == "uz"
        else
        f"✅ *Вы успешно зарегистрировались!*\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Телефон: {phone}\n\n"
        "⏳ Ожидайте подтверждения активации от администратора.\n"
        "После подтверждения вы получите доступ к тестам.\n\n"
        "📞 Контакт: +998940907300"
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(lang, activated=False),
    )


# ─────────────────────────────────────────────
# ADMIN: USERLARNI KO'RISH
# ─────────────────────────────────────────────
@dp.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    users = await db.get_all_users()
    if not users:
        return await callback.answer("Foydalanuvchilar yo'q", show_alert=True)

    lines = ["👥 *Barcha foydalanuvchilar:*\n"]
    for i, u in enumerate(users, 1):
        icon = "✅" if u["is_activated"] else "⏳"
        name = u["full_name"] or "—"
        phone = u["phone"] or "—"
        lines.append(
            f"{i}. {icon} *{name}*\n"
            f"   📱 {phone}\n"
            f"   🆔 `{u['user_id']}` | 🌐 {u['lang'].upper()}\n"
        )

    text = "\n".join(lines)
    # Telegram limit 4096
    if len(text) > 4000:
        text = text[:4000] + "\n\n_(Ro'yxat qisqartirildi)_"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await callback.answer()


# ─────────────────────────────────────────────
# ADMIN: STATISTIKA
# ─────────────────────────────────────────────
@dp.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    total, activated, pending = await db.get_stats()
    not_registered = total - activated - pending

    text = (
        f"📊 *Bot statistikasi*\n\n"
        f"👥 Jami foydalanuvchilar: *{total}*\n"
        f"✅ Faollashtirilgan: *{activated}*\n"
        f"⏳ Aktivatsiya kutayotgan: *{pending}*\n"
        f"🔸 Ro'yxatdan o'tmagan: *{not_registered}*"
    )

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    back_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")]
    ])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb)
    await callback.answer()


# ─────────────────────────────────────────────
# ADMIN: AKTIVATSIYA TASDIQLASH — RO'YXAT
# ─────────────────────────────────────────────
@dp.callback_query(F.data == "admin_activate")
async def cb_admin_activate_list(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    users = await db.get_pending_users()
    if not users:
        return await callback.answer(
            "✅ Kutayotgan foydalanuvchilar yo'q!", show_alert=True
        )

    kb = get_user_select_keyboard(users, "activate")
    await callback.message.edit_text(
        f"✅ *Aktivatsiya qilish uchun userni tanlang:*\n_(Jami: {len(users)} ta)_",
        parse_mode="Markdown",
        reply_markup=kb,
    )
    await callback.answer()


# ─────────────────────────────────────────────
# ADMIN: AKTIVATSIYANI O'CHIRISH — RO'YXAT
# ─────────────────────────────────────────────
@dp.callback_query(F.data == "admin_deactivate")
async def cb_admin_deactivate_list(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    users = await db.get_activated_users()
    if not users:
        return await callback.answer(
            "❌ Faollashtirilgan foydalanuvchilar yo'q!", show_alert=True
        )

    kb = get_user_select_keyboard(users, "deactivate")
    await callback.message.edit_text(
        f"❌ *Aktivatsiyani o'chirish uchun userni tanlang:*\n_(Jami: {len(users)} ta)_",
        parse_mode="Markdown",
        reply_markup=kb,
    )
    await callback.answer()


# ─────────────────────────────────────────────
# ADMIN: AKTIVATSIYA — BAJARISH
# ─────────────────────────────────────────────
@dp.callback_query(F.data.startswith("activate_"))
async def cb_do_activate(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    target_id = int(callback.data.split("_", 1)[1])
    await db.activate_user(target_id)

    user = await db.get_user(target_id)
    lang = user["lang"] if user else "uz"
    name = user["full_name"] if user else str(target_id)

    # ── Userga xabar ──
    notify_text = (
        "🎉 *Tabriklaymiz!*\n\n"
        "✅ Hisobingiz faollashtirildi!\n"
        "Endi testlardan to'liq foydalana olasiz.\n\n"
        "📝 *Mavzuni tanlash* tugmasini bosing va testni boshlang! 🚗"
        if lang == "uz"
        else
        "🎉 *Поздравляем!*\n\n"
        "✅ Ваш аккаунт активирован!\n"
        "Теперь у вас есть полный доступ к тестам.\n\n"
        "📝 Нажмите *Выбрать тему* и начните тест! 🚗"
    )
    try:
        await bot.send_message(
            target_id,
            notify_text,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(lang, activated=True),
        )
    except Exception:
        pass

    await callback.answer(f"✅ {name} faollashtirildi!", show_alert=True)
    await callback.message.edit_text(
        "👨‍💼 *Admin paneliga xush kelibsiz!*\n\nQuyidagi amallardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )


# ─────────────────────────────────────────────
# ADMIN: DEAKTIVATSIYA — BAJARISH
# ─────────────────────────────────────────────
@dp.callback_query(F.data.startswith("deactivate_"))
async def cb_do_deactivate(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    target_id = int(callback.data.split("_", 1)[1])
    await db.deactivate_user(target_id)

    user = await db.get_user(target_id)
    lang = user["lang"] if user else "uz"
    name = user["full_name"] if user else str(target_id)

    # ── Userga xabar ──
    notify_text = (
        "⚠️ *Hisobingiz aktivatsiyasi o'chirildi\\.*\n\n"
        "Murojaat uchun: @DRIVE\\_PRO\\_admin\n"
        "📞 Tel: \\+998940907300"
        if lang == "uz"
        else
        "⚠️ *Активация вашего аккаунта отключена\\.*\n\n"
        "Для связи: @DRIVE\\_PRO\\_admin\n"
        "📞 Тел: \\+998940907300"
    )
    try:
        await bot.send_message(
            target_id,
            notify_text,
            parse_mode="MarkdownV2",
            reply_markup=get_main_keyboard(lang, activated=False),
        )
    except Exception:
        pass

    await callback.answer(f"❌ {name} aktivatsiyasi o'chirildi!", show_alert=True)
    await callback.message.edit_text(
        "👨‍💼 *Admin paneliga xush kelibsiz!*\n\nQuyidagi amallardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )


# ─────────────────────────────────────────────
# ADMIN: ORQAGA
# ─────────────────────────────────────────────
@dp.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer()
    await callback.message.edit_text(
        "👨‍💼 *Admin paneliga xush kelibsiz!*\n\nQuyidagi amallardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )
    await callback.answer()


# ─────────────────────────────────────────────
# AKTIVATSIYA TUGMASI
# ─────────────────────────────────────────────
@dp.message(F.text.in_(ACTIVATION_TEXTS))
async def msg_activation(message: types.Message):
    user_id = message.from_user.id
    lang = await db.get_lang(user_id)
    is_active = await db.is_activated(user_id)

    if is_active:
        # ── Allaqachon faollashtirilgan ──
        text = (
            "✅ *Siz allaqachon aktivatsiyaga egasiz\\!*\n\n"
            "Testlardan to'liq foydalana olasiz\\. 🚗"
            if lang == "uz"
            else
            "✅ *У вас уже есть активация\\!*\n\n"
            "Вы можете пользоваться тестами в полном объёме\\. 🚗"
        )
    else:
        # ── Hali faollashtirilmagan ──
        text = (
            "💳 *Aktivatsiya*\n\n"
            "Aktivatsiya uchun admin bilan bog'laning:\n"
            "@DRIVE\\_PRO\\_admin\n\n"
            "📞 Tel: \\+998940907300"
            if lang == "uz"
            else
            "💳 *Активация*\n\n"
            "Для активации свяжитесь с администратором:\n"
            "@DRIVE\\_PRO\\_admin\n\n"
            "📞 Тел: \\+998940907300"
        )
    await message.answer(text, parse_mode="MarkdownV2")


# ─────────────────────────────────────────────
# VIDEO TUGMASI
# ─────────────────────────────────────────────
@dp.message(F.text.in_(VIDEO_TEXTS))
async def msg_video(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    text = (
        "🎥 Video qo'llanma hozircha tayyorlanmoqda.\n"
        "Tez orada qo'shiladi! ⏳"
        if lang == "uz"
        else
        "🎥 Видео инструкция пока в разработке.\n"
        "Скоро будет добавлена! ⏳"
    )
    await message.answer(text)


# ─────────────────────────────────────────────
# TIL O'ZGARTIRISH
# ─────────────────────────────────────────────
@dp.message(F.text == LANG_CHANGE_UZ)
async def msg_to_ru(message: types.Message):
    user_id = message.from_user.id
    await db.set_lang(user_id, "ru")
    activated = await db.is_activated(user_id)
    await message.answer(
        "🇷🇺 Til rus tiliga o'zgartirildi!",
        reply_markup=get_main_keyboard("ru", activated),
    )


@dp.message(F.text == LANG_CHANGE_RU)
async def msg_to_uz(message: types.Message):
    user_id = message.from_user.id
    await db.set_lang(user_id, "uz")
    activated = await db.is_activated(user_id)
    await message.answer(
        "🇺🇿 Til o'zbek tiliga o'zgartirildi!",
        reply_markup=get_main_keyboard("uz", activated),
    )


# ─────────────────────────────────────────────
# WEBAPP DATA
# ─────────────────────────────────────────────
@dp.message(F.web_app_data)
async def msg_webapp_data(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    raw = message.web_app_data.data
    try:
        import json
        data = json.loads(raw)
        score = data.get("score", "—")
        correct = data.get("correct", "—")
        total = data.get("total", "—")
        category = data.get("category", "—")
        text = (
            f"📊 *Test natijasi*\n\n"
            f"🏷 Mavzu: {category}\n"
            f"✅ To'g'ri: {correct}/{total}\n"
            f"📈 Foiz: {score}%"
            if lang == "uz"
            else
            f"📊 *Результат теста*\n\n"
            f"🏷 Тема: {category}\n"
            f"✅ Правильных: {correct}/{total}\n"
            f"📈 Процент: {score}%"
        )
    except Exception:
        text = f"📊 Natijangiz: {raw}" if lang == "uz" else f"📊 Ваш результат: {raw}"

    await message.answer(text, parse_mode="Markdown")


# ─────────────────────────────────────────────
# FALLBACK
# ─────────────────────────────────────────────
@dp.message()
async def msg_fallback(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current:
        return  # FSM jarayonida — e'tiborsiz qoldir

    lang = await db.get_lang(message.from_user.id)
    text = (
        "⚠️ Iltimos, tugmalardan foydalaning 👇"
        if lang == "uz"
        else "⚠️ Пожалуйста, используйте кнопки 👇"
    )
    await message.answer(text)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
async def main():
    await db.init_pool()
    await db.init_db()
    logging.info("✅ PostgreSQL ulanish o'rnatildi")
    logging.info("🤖 Bot ishga tushdi — polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())