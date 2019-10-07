from pathlib import Path
from typing import Dict

from environs import Env
from furl import furl

from .utils import FilterSettings

env = Env()

BASE_DIR = Path(__file__).parent.parent

LOCALES_DIR = BASE_DIR / "locales"

I18N_DOMAIN = "messages"

BOT_TOKEN = env("BOT_TOKEN")

ADMINS = env.list("ADMINS", subcast=int)

MANAGERS = env.list("MANAGERS", subcast=int)

BASE_URL = env("BASE_URL")

API_BASE_URL = furl(BASE_URL).add(path=env("API_PATH")).url

API_TOKEN = env("API_TOKEN")

PAYMENTS_PROVIDER_TOKEN = env("PAYMENTS_PROVIDER_TOKEN")

FSM_STORAGE = {"host": env("STORAGE_HOST"), "port": env.int("STORAGE_PORT")}

TIMEZONE = env("TIMEZONE", "UTC")

DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S %Z%z"

SHORT_DATETIME_FORMAT = "%d/%m/%Y %H:%M"

FILTERS_STORAGE_KEY = "filters"

CACHED_PAGE_STORAGE_KEY = "cached_page"

PRODUCT_PAGE_SIZE = 10

_ = lambda s: s  # noqa


PRODUCT_FILTERS: Dict[str, FilterSettings] = {
    "gender": FilterSettings(
        _("Gender"), ("title",), api_endpoint="/categories/", query_name="category"
    ),
    "category": FilterSettings(
        _("Category"), ("title",), api_endpoint="/categories/", depends_on="gender"
    ),
    "season": FilterSettings(_("Season"), ("name",)),
    "brand": FilterSettings(_("Brand"), ("name",), api_endpoint="/brands/"),
    "color": FilterSettings(_("Color"), ("name",), api_endpoint="/colors/"),
    "outer_material": FilterSettings(
        _("Outer material"), ("name",), api_endpoint="/outer_materials/"
    ),
}

SHIPPING_OPTIONS = [
    ("nova_poshta", _("Nova Poshta (Сustomer pays shipping)"), [(_("Nova Poshta"), 0)]),
    ("local_pickup", _("Local pickup (Mykolaiv)"), [(_("Local pickup"), 0)]),
]

SUCCESSFUL_PAYMENT_STICKER_ID = env("SUCCESSFUL_PAYMENT_STICKER_ID")

CONTACT_PHONES = env.list("CONTACT_PHONES")

CONTACT_EMAILS = env.list("CONTACT_EMAILS")

# fmt: off
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "bot": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
# fmt: on
