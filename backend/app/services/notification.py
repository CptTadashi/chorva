import logging
from aiogram import Bot
from app.core.config import settings

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.core.bot import bot

async def notify_user(telegram_id: int, text: str):
    try:
        await bot.send_message(telegram_id, text)
        logger.info(f"SUCCESS: NOTIFICATION to {telegram_id}")
        return True
    except Exception as e:
        logger.error(f"FAILED: NOTIFICATION to {telegram_id}: {e}")
        return False
