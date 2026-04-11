import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.models.location import Region, District
import sys

# Windows terminalida Unicode muammosini hal qilish
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Foydalanuvchi taqdim etgan ma'lumotlar
LOCATIONS_DATA = {
    "Andijon viloyati": [
        "Andijon", "Asaka", "Qorasuv", "Xonobod", "Shahrixon",
        "Andijon tumani", "Asaka tumani", "Baliqchi", "Boʻston", "Buloqboshi", 
        "Izboskan", "Jalaquduq", "Marhamat", "Oltinkoʻl", "Paxtaobod", 
        "Qoʻrgʻontepa", "Shahrixon tumani", "Ulugʻnor", "Xoʻjaobod"
    ],
    "Buxoro viloyati": [
        "Buxoro", "Kogon",
        "Buxoro tumani", "Vobkent", "Gʻijduvon", "Jondor", "Kogon tumani", 
        "Olot", "Peshku", "Romitan", "Shofirkon", "Qorovulbozor", "Qorakoʻl"
    ],
    "Fargʻona viloyati": [
        "Fargʻona", "Margʻilon", "Qoʻqon", "Quvasoy",
        "Beshariq", "Bogʻdod", "Buvayda", "Dangʻara", "Oltiariq", 
        "Qoʻshtepa", "Quva", "Rishton", "Soʻx", "Toshloq", "Uchkoʻprik", 
        "Fargʻona tumani", "Furqat", "Yozyovon"
    ],
    "Jizzax viloyati": [
        "Jizzax",
        "Arnasoy", "Baxmal", "Doʻstlik", "Zarbdor", "Zafarobod", "Zomin", 
        "Mirzachoʻl", "Paxtakor", "Forish", "Sharof Rashidov", "Gʻallaorol", "Yangiobod"
    ],
    "Xorazm viloyati": [
        "Urganch", "Xiva",
        "Bogʻot", "Gurlan", "Tuproqqal'a", "Urganch tumani", "Xazarasp", 
        "Xiva tumani", "Xonqa", "Qoʻshkoʻpir", "Shovot", "Yangiariq", "Yangibozor"
    ],
    "Namangan viloyati": [
        "Namangan",
        "Davlatobod", "Kosonsoy", "Mingbuloq", "Namangan tumani", "Norin", 
        "Pop", "Toʻraqoʻrgʻon", "Uychi", "Uchqoʻrgʻon", "Chortoq", "Chust", "Yangi Namangan", "Yangiqoʻrgʻon"
    ],
    "Navoiy viloyati": [
        "Navoiy", "Zarafshon", "Gʻozgʻon",
        "Karmana", "Konimex", "Navbahor", "Nurota", "Tomdi", "Uchquduq", "Xatirchi", "Qiziltepa"
    ],
    "Qashqadaryo viloyati": [
        "Qarshi", "Shahrisabz",
        "Dehqonobod", "Kasbi", "Kitob", "Koson", "Koʻkdala", "Mirishkor", 
        "Muborak", "Nishon", "Qamashi", "Qarshi tumani", "Shahrisabz tumani", "Chiroqchi", "Yakkabogʻ", "Gʻuzor"
    ],
    "Samarqand viloyati": [
        "Samarqand", "Kattaqoʻrgʻon",
        "Bulungʻur", "Ishtixon", "Jomboy", "Kattaqoʻrgʻon tumani", "Narpay", 
        "Nurobod", "Oqdaryo", "Pastdargʻom", "Paxtachi", "Payariq", "Qoʻshrabot", 
        "Samarqand tumani", "Toyloq", "Urgut"
    ],
    "Sirdaryo viloyati": [
        "Guliston", "Shirin", "Yangiyer",
        "Boyovut", "Guliston tumani", "Mirzaobod", "Oqoltin", "Sayxunobod", "Sardoba", "Sirdaryo tumani", "Xavos"
    ],
    "Surxondaryo viloyati": [
        "Termiz",
        "Angor", "Bandixon", "Boysun", "Denov", "Jarqoʻrgʻon", "Muzrabot", 
        "Oltinsoy", "Qiziriq", "Qumqoʻrgʻon", "Sariosiyo", "Termiz tumani", "Uzun", "Sherobod", "Shoʻrchi"
    ],
    "Toshkent viloyati": [
        "Nurafshon", "Angren", "Bekobod", "Olmaliq", "Ohangaron", "Chirchiq", "Yangiyoʻl",
        "Bekobod tumani", "Boʻka", "Boʻstonliq", "Zangiota", "Qibray", "Quyi Chirchiq", 
        "Oqqoʻrgʻon", "Ohangaron tumani", "Parkent", "Piskent", "Toshkent tumani", 
        "Oʻrta Chirchiq", "Chinoz", "Yuqori Chirchiq", "Yangiyoʻl tumani"
    ],
    "Qoraqalpogʻiston Respublikasi": [
        "Nukus",
        "Amudaryo", "Beruniy", "Boʻzatov", "Kegeyli", "Moʻynoq", "Nukus tumani", 
        "Taxiatosh", "Taxtakoʻpir", "Toʻrtkoʻl", "Xoʻjayli", "Chimboy", "Shumanay", "Ellikqalʼa", "Qanlikoʻl", "Qoraoʻzak", "Qoʻngʻirot"
    ],
    "Toshkent shahri": [
        "Bektemir", "Chilonzor", "Hamza (Yashnobod)", "Mirobod", "Mirzo Ulugʻbek", 
        "Olmazor", "Sergeli", "Shayxontohur", "Uchtepa", "Yakkasaroy", "Yunusobod", "Yangihayot"
    ]
}

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Mavjud hududlarni tozalash...")
        # ForeignKey borligi uchun tumanlarni birinchi o'chiramiz
        await session.execute(text("DELETE FROM districts"))
        await session.execute(text("DELETE FROM regions"))
        await session.commit()
        
        print("Yangi hududlarni kiritish boshlandi...")
        
        idx = 1
        for region_name, district_names in LOCATIONS_DATA.items():
            region = Region(name=region_name, sort_order=idx)
            session.add(region)
            await session.flush() # ID olish uchun
            
            d_idx = 1
            for d_name in district_names:
                district = District(name=d_name, region_id=region.id, sort_order=d_idx)
                session.add(district)
                d_idx += 1
            
            idx += 1
            print(f"- {region_name} va uning {len(district_names)} tumanlari qo'shildi.")

        await session.commit()
    
    print("\n✅ Muvaffaqiyatli: O'zbekistonning barcha hududlari bazaga kiritildi!")

if __name__ == "__main__":
    asyncio.run(seed())
