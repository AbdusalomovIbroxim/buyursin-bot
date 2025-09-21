import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InputMediaPhoto, CallbackQuery
from aiogram.utils.markdown import hlink
from aiobot.buttons.keyboards.reply import main_keyboard, lang_keyboard, size_category_keyboard, clothing_size_keyboard, photos_keyboard, condition_keyboard
from aiobot.buttons.keyboards.inline import admin_inline_keyboard, user_confirm_keyboard
from aiobot.models import Ads, Users
from aiobot.texts import TEXTS
from aiobot.states import AdForm, Register
from config import ADMIN_GROUP_ID
from dispatcher.dispatcher import bot

router = Router()
media_groups_cache = {}

CONFIRM_WORDS = {
    "yes": ["да", "ha", "yes", "xa"],
    "no": ["нет", "yo‘q", "yoq", "no", "yo'q"]
}

def is_yes(text: str) -> bool:
    return text.lower() in CONFIRM_WORDS["yes"]

def is_no(text: str) -> bool:
    return text.lower() in CONFIRM_WORDS["no"]

# 📢 Мои объявления
# @router.message(Command("my_ads"))
# async def my_ads(message: Message, state: FSMContext):
    
#     user = await Users.get(user_id=message.from_user.id)
#     if not user:
#         await message.answer(TEXTS["welcome"]["ru"], reply_markup=lang_keyboard())
#         await state.set_state(Register.language)
#         return

#     ads = await Ads.filter(user=user)
#     if not ads:
#         await message.answer({
#             "ru": "У вас пока нет объявлений.",
#             "uz": "Sizda hali e'lonlar yo'q.",
#             "en": "You don’t have any ads yet."
#         }[user.lang])
#         return

#     text = {
#         "ru": "📋 Ваши объявления:\n\n",
#         "uz": "📋 Sizning e'lonlaringiz:\n\n",
#         "en": "📋 Your ads:\n\n"
#     }[user.lang]

#     for ad in ads:
#         text += f"• {ad.title} — {ad.price} UZS\n"
#     await message.answer(text, reply_markup=main_keyboard(user.lang))


# 📢 Добавить объявление
# @router.message(Command("add_ad"))
@router.message(
    F.text.in_([
        TEXTS["add_ad"]["ru"],
        TEXTS["add_ad"]["uz"],
        TEXTS["add_ad"]["en"]
    ])
)
async def add_ad(message: Message, state: FSMContext):
    user = await Users.get(user_id=message.from_user.id)
    if not user:
        await message.answer(TEXTS["welcome"]["ru"], reply_markup=lang_keyboard())
        await state.set_state(Register.language)
        return

    await message.answer(TEXTS["ad_title"][user.lang])
    await state.set_state(AdForm.title)


@router.message(AdForm.title, F.text)
async def ad_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    user = await Users.get(user_id=message.from_user.id)
    await message.answer(TEXTS["ad_price"][user.lang])
    await state.set_state(AdForm.price)


import re

@router.message(AdForm.price, F.text)
async def ad_price(message: Message, state: FSMContext):
    user = await Users.get(user_id=message.from_user.id)
    lang = user.lang

    text = message.text.strip().lower()
    price = None

    # ❌ Отрицательные значения сразу отбрасываем
    if "-" in text:
        await message.answer({
            "ru": "❌ Цена не может быть отрицательной.",
            "uz": "❌ Narx manfiy bo‘lishi mumkin emas.",
            "en": "❌ Price cannot be negative."
        }[lang])
        return

    # Форматы: число, число + som/sum/$, число + k/к
    match = re.match(r"^(\d+)(k|к|som|sum|\$)?$", text)
    if not match:
        await message.answer({
            "ru": "❌ Неверный формат цены. Примеры: 100000 som, 200$, 100k",
            "uz": "❌ Narx formati noto‘g‘ri. Misollar: 100000 som, 200$, 100k",
            "en": "❌ Invalid price format. Examples: 100000 som, 200$, 100k"
        }[lang])
        return

    amount = int(match.group(1))
    suffix = match.group(2)

    # # Обработка сокращений
    # if suffix in ("k", "к"):   # 100k → 100000
    #     price = amount * 1000
    # elif suffix == "$":        # 200$ → переводим в сумы (например, * 12500)
    #     price = amount * 12500
    # else:                      # som / sum / ничего → считаем как есть
    price = amount

    # Лимит
    if price > 10_000_000:
        await message.answer({
            "ru": "❌ Слишком высокая цена. Введите сумму меньше 10 млн.",
            "uz": "❌ Juda katta narx. 10 mln dan kichikroq summani kiriting.",
            "en": "❌ Price too high. Enter less than 10M."
        }[lang])
        return

    await state.update_data(price=price)
    await message.answer(TEXTS["ad_size_category"][lang], reply_markup=size_category_keyboard(lang))
    await state.set_state(AdForm.size_category)


@router.message(AdForm.size_category, F.text)
async def ad_size_category(message: Message, state: FSMContext):
    await state.update_data(size_category=message.text)
    user = await Users.get(user_id=message.from_user.id)
    await message.answer(TEXTS["ad_size"][user.lang], reply_markup=clothing_size_keyboard())
    await state.set_state(AdForm.size)


@router.message(AdForm.size, F.text)
async def ad_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    user = await Users.get(user_id=message.from_user.id)
    await message.answer(TEXTS["ad_condition"][user.lang], reply_markup=condition_keyboard(user.lang))
    await state.set_state(AdForm.condition)


