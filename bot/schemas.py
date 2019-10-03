from typing import Any, Callable, Dict, Type

from marshmallow import Schema, fields, post_load
from typing_extensions import Protocol

from .dataclasses import Picture, Product, ProductPage, Size, StockItem


class Dataclass(Protocol):
    def __init__(self, **kwargs):
        ...


def get_dataclass_maker(cls: Type[Dataclass]) -> Callable[..., Dataclass]:
    def make_dataclass(self, data: Dict[str, Any], **kwargs: Any) -> Dataclass:
        return cls(**data)

    return make_dataclass


class PictureSchema(Schema):
    id = fields.Int(required=True)
    pic = fields.Url(required=True)
    thumbnail = fields.Url(required=True)

    make_picture = post_load(get_dataclass_maker(Picture))


class SizeSchema(Schema):
    id = fields.Int(required=True)
    size = fields.Int(required=True)

    make_size = post_load(get_dataclass_maker(Size))


class StockItemSchema(Schema):
    id = fields.Int(required=True)
    size = fields.Nested(SizeSchema, required=True)
    stock = fields.Int(required=True)

    make_stock_item = post_load(get_dataclass_maker(StockItem))


class ProductSchema(Schema):
    url = fields.Url(required=True)
    id = fields.Int(required=True)
    code = fields.Str(required=True)
    name = fields.Str(required=True)
    brand = fields.Str(required=True)
    category = fields.Str(required=True)
    season = fields.Str(required=True)
    price = fields.Str(required=True)
    price_currency = fields.Str(required=True)
    is_new = fields.Bool(required=True)
    color = fields.Str(required=True)
    inner_material = fields.Str(required=True)
    outer_material = fields.Str(required=True)
    sole = fields.Str(required=True, allow_none=True)
    main_picture = fields.Nested(PictureSchema, required=True)
    secondary_pictures = fields.Nested(PictureSchema, many=True, required=True)
    stock_items = fields.Nested(StockItemSchema, many=True, required=True)

    make_product = post_load(get_dataclass_maker(Product))


class ProductPageSchema(Schema):
    count = fields.Int(required=True)
    page = fields.Int(required=True)
    num_pages = fields.Int(required=True, data_key="numPages")
    has_previous_page = fields.Bool(required=True, data_key="hasPrevious")
    has_next_page = fields.Bool(required=True, data_key="hasNext")
    results = fields.List(fields.Nested(ProductSchema), required=True)

    make_product_page = post_load(get_dataclass_maker(ProductPage))
