# type: ignore
import importlib
import logging
import logging.config

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
