from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ E'lon berish"), KeyboardButton(text="🔍 E'lonlarni ko'rish")],
            [KeyboardButton(text="📋 Mening e'lonlarim"), KeyboardButton(text="🆘 Yordam")]
        ],
        resize_keyboard=True
    )

def get_categories_keyboard(categories):
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(text=cat['name'], callback_data=f"cat_{cat['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirmation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Tasdiqlash")],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏩ O'tkazib yuborish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_location_confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha, to'g'ri")],
            [KeyboardButton(text="📍 Manzilni o'zgartirish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_done_media_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Bo'ldi, yakunlash")]
        ],
        resize_keyboard=True
    )
def get_regions_keyboard(regions):
    keyboard = []
    for r in regions:
        keyboard.append([InlineKeyboardButton(text=r['name'], callback_data=f"reg_{r['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_districts_keyboard(districts):
    keyboard = []
    for d in districts:
        keyboard.append([InlineKeyboardButton(text=d['name'], callback_data=f"dist_{d['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
