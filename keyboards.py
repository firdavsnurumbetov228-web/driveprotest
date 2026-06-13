import time as _time

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from config import WEBAPP_URL, INFO_URL

# Til o'zgartirish tugmalari matni
LANG_CHANGE_UZ = "🌐 Tilni o'zgartirish"
LANG_CHANGE_RU = "🌐 Сменить язык"

# Video tugmalar matni
VIDEO_TEXTS = {"🎥 Video qo'llanma", "🎥 Видео инструкция"}

# Aktivatsiya tugmalar matni
ACTIVATION_TEXTS = {"💳 Aktivatsiya", "💳 Активация подписки"}


# =========================
# ASOSIY KLAVIATURA
# =========================
def get_main_keyboard(lang: str, activated: bool = False) -> ReplyKeyboardMarkup:
    """
    activated=True  → mini-app tugmasi bor (to'liq klaviatura)
    activated=False → mini-app tugmasi yo'q (cheklangan klaviatura)

    URL ga 't=' timestamp qo'shiladi — Telegram keshini o'chiradi,
    til o'zgarganda mini-app ham yangi tilda ochiladi.
    """
    # Cache-buster: har safar til o'zgarganda Telegram yangi URL ko'radi
    ts = int(_time.time())

    if lang == "uz":
        rows = []
        if activated:
            rows.append([
                KeyboardButton(
                    text="📝 Mavzuni tanlash",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?lang={lang}&t={ts}")
                )
            ])
        rows.append([KeyboardButton(text="💳 Aktivatsiya")])
        rows.append([
            KeyboardButton(text="🎥 Video qo'llanma"),
            KeyboardButton(
                text="ℹ️ Bot haqida qisqacha",
                web_app=WebAppInfo(url=INFO_URL)
            )
        ])
        rows.append([KeyboardButton(text=LANG_CHANGE_UZ)])
    else:  # ru
        rows = []
        if activated:
            rows.append([
                KeyboardButton(
                    text="📝 ВЫБИРАЕМ ТЕМУ",
                    web_app=WebAppInfo(url=f"{WEBAPP_URL}?lang={lang}&t={ts}")
                )
            ])
        rows.append([KeyboardButton(text="💳 Активация подписки")])
        rows.append([
            KeyboardButton(text="🎥 Видео инструкция"),
            KeyboardButton(
                text="ℹ️ Коротко о Боте",
                web_app=WebAppInfo(url=INFO_URL)
            )
        ])
        rows.append([KeyboardButton(text=LANG_CHANGE_RU)])

    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


# =========================
# TELEFON KLAVIATURASI
# =========================
def get_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    text = (
        "📱 Telefon raqamni yuborish"
        if lang == "uz"
        else "📱 Отправить номер телефона"
    )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# =========================
# ADMIN PANEL KLAVIATURASI
# =========================
def get_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👥 Userlarni ko'rish",
                    callback_data="admin_users"
                ),
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="admin_stats"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✅ Aktivatsiya tasdiqlash",
                    callback_data="admin_activate"
                ),
                InlineKeyboardButton(
                    text="❌ Aktivatsiyani o'chirish",
                    callback_data="admin_deactivate"
                ),
            ],
        ]
    )


# =========================
# USER TANLASH KLAVIATURASI
# =========================
def get_user_select_keyboard(users, action: str) -> InlineKeyboardMarkup:
    """
    action: 'activate' yoki 'deactivate'
    Har bir user uchun bitta tugma + Orqaga tugmasi.
    """
    buttons = []
    for user in users:
        name = user["full_name"] or f"User {user['user_id']}"
        phone = user["phone"] or "—"
        label = f"{name} | {phone}"
        buttons.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"{action}_{user['user_id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
