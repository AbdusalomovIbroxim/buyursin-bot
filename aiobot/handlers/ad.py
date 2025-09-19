import logging
from aiogram import Router, F
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiobot.states import AdForm
from aiobot.buttons.keyboards.reply import condition_keyboard, confirm_keyboard, main_keyboard, photos_keyboard, size_category_keyboard, clothing_size_keyboard, shoes_size_keyboard
from aiobot.buttons.keyboards.inline import admin_inline_keyboard
from aiobot.texts import TEXTS
from aiobot.models.users import Users
from aiobot.models.ads import Ads
from config import ADMIN_GROUP_ID
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import BufferedInputFile

router = Router()


# 1. Получение заголовка объявления
@router.message(AdForm.title)
async def ad_title(message: Message, state: FSMContext):
    print(f"ad_title: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_title: user_id={message.from_user.id}, text={message.text}")
    try:
        await state.update_data(title=message.text)
        lang = await Users.get_language(message.from_user.id)
        print(f"ad_title: lang={lang}")
        logging.info(f"ad_title: lang={lang}")
        await state.set_state(AdForm.price)
        await message.answer(TEXTS["ad_price"][lang])
        print(f"ad_title: sent price request to user_id={message.from_user.id}")
        logging.info(f"ad_title: sent price request to user_id={message.from_user.id}")
    except Exception as e:
        print(f"ad_title error: {e}")
        logging.error(f"ad_title error: {e}")
        await message.answer(f"Ошибка: {e}")

    
# 2. Получение цены
@router.message(AdForm.price)
async def ad_price(message: Message, state: FSMContext):
    print(f"ad_price: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_price: user_id={message.from_user.id}, text={message.text}")
    await state.update_data(price=message.text)
    lang = await Users.get_language(message.from_user.id)

    # 👉 сначала спрашиваем категорию размеров
    await state.set_state(AdForm.size_category)
    await message.answer(TEXTS["ad_size_category"][lang], reply_markup=size_category_keyboard())

    print(f"ad_price: sent size_category request to user_id={message.from_user.id}")
    logging.info(f"ad_price: sent size_category request to user_id={message.from_user.id}")


# 2.1. Получение категории размера
@router.message(AdForm.size_category, F.text.in_(["👕 Одежда", "👟 Обувь", "👜 Аксессуары"]))
async def ad_size_category(message: Message, state: FSMContext):
    print(f"ad_size_category: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_size_category: user_id={message.from_user.id}, text={message.text}")

    category = message.text
    await state.update_data(size_category=category)
    lang = await Users.get_language(message.from_user.id)

    if category == "👕 Одежда":
        await state.set_state(AdForm.size)
        await message.answer(TEXTS["ad_size_clothing"][lang], reply_markup=clothing_size_keyboard())
    elif category == "👟 Обувь":
        await state.set_state(AdForm.size)
        await message.answer(TEXTS["ad_size_shoes"][lang], reply_markup=shoes_size_keyboard())
    else:  # 👜 Аксессуары
        await state.update_data(size="Без размера")
        await state.set_state(AdForm.condition)
        await message.answer(TEXTS["ad_condition"][lang], reply_markup=condition_keyboard())


# 3. Получение размера (с кнопками и вводом вручную)
@router.message(AdForm.size)
async def ad_size(message: Message, state: FSMContext):
    print(f"ad_size: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_size: user_id={message.from_user.id}, text={message.text}")

    size_value = message.text.strip()  # можно выбрать из кнопок или ввести свой
    await state.update_data(size=size_value)

    lang = await Users.get_language(message.from_user.id)
    await state.set_state(AdForm.condition)
    await message.answer(TEXTS["ad_condition"][lang], reply_markup=condition_keyboard())

    print(f"ad_size: sent condition request to user_id={message.from_user.id}")
    logging.info(f"ad_size: sent condition request to user_id={message.from_user.id}")



