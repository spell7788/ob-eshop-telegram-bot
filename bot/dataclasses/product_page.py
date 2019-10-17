from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from ..bot import settings  # type: ignore
from .product import Product


class ProductPageException(Exception):
    pass


class PageResultsState:
    def __init__(self, page: ProductPage) -> None:
        self.page = page

    def __getitem__(self, index: int) -> Product:
        raise NotImplementedError()

    def has_previous_slide(self, index: int) -> bool:
        raise NotImplementedError()

    def has_next_slide(self, index: int) -> bool:
        raise NotImplementedError()

    def get_out_of_all_number(self, index: int) -> int:
        raise NotImplementedError()

    @property
    def last_item_index(self) -> int:
        raise NotImplementedError()


class PageNoResultsState(PageResultsState):
    def __getitem__(self, index: int) -> Product:
        raise ProductPageException()

    def has_previous_slide(self, index: int) -> bool:
        raise ProductPageException()

    def has_next_slide(self, index: int) -> bool:
        raise ProductPageException()

    def get_out_of_all_number(self, index: int) -> int:
        raise ProductPageException()

    @property
    def last_item_index(self) -> int:
        raise ProductPageException()


class PageHasResultsState(PageResultsState):
    def __getitem__(self, product: int) -> Product:
        return self.page.results[product]  # type: ignore

    def has_previous_slide(self, index: int) -> bool:
        return index > 0

    def has_next_slide(self, index: int) -> bool:
        return index < self.page.last_item_index

    def get_out_of_all_number(self, index: int) -> int:
        page_number = self.page.page
        return (page_number - 1) * settings.PRODUCT_PAGE_SIZE + index + 1

    @property
    def last_item_index(self) -> int:
        return len(self.page.results) - 1  # type: ignore


@dataclass
class ProductPage:
    count: int
    page: int
    num_pages: int
    has_previous_page: bool
    has_next_page: bool
    results: Sequence[Product] = field(repr=False)

    def __post_init__(self) -> None:
        self.state: PageResultsState
        if self.results:
            self.state = PageHasResultsState(self)
        else:
            self.state = PageNoResultsState(self)

    def __getitem__(self, product_index: int) -> Product:
        return self.state[product_index]

    def has_previous_slide(self, index: int) -> bool:
        return self.state.has_previous_slide(index)

    def has_next_slide(self, index: int) -> bool:
        return self.state.has_next_slide(index)

    def get_out_of_all_number(self, index: int) -> int:
        return self.state.get_out_of_all_number(index)

    @property
    def last_item_index(self) -> int:
        return self.state.last_item_index
