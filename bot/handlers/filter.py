import logging

from aiogram import types
from aiogram.dispatcher import FSMContext, filters

from ..bot import dp, settings  # type: ignore
from ..states import ProductFiltersForm
from ..utils import handle_regex_params
from .common import answer_next_filter_or_results

logger = logging.getLogger(__name__)


@dp.callback_query_handler(
    filters.Text("filter:skip"), state=ProductFiltersForm.all_states
)
async def process_filter_skip(
    callback_query: types.CallbackQuery, state: FSMContext, locale: str
) -> None:
    next_filter = await ProductFiltersForm.next()
    await answer_next_filter_or_results(
        callback_query.message, state, locale, next_filter
    )
    await callback_query.answer()


@dp.callback_query_handler(
    filters.Text(r"filter:skip_all"), state=ProductFiltersForm.all_states
)
async def process_filter_skip_all(
    callback_query: types.CallbackQuery, state: FSMContext, locale: str
) -> None:
    # None state finishes the filtering
    await answer_next_filter_or_results(callback_query.message, state, locale, None)
    await callback_query.answer()


@dp.callback_query_handler(
    filters.Regexp(r"filter:choice:(\w+):(\w+)"), state=ProductFiltersForm.all_states
)
@handle_regex_params(None, None)
async def process_filter_choice(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    locale: str,
    handled_params: tuple,
    **kwargs,
) -> None:
    filter_name, query_value = handled_params
    logger.debug("Filter name: %s. Filter query value: %s", filter_name, query_value)

    store_name = settings.PRODUCT_FILTERS[filter_name].query_name or filter_name
    async with state.proxy() as generic_data:
        generic_data.setdefault(settings.FILTERS_STORAGE_KEY, {})
        generic_data[settings.FILTERS_STORAGE_KEY][store_name] = query_value

    logger.debug("Updated filters data: %s", generic_data[settings.FILTERS_STORAGE_KEY])

    next_filter = await ProductFiltersForm.next()
    logger.debug("Next filter: %s", next_filter)
    await answer_next_filter_or_results(
        callback_query.message, state, locale, next_filter
    )

    await callback_query.answer()
