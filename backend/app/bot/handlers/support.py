from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.core.config import settings
import re

router = Router()

class SupportStates(StatesGroup):
    waiting_for_message = State()

@router.message(F.text == "🆘 Yordam")
async def start_support(message: Message, state: FSMContext):
    await message.answer(
        "Savol, taklif yoki murojaatingiz bo'lsa, uni quyida yozib qoldiring. "
        "Adminlarimiz sizga tez orada javob berishadi.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
            resize_keyboard=True
        )
    )
    await state.set_state(SupportStates.waiting_for_message)

@router.message(SupportStates.waiting_for_message, F.text == "⬅️ Orqaga")
async def cancel_support(message: Message, state: FSMContext):
    from app.bot.keyboards.ads import get_main_menu
    await state.clear()
    await message.answer("Bosh menyuga qaytdingiz.", reply_markup=get_main_menu())

@router.message(SupportStates.waiting_for_message)
async def handle_support_message(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "mavjud emas"
    
    # Guruhga yuboriladigan matn
    report_text = (
        f"📩 #Murojaat\n"
        f"👤 **Foydalanuvchi**: {full_name} ({username})\n"
        f"🆔 ID: `{user_id}`\n\n"
        f"📝 **Xabar**:\n{message.text or '[Media xabar]'}"
    )

    try:
        # Guruhga xabar yuborish
        if message.photo:
            await bot.send_photo(
                chat_id=settings.SUPPORT_GROUP_ID,
                photo=message.photo[-1].file_id,
                caption=report_text,
                parse_mode="Markdown"
            )
        elif message.video:
            await bot.send_video(
                chat_id=settings.SUPPORT_GROUP_ID,
                video=message.video.file_id,
                caption=report_text,
                parse_mode="Markdown"
            )
        else:
            await bot.send_message(
                chat_id=settings.SUPPORT_GROUP_ID,
                text=report_text,
                parse_mode="Markdown"
            )
            
        from app.bot.keyboards.ads import get_main_menu
        await message.answer(
            "✅ Murojaatingiz yuborildi! Adminlarimiz ko'rib chiqib, sizga shu yerda javob yozishadi.", 
            reply_markup=get_main_menu()
        )
        await state.clear()
        
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {str(e)}")

# ADMIN REPLY HANDLER (Guruhdagi javoblarni ushlaydi)
@router.message(F.chat.id == int(settings.SUPPORT_GROUP_ID), F.reply_to_message)
async def handle_admin_reply(message: Message, bot: Bot):
    original_msg = message.reply_to_message
    
    # Original xabardan ID ni qidirib topish
    text = original_msg.text or original_msg.caption
    if not text:
        return

    # Regex yordamida ID: 12345 qismini topish (Markdown belgilari bo'lsa ham, bo'lmasa ham)
    match = re.search(r"🆔 ID:\s*`?(\d+)`?", text)
    if not match:
        return
        
    target_user_id = int(match.group(1))
    
    reply_prefix = "👩‍💻 **Admin javobi**:\n\n"
    
    try:
        if message.text:
            await bot.send_message(target_user_id, f"{reply_prefix}{message.text}", parse_mode="Markdown")
        elif message.photo:
            await bot.send_photo(target_user_id, message.photo[-1].file_id, caption=f"{reply_prefix}{message.caption or ''}", parse_mode="Markdown")
        elif message.video:
            await bot.send_video(target_user_id, message.video.file_id, caption=f"{reply_prefix}{message.caption or ''}", parse_mode="Markdown")
        
        # Admin guruhida tasdiqlash uchun reaksiya yoki xabar
        await message.reply("✅ Javob foydalanuvchiga yuborildi.")
        
    except Exception as e:
        await message.reply(f"❌ Foydalanuvchiga yuborishda xatolik: {str(e)}")
