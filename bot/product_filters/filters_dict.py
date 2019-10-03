import logging
from collections import UserDict
from typing import Dict, Optional, Union
from urllib.parse import parse_qsl, urlencode

from .choices import FilterChoice, get_filter_choice

logger = logging.getLogger(__name__)


StoredProductFilters = Dict[str, str]
InitFilters = Union[str, StoredProductFilters]


class ProductFilters(UserDict):
    NOT_FILTERS = ["page", "page_size"]

    def __init__(self, init_filters: Optional[InitFilters] = None) -> None:
        filters: Optional[StoredProductFilters]
        if isinstance(init_filters, str):
            filters = dict(parse_qsl(init_filters))
        else:
            filters = init_filters
        super().__init__(filters)

    def __repr__(self) -> str:
        class_name = type(self).__name__
        return f"{class_name}({self.as_query_string()})"

    def as_query_string(self) -> str:
        return urlencode(self.data)

    async def get_with_associated_choices(self) -> Dict[str, FilterChoice]:
        return {
            filter_name: await get_filter_choice(filter_name, query_value)
            for filter_name, query_value in self.data.items()
            if filter_name not in self.NOT_FILTERS
        }
