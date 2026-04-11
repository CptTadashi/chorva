from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_pagination_keyboard(
    page: int, 
    has_next: bool, 
    prefix: str, 
    extra_id: str = "",
    ad_id: int = None,
    is_owner: bool = False
) -> InlineKeyboardMarkup:
    """
    Sahifalash tugmalarini yaratadi.
    """
    buttons = []
    
    # Navigatsiya qatori
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⏮ Oldingi", callback_data=f"{prefix}_page_{extra_id}_{page-1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"📄 {page}", callback_data="none"))
    
    if has_next:
        nav_row.append(InlineKeyboardButton(text="Keyingi ⏭", callback_data=f"{prefix}_page_{extra_id}_{page+1}"))
    
    buttons.append(nav_row)
    
    if is_owner and ad_id:
        buttons.append([
            InlineKeyboardButton(text="💰 Sotildi", callback_data=f"sold_{ad_id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel_{ad_id}")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_batch_view_keyboard(
    page: int,
    has_next: bool,
    cat_id: int,
    reg_id: int
) -> InlineKeyboardMarkup:
    """
    10 talik guruhlar uchun navigatsiya tugmalari
    """
    buttons = []
    
    # Navigatsiya qatori
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Avvalgi 10 ta", callback_data=f"list_page_{cat_id}_{reg_id}_{page-1}"))
    
    if has_next:
        nav_row.append(InlineKeyboardButton(text="Keyingi 10 ta ➡️", callback_data=f"list_page_{cat_id}_{reg_id}_{page+1}"))
    
    if nav_row:
        buttons.append(nav_row)
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)
