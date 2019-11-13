import logging
from typing import Dict, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils.emoji import emojize

from ..bot import _, settings  # type: ignore
from ..dataclasses import ProductPageException
from ..keyboards import get_filter_choices_keyboard
from ..product_answers import ProductAnswer, get_product_slide_answer
from ..product_filters import FILTER_CHOICES_GETTERS, ProductFilters
from ..utils import handle_regex_params

logger = logging.getLogger(__name__)

PRODUCT_REGEX = r"(\d+):(.+|)"

handle_product_params = handle_regex_params(int, ProductFilters)


async def answer_product_slide(
    message: types.Message,
    state: FSMContext,
    locale: str,
    product_slide: ProductAnswer,
    edit: bool = False,
) -> None:
    product = product_slide.product
    caption = await product_slide.get_caption()
    keyboard = product_slide.make_keyboard()

    if not edit:
        await message.answer_photo(
            product.main_picture.pic,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )
    else:
        await message.edit_media(
            types.InputMediaPhoto(
                product.main_picture.pic,
                product.main_picture.thumbnail,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
            ),
            reply_markup=keyboard,
        )


async def _answer_filter_results(
    message: types.Message, state: FSMContext, locale: str
) -> None:
    generic_data = await state.get_data()
    filters: Dict[str, str] = generic_data.get(settings.FILTERS_STORAGE_KEY, {})
    logger.debug("Resulting filters: %s", filters)

    try:
        product_slide = await get_product_slide_answer(
            state, locale, 0, ProductFilters(filters)
        )
    except ProductPageException:
        await message.answer(_("No results, try to /browse again."))
    else:
        await answer_product_slide(message, state, locale, product_slide)
        # don't need to reset page cache and filters
        await state.reset_state(with_data=False)


async def _answer_product_filter(
    message: types.Message, state: FSMContext, edit: bool = False
) -> None:
    current_filter = await state.get_state()
    logger.debug("Current filter: %s", current_filter)
    filter_name = str(current_filter).split(":")[-1]
    filter_settings = settings.PRODUCT_FILTERS[filter_name]

    if filter_settings.depends_on:
        filters = (await state.get_data())[settings.FILTERS_STORAGE_KEY]
        store_name = settings.PRODUCT_FILTERS[filter_name].query_name or filter_name
        try:
            relation_value = filters[store_name]
        except KeyError as e:
            logger.error(
                "Can't get relation value for '%s' filter, "
                "which depends on '%s' filter. Saved filters: %s.",
                filter_name,
                filter_settings.depends_on,
                filters,
            )
            raise e

        logger.debug(
            "Relation value %s of type %s.", relation_value, type(relation_value)
        )
    else:
        relation_value = None

    choices_getter = FILTER_CHOICES_GETTERS[filter_name]
    filter_choices = await choices_getter(relation_value=relation_value)

    filter_title = _(filter_settings.title)
    text = emojize(
        _(":wavy_dash: Select a {filter_title} option").format(
            filter_title=filter_title
        )
    )
    keyboard = get_filter_choices_keyboard(
        filter_choices, row_width=filter_settings.choices_keyboard_width
    )

    if not edit:
        await message.answer(text, reply_markup=keyboard)
    else:
        await message.edit_text(text, reply_markup=keyboard)


async def answer_next_filter_or_results(
    message: types.Message,
    state: FSMContext,
    locale: str,
    next_filter: Optional[str],
    starts_up: bool = False,
) -> None:
    if next_filter:
        await _answer_product_filter(message, state, edit=not starts_up)
    else:
        await message.delete()
        await _answer_filter_results(message, state, locale)
