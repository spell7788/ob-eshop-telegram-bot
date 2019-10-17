import json
import logging
import re

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import any_state
from aiogram.types.message import ContentTypes
from aiogram.utils.emoji import emojize

from .. import texts
from ..bot import _, bot, dp, settings  # type: ignore
from ..callback_forms import CallbackForm
from ..keyboards import get_invoice_keyboard, get_product_sizes_keyboard
from ..product_answers import get_product
from ..product_filters import ProductFilters
from ..utils import (
    decode_parameter,
    encode_parameter,
    handle_regex_params,
    to_telegram_price,
)
from .common import PRODUCT_REGEX, handle_product_params, notify_managers_new_order

logger = logging.getLogger(__name__)


async def answer_product_invoice(
    message: types.Message,
    state: FSMContext,
    locale: str,
    product_index: int,
    product_filters: ProductFilters,
    product_size: int,
) -> None:
    product = await get_product(state, product_index, product_filters)
    product_identifier = (
        CallbackForm(str(product_index))
        + product_filters.as_query_string()
        + str(product_size)
    ).callback_string
    payload = json.dumps(
        (product_index, product_filters.as_query_string(), product_size)
    )

    await bot.send_invoice(
        message.chat.id,
        f"{product.name} {product.code}",
        emojize(texts.INVOICE_DESCRIPTION.value),
        payload,
        provider_token=settings.PAYMENTS_PROVIDER_TOKEN,
        start_parameter=encode_parameter(product_identifier),
        currency=product.price_currency,
        prices=[types.LabeledPrice(_("Price"), to_telegram_price(int(product.price)))],
        photo_url=product.main_picture.thumbnail,
        photo_height=150,
        photo_width=200,
        need_name=True,
        need_phone_number=True,
        need_shipping_address=True,
        is_flexible=True,
        reply_markup=get_invoice_keyboard(product, locale),
    )


@dp.message_handler(filters.CommandStart(re.compile(r"([\w-]+)")), state=any_state)
@handle_regex_params(decode_parameter, regex_key="deep_link")
async def process_start_invoice_param(
    message: types.Message,
    *,
    state: FSMContext,
    locale: str,
    handled_params: tuple,
    **kwargs,
) -> None:
    product_identifier, = handled_params
    logger.debug("Product identifier: %s", product_identifier)

    match = re.match(rf"{PRODUCT_REGEX}:(\d+)", product_identifier)
    if not match:
        await message.answer(_("Wrong invoice link."))
        return

    product_index, product_filters, product_size = match.groups()
    await answer_product_invoice(
        message,
        state,
        locale,
        int(product_index),
        ProductFilters(product_filters),
        int(product_size),
    )


@dp.callback_query_handler(
    filters.Regexp(rf"list_sizes:{PRODUCT_REGEX}"), state=any_state
)
@handle_product_params
async def list_product_sizes(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    handled_params: tuple,
    locale: str,
    **kwargs,
) -> None:
    product_index, product_filters = handled_params
    product = await get_product(state, product_index, product_filters)
    await callback_query.message.reply(
        emojize(_(":shoe: Choose shoe size")),
        reply_markup=get_product_sizes_keyboard(
            product, product_index, product_filters
        ),
    )
    await callback_query.answer()


@dp.callback_query_handler(
    filters.Regexp(rf"buy:(\d+):{PRODUCT_REGEX}"), state=any_state
)
@handle_regex_params(int, int, ProductFilters)
async def process_buy(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    handled_params: tuple,
    locale: str,
    **kwargs,
) -> None:
    size, product_index, product_filters = handled_params
    await callback_query.message.delete()
    await answer_product_invoice(
        callback_query.message, state, locale, product_index, product_filters, size
    )
    await callback_query.answer()


@dp.shipping_query_handler(state=any_state)
async def process_shipping(shipping_query: types.ShippingQuery):
    shipping_options = [
        types.ShippingOption(
            id,
            _(title),
            prices=[
                types.LabeledPrice(_(label), to_telegram_price(price))
                for label, price in prices
            ],
        )
        for id, title, prices in settings.SHIPPING_OPTIONS
    ]
    await bot.answer_shipping_query(
        shipping_query.id, ok=True, shipping_options=shipping_options
    )


@dp.pre_checkout_query_handler(state=any_state)
async def process_pre_checkout(
    pre_checkout_query: types.PreCheckoutQuery, state: FSMContext
):
    try:
        await notify_managers_new_order(state, pre_checkout_query)
    except Exception:
        logger.exception("An order notification wasn't sent to the admin.")
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message=_("Something went wrong. Try again later."),
        )
    else:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT, state=any_state)
async def got_payment(message: types.Message) -> None:
    await message.answer_sticker(
        settings.SUCCESSFUL_PAYMENT_STICKER_ID, disable_notification=True
    )
    text = _(
        ":clap: :smile: Woah! Thank's for the purchase! We will contact you shortly."
    )
    await message.answer(emojize(text))
