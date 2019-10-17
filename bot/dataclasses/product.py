from dataclasses import dataclass, field
from decimal import Decimal
from typing import NamedTuple, Optional, Sequence

from babel.numbers import format_currency

from ..bot import N_  # type: ignore


class Picture(NamedTuple):
    id: int
    pic: str
    thumbnail: str


class Size(NamedTuple):
    id: int
    size: int


class StockItem(NamedTuple):
    id: int
    size: Size
    stock: int


@dataclass
class Product:
    url: str = field(repr=False)
    id: int
    code: str = field(metadata={"title": N_("Code")})
    name: str
    brand: str = field(repr=False, metadata={"title": N_("Brand")})
    category: str = field(repr=False, metadata={"title": N_("Category")})
    season: str = field(repr=False, metadata={"title": N_("Season")})
    price: str
    price_currency: str
    is_new: bool
    color: str = field(repr=False, metadata={"title": N_("Color")})
    inner_material: str = field(repr=False, metadata={"title": N_("Inner material")})
    outer_material: str = field(repr=False, metadata={"title": N_("Outer material")})
    sole: Optional[str] = field(repr=False, metadata={"title": N_("Sole")})
    main_picture: Picture = field(repr=False)
    secondary_pictures: Sequence[Picture] = field(repr=False)
    stock_items: Sequence[StockItem] = field(repr=False)

    def format_price(self, locale: str) -> str:
        return format_currency(Decimal(self.price), self.price_currency, locale=locale)

    @property
    def pictures(self) -> Sequence[Picture]:
        return [pic for pic in [self.main_picture, *self.secondary_pictures]]

    @property
    def available_stock_items(self) -> Sequence[StockItem]:
        return [stock_item for stock_item in self.stock_items if stock_item.stock > 0]
