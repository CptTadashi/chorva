import os
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile, InputMediaPhoto, InputMediaVideo
)
from aiogram.fsm.context import FSMContext
from app.bot.client import api_client
from app.core.config import settings
from app.core.bot import bot
from app.bot.keyboards.pagination import get_pagination_keyboard
from app.bot.utils.formatter import format_ad_text

router = Router()

async def delete_previous_my_messages(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids = data.get("my_msg_ids", [])
    for msg_id in msg_ids:
        try:
            await callback.message.bot.delete_message(callback.message.chat.id, msg_id)
        except:
            pass
    await state.update_data(my_msg_ids=[])

async def show_my_ad_page(chat_id: int, bot, state: FSMContext, telegram_id: int, page: int):
    limit = 1
    ads = await api_client.get_user_ads(telegram_id, page=page, limit=limit)
    
    if not ads:
        if page > 1:
            return await bot.send_message(chat_id, "Boshqa e'lonlar yo'q.")
        else:
            return await bot.send_message(chat_id, "Sizda hali e'lonlar mavjud emas.")

    ad = ads[0]
    next_ads = await api_client.get_user_ads(telegram_id, page=page+1, limit=1)
    has_next = len(next_ads) > 0
    
    text = format_ad_text(ad)
    # My ads uchun extra_id shart emas, chunki telegram_id message'dan olinadi
    kb = get_pagination_keyboard(
        page, has_next, prefix="my", 
        ad_id=ad['id'], is_owner=True
    )
    
    new_msg_ids = []

    # AGAR E'LON TASDIQLANGAN VA KANALDA BO'LSA - NUSXALASH
    if ad.get('telegram_channel_message_id'):
        try:
            res = await bot.copy_message(
                chat_id=chat_id,
                from_chat_id=settings.CHANNEL_ID,
                message_id=ad['telegram_channel_message_id'],
                reply_markup=kb
            )
            new_msg_ids.append(res.message_id)
            await state.update_data(my_msg_ids=new_msg_ids, current_my_page=page)
            return
        except Exception as e:
            print(f"My ads copy message error: {e}")

    # ESKI USUL (Hali tasdiqlanmagan yoki xatolik bo'lsa)
    try:
        if ad['media_files']:
            media_group = []
            valid_files = []
            for m in ad['media_files'][:10]:
                if os.path.exists(m['file_path']):
                    valid_files.append(m)
            
            if not valid_files:
                # Fayllar fizik ravishda yo'q bo'lsa, faqat matn
                res = await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="Markdown")
                new_msg_ids.append(res.message_id)
            elif len(valid_files) == 1:
                single = valid_files[0]
                input_file = FSInputFile(single['file_path'])
                if single['media_type'] == "photo":
                    res = await bot.send_photo(chat_id, input_file, caption=text, reply_markup=kb, parse_mode="Markdown")
                else:
                    res = await bot.send_video(chat_id, input_file, caption=text, reply_markup=kb, parse_mode="Markdown")
                new_msg_ids.append(res.message_id)
            else:
                for idx, m in enumerate(valid_files):
                    input_file = FSInputFile(m['file_path'])
                    caption = text if idx == 0 else None
                    if m['media_type'] == "photo":
                        media_group.append(InputMediaPhoto(media=input_file, caption=caption, parse_mode="Markdown"))
                    else:
                        media_group.append(InputMediaVideo(media=input_file, caption=caption, parse_mode="Markdown"))
                
                messages = await bot.send_media_group(chat_id, media=media_group)
                new_msg_ids.extend([m.message_id for m in messages])
                res = await bot.send_message(chat_id, "Boshqaruv:", reply_markup=kb)
                new_msg_ids.append(res.message_id)
        else:
            res = await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="Markdown")
            new_msg_ids.append(res.message_id)
    except Exception as e:
        print(f"Error sending my ad media: {e}")
        # Har qanday xatolikda matnni o'zini yuboramiz
        res = await bot.send_message(chat_id, text, reply_markup=kb, parse_mode="Markdown")
        new_msg_ids.append(res.message_id)
        
    await state.update_data(my_msg_ids=new_msg_ids, current_my_page=page)

@router.message(F.text == "📋 Mening e'lonlarim")
async def show_my_ads(message: Message, state: FSMContext):
    await show_my_ad_page(message.chat.id, message.bot, state, message.from_user.id, 1)

@router.callback_query(F.data.startswith("my_page_"))
async def process_my_pagination(callback: CallbackQuery, state: FSMContext):
    # Format: my_page__[page] -> extra_id bo'sh bo'lgani uchun __ bo'lib qoladi
    page = int(callback.data.split("_")[-1])
    await delete_previous_my_messages(callback, state)
    await show_my_ad_page(callback.message.chat.id, callback.message.bot, state, callback.from_user.id, page)
    await callback.answer()

@router.callback_query(F.data.startswith("sold_"))
async def process_ad_sold(callback: CallbackQuery, state: FSMContext):
    ad_id = int(callback.data.split("_")[1])
    response = await api_client.mark_as_sold(ad_id)

    if response:
        await callback.answer("✅ E'lon 'Sotildi' deb belgilandi!", show_alert=True)
        # Sahifani yangilash
        data = await state.get_data()
        page = data.get("current_my_page", 1)
        await delete_previous_my_messages(callback, state)
        await show_my_ad_page(callback.message.chat.id, callback.message.bot, state, callback.from_user.id, page)
    else:
        await callback.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.", show_alert=True)


@router.callback_query(F.data.startswith("cancel_"))
async def process_ad_cancel(callback: CallbackQuery, state: FSMContext):
    ad_id = int(callback.data.split("_")[1])
    response = await api_client.cancel_ad(ad_id)

    if response:
        await callback.answer("✅ E'lon bekor qilindi!", show_alert=True)
        # Sahifani yangilash
        data = await state.get_data()
        page = data.get("current_my_page", 1)
        await delete_previous_my_messages(callback, state)
        await show_my_ad_page(callback.message.chat.id, callback.message.bot, state, callback.from_user.id, page)
    else:
        await callback.answer("Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.", show_alert=True)
