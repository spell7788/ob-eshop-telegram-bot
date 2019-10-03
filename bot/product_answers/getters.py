import logging
from functools import partial
from typing import Any, Dict, Type, TypeVar

import aiohttp
from aiogram.dispatcher import FSMContext
from furl import furl

from ..bot import settings
from ..dataclasses import Product, ProductPage
from ..http_session import HttpSession
from ..product_filters import ProductFilters
from ..schemas import ProductPageSchema
from .answers import BookmarkAnswer, ProductAnswer, ProductSlideAnswer

logger = logging.getLogger(__name__)


def get_product_page_url(product_filters: ProductFilters) -> str:
    f = furl(settings.API_BASE_URL)
    f = f.add(
        path="/shoes/",
        args={"page_size": settings.PRODUCT_PAGE_SIZE, **product_filters},
    )
    return f.url


async def fetch_product_page(product_filters: ProductFilters) -> Dict[str, Any]:
    session = HttpSession.get_session()
    page_url = get_product_page_url(product_filters)
    logger.debug("Requesting product page from '%s'.", page_url)
    try:
        async with session.get(page_url) as response:
            return await response.json()
    except aiohttp.ClientError as e:
        logger.exception(
            "An error occurred while requesting the product page. "
            "Page url: %s. Product filters: %s.",
            page_url,
            product_filters,
        )
        raise e


async def get_product_page(
    state: FSMContext, product_filters: ProductFilters
) -> ProductPage:
    generic_data = await state.get_data()
    cached_page: Dict[str, Any] = generic_data.get(settings.CACHED_PAGE_STORAGE_KEY)

    raw_page: Dict[str, Any]
    if cached_page and cached_page["filters"] == product_filters:
        raw_page = cached_page["page"]
    else:
        raw_page = await fetch_product_page(product_filters)
        cached_page = {"page": raw_page, "filters": product_filters.data}
        await state.update_data({settings.CACHED_PAGE_STORAGE_KEY: cached_page})

    return ProductPageSchema().load(raw_page)


async def get_product(
    state: FSMContext, product_index: int, product_filters: ProductFilters
) -> Product:
    product_page = await get_product_page(state, product_filters)
    return product_page[product_index]


T = TypeVar("T", bound=ProductAnswer)


async def get_product_answer(
    answer_type: Type[T],
    state: FSMContext,
    locale: str,
    product_index: int,
    product_filters: ProductFilters,
) -> T:
    page = await get_product_page(state, product_filters)
    return answer_type(page, product_index, product_filters, locale)


get_product_slide_answer = partial(get_product_answer, ProductSlideAnswer)

get_bookmark_answer = partial(get_product_answer, BookmarkAnswer)
