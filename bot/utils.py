import base64
import functools
import logging
from datetime import datetime
from functools import partial
from typing import Any, Awaitable, Callable, Optional, Sequence, Type, TypeVar

import pytz

from .bot import settings  # type: ignore

logger = logging.getLogger(__name__)

T = TypeVar("T")


def simple_repr(cls: Type[T]) -> Type[T]:
    def __repr__(self) -> str:
        class_name = type(self).__name__
        attrs = ", ".join(f"{name}={value!r}" for name, value in self.__dict__.items())
        return f"{class_name}({attrs})"

    cls.__repr__ = __repr__  # type: ignore
    return cls


async def mass_massage(
    recipients: Sequence[int], message: Callable[[int], Awaitable[None]]
) -> None:
    for recipient in recipients:
        await message(recipient)


message_admins = partial(mass_massage, settings.ADMINS)

message_managers = partial(mass_massage, settings.MANAGERS)


def tz_aware_datetime(utc_dt: datetime) -> datetime:
    timezone = pytz.timezone(settings.TIMEZONE)
    return utc_dt.astimezone(timezone)


tz_aware_now = partial(tz_aware_datetime, datetime.utcnow())


def handle_regex_params(
    *handlers: Optional[Callable[[str], Any]], regex_key: str = "regexp"
):
    def decorator(func: Callable[..., Awaitable[None]]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> None:
            match = kwargs[regex_key]
            values = match.groups(default=())
            assert len(values) == len(
                handlers
            ), "Number of handlers and values must be the same."

            handle_groups = list(zip(handlers, values))
            logger.debug("Handle groups: %s", handle_groups)

            handled_params = [
                type_(captured_value) if type_ is not None else captured_value
                for type_, captured_value in handle_groups
            ]
            logger.debug("Handled params: %s", handled_params)
            return await func(*args, handled_params=handled_params, **kwargs)

        return wrapper

    return decorator


def encode_parameter(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode("utf-8")).decode("utf-8")


def decode_parameter(value: str) -> str:
    return base64.urlsafe_b64decode(value).decode("utf-8")


def to_telegram_price(price: int) -> int:
    return price * 100


def from_telegram_price(price: int) -> str:
    return str(price / 100)
