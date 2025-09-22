from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiobot.models.ads import Ads
from aiobot.texts import TEXTS
from config import ADMIN_GROUP_ID, CHANNEL_ID

router = Router()

@router.callback_query(F.data.startswith("approve_"))
async def approve_ad(call: CallbackQuery):
    pk = int(call.data.split("_")[1])
    ad = await Ads.get(pk)
    if not ad:
        await call.answer("Not found", show_alert=True)
        return
    
    # Обновляем статус объявления
    await Ads.update_status(pk, "approved")
    
    # Обновляем текст исходного сообщения админа на "Одобрено"
    try:
        await call.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Одобрено",
            reply_markup=None  # убираем все кнопки
        )
    except Exception as e:
        print(f"approve_ad: error editing admin message: {e}")
    
    # Отправляем уведомление пользователю
    user_id = ad.user_id
    lang = "ru"  # язык пользователя
    await call.bot.send_message(user_id, TEXTS["ad_approved"][lang])
    
    # Отправка в канал
    from aiogram.types import InputMediaPhoto
    from aiobot.models.users import Users
    user = await Users.get(user_id)
    phone = user.phone_number if user and user.phone_number else "-"
    desc_channel = (
        f"<b>{ad.title}</b>\n"
        f"Состояние: <b>{ad.condition}</b>\n"
        f"Цена: <b>{ad.price}</b>\n"
        f"Размер: <b>{ad.size}</b>\n"
    )

    # Дефекты
    if ad.defect_info:
        desc_channel += f"Дефекты: <b>{ad.defect_info}</b>\n"

    # Статус объявления
    desc_channel += f"Статус: <b>{ad.status}</b>\n"
    photos_str = ad.photos
    photos = photos_str.split(",") if photos_str else []
    try:
        if photos:
            media = [InputMediaPhoto(media=photos[0], caption=desc_channel, parse_mode="HTML")]
            media += [InputMediaPhoto(media=pid) for pid in photos[1:]]
            await call.bot.send_media_group(CHANNEL_ID, media)
        else:
            await call.bot.send_message(CHANNEL_ID, desc_channel, parse_mode="HTML")
    except Exception as e:
        print(f"approve_ad: error sending to channel: {e}")
    
    await call.answer("Объявление одобрено", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def reject_ad(call: CallbackQuery):
    pk = int(call.data.split("_")[1])
    ad = await Ads.get(pk)
    if not ad:
        await call.answer("Not found", show_alert=True)
        return
    await Ads.update_status(pk, "rejected")
    if ad.admin_message_id:
        try:
            title = ad.title
            price = ad.price
            size = ad.size
            condition = ad.condition
            desc = (
                f"<b>{title}</b>\n"
                f"состояние: <b>{condition}</b>\n"
                f"цена: <b>{price}</b>\n"
                f"размер: <b>{size}</b>\n\n"
                f"❌ <b>ОТКЛОНЕНО</b>"
            )
            await call.bot.edit_message_text(
                chat_id=ADMIN_GROUP_ID,
                message_id=ad.admin_message_id,
                text=desc,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"reject_ad: error editing admin message: {e}")
    user_id = ad.user_id
    lang = "ru"  # Можно доработать: получить язык пользователя из БД
    await call.bot.send_message(user_id, TEXTS["ad_rejected"][lang])
    await call.answer("Объявление отклонено", show_alert=True) 