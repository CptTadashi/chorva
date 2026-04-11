from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from app.core.config import settings

# Yagona bot instansiyasi
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
