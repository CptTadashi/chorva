from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.auth import get_phone_keyboard, get_regions_keyboard, get_districts_keyboard
from app.bot.client import api_client

router = Router()

class RegistrationStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_region = State()
    waiting_for_district = State()

from app.bot.keyboards.ads import get_main_menu

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # Foydalanuvchini bazadan tekshirish
    user = await api_client.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        await message.answer(
            f"Xush kelibsiz, {user.get('full_name') or message.from_user.full_name}!\n"
            "Bosh menyudan kerakli bo'limni tanlang:",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            f"Assalomu alaykum, {message.from_user.full_name}!\n"
            "Chorva va Yem e'lonlari botiga xush kelibsiz.\n"
            "Ro'yxatdan o'tish uchun telefon raqamingizni yuboring:",
            reply_markup=get_phone_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_phone)

@router.message(RegistrationStates.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone, full_name=message.from_user.full_name)
    
    regions = await api_client.get_regions()
    if not regions:
        await message.answer("Xatolik: viloyatlar topilmadi. Keyinroq urinib ko'ring.")
        return

    await message.answer(
        "Viloyatni tanlang:",
        reply_markup=get_regions_keyboard(regions)
    )
    await state.set_state(RegistrationStates.waiting_for_region)

@router.callback_query(RegistrationStates.waiting_for_region, F.data.startswith("reg_"))
async def process_region(callback: CallbackQuery, state: FSMContext):
    region_id = int(callback.data.split("_")[1])
    await state.update_data(region_id=region_id)
    
    districts = await api_client.get_districts(region_id)
    if not districts:
        await callback.message.answer("Ushbu viloyatda tumanlar topilmadi.")
        return

    await callback.message.edit_text(
        "Tumanni tanlang:",
        reply_markup=get_districts_keyboard(districts)
    )
    await state.set_state(RegistrationStates.waiting_for_district)

from app.bot.keyboards.ads import get_main_menu

@router.callback_query(RegistrationStates.waiting_for_district, F.data.startswith("dist_"))
async def process_district(callback: CallbackQuery, state: FSMContext):
    district_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    
    # API orqali ro'yxatdan o'tkazish
    response = await api_client.register_user(
        telegram_id=callback.from_user.id,
        phone_number=data['phone'],
        full_name=data['full_name'],
        region_id=data['region_id'],
        district_id=district_id
    )
    
    if response:
        await callback.message.delete()
        await callback.message.answer(
            "Muvaffaqiyatli ro'yxatdan o'tdingiz! Bosh menyudan foydalanishingiz mumkin:",
            reply_markup=get_main_menu()
        )
        await state.clear()
    else:
        await callback.message.answer("Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring /start.")
