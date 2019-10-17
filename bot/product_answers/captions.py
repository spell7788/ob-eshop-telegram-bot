import logging
from dataclasses import fields
from typing import AsyncIterator, Iterator, NamedTuple, Optional, Tuple

from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, italic, link as md_link, text as md_text

from ..bot import _, settings  # type: ignore
from ..dataclasses import Product
from ..product_filters import ProductFilters

logger = logging.getLogger(__name__)


class CaptionFormat(NamedTuple):
    caption_text_sep: str = "\n"
    attrs_sep: str = "\n"
    attr_symbol: Optional[str] = None
    attr_title_label_sep: str = " - "
    text_filters_sep: str = "\n\n"
    filters_group_sep: str = ": "
    filters_sep: str = " • "


class Caption:
    format = CaptionFormat()

    def __init__(self, product: Product, product_filters: ProductFilters, locale: str):
        self.product = product
        self.product_filters = product_filters
        self._pictures_links = [picture.pic for picture in self.product.pictures]
        self._product_link = md_link(self.product.name, self.product.url)
        self._new_text = italic(_("New")) if self.product.is_new else ""
        self._price_text = self.product.format_price(locale)

    async def to_string(self) -> str:
        filters_texts = await self._join_product_filters_texts()
        caption = md_text(
            self._get_title(),
            md_text(self._get_text(), filters_texts, sep=self.format.text_filters_sep),
            sep=self.format.caption_text_sep,
        )
        return emojize(caption)

    def _get_title(self) -> str:
        raise NotImplementedError()

    def _get_text(self) -> str:
        return self._join_product_attributes()

    async def _join_product_filters_texts(self) -> str:
        texts = [
            italic(str(title), label, sep=self.format.filters_group_sep)
            async for title, label in self._filters_text_pairs()
        ]
        return self.format.filters_sep.join(texts)

    async def _filters_text_pairs(self) -> AsyncIterator[Tuple[str, str]]:
        filters = await self.product_filters.get_with_associated_choices()
        for filter_name, choice in filters.items():
            title = _(settings.PRODUCT_FILTERS[filter_name].title)
            yield (title, choice.label)

    def _join_product_attributes(self) -> str:
        attrs_texts = [
            md_text(title, label, sep=self.format.attr_title_label_sep)
            for title, label in self._attr_title_label_pairs()
        ]
        if self.format.attr_symbol is not None:
            attrs_texts = [
                md_text(self.format.attr_symbol, text) for text in attrs_texts
            ]

        return md_text(*attrs_texts, sep=self.format.attrs_sep)

    def _attr_title_label_pairs(self) -> Iterator[Tuple[str, str]]:
        for field_ in fields(self.product):
            if field_.metadata and "title" in field_.metadata:
                field_value = getattr(self.product, field_.name)
                # Don't display optional None specified attribute
                if field_value is None:
                    continue

                yield (field_.metadata["title"], field_value)


class SlideCaption(Caption):
    format = CaptionFormat(attr_symbol="•")

    def _get_title(self) -> str:
        return md_text(
            self._new_text,
            ":small_blue_diamond:",
            self._product_link,
            ":moneybag:",
            self._price_text,
        )


class BookmarkCaption(Caption):
    format = CaptionFormat(attrs_sep=" • ", text_filters_sep="\n")

    def _get_title(self) -> str:
        return md_text(
            ":star:",
            bold(_("Bookmark")),
            self._new_text,
            ":small_orange_diamond:",
            self._product_link,
            ":moneybag:",
            self._price_text,
        )
