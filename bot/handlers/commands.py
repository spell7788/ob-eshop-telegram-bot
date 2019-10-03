from string import Template

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import any_state
from aiogram.types import ParseMode
from aiogram.utils.emoji import emojize

from .. import texts
from ..bot import _, dp, settings
from ..keyboards import PRIME_KEYBOARD_TEXTS, prime_keyboard
from ..states import ProductFiltersForm
from .common import answer_next_filter_or_results


@dp.message_handler(commands=["start"], state=any_state)
async def process_start_command(message: types.Message) -> None:
    text = Template(texts.START.value).substitute(
        first_name=message.from_user.first_name,
        bot_mention=(await message.bot.me).mention,
    )
    await message.answer(text, reply_markup=prime_keyboard)


@dp.message_handler(filters.Text(PRIME_KEYBOARD_TEXTS["help"]))
@dp.message_handler(commands=["help"], state=any_state)
async def process_help_command(message: types.Message) -> None:
    await message.answer(texts.HELP)


@dp.message_handler(filters.Text(PRIME_KEYBOARD_TEXTS["contacts"]))
@dp.message_handler(commands=["contacts"], state=any_state)
async def process_contacts_command(message: types.Message) -> None:
    text = Template(texts.CONTACTS.value).substitute(
        phones="\n".join(settings.CONTACT_PHONES),
        emails="\n".join(settings.CONTACT_EMAILS),
    )
    await message.answer(emojize(text), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(filters.Text(PRIME_KEYBOARD_TEXTS["browse"]))
@dp.message_handler(commands=["b", "browse"], state=any_state)
async def process_browse_command(
    message: types.Message, state: FSMContext, locale: str
) -> None:
    await state.reset_state()
    next_filter = await ProductFiltersForm.first()
    await answer_next_filter_or_results(
        message, state, locale, next_filter, starts_up=True
    )


@dp.message_handler(state=any_state)
async def process_unknown(message: types.Message) -> None:
    await message.reply(emojize(_("What..? :confused: I can't recognize that.")))
