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


def size_category_keyboard(lang: str = "ru"):
    # fallback если язык неизвестен
    if lang not in ["ru", "uz", "en"]:
        lang = "ru"

    buttons = [
        [KeyboardButton(text=TEXTS["size_category"]["clothes"][lang])],
        [KeyboardButton(text=TEXTS["size_category"]["shoes"][lang])],
        [KeyboardButton(text=TEXTS["size_category"]["accessories"][lang])]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Клавиатура размеров одежды
def clothing_size_keyboard():
    buttons = [
        [KeyboardButton(text="XS (42)"), KeyboardButton(text="S (44)")],
        [KeyboardButton(text="M (46-48)"), KeyboardButton(text="L (50-52)")],
        [KeyboardButton(text="XL (54-56)"), KeyboardButton(text="XXL (58-60)")],
        [KeyboardButton(text="XXXL (62-64)"), KeyboardButton(text="Другое")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Клавиатура размеров обуви
def shoes_size_keyboard():
    buttons = [
        [KeyboardButton(text="36"), KeyboardButton(text="37"), KeyboardButton(text="38")],
        [KeyboardButton(text="39"), KeyboardButton(text="40"), KeyboardButton(text="41")],
        [KeyboardButton(text="42"), KeyboardButton(text="43"), KeyboardButton(text="44")],
        [KeyboardButton(text="45"), KeyboardButton(text="46"), KeyboardButton(text="Другое")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


# Клавиатура состояния
def condition_keyboard(lang: str):
    items = TEXTS["conditions"].get(lang, TEXTS["conditions"]["ru"])
    buttons = [
        [KeyboardButton(text=items[0]), KeyboardButton(text=items[1])],
        [KeyboardButton(text=items[2]), KeyboardButton(text=items[3])],
        [KeyboardButton(text=items[4])]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

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

def photos_keyboard(lang: str):
    button_text = TEXTS["photos_done"].get(lang, TEXTS["photos_done"]["ru"])
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=button_text)]],
        resize_keyboard=True
    )