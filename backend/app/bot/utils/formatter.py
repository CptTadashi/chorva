def format_ad_text(ad: dict) -> str:
    """
    E'lon ma'lumotlarini bot uchun chiroyli matn ko'rinishiga keltiradi.
    """
    status_map = {
        "pending_review": "⏳ Ko'rib chiqilmoqda",
        "published": "✅ Tasdiqlangan",
        "rejected": "❌ Rad etilgan",
        "sold": "💰 Sotilgan",
        "archive": "📦 Arxivlangan"
    }
    
    status_text = status_map.get(ad.get('status'), "")
    price_text = f"{int(ad['price']):,}".replace(",", " ") + " so'm" if ad.get('price') and ad['price'] > 0 else "Kelishiladi"
    
    text = (
        f"📌 *{ad['title']}*\n"
        f"📂 Kategoriya: {ad['category']['name']}\n"
        f"💰 Narxi: {price_text}\n"
        f"📍 Manzil: {ad['region']['name']}, {ad['district']['name']}\n"
        f"📞 Aloqa: `{ad['owner_phone']}`\n"
    )
    
    if ad.get('extra_contact'):
        text += f"📞 Qo'shimcha: `{ad['extra_contact']}`\n"
    
    if status_text:
        text += f"📊 Holati: {status_text}\n"
        if ad.get('status') == "rejected" and ad.get('reject_reason'):
            text += f"⚠️ Sabab: {ad['reject_reason']}\n"
            
    text += f"\n📝 {ad['description'][:400]}{'...' if len(ad['description']) > 400 else ''}\n"
    text += f"📅 Sana: {ad['created_at'][:10]}"
    
    return text
