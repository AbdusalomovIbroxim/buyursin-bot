from aiogram import BaseMiddleware, Router
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
from aiobot.database import db


router = Router()


class AuthMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        user = db.get_user(user_id)

        # если не авторизован
        if not user or not user.is_verified:
            await event.answer("❌ Вы не авторизованы. Используйте /start для входа.")
            return  # прерываем цепочку
        return await handler(event, data)

router.message.middleware(AuthMiddleware())