from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiobot.texts import TEXTS

# Главная клавиатура

def main_keyboard(lang):
    btn = {
        "ru": ["➕ Подать объявление"],
        "uz": ["➕ E'lon joylashtirish"],
        "en": ["➕ Submit Ad"]
    }
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in btn[lang]],
        resize_keyboard=True
    )

# Клавиатура выбора языка

def lang_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=flag)] for flag in ["🇷🇺 Русский", "🇺🇿 O‘zbekcha", "🇬🇧 English"]],
        resize_keyboard=True
    )

# Клавиатура для отправки телефона

def phone_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS["send_phone"][lang], request_contact=True)]],
        resize_keyboard=True
    )

# Клавиатура размеров

def size_keyboard():
    size_buttons = [
        [KeyboardButton(text="XS (42)"), KeyboardButton(text="S (44)"), KeyboardButton(text="M (46-48)")],
        [KeyboardButton(text="L (50-52)"), KeyboardButton(text="XL (54-56)")],
        [KeyboardButton(text="XXL (58-60)"), KeyboardButton(text="XXXL (62-64)")]
    ]
    return ReplyKeyboardMarkup(keyboard=size_buttons, resize_keyboard=True)

# Клавиатура состояния

def condition_keyboard():
    condition_buttons = [
        [KeyboardButton(text="Новый"), KeyboardButton(text="Почти новый")],
        [KeyboardButton(text="Хорошее"), KeyboardButton(text="Среднее")],
        [KeyboardButton(text="Требует ремонта")]
    ]
    return ReplyKeyboardMarkup(keyboard=condition_buttons, resize_keyboard=True)

# Клавиатура подтверждения

def confirm_keyboard(lang):
    btns = {
        "ru": ["✅ Подтвердить", "✏️ Изменить", "❌ Отменить"],
        "uz": ["✅ Tasdiqlash", "✏️ O'zgartirish", "❌ Bekor qilish"],
        "en": ["✅ Confirm", "✏️ Edit", "❌ Cancel"]
    }
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=b)] for b in btns[lang]],
        resize_keyboard=True
    )

def photos_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Готово")]],
        resize_keyboard=True
    ) 