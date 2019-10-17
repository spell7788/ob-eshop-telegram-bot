import json
import logging
from string import Template
from typing import Dict, Optional

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils.emoji import emojize

from .. import texts
from ..bot import _, bot, settings  # type: ignore
from ..dataclasses import ProductPageException
from ..keyboards import get_filter_choices_keyboard
from ..product_answers import ProductAnswer, get_product, get_product_slide_answer
from ..product_filters import FILTER_CHOICES_GETTERS, ProductFilters
from ..utils import (
    from_telegram_price,
    handle_regex_params,
    message_managers,
    tz_aware_now,
)

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


async def notify_managers_new_order(
    state: FSMContext, pre_checkout_query: types.PreCheckoutQuery
) -> None:
    payload = json.loads(pre_checkout_query.invoice_payload)
    product_index, product_filters, size = payload
    product = await get_product(state, product_index, ProductFilters(product_filters))
    text = Template(texts.ORDER_NOTIFICATION.value).substitute(
        datetime_now=tz_aware_now().strftime(settings.SHORT_DATETIME_FORMAT),
        total_amount=from_telegram_price(pre_checkout_query.total_amount),
        currency=pre_checkout_query.currency,
        product_name=product.name,
        product_code=product.code,
        product_url=product.url,
        size=size,
        **{key: value for key, value in pre_checkout_query.order_info},
        **{key: value for key, value in pre_checkout_query.order_info.shipping_address},
    )
    await message_managers(
        lambda manager_id: bot.send_message(
            manager_id,
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    )