@router.message(AdForm.condition, F.text)
async def ad_condition(message: Message, state: FSMContext):
    await state.update_data(condition=message.text)
    user = await Users.get(user_id=message.from_user.id)
    await message.answer(TEXTS["ad_photos"][user.lang], reply_markup=photos_keyboard(user.lang))
    await state.set_state(AdForm.photos)


@router.message(AdForm.photos, F.photo)
async def ad_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    # Если сообщение часть альбома
    if message.media_group_id:
        group_id = message.media_group_id

        # добавляем фото во временный кэш
        if group_id not in media_groups_cache:
            media_groups_cache[group_id] = []

        media_groups_cache[group_id].append(message.photo[-1].file_id)

        # ждём немного, пока придут все фото альбома
        await asyncio.sleep(0.5)

        # обрабатываем только один раз, когда альбом уже собран
        if group_id in media_groups_cache:
            new_photos = media_groups_cache.pop(group_id)
            for p in new_photos:
                if len(photos) < 10:
                    photos.append(p)

            await state.update_data(photos=photos)
            await message.answer(
                f"Фотографии сохранены ✅ ({len(photos)}/{10}). "
                f"Отправьте ещё или нажмите 'Готово'."
            )
    else:
        # одиночная фотография
        if len(photos) >= 10:
            await message.answer("❌ Нельзя добавить больше 10 фотографий.")
            return

        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)

        await message.answer(
            f"Фото сохранено ✅ ({len(photos)}/{10}). "
            f"Отправьте ещё или нажмите 'Готово'."
        )


@router.message(AdForm.photos, F.text)
async def photos_done(message: Message, state: FSMContext):
    user = await Users.get(user_id=message.from_user.id)
    lang = user.lang
    done_text = TEXTS["photos_done"].get(lang, TEXTS["photos_done"]["ru"])
    data = await state.get_data()

    photos = data.get("photos", [])

    # Проверяем, нажал ли юзер кнопку "Готово"
    if message.text.strip() == done_text:
        if not photos:
            await message.answer("❌ Нужно добавить хотя бы одно фото.")
            return


        # Текст объявления
        ad_text = (
            f"{TEXTS['ad_confirm'][lang]}\n\n"
            f"📌 {TEXTS['field_title'][lang]}: {data['title']}\n"
            f"💰 {TEXTS['field_price'][lang]}: {data['price']} UZS\n"
            f"📏 {TEXTS['field_size'][lang]}: {data['size']}\n"
            f"⚡ {TEXTS['field_condition'][lang]}: {data['condition']}\n"
        )

        # Если есть несколько фото — отправляем альбом
        if photos:
            media = [InputMediaPhoto(media=p) for p in photos[:10]]
            media[0].caption = ad_text  # текст к первой фотке
            await message.answer_media_group(media, )
        else:
            await message.answer(ad_text)
        
        confirm_texts = {
            "ru": "Проверьте данные, всё верно?",
            "uz": "Ma’lumotlarni tekshiring, hammasi to‘g‘ri?",
            "en": "Check the data, everything correct?"
        }

        # Пример отправки пользователю после добавления всех данных и фото
        await bot.send_message(
            user.user_id,
            text=confirm_texts.get(user.lang, confirm_texts["ru"]),
            reply_markup=user_confirm_keyboard(user.lang)
        )

        await state.set_state(AdForm.confirm)
        

@router.callback_query(lambda c: c.data and c.data.startswith("user_confirm_"))
async def ad_confirm(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = await Users.get(user_id=query.from_user.id)
    lang = user.lang

    if query.data == "user_confirm_no":
        await query.message.edit_text(TEXTS["ad_cancel"][lang], reply_markup=None)
        await state.clear()
        return

    if query.data == "user_confirm_yes":
        ad = await Ads.create(
            user_id=user.user_id,
            title=data["title"],
            price=data["price"],
            size=data["size"],
            condition=data["condition"],
            photos=",".join(data.get("photos", [])) if data.get("photos") else None
        )

        await bot.send_message(user.user_id, TEXTS["ad_sent"][lang], reply_markup=main_keyboard(lang))

        ad_text = (
            f"📝 Новое объявление #{ad.pk}\n\n"
            f"📌 {TEXTS['field_title'][lang]}: {data['title']}\n"
            f"💰 {TEXTS['field_price'][lang]}: {data['price']} UZS\n"
            f"📏 {TEXTS['field_size'][lang]}: {data['size']}\n"
            f"⚡ {TEXTS['field_condition'][lang]}: {data['condition']}\n"
            f"👤 Пользователь: {hlink(user.full_name, f'tg://user?id={user.user_id}')}\n"
            f"📞: {user.phone_number}\n\n"
            "Управление объявлением:"
        )

        if data.get("photos"):
            media = []
            for i, file_id in enumerate(data["photos"]):
                if i == 0:
                    media.append({
                        "type": "photo",
                        "media": file_id,
                        "caption": ad_text,
                        "parse_mode": "HTML"
                    })
                else:
                    media.append({"type": "photo", "media": file_id})

            await bot.send_media_group(chat_id=ADMIN_GROUP_ID, media=media)
            # Кнопки добавляем отдельным сообщением
            await bot.send_message(chat_id=ADMIN_GROUP_ID, text="Выберите действие:", reply_markup=admin_inline_keyboard(ad.pk))
        else:
            await bot.send_message(chat_id=ADMIN_GROUP_ID, text=ad_text, parse_mode="HTML", reply_markup=admin_inline_keyboard(ad.pk))

        await state.clear()
        return

    await bot.send_message(user.user_id, TEXTS["ad_confirm_repeat"][lang])

