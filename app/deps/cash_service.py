from fastapi.exceptions import HTTPException

from app.core.config import settings
from app import schemas

import aiohttp


class CashService():
    async def create_consumer(self, token):
        headers={"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(f"{settings.CASH_SERVICE_BASE_URL}/api/v1/cash/consumers") as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail=await resp.text())

