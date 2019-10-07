from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Sequence

import aiohttp
from aiogram.types import User
from async_lru import alru_cache
from furl import furl

from .bot import get_http_session, settings  # type: ignore

if TYPE_CHECKING:
    from .product_filters import ProductFilters

logger = logging.getLogger(__name__)


class Client:
    def __init__(self) -> None:
        self._session = get_http_session()
        user: User = User.get_current()
        self._headers = {"Accept-Language": user.locale.language}
        self._api_base = furl(settings.API_BASE_URL)

    @alru_cache
    async def fetch_filter_choices(self, route: str) -> Sequence[Dict[str, Any]]:
        return await self._fetch(self._api_base.add(path=route).url)

    async def fetch_product_page(
        self, product_filters: ProductFilters
    ) -> Dict[str, Any]:
        url = self._api_base.add(
            path="/shoes/",
            args={"page_size": settings.PRODUCT_PAGE_SIZE, **product_filters},
        ).url
        return await self._fetch(url)

    async def _fetch(self, url: str) -> Any:
        logger.debug("Fetching data from API %r", url)
        try:
            async with self._session.get(
                url, allow_redirects=False, headers=self._headers
            ) as response:
                return await response.json()
        except aiohttp.ClientError as e:
            logger.exception(
                "Can't fetch data from API url %r. Response: %r", url, response
            )
            raise e
