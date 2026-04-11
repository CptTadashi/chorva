from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from app.bot.client import api_client

class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            # Foydalanuvchini API orqali tekshirish
            user = await api_client.get_user_by_telegram_id(user_id)
            
            # Agar foydalanuvchi bazada bo'lsa va is_active = False bo'lsa
            if user and not user.get("is_active", True):
                msg_text = "🚫 Siz admin tomonidan bloklangansiz.\nMa'lumot uchun admin bilan bog'laning."
                
                if isinstance(event, Message):
                    await event.answer(msg_text)
                elif isinstance(event, CallbackQuery):
                    await event.answer(msg_text, show_alert=True)
                
                return # Keyingi handlerga o'tkazmaymiz

        return await handler(event, data)
