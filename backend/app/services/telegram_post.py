from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
from app.core.config import settings
from app.core.bot import bot
from app.models.ad import Ad
import os

async def post_ad_to_channel(ad: Ad):
    """
    E'lonni Telegram kanalga yuborish.
    """
    try:
        
        # Matn tayyorlash
        price_text = f"{int(ad.price):,}".replace(",", " ") + " so'm" if ad.price > 0 else "Kelishiladi"
        
        caption = (
            f"<b>{ad.title}</b>\n\n"
            f"📂 Kategoriya: #{ad.category.slug}\n"
            f"💰 Narxi: {price_text}\n"
            f"📍 Manzil: {ad.region.name}, {ad.district.name}\n\n"
            f"📝 Tavsif:\n{ad.description[:500]}{'...' if len(ad.description) > 500 else ''}\n\n"
            f"📞 Tel: <code>{ad.owner_phone}</code>\n"
            f"🔗 <a href='{settings.FRONTEND_URL}/ad/{ad.id}'>Batafsil ma'lumot (Saytda)</a>\n\n"
            f"🤖 @chorvabozor_bot - Chorva va Yem bozori"
        )

        media_files = ad.media_files
        
        res = None
        if not media_files:
            # Rasm bo'lmasa faqat matn
            res = await bot.send_message(
                chat_id=settings.CHANNEL_ID,
                text=caption,
                parse_mode="HTML"
            )
        elif len(media_files) == 1:
            # Bitta rasm yoki video
            file_path = media_files[0].file_path
            if os.path.exists(file_path):
                input_file = FSInputFile(file_path)
                if media_files[0].media_type == "photo":
                    res = await bot.send_photo(
                        chat_id=settings.CHANNEL_ID,
                        photo=input_file,
                        caption=caption,
                        parse_mode="HTML"
                    )
                else:
                    res = await bot.send_video(
                        chat_id=settings.CHANNEL_ID,
                        video=input_file,
                        caption=caption,
                        parse_mode="HTML"
                    )
        else:
            # Bir nechta media (Album shaklida)
            media_group = []
            for i, m in enumerate(media_files[:10]): # Maksimum 10 ta
                if os.path.exists(m.file_path):
                    input_file = FSInputFile(m.file_path)
                    item_caption = caption if i == 0 else "" # Faqat birinchisiga caption qo'shish
                    
                    if m.media_type == "photo":
                        media_group.append(InputMediaPhoto(media=input_file, caption=item_caption, parse_mode="HTML"))
                    else:
                        media_group.append(InputMediaVideo(media=input_file, caption=item_caption, parse_mode="HTML"))
            
            if media_group:
                messages = await bot.send_media_group(
                    chat_id=settings.CHANNEL_ID,
                    media=media_group
                )
                if messages:
                    res = messages[0] # Birinchi xabarning IDsi kerak
            else:
                # Agar fayllar topilmasa faqat matn
                res = await bot.send_message(chat_id=settings.CHANNEL_ID, text=caption, parse_mode="HTML")

        return res.message_id if res else None
    except Exception as e:
        print(f"Kanalga post yuborishda xato: {e}")
        return None
