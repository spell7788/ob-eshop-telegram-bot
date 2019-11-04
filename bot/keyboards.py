import logging
from collections import OrderedDict
from typing import Sequence

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.emoji import emojize

from . import callback_forms
from .bot import N_, _  # type: ignore
from .dataclasses import Product
from .product_filters import FilterChoice, ProductFilters

logger = logging.getLogger(__name__)


PRIME_KEYBOARD_TEXTS = OrderedDict(
    [("browse", N_("Browse")), ("help", N_("Help")), ("contacts", N_("Contacts"))]
)

prime_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text) for text in PRIME_KEYBOARD_TEXTS.values()]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def get_filter_choices_keyboard(
    choices: Sequence[FilterChoice], *, row_width: int
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=row_width)
    for choice in choices:
        markup.insert(
            InlineKeyboardButton(choice.label, callback_data=choice.callback_data)
        )

    markup.add(
        InlineKeyboardButton(
            emojize(_(":white_small_square: Skip")),
            callback_data=callback_forms.SKIP.callback_string,
        ),
        InlineKeyboardButton(
            emojize(_(":black_small_square: Skip all")),
            callback_data=callback_forms.SKIP_ALL.callback_string,
        ),
    )
    return markup


def get_product_sizes_keyboard(
    product: Product, product_index: int, product_filters: ProductFilters
) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=5)
    for __, (size_id, size), __ in product.stock_items:
        callback_data = (
            callback_forms.BUY
            + str(size_id)
            + str(product_index)
            + product_filters.as_query_string()
        ).callback_string
        markup.insert(
            InlineKeyboardButton(
                emojize(f":white_small_square: {size}"), callback_data=callback_data
            )
        )

    return markup


def get_invoice_keyboard(product: Product, locale: str) -> InlineKeyboardMarkup:
    pay_text = _(":moneybag: Buy {price}").format(price=product.format_price(locale))
    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[[InlineKeyboardButton(emojize(pay_text), pay=True)]],
    )
