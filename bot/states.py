from aiogram.dispatcher.filters.state import State, StatesGroup


class ProductFiltersForm(StatesGroup):
    gender = State()
    category = State()
    season = State()
    brand = State()
    color = State()
    outer_material = State()
