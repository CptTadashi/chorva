from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, PhotoSize, InputMediaPhoto, InputMediaVideo, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import io
import asyncio

from app.bot.keyboards.ads import (
    get_categories_keyboard, get_confirmation_keyboard, 
    get_skip_keyboard, get_location_confirm_keyboard, 
    get_done_media_keyboard, get_main_menu,
    get_regions_keyboard, get_districts_keyboard
)
from app.bot.client import api_client

router = Router()

class AdCreationStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_extra_contact = State()
    waiting_for_media = State()
    waiting_for_location_confirm = State()
    waiting_for_new_region = State()
    waiting_for_new_district = State()

@router.message(F.text == "➕ E'lon berish")
async def start_ad_creation(message: Message, state: FSMContext):
    categories = await api_client.get_categories()
    if not categories:
        await message.answer("Xatolik: kategoriyalar topilmadi.")
        return

    await message.answer(
        "Kategoriyani tanlang:",
        reply_markup=get_categories_keyboard(categories)
    )
    await state.set_state(AdCreationStates.waiting_for_category)

@router.callback_query(AdCreationStates.waiting_for_category, F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)
    
    await callback.message.answer("E'lon sarlavhasini yuboring (masalan: Sotiladi bo'rdoqi mol):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdCreationStates.waiting_for_title)

@router.message(AdCreationStates.waiting_for_title, F.text)
async def process_title(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 10:
        await message.answer("⚠️ Sarlavha juda qisqa. Iltimos, kamida 10 ta belgi bilan batafsilroq yozing:")
        return
    if len(text) > 150:
        await message.answer("⚠️ Sarlavha juda uzun (maksimal 150 belgi). Qisqartirib yozing:")
        return
        
    await state.update_data(title=text)
    await message.answer("E'lon tavsifini yuboring (yoshi, vazni, holati haqida batafsil):")
    await state.set_state(AdCreationStates.waiting_for_description)

@router.message(AdCreationStates.waiting_for_title)
async def process_title_invalid(message: Message):
    await message.answer("⚠️ Iltimos, e'lon sarlavhasini faqat matn ko'rinishida yuboring:")

@router.message(AdCreationStates.waiting_for_description, F.text)
async def process_description(message: Message, state: FSMContext):
    text = message.text.strip()
    if len(text) < 20:
        await message.answer("⚠️ Tavsif juda qisqa. Iltimos, kamida 20 ta belgi bilan batafsilroq yozing:")
        return
    if len(text) > 2000:
        await message.answer("⚠️ Tavsif juda uzun (maksimal 2000 belgi). Bir оз qisqartiring:")
        return

    await state.update_data(description=text)
    await message.answer("Narxni kiriting (faqat raqamda, so'mda):")
    await state.set_state(AdCreationStates.waiting_for_price)

@router.message(AdCreationStates.waiting_for_description)
async def process_description_invalid(message: Message):
    await message.answer("⚠️ Iltimos, e'lon tavsifini faqat matn ko'rinishida yuboring:")

@router.message(AdCreationStates.waiting_for_price, F.text)
async def process_price(message: Message, state: FSMContext):
    try:
        price_raw = message.text.replace(" ", "").replace(",", ".").replace("so'm", "").replace("som", "").lower()
        price = float(price_raw)
        
        if price <= 0:
            await message.answer("⚠️ Narx musbat raqam bo'lishi kerak:")
            return
            
        if price > 1_000_000_000_000:
            await message.answer("⚠️ Narx juda katta (maksimal 1 trillion so'm). Iltimos, to'g'ri narx kiriting:")
            return

        await state.update_data(price=price)
        await message.answer(
            "Qo'shimcha aloqa raqami bormi? (Agar bo'lmasa 'O'tkazib yuborish'ni bosing):",
            reply_markup=get_skip_keyboard()
        )
        await state.set_state(AdCreationStates.waiting_for_extra_contact)
    except ValueError:
        await message.answer("⚠️ Iltimos, narxni faqat raqamlarda kiriting (masalan: 5000000):")

@router.message(AdCreationStates.waiting_for_price)
async def process_price_invalid(message: Message):
    await message.answer("⚠️ Iltimos, narxni raqam ko'rinishida yuboring:")

@router.message(AdCreationStates.waiting_for_extra_contact)
async def process_extra_contact(message: Message, state: FSMContext):
    if message.text != "⏩ O'tkazib yuborish":
        await state.update_data(extra_contact=message.text)
    
    await message.answer(
        "Endi e'lon uchun medialarni yuboring:\n"
        "1. Birinchi yuborgan rasmingiz - **Asosiy rasm** bo'ladi.\n"
        "2. Qo'shimcha yana **3 ta rasm** va **1 ta video** yuborishingiz mumkin.\n\n"
        "Yuklab bo'lgach '✅ Bo'ldi, yakunlash' tugmasini bosing.",
        reply_markup=get_done_media_keyboard(),
        parse_mode="Markdown"
    )
    await state.set_state(AdCreationStates.waiting_for_media)

# "Bo'ldi, yakunlash" tugmasi uchun alohida handler
@router.message(AdCreationStates.waiting_for_media, F.text == "✅ Bo'ldi, yakunlash")
async def process_media_done(message: Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media_list", [])

    if not media_list:
        await message.answer("⚠️ Iltimos, kamida 1 ta rasm yoki video yuboring.")
        return
    
    # User manzilini tekshirish
    user_info = await api_client.get_user_by_telegram_id(message.from_user.id)
    if user_info and user_info.get('region_id'):
        await message.answer(
            f"E'lon manzili sifatida profilingizdagi manzil ishlatiladi.\n"
            f"Siz kiritgan manzil to'g'rimi?",
            reply_markup=get_location_confirm_keyboard()
        )
        await state.set_state(AdCreationStates.waiting_for_location_confirm)
    else:
        await message.answer("❌ Xatolik: profilingizda manzil topilmadi. Iltimos /start orqali yangilang.")
        await state.clear()

# Media qabul qilish uchun handler (Photo, Video, Document)
@router.message(AdCreationStates.waiting_for_media, F.photo | F.video | F.document)
async def process_media_upload(message: Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media_list", [])
    
    photos_count = len([m for m in media_list if m['media_type'] == 'photo'])
    videos_count = len([m for m in media_list if m['media_type'] == 'video'])
    
    MAX_FILE_SIZE = 20 * 1024 * 1024 # 20 MB

    if message.photo:
        if photos_count >= 4:
            await message.answer("⚠️ Maksimal 4 ta rasm (1 asosiy + 3 qo'shimcha) yuklash mumkin.")
            return
        
        largest_photo = message.photo[-1]
        if largest_photo.file_size > MAX_FILE_SIZE:
             await message.answer("❌ Fayl hajmi juda katta (maksimal 20 MB). Iltimos, kichikroq hajmdagi rasm yuboring.")
             return
             
        file_id = largest_photo.file_id
        media_type = "photo"
    
    elif message.video:
        if videos_count >= 1:
            await message.answer("⚠️ Faqat 1 ta video yuklash mumkin.")
            return
            
        if message.video.file_size > MAX_FILE_SIZE:
             await message.answer("❌ Video hajmi juda katta (maksimal 20 MB). Iltimos, qisqaroq yoki pastroq sifatdagi video yuboring.")
             return
             
        file_id = message.video.file_id
        media_type = "video"
    
    elif message.document:
        if message.document.file_size > MAX_FILE_SIZE:
             await message.answer("❌ Fayl hajmi juda katta (maksimal 20 MB).")
             return
             
        mime = message.document.mime_type
        if mime.startswith("image/"):
            if photos_count >= 4:
                await message.answer("⚠️ Maksimal 4 ta rasm yuklash mumkin.")
                return
            file_id = message.document.file_id
            media_type = "photo"
        elif mime.startswith("video/"):
            if videos_count >= 1:
                await message.answer("⚠️ Faqat 1 ta video yuklash mumkin.")
                return
            file_id = message.document.file_id
            media_type = "video"
        else:
            await message.answer("⚠️ Iltimos, faqat rasm yoki video formatidagi fayllarni yuboring.")
            return

    if file_id:
        media_list.append({"file_id": file_id, "media_type": media_type})
        await state.update_data(media_list=media_list)
        
        # Xabarni chiroyli qilish
        if media_type == "photo":
            current_photo_idx = len([m for m in media_list if m['media_type'] == 'photo'])
            if current_photo_idx == 1:
                await message.answer("✅ Asosiy rasm qabul qilindi.")
            else:
                await message.answer(f"✅ {current_photo_idx-1}-qo'shimcha rasm qabul qilindi.")
        else:
            await message.answer("✅ Video qabul qilindi.")

# Kutilmagan boshqa xabarlar uchun (masalan oddiy matn)
@router.message(AdCreationStates.waiting_for_media)
async def process_media_unknown(message: Message):
    await message.answer(
        "Iltimos, e'lon uchun rasm yoki video yuboring.\n"
        "Yuklab bo'lgach '✅ Bo'ldi, yakunlash' tugmasini bosing."
    )

@router.message(AdCreationStates.waiting_for_location_confirm, F.text.in_(["✅ Ha, to'g'ri", "📍 Manzilni o'zgartirish"]))
async def process_location_confirm(message: Message, state: FSMContext):
    if message.text == "📍 Manzilni o'zgartirish":
        regions = await api_client.get_regions()
        if not regions:
            await message.answer("Xatolik: viloyatlar topilmadi.")
            return

        await message.answer(
            "Yangi viloyatni tanlang:",
            reply_markup=get_regions_keyboard(regions)
        )
        await state.set_state(AdCreationStates.waiting_for_new_region)
        return
    
    # 📍 Ha, to'g'ri tanlasa, profil manzilini ishlatamiz
    user_info = await api_client.get_user_by_telegram_id(message.from_user.id)
    await complete_ad_creation(message, state, user_info['region_id'], user_info['district_id'])

@router.callback_query(AdCreationStates.waiting_for_new_region, F.data.startswith("reg_"))
async def process_new_region(callback: CallbackQuery, state: FSMContext):
    region_id = int(callback.data.split("_")[1])
    await state.update_data(new_region_id=region_id)
    
    districts = await api_client.get_districts(region_id)
    if not districts:
        await callback.message.answer("Ushbu viloyatda tumanlar topilmadi.")
        return

    await callback.message.edit_text(
        "Yangi tumanni tanlang:",
        reply_markup=get_districts_keyboard(districts)
    )
    await state.set_state(AdCreationStates.waiting_for_new_district)

@router.callback_query(AdCreationStates.waiting_for_new_district, F.data.startswith("dist_"))
async def process_new_district(callback: CallbackQuery, state: FSMContext):
    district_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    await complete_ad_creation(callback.message, state, data['new_region_id'], district_id, callback.from_user.id)
    await callback.answer()

async def complete_ad_creation(message: Message, state: FSMContext, region_id: int, district_id: int, telegram_id: int = None):
    # Agar telegram_id callback'dan kelayotgan bo'lsa uni ishlatamiz, aks holda message.from_user'dan
    user_tid = telegram_id or message.from_user.id
    data = await state.get_data()
    
    # 1. E'lon yaratish
    ad_data = {
        "telegram_id": user_tid,
        "category_id": data['category_id'],
        "title": data['title'],
        "description": data['description'],
        "price": data['price'],
        "extra_contact": data.get('extra_contact'),
        "region_id": region_id,
        "district_id": district_id
    }
    
    ad_resp = await api_client.create_ad(ad_data)
    if not ad_resp:
        await message.answer("E'lon yaratishda xatolik yuz berdi.")
        return

    ad_id = ad_resp['id']
    
    # Yuklash xabari
    status_msg = await message.answer("⏳ E'lon saqlanmoqda, medialar yuklanmoqda...")
    
    # 2. Medialarni parallel ravishda yuklash
    bot = message.bot
    
    async def upload_single_media(idx, item):
        try:
            file = await bot.get_file(item['file_id'])
            dest = io.BytesIO()
            await bot.download_file(file.file_path, dest)
            dest.seek(0)
            
            return await api_client.upload_media(
                ad_id=ad_id,
                files={"file": (f"media_{idx}.jpg", dest, "image/jpeg")},
                data={"media_type": item['media_type'], "sort_order": idx}
            )
        except Exception as e:
            print(f"Media upload error: {e}")
            return None

    # Barcha medialarni bir vaqtda yuboramiz
    upload_tasks = [upload_single_media(idx, item) for idx, item in enumerate(data['media_list'])]
    await asyncio.gather(*upload_tasks)

    # 3. Submit qilish
    await api_client.submit_ad(ad_id)
    
    # Yuklash xabarini o'chirish
    try:
        await status_msg.delete()
    except:
        pass

    # 4. Preview ko'rsatish
    await message.answer("✅ Tabriklaymiz! E'loningiz qabul qilindi.\nModerator tasdiqlasa, u quyidagicha ko'rinishda bo'ladi:")
    
    text_preview = (
        f"📌 *{ad_resp['title']}*\n"
        f"💰 Narxi: {ad_resp['price']:,.0f} so'm\n"
        f"📍 Manzil: {ad_resp['region']['name']}, {ad_resp['district']['name']}\n"
        f"📞 Aloqa: {ad_resp['owner_phone']}\n"
    )
    if ad_resp.get('extra_contact'):
        text_preview += f"📞 Qo'shimcha: {ad_resp['extra_contact']}\n"
    text_preview += f"\n📝 {ad_resp['description']}"


    media_group = []
    for idx, item in enumerate(data['media_list']):
        # Preview uchun foydalanuvchi yuborgan original file_id dan foydalanamiz (tezroq bo'ladi)
        caption = text_preview if idx == 0 else None
        if item['media_type'] == "photo":
            media_group.append(InputMediaPhoto(media=item['file_id'], caption=caption, parse_mode="Markdown"))
        else:
            media_group.append(InputMediaVideo(media=item['file_id'], caption=caption, parse_mode="Markdown"))

    if len(media_group) == 1:
        single = data['media_list'][0]
        if single['media_type'] == "photo":
            await message.answer_photo(single['file_id'], caption=text_preview, parse_mode="Markdown")
        else:
            await message.answer_video(single['file_id'], caption=text_preview, parse_mode="Markdown")
    else:
        await message.answer_media_group(media=media_group)

    await message.answer(
        "E'lon moderatsiyaga yuborildi. Tez orada javobini bot orqali olasiz.",
        reply_markup=get_main_menu()
    )
    await state.clear()
