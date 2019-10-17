import logging
from functools import partial
from typing import Any, Dict, Type, TypeVar

from aiogram.dispatcher import FSMContext

from ..bot import settings  # type: ignore
from ..client import Client
from ..dataclasses import Product, ProductPage
from ..product_filters import ProductFilters
from ..schemas import ProductPageSchema
from .answers import BookmarkAnswer, ProductAnswer, ProductSlideAnswer

logger = logging.getLogger(__name__)


async def get_product_page(
    state: FSMContext, product_filters: ProductFilters
) -> ProductPage:
    generic_data = await state.get_data()
    cached_page: Dict[str, Any] = generic_data.get(settings.CACHED_PAGE_STORAGE_KEY)

    raw_page: Dict[str, Any]
    if cached_page and cached_page["filters"] == product_filters:
        raw_page = cached_page["page"]
    else:
        raw_page = await Client().fetch_product_page(product_filters)
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
