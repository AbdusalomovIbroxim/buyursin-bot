from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiobot.buttons.keyboards.reply import main_keyboard, lang_keyboard, phone_keyboard, confirm_keyboard
from aiobot.texts import TEXTS
from aiobot.models.users import Users
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
import logging
router = Router()

LANGS = {"🇷🇺 Русский": "ru", "🇺🇿 O‘zbekcha": "uz", "🇬🇧 English": "en"}

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Всегда сбрасываем состояние и данные
    await state.clear()
    print(f"cmd_start: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"cmd_start: user_id={message.from_user.id}, text={message.text}")

    user = await Users.get(message.from_user.id)
    if user:
        lang = user.lang or "ru"
        await message.answer(
            TEXTS["start_desc"][lang],
            reply_markup=main_keyboard(lang)
        )
    else:
        await message.answer(
            TEXTS["welcome"]["ru"],
            reply_markup=lang_keyboard()
        )
        # ставим первое состояние регистрации (например, выбор языка)
        await state.set_state("register_language")


@router.message(StateFilter("register_language"), F.text.in_(LANGS.keys()))
async def register_choose_lang(message: Message, state: FSMContext):
    print(f"register_choose_lang: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"register_choose_lang: user_id={message.from_user.id}, text={message.text}")
    lang = LANGS[message.text]
    await state.update_data(lang=lang)
    from aiobot.models.users import Users
    user = await Users.get(message.from_user.id)
    if user and user.phone_number:
        # Просто меняем язык и показываем главное меню
        await Users.update(message.from_user.id, lang=lang)
        await message.answer(TEXTS["start_desc"][lang], reply_markup=main_keyboard(lang))
        await state.clear()
    else:
        # Новый пользователь — продолжаем регистрацию
        kb = phone_keyboard(lang)
        await message.answer(TEXTS["ask_phone"][lang], reply_markup=kb)
        await state.set_state("register_phone")

@router.message(StateFilter("register_phone"), F.contact)
async def register_phone(message: Message, state: FSMContext):
    print(f"register_phone: user_id={message.from_user.id}, contact={message.contact}")
    logging.info(f"register_phone: user_id={message.from_user.id}, contact={message.contact}")
    data = await state.get_data()
    lang = data.get("lang", "ru")
    phone = message.contact.phone_number
    await Users.create(
        user_id=message.from_user.id,
        lang=lang,
        full_name=message.from_user.full_name,
        phone_number=phone
    )
    await message.answer(TEXTS["reg_success"][lang], reply_markup=main_keyboard(lang))
    await state.clear()

@router.message(default_state, ~Command("lang"))
async def main_menu(message: Message, state: FSMContext):
    print(f"main_menu: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"main_menu: user_id={message.from_user.id}, text={message.text}")
    lang = await Users.get_language(message.from_user.id)
    btn = {"ru": "➕ Подать объявление", "uz": "➕ E'lon joylashtirish", "en": "➕ Submit Ad"}
    if message.text == btn[lang]:
        user = await Users.get(message.from_user.id)
        if not user or not user.phone_number:
            texts = {
                "ru": "Вы не зарегистрированы! Пожалуйста, нажмите /start и пройдите регистрацию.",
                "uz": "Siz ro'yxatdan o'tmagansiz! Iltimos, /start buyrug'ini bosing va ro'yxatdan o'ting.",
                "en": "You are not registered! Please press /start and complete registration."
            }
            await message.answer(texts.get(lang, texts["ru"]))
            return
        from aiobot.states import AdForm
        await state.clear()
        await state.set_state(AdForm.title)
        print(f"main_menu: set state to {await state.get_state()} for user_id={message.from_user.id}")
        logging.info(f"main_menu: set state to {await state.get_state()} for user_id={message.from_user.id}")
        await message.answer(TEXTS["ad_title"][lang])

@router.message(Command("lang"))
async def change_lang(message: Message, state: FSMContext):
    print(f"/lang: user_id={message.from_user.id}")
    logging.info(f"/lang: user_id={message.from_user.id}")
    await state.clear()
    print(f"/lang: state cleared for user_id={message.from_user.id}")
    logging.info(f"/lang: state cleared for user_id={message.from_user.id}")
    await message.answer(
        "Пожалуйста, выберите язык / Iltimos, tilni tanlang / Please select a language:",
        reply_markup=lang_keyboard()
    )
    print(f"/lang: sent lang_keyboard to user_id={message.from_user.id}")
    logging.info(f"/lang: sent lang_keyboard to user_id={message.from_user.id}")
    await state.set_state("register_language")
    print(f"/lang: set state to register_language for user_id={message.from_user.id}")
    logging.info(f"/lang: set state to register_language for user_id={message.from_user.id}")

# @router.message()
# async def check_registration(message: Message):
#     from aiobot.models.users import Users
#     user = await Users.get(message.from_user.id)
    
#     lang = "ru"
#     if user and hasattr(user, "lang") and user.lang:
#         lang = user.lang
#     texts = {
#         "ru": "Вы не зарегистрированы! Пожалуйста, нажмите /start и пройдите регистрацию.",
#         "uz": "Siz ro'yxatdan o'tmagansiz! Iltimos, /start buyrug'ini bosing va ro'yxatdan o'ting.",
#         "en": "You are not registered! Please press /start and complete registration."
#     }
#     if not user or not user.phone_number:
#         await message.answer(texts.get(lang, texts["ru"]))
