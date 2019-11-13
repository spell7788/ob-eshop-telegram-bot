from aiogram import Dispatcher, executor

from .bot import _, bot, dp, settings  # type: ignore
from .client import Client
from .utils import message_admins, tz_aware_now


async def on_startup(dispatcher: Dispatcher) -> None:
    now = tz_aware_now().strftime(settings.DATETIME_FORMAT)
    await message_admins(
        lambda admin_id: bot.send_message(
            admin_id, _("I started at {now}").format(now=now)
        )
    )


async def on_shutdown(dispatcher: Dispatcher) -> None:
    client = Client.get_client()
    await client.close()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    now = tz_aware_now().strftime(settings.DATETIME_FORMAT)
    await message_admins(
        lambda admin_id: bot.send_message(
            admin_id, _("I turned off at {now}").format(now=now)
        )
    )


if __name__ == "__main__":
    from . import handlers  # noqa

    executor.start_polling(
        dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown
    )
