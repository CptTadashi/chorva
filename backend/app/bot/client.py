import httpx
from app.core.config import settings

class APIClient:
    def __init__(self):
        self.base_url = settings.API_URL

    async def get_user_by_telegram_id(self, telegram_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/bot/users/{telegram_id}")
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                print(f"API Error (get_user): {e}")
                return None

    async def register_user(self, telegram_id: int, phone_number: str, full_name: str = None, region_id: int = None, district_id: int = None):
        async with httpx.AsyncClient() as client:
            try:
                data = {
                    "telegram_id": telegram_id,
                    "phone_number": phone_number,
                    "full_name": full_name,
                    "region_id": region_id,
                    "district_id": district_id
                }
                response = await client.post(f"{self.base_url}/bot/auth/register", json=data)
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                print(f"API Error: {e}")
                return None

    async def get_categories(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/public/categories")
                return response.json() if response.status_code == 200 else []
            except Exception as e:
                return []

    async def get_regions(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/public/regions")
                return response.json() if response.status_code == 200 else []
            except Exception as e:
                return []

    async def get_districts(self, region_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/public/regions/{region_id}/districts")
                return response.json() if response.status_code == 200 else []
            except Exception as e:
                return []

    async def create_ad(self, data: dict):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/bot/ads/", json=data)
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                return None

    async def upload_media(self, ad_id: int, files: dict, data: dict):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/bot/ads/{ad_id}/media", files=files, data=data)
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                return None

    async def submit_ad(self, ad_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/bot/ads/{ad_id}/submit")
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                return None

    async def get_user_ads(self, telegram_id: int, page: int = 1, limit: int = 10):
        async with httpx.AsyncClient() as client:
            try:
                params = {"page": page, "limit": limit}
                response = await client.get(f"{self.base_url}/bot/ads/users/{telegram_id}", params=params)
                return response.json() if response.status_code == 200 else []
            except Exception as e:
                return []

    async def get_public_ads(self, category_id: int = None, region_id: int = None, page: int = 1, limit: int = 10):
        async with httpx.AsyncClient() as client:
            try:
                params = {"page": page, "limit": limit}
                if category_id: params['category_id'] = category_id
                if region_id: params['region_id'] = region_id
                response = await client.get(f"{self.base_url}/public/ads", params=params)
                return response.json() if response.status_code == 200 else []
            except Exception as e:
                return []

    async def mark_as_sold(self, ad_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/bot/ads/{ad_id}/sold")
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                return None

    async def cancel_ad(self, ad_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/bot/ads/{ad_id}/cancel")
                return response.json() if response.status_code == 200 else None
            except Exception as e:
                return None

api_client = APIClient()
