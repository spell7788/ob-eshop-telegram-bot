import logging
from typing import Match

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import any_state
from aiogram.utils.exceptions import Throttled

from ..bot import _, dp  # type: ignore
from ..product_answers import get_bookmark_answer, get_product, get_product_slide_answer
from .common import PRODUCT_REGEX, answer_product_slide, handle_product_params

logger = logging.getLogger(__name__)


@dp.callback_query_handler(
    filters.Regexp(rf"controls:(?:previous|next):{PRODUCT_REGEX}"), state=any_state
)
@handle_product_params
async def process_browse_controls(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    handled_params: tuple,
    locale: str,
    **kwargs,
) -> None:
    next_product_index, product_filters = handled_params
    product_slide = await get_product_slide_answer(
        state, locale, next_product_index, product_filters
    )
    await answer_product_slide(
        callback_query.message, state, locale, product_slide, edit=True
    )
    await callback_query.answer()


@dp.callback_query_handler(
    filters.Regexp(rf"all_pics:{PRODUCT_REGEX}"), state=any_state
)
@handle_product_params
async def post_all_pictures(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    handled_params: tuple,
    locale: str,
    regexp: Match,
    **kwargs,
) -> None:
    try:
        await dp.throttle(regexp.string, rate=60)
    except Throttled:
        await callback_query.answer(_("Please try again in a minute."))
    else:
        product = await get_product(state, *handled_params)
        pictures = [
            types.InputMediaPhoto(picture.pic, picture.thumbnail)
            for picture in product.pictures
        ]
        await callback_query.message.reply_media_group(pictures)
        await callback_query.answer()


@dp.callback_query_handler(
    filters.Regexp(rf"bookmark:add:{PRODUCT_REGEX}"), state=any_state
)
@handle_product_params
async def add_bookmark(
    callback_query: types.CallbackQuery,
    *,
    state: FSMContext,
    handled_params: tuple,
    locale: str,
    regexp: Match,
    **kwargs,
) -> None:
    try:
        await dp.throttle(regexp.string, rate=30)
    except Throttled:
        await callback_query.answer(_("Please try again in a minute."))
    else:
        bookmark = await get_bookmark_answer(state, locale, *handled_params)
        await callback_query.message.reply(
            await bookmark.get_caption(),
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=bookmark.make_keyboard(),
        )
        await callback_query.answer()


@dp.callback_query_handler(filters.Text("bookmark:delete"), state=any_state)
async def delete_bookmark(callback_query: types.CallbackQuery) -> None:
    await callback_query.message.delete()
    await callback_query.answer()