# 4. Получение состояния через кнопки (без 'Другое')
@router.message(AdForm.condition, F.text.in_(["Новый", "Почти новый", "Хорошее", "Среднее", "Требует ремонта"]))
async def ad_condition(message: Message, state: FSMContext):
    print(f"ad_condition: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_condition: user_id={message.from_user.id}, text={message.text}")
    await state.update_data(condition=message.text)
    lang = await Users.get_language(message.from_user.id)
    await state.set_state(AdForm.photos)
    # Отправляем инструкцию-картинку и текст
    photo = FSInputFile("aiobot/static/instruction.png")
    await message.answer_photo(photo, caption=TEXTS["ad_photos"][lang], reply_markup=photos_keyboard())
    # await message.answer(TEXTS["ad_photos"][lang], reply_markup=photos_keyboard())
    print(f"ad_condition: sent photos request to user_id={message.from_user.id}")
    logging.info(f"ad_condition: sent photos request to user_id={message.from_user.id}")

# --- Обработка альбомов (media_group) ---
@router.message(AdForm.photos, F.media_group_id)
async def ad_photos_album(message: Message, state: FSMContext):
    # Сохраняем все фото из альбома
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    # Не отвечаем на каждое фото, только на последнее (будет обработано обычным ad_photos или ad_photos_done)

# 5. Получение фотографий (до 10)
@router.message(AdForm.photos, F.photo)
async def ad_photos(message: Message, state: FSMContext):
    print(f"ad_photos: user_id={message.from_user.id}, photo received")
    logging.info(f"ad_photos: user_id={message.from_user.id}, photo received")
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    if len(photos) < 10:
        await state.update_data(photos=photos)
        lang = await Users.get_language(message.from_user.id)
        await message.answer(TEXTS["ad_photos"][lang] + f" ({len(photos)}/10)", reply_markup=photos_keyboard())
        print(f"ad_photos: {len(photos)}/10 photos collected for user_id={message.from_user.id}")
        logging.info(f"ad_photos: {len(photos)}/10 photos collected for user_id={message.from_user.id}")
    else:
        await state.update_data(photos=photos)
        await show_confirm(message, state)
        print(f"ad_photos: max photos reached, moving to confirm for user_id={message.from_user.id}")
        logging.info(f"ad_photos: max photos reached, moving to confirm for user_id={message.from_user.id}")

# Обработка кнопки 'Готово' на этапе фото
@router.message(AdForm.photos, F.text == "Готово")
async def ad_photos_done(message: Message, state: FSMContext):
    print(f"ad_photos_done: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_photos_done: user_id={message.from_user.id}, text={message.text}")
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) == 0:
        lang = await Users.get_language(message.from_user.id)
        await message.answer("Пожалуйста, добавьте хотя бы одну фотографию.")
        print(f"ad_photos_done: user_id={message.from_user.id} tried to finish without photos")
        logging.info(f"ad_photos_done: user_id={message.from_user.id} tried to finish without photos")
        return
    await show_confirm(message, state)


# Если пользователь отправил не фото, а текст/что-то ещё на этапе фото
@router.message(AdForm.photos)
async def ad_photos_text(message: Message, state: FSMContext):
    print(f"ad_photos_text: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_photos_text: user_id={message.from_user.id}, text={message.text}")
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) == 0:
        lang = await Users.get_language(message.from_user.id)
        await message.answer("Пожалуйста, добавьте хотя бы одну фотографию.")
        print(f"ad_photos_text: user_id={message.from_user.id} tried to continue without photos")
        logging.info(f"ad_photos_text: user_id={message.from_user.id} tried to continue without photos")
        return
    else:
        await show_confirm(message, state)


