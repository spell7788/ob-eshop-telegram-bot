from dataclasses import InitVar, dataclass, field
from typing import ClassVar, Optional, Type

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.emoji import emojize

from .. import callback_forms
from ..bot import _, settings  # type: ignore
from ..dataclasses import Product, ProductPage
from ..product_filters import ProductFilters
from .captions import BookmarkCaption, Caption, SlideCaption


@dataclass
class ProductAnswer:
    product_page: ProductPage
    product_index: int
    product_filters: ProductFilters
    product: Product = field(init=False)
    caption_type: ClassVar[Type[Caption]]
    locale: InitVar[str]

    def __post_init__(self, locale: str) -> None:
        self.product = self.product_page[self.product_index]
        self.caption = self.caption_type(self.product, self.product_filters, locale)

    async def get_caption(self) -> str:
        return await self.caption.to_string()

    def make_keyboard(self) -> InlineKeyboardMarkup:
        raise NotImplementedError()

    @property
    def detail_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(emojize(_(":link: Detail")), url=self.product.url)

    @property
    def buy_procedure_button(self) -> InlineKeyboardButton:
        callback_data = (
            callback_forms.LIST_SIZES
            + str(self.product_index)
            + self.product_filters.as_query_string()
        ).callback_string
        return InlineKeyboardButton(
            emojize(_(":moneybag: Buy")), callback_data=callback_data
        )


@dataclass
class ProductSlideAnswer(ProductAnswer):
    caption_type = SlideCaption

    FIRST_SLIDE_INDEX, LAST_SLIDE_INDEX = 0, settings.PRODUCT_PAGE_SIZE - 1

    has_previous_slide: bool = field(init=False)
    has_next_slide: bool = field(init=False)
    has_previous_page: bool = field(init=False)
    has_next_page: bool = field(init=False)
    out_of_all: str = field(init=False)

    def __post_init__(self, *args, **kwargs):
        super().__post_init__(*args, **kwargs)
        self.has_previous_slide = self.product_page.has_previous_slide(
            self.product_index
        )
        self.has_next_slide = self.product_page.has_next_slide(self.product_index)
        self.has_previous_page = self.product_page.has_previous_page
        self.has_next_page = self.product_page.has_next_page
        out_of_all_number = self.product_page.get_out_of_all_number(self.product_index)
        self.out_of_all = f"{out_of_all_number} / {self.product_page.count}"

    def make_keyboard(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=4)

        prev_button = self.previous_button
        if prev_button is not None:
            markup.insert(prev_button)

        markup.insert(InlineKeyboardButton(self.out_of_all, url=self.product.url))

        next_button = self.next_button
        if next_button is not None:
            markup.insert(next_button)

        markup.add(
            self.all_pictures_button,
            self.add_bookmark_button,
            self.detail_button,
            self.buy_procedure_button,
        )
        return markup

    @property
    def previous_button(self) -> Optional[InlineKeyboardButton]:
        button_text = emojize(_(":arrow_backward: Previous"))
        if self.has_previous_slide:
            return InlineKeyboardButton(
                button_text,
                callback_data=self._make_controls_callback(
                    callback_forms.PREVIOUS, self.product_index - 1
                ),
            )
        elif self.has_previous_page:
            return InlineKeyboardButton(
                button_text,
                callback_data=self._make_controls_callback(
                    callback_forms.PREVIOUS,
                    self.product_index - 1,
                    self.LAST_SLIDE_INDEX,
                ),
            )
        return None

    @property
    def next_button(self) -> Optional[InlineKeyboardButton]:
        button_text = emojize(_(":arrow_forward: Next"))
        if self.has_next_slide:
            return InlineKeyboardButton(
                button_text,
                callback_data=self._make_controls_callback(
                    callback_forms.NEXT, self.product_index + 1
                ),
            )
        elif self.has_next_page:
            return InlineKeyboardButton(
                button_text,
                callback_data=self._make_controls_callback(
                    callback_forms.NEXT,
                    self.FIRST_SLIDE_INDEX,
                    self.product_page.page + 1,
                ),
            )
        return None

    @property
    def all_pictures_button(self) -> InlineKeyboardButton:
        callback_data = (
            callback_forms.ALL_PICTURES
            + str(self.product_index)
            + self.product_filters.as_query_string()
        ).callback_string
        return InlineKeyboardButton(
            emojize(_(":framed_picture: Pictures")), callback_data=callback_data
        )

    @property
    def add_bookmark_button(self) -> InlineKeyboardButton:
        callback_data = (
            callback_forms.ADD
            + str(self.product_index)
            + self.product_filters.as_query_string()
        ).callback_string
        return InlineKeyboardButton(
            emojize(_(":bookmark: Bookmark")), callback_data=callback_data
        )

    def _make_controls_callback(
        self,
        form: callback_forms.CallbackForm,
        product_index: int,
        page_num: Optional[int] = None,
    ) -> str:
        filters: ProductFilters = self.product_filters.copy()
        if page_num is not None:
            filters["page"] = page_num

        callback_form = form + str(product_index) + filters.as_query_string()
        return callback_form.callback_string


class BookmarkAnswer(ProductAnswer):
    caption_type = BookmarkCaption

    def make_keyboard(self) -> InlineKeyboardMarkup:
        buttons = [
            self.delete_bookmark_button,
            self.detail_button,
            self.buy_procedure_button,
        ]
        return InlineKeyboardMarkup(inline_keyboard=[buttons])

    @property
    def delete_bookmark_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(
            emojize(":x:"), callback_data=callback_forms.DELETE.callback_string
        )
