from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Sequence

import aiohttp
from aiogram.types import User
from async_lru import alru_cache
from furl import furl

from .bot import settings  # type: ignore

if TYPE_CHECKING:
    from .product_filters import ProductFilters

logger = logging.getLogger(__name__)


class Client:
    _client = None

    def __init__(self) -> None:
        headers = {
            "Authorization": f"Token {settings.API_TOKEN}",
            "Accept-Language": User.get_current().locale.language,
        }
        self._session = aiohttp.ClientSession(headers=headers)
        self._api_base = furl(settings.API_BASE_URL)

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            cls._client = cls()
        return cls._client

    async def close(self):
        await self._session.close()

    @alru_cache
    async def fetch_filter_choices(self, route: str) -> Sequence[Dict[str, Any]]:
        url = self._api_base.copy().add(path=route).url
        async with self._session.get(url, allow_redirects=False) as response:
            return await response.json()

    async def fetch_product_page(
        self, product_filters: ProductFilters
    ) -> Dict[str, Any]:
        url = (
            self._api_base.copy()
            .add(
                path="/shoes/",
                args={"page_size": settings.PRODUCT_PAGE_SIZE, **product_filters},
            )
            .url
        )
        async with self._session.get(url, allow_redirects=False) as response:
            return await response.json()

    async def create_order(self, order_data: Dict[str, Any]) -> None:
        url = self._api_base.copy().add(path="/order/").url
        async with self._session.post(url, json=order_data) as response:
            if response.status == 201:
                data = await response.json()
                logger.info(f"Order was successfully created: {data}")
            else:
                errors = await response.json()
                raise ValueError(f"Order wasn't created {errors}")
