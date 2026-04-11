import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.location import Region, District
from app.models.category import Category
from app.models.user import AdminUser
from app.core.database import Base

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Kategoriyalar
        from sqlalchemy import select, delete
        res = await session.execute(select(Category).limit(1))
        if not res.scalars().first():
            categories = [
                Category(name="Mol", slug="mol", sort_order=1),
                Category(name="Qo'y", slug="qoy", sort_order=2),
                Category(name="Echki", slug="echki", sort_order=3),
                Category(name="Yem", slug="yem", sort_order=4),
            ]
            session.add_all(categories)
            print("Kategoriyalar qo'shildi.")

        # 2. To'liq Hududlar (Viloyatlar va Tumanlar)
        # Avval eski hududlarni o'chiramiz (Toza baza uchun)
        await session.execute(delete(District))
        await session.execute(delete(Region))
        await session.flush()

        locations_data = {
            "Andijon viloyati": [
                "Andijon shahri", "Asaka shahri", "Qorasuv shahri", "Xonobod shahri", "Shahrixon shahri",
                "Andijon tumani", "Asaka tumani", "Baliqchi tumani", "Boʻston tumani", "Buloqboshi tumani", 
                "Izboskan tumani", "Jalaquduq tumani", "Marhamat tumani", "Oltinkoʻl tumani", "Paxtaobod tumani", 
                "Qoʻrgʻontepa tumani", "Shahrixon tumani", "Ulugʻnor tumani", "Xoʻjaobod tumani"
            ],
            "Buxoro viloyati": [
                "Buxoro shahri", "Kogon shahri",
                "Buxoro tumani", "Vobkent tumani", "Gʻijduvon tumani", "Jondor tumani", "Kogon tumani", 
                "Olot tumani", "Peshku tumani", "Romitan tumani", "Shofirkon tumani", "Qorovulbozor tumani", "Qorakoʻl tumani"
            ],
            "Fargʻona viloyati": [
                "Fargʻona shahri", "Margʻilon shahri", "Qoʻqon shahri", "Quvasoy shahri",
                "Beshariq tumani", "Bogʻdod tumani", "Buvayda tumani", "Dangʻara tumani", "Oltiariq tumani", 
                "Qoʻshtepa tumani", "Quva tumani", "Rishton tumani", "Soʻx tumani", "Toshloq tumani", 
                "Uchkoʻprik tumani", "Fargʻona tumani", "Furqat tumani", "Yozyovon tumani"
            ],
            "Jizzax viloyati": [
                "Jizzax shahri",
                "Arnasoy tumani", "Baxmal tumani", "Doʻstlik tumani", "Zarbdor tumani", "Zafarobod tumani", 
                "Zomin tumani", "Mirzachoʻl tumani", "Paxtakor tumani", "Forish tumani", "Sharof Rashidov tumani", 
                "Gʻallaorol tumani", "Yangiobod tumani"
            ],
            "Xorazm viloyati": [
                "Urganch shahri", "Xiva shahri",
                "Bogʻot tumani", "Gurlan tumani", "Tuproqqal'a tumani", "Urganch tumani", "Xazarasp tumani", 
                "Xiva tumani", "Xonqa tumani", "Qoʻshkoʻpir tumani", "Shovot tumani", "Yangiariq tumani", "Yangibozor tumani"
            ],
            "Namangan viloyati": [
                "Namangan shahri",
                "Davlatobod tumani", "Kosonsoy tumani", "Mingbuloq tumani", "Namangan tumani", "Norin tumani", 
                "Pop tumani", "Toʻraqoʻrgʻon tumani", "Uychi tumani", "Uchqoʻrgʻon tumani", "Chortoq tumani", 
                "Chust tumani", "Yangiqorg'on tumani", "Yangi Namangan tumani"
            ],
            "Navoiy viloyati": [
                "Navoiy shahri", "Zarafshon shahri", "Gʻozgʻon shahri",
                "Karmana tumani", "Konimex tumani", "Navbahor tumani", "Nurota tumani", "Tomdi tumani", 
                "Uchquduq tumani", "Xatirchi tumani", "Qiziltepa tumani"
            ],
            "Qashqadaryo viloyati": [
                "Qarshi shahri", "Shahrisabz shahri",
                "Dehqonobod tumani", "Kasbi tumani", "Kitob tumani", "Koson tumani", "Koʻkdala tumani", 
                "Mirishkor tumani", "Muborak tumani", "Nishon tumani", "Qamashi tumani", "Qarshi tumani", 
                "Shahrisabz tumani", "Chiroqchi tumani", "Yakkabogʻ tumani", "Gʻuzor tumani"
            ],
            "Samarqand viloyati": [
                "Samarqand shahri", "Kattaqoʻrgʻon shahri",
                "Bulungʻur tumani", "Ishtixon tumani", "Jomboy tumani", "Kattaqoʻrgʻon tumani", "Narpay tumani", 
                "Nurobod tumani", "Oqdaryo tumani", "Pastdargʻom tumani", "Paxtachi tumani", "Payariq tumani", 
                "Qoʻshrabot tumani", "Samarqand tumani", "Toyloq tumani", "Urgut tumani"
            ],
            "Sirdaryo viloyati": [
                "Guliston shahri", "Shirin shahri", "Yangiyer shahri",
                "Boyovut tumani", "Guliston tumani", "Mirzaobod tumani", "Oqoltin tumani", "Sayxunobod tumani", 
                "Sardoba tumani", "Sirdaryo tumani", "Xavos tumani"
            ],
            "Surxondaryo viloyati": [
                "Termiz shahri",
                "Angor tumani", "Bandixon tumani", "Boysun tumani", "Denov tumani", "Jarqoʻrgʻon tumani", 
                "Muzrabot tumani", "Oltinsoy tumani", "Qiziriq tumani", "Qumqoʻrgʻon tumani", "Sariosiyo tumani", 
                "Termiz tumani", "Uzun tumani", "Sherobod tumani", "Shoʻrchi tumani"
            ],
            "Toshkent viloyati": [
                "Nurafshon shahri", "Angren shahri", "Bekobod shahri", "Olmaliq shahri", "Ohangaron shahri", 
                "Chirchiq shahri", "Yangiyoʻl shahri",
                "Bekobod tumani", "Boʻka tumani", "Boʻstonliq tumani", "Zangiota tumani", "Qibray tumani", 
                "Quyi Chirchiq tumani", "Oqqoʻrgʻon tumani", "Ohangaron tumani", "Parkent tumani", "Piskent tumani", 
                "Toshkent tumani", "Oʻrta Chirchiq tumani", "Chinoz tumani", "Yuqori Chirchiq tumani", "Yangiyoʻl tumani"
            ],
            "Qoraqalpogʻiston Respublikasi": [
                "Nukus shahri",
                "Amudaryo tumani", "Beruniy tumani", "Boʻzatov tumani", "Kegeyli tumani", "Moʻynoq tumani", 
                "Nukus tumani", "Taxiatosh tumani", "Taxtakoʻpir tumani", "Toʻrtkoʻl tumani", "Xoʻjayli tumani", 
                "Chimboy tumani", "Shumanay tumani", "Ellikqalʼa tumani", "Qanlikoʻl tumani", "Qoraoʻzak tumani", "Qoʻngʻirot tumani"
            ],
            "Toshkent shahri": [
                "Bektemir tumani", "Mirzo Ulugʻbek tumani", "Mirobod tumani", "Olmazor tumani", "Sergeli tumani", 
                "Uchtepa tumani", "Chilonzor tumani", "Shayxontohur tumani", "Yunusobod tumani", "Yakkasaroy tumani", 
                "Yashnobod tumani", "Yangihayot tumani"
            ]
        }

        i = 1
        for region_name, districts in locations_data.items():
            region = Region(name=region_name, sort_order=i)
            session.add(region)
            await session.flush()
            
            j = 1
            for dist_name in districts:
                district = District(name=dist_name, region_id=region.id, sort_order=j)
                session.add(district)
                j += 1
            
            i += 1
        
        print(f"{len(locations_data)} ta viloyat va ularning tumanlari qo'shildi.")

        # 3. Admin User
        from app.core.security import get_password_hash
        res = await session.execute(select(AdminUser).filter_by(username="admin"))
        admin = res.scalars().first()
        if not admin:
            admin = AdminUser(
                username="admin", 
                password_hash=get_password_hash("admin123"), 
                role="superadmin"
            )
            session.add(admin)
            print("Admin user yaratildi.")
        else:
            # Mavjud admin parolini xeshga o'tkazamiz (Majburiy yangilash)
            admin.password_hash = get_password_hash("admin123")
            print("Admin paroli xeshlandi.")

        await session.commit()
    
    print("Seeding muvaffaqiyatli yakunlandi!")

if __name__ == "__main__":
    asyncio.run(seed())
