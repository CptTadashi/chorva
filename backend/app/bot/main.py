import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import start, ads, my_ads, view_ads, support
from app.bot.middlewares.auth import AuthMiddleware

async def main():
    logging.basicConfig(level=logging.INFO)
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Middleware'larni ulash
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())
    
    # Routerlarni ulash
    dp.include_router(start.router)
    dp.include_router(ads.router)
    dp.include_router(my_ads.router)
    dp.include_router(view_ads.router)
    dp.include_router(support.router)
    
    print("Bot ishlashga tayyor...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
