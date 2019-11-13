import logging
import operator
from functools import partial
from typing import Any, Callable, Dict, Hashable, Optional, Sequence, Tuple

from babel.support import LazyProxy

from .. import callback_forms
from ..bot import settings  # type: ignore
from ..client import Client
from ..utils import simple_repr
from . import constant_choices

logger = logging.getLogger(__name__)


@simple_repr
class FilterChoice:
    def __init__(
        self,
        choice_data: Dict[str, Any],
        filter_name: str,
        label_getter: Callable,
        label_sep: str = " ",
        id_field_name: str = "id",
    ) -> None:
        self.id = str(choice_data[id_field_name])

        label_values = label_getter(choice_data)
        if isinstance(label_values, (str, LazyProxy)):
            self.label = label_values
        else:
            self.label = label_sep.join(label_values)

        callback_form = callback_forms.CHOICE + filter_name + str(self.id)
        self.callback_data = callback_form.callback_string

    def __str__(self) -> str:
        return self.label


RawChoices = Sequence[Dict[str, Any]]


async def get_choices(
    filter_name: str,
    label_fields: Tuple[str],
    handler: Optional[Callable[..., RawChoices]] = None,
    relation_value: Optional[Any] = None,
    **kwargs: Any,
) -> Sequence[FilterChoice]:
    api_endpoint = settings.PRODUCT_FILTERS[filter_name].api_endpoint
    if api_endpoint is not None:
        client = Client.get_client()
        choices = await client.fetch_filter_choices(api_endpoint)
        logger.debug("Choices cache info: %s", client.fetch_filter_choices.cache_info())
    else:
        choices = getattr(constant_choices, f"{filter_name}_choices".upper())

    if handler is not None:
        choices = handler(choices, relation_value)

    label_getter = operator.itemgetter(*label_fields)
    return [
        FilterChoice(choice, filter_name, label_getter, **kwargs) for choice in choices
    ]


def extract_genders(categories: RawChoices, *args: Any) -> RawChoices:
    return [category for category in categories if category["parent"] is None]


def extract_subcategories(
    categories: RawChoices, gender: Optional[str] = None
) -> RawChoices:
    if gender is not None:
        return [
            category for category in categories if category["parent"] == int(gender)
        ]
    return categories


FILTER_CHOICES_GETTERS = {
    filter_name: partial(
        get_choices,
        filter_name,
        settings.PRODUCT_FILTERS[filter_name].label_fields,
        handler=handler,
    )
    for filter_name, handler in [
        ("gender", extract_genders),
        ("category", extract_subcategories),
        ("season", None),
        ("brand", None),
        ("color", None),
        ("outer_material", None),
    ]
}


async def get_filter_choice(filter_name: str, filter_id: Hashable) -> FilterChoice:
    get_choices = FILTER_CHOICES_GETTERS[filter_name]
    for choice in await get_choices():
        if choice.id == filter_id:
            return choice

    raise ValueError(f"Can't get filter choice for {filter_name} with id {filter_id}.")
