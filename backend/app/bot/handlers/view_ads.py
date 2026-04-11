import os
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, InputMediaVideo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.core.config import settings
from app.bot.keyboards.ads import get_categories_keyboard, get_regions_keyboard
from app.bot.keyboards.pagination import get_batch_view_keyboard
from app.bot.utils.formatter import format_ad_text
from app.bot.client import api_client

router = Router()

class ViewAdsStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_region = State()
    browsing = State()

async def send_single_ad(bot, chat_id, ad):
    """Bitta e'lonni yuborish vazifasini bajaruvchi yordamchi funksiya"""
    text = format_ad_text(ad)
    
    # 1. Kanalda bo'lsa copy_message (tezkor)
    if ad.get('telegram_channel_message_id'):
        try:
            return await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=settings.CHANNEL_ID,
                message_id=ad['telegram_channel_message_id']
            )
        except:
            pass

    # 2. Kanalda bo'lmasa yoki xatolik bo'lsa manual ko'rsatish
    try:
        if ad.get('media_files'):
            media_group = []
            valid_files = []
            for m in ad['media_files'][:10]:
                if os.path.exists(m['file_path']):
                    valid_files.append(m)
            
            if not valid_files:
                return await bot.send_message(chat_id, text, parse_mode="Markdown")
            elif len(valid_files) == 1:
                m = valid_files[0]
                if m['media_type'] == "photo":
                    return await bot.send_photo(chat_id, FSInputFile(m['file_path']), caption=text, parse_mode="Markdown")
                else:
                    return await bot.send_video(chat_id, FSInputFile(m['file_path']), caption=text, parse_mode="Markdown")
            else:
                for i, m in enumerate(valid_files):
                    input_file = FSInputFile(m['file_path'])
                    caption = text if i == 0 else None
                    if m['media_type'] == "photo":
                        media_group.append(InputMediaPhoto(media=input_file, caption=caption, parse_mode="Markdown"))
                    else:
                        media_group.append(InputMediaVideo(media=input_file, caption=caption, parse_mode="Markdown"))
                return await bot.send_media_group(chat_id, media=media_group)
        else:
            return await bot.send_message(chat_id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending single ad in view: {e}")
        return await bot.send_message(chat_id, text, parse_mode="Markdown")

async def send_ads_batch(chat_id: int, bot, category_id: int, region_id: int, page: int):
    """10 ta e'lonni PARALLEL (Batch) yuboruvchi funksiya"""
    limit = 10
    ads = await api_client.get_public_ads(category_id=category_id, region_id=region_id, page=page, limit=limit)
    
    if not ads:
        if page == 1:
            return await bot.send_message(chat_id, "Ushbu hududda e'lonlar topilmadi.")
        else:
            return await bot.send_message(chat_id, "Boshqa e'lonlar qolmadi.")

    msg = await bot.send_message(chat_id, f"📥 {len(ads)} ta e'lon yuklanmoqda...")

    # Vazifalarni (tasks) tayyorlaymiz
    tasks = [send_single_ad(bot, chat_id, ad) for ad in ads]
    
    # Parallel yuboramiz
    await asyncio.gather(*tasks)

    # Keyingi sahifa bormi tekshirish
    next_ads = await api_client.get_public_ads(category_id=category_id, region_id=region_id, page=page+1, limit=1)
    has_next = len(next_ads) > 0
    
    kb = get_batch_view_keyboard(page, has_next, category_id, region_id)
    await bot.send_message(chat_id, "Navbatdagi e'lonlar tugadi. Davom etishni xohlaysizmi?", reply_markup=kb)
    
    # "Yuklanmoqda..." xabarini o'chirib tashlaymiz (aniqlik uchun)
    try:
        await bot.delete_message(chat_id, msg.message_id)
    except:
        pass

@router.message(F.text == "🔍 E'lonlarni ko'rish")
async def start_view_ads(message: Message, state: FSMContext):
    categories = await api_client.get_categories()
    if not categories:
        await message.answer("Xatolik: kategoriyalar topilmadi.")
        return

    await message.answer("Qaysi kategoriyani tanlaysiz?", reply_markup=get_categories_keyboard(categories))
    await state.set_state(ViewAdsStates.waiting_for_category)

@router.callback_query(ViewAdsStates.waiting_for_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)
    regions = await api_client.get_regions()
    await callback.message.edit_text("Hududni tanlang:", reply_markup=get_regions_keyboard(regions))
    await state.set_state(ViewAdsStates.waiting_for_region)

@router.callback_query(ViewAdsStates.waiting_for_region, F.data.startswith("reg_"))
async def process_region(callback: CallbackQuery, state: FSMContext):
    region_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    category_id = data['category_id']
    
    await callback.message.delete()
    await send_ads_batch(callback.message.chat.id, callback.message.bot, category_id, region_id, 1)
    await state.set_state(ViewAdsStates.browsing)

@router.callback_query(F.data.startswith("list_page_"))
async def process_view_pagination(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    cat_id = int(parts[2])
    reg_id = int(parts[3])
    page = int(parts[4])
    
    await send_ads_batch(callback.message.chat.id, callback.message.bot, cat_id, reg_id, page)
    await callback.answer()
