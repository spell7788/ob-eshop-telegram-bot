# type: ignore
import importlib
import logging
import logging.config

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from babel.support import LazyProxy
from environs import Env

env = Env()

settings_name = env("BOT_SETTINGS_MODULE", "bot.settings.production")

settings = importlib.import_module(settings_name)

logging.config.dictConfig(settings.LOGGING)

bot = Bot(settings.BOT_TOKEN)

dp = Dispatcher(bot, storage=RedisStorage2(**settings.FSM_STORAGE))

i18n = I18nMiddleware(settings.I18N_DOMAIN, settings.LOCALES_DIR)

dp.middleware.setup(i18n)

_ = i18n.gettext


def N_(*args, **kwargs) -> LazyProxy:
    return i18n.lazy_gettext(*args, enable_cache=False, **kwargs)


def get_http_session() -> aiohttp.ClientSession:
    if not hasattr(get_http_session, "_session"):
        headers = {"Authorization": f"Token {settings.API_TOKEN}"}
        get_http_session._session = aiohttp.ClientSession(headers=headers)
    return get_http_session._session
