# flake8: noqa
from .base import *

DEBUG = True

LOGGING["loggers"]["bot"]["level"] = "DEBUG"  # type: ignore
