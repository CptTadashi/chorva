import httpx
import asyncio

async def test():
    base_url = "http://127.0.0.1:8000/api"
    
    async with httpx.AsyncClient() as client:
        # 1. Kategoriyalar testi
        print("Checking Categories...")
        resp = await client.get(f"{base_url}/public/categories")
        print(f"Categories: {resp.status_code}, Count: {len(resp.json())}")
        
        # 2. Hududlar testi
        print("\nChecking Regions...")
        resp = await client.get(f"{base_url}/public/regions")
        regions = resp.json()
        print(f"Regions: {resp.status_code}, Count: {len(regions)}")
        
        # 3. Ro'yxatdan o'tish testi
        print("\nRegistering User...")
        user_data = {
            "telegram_id": 123456789,
            "phone_number": "+998901234567",
            "full_name": "Test User",
            "region_id": regions[0]['id'],
            "district_id": 1 # Zangiota (seeded)
        }
        resp = await client.post(f"{base_url}/bot/auth/register", json=user_data)
        print(f"Register: {resp.status_code}, Data: {resp.json().get('full_name')}")

        # 4. E'lon yaratish testi
        print("\nCreating Ad...")
        ad_data = {
            "telegram_id": 123456789,
            "category_id": 1, # Mol
            "title": "Test Mol",
            "description": "Zo'r mol",
            "price": 10000000,
            "region_id": 1,
            "district_id": 1
        }
        resp = await client.post(f"{base_url}/bot/ads/", json=ad_data)
        print(f"Ad Creation: {resp.status_code}, ID: {resp.json().get('id')}")

if __name__ == "__main__":
    asyncio.run(test())