# 6. Подтверждение объявления
async def show_confirm(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = await Users.get_language(message.from_user.id)
    user = await Users.get(message.from_user.id)
    phone = user.phone_number if user and user.phone_number else "-"
    desc = (
        f"<b>{data['title']}</b>\n"
        f"состояние: <b>{data['condition']}</b>\n"
        f"цена: <b>{data['price']}</b>\n"
        f"размер: <b>{data['size']}</b>\n"
        f"Телефон: <b>+{phone}</b>"
    )
    await state.set_state(AdForm.confirm)
    photos = data.get("photos", [])
    if photos:
        media = [InputMediaPhoto(media=photos[0], caption=desc, parse_mode="HTML")]
        media += [InputMediaPhoto(media=pid) for pid in photos[1:]]
        await message.answer_media_group(media)
        await message.answer(TEXTS['ad_confirm'][lang], reply_markup=confirm_keyboard(lang))
    else:
        await message.answer(desc, parse_mode="HTML", reply_markup=confirm_keyboard(lang))
    print(f"show_confirm: confirmation sent to user_id={message.from_user.id}")
    logging.info(f"show_confirm: confirmation sent to user_id={message.from_user.id}")


@router.message(AdForm.confirm)
async def ad_confirm(message: Message, state: FSMContext):
    print(f"ad_confirm: user_id={message.from_user.id}, text={message.text}")
    logging.info(f"ad_confirm: user_id={message.from_user.id}, text={message.text}")
    lang = await Users.get_language(message.from_user.id)
    btns = {
        "ru": ["✅ Подтвердить", "✏️ Изменить", "❌ Отменить"],
        "uz": ["✅ Tasdiqlash", "✏️ O'zgartirish", "❌ Bekor qilish"],
        "en": ["✅ Confirm", "✏️ Edit", "❌ Cancel"]
    }
    data = await state.get_data()
    if message.text == btns[lang][0]:
        photos = data.get('photos', [])
        photos_str = ','.join(photos) if photos else ''
        ad = await Ads.create(message.from_user.id, data['title'], data['price'], data['size'], data['condition'], photos_str)
        await message.answer(TEXTS['ad_sent'][lang], reply_markup=main_keyboard(lang))
        user = await Users.get(message.from_user.id)
        phone = user.phone_number if user and user.phone_number else "-"
        desc = (
            f"<b>{data['title']}</b>\n"
            f"состояние: <b>{data['condition']}</b>\n"
            f"цена: <b>{data['price']}</b>\n"
            f"размер: <b>{data['size']}</b>\n"
            f"Телефон: <b>+{phone}</b>"
        )
        if photos:
            media = [InputMediaPhoto(media=photos[0], caption=desc, parse_mode="HTML")]
            media += [InputMediaPhoto(media=pid) for pid in photos[1:]]
            await message.bot.send_media_group(ADMIN_GROUP_ID, media)
            admin_msg = await message.bot.send_message(ADMIN_GROUP_ID, "Управление объявлением:", reply_markup=admin_inline_keyboard(ad.pk))
            await Ads.update_admin_message_id(ad.pk, admin_msg.message_id)
        else:
            admin_msg = await message.bot.send_message(ADMIN_GROUP_ID, desc, parse_mode="HTML", reply_markup=admin_inline_keyboard(ad.pk))
            await Ads.update_admin_message_id(ad.pk, admin_msg.message_id)
        await state.clear()
        print(f"ad_confirm: ad sent to group and user_id={message.from_user.id} finished")
        logging.info(f"ad_confirm: ad sent to group and user_id={message.from_user.id} finished")
    elif message.text == btns[lang][1]:
        await state.clear()  # Очищаем все старые данные, включая фото
        await state.set_state(AdForm.title)
        await message.answer(TEXTS['ad_title'][lang])
        print(f"ad_confirm: user_id={message.from_user.id} chose to edit ad")
        logging.info(f"ad_confirm: user_id={message.from_user.id} chose to edit ad")
    elif message.text == btns[lang][2]:
        await state.clear()
        await message.answer("❌", reply_markup=main_keyboard(lang))
        print(f"ad_confirm: user_id={message.from_user.id} cancelled ad")
        logging.info(f"ad_confirm: user_id={message.from_user.id} cancelled ad")
