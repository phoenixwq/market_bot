from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.content_types import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from bot.db.base import session
from bot.db.models import User, City
from aiogram import types
from bot.db.utils import get_or_create
from bot.geocoder import get_city_by_coords

router = Router()


class Location(StatesGroup):
    waiting_location = State()


@router.message(commands=["location"])
async def set_users_location(message: types.Message, state: FSMContext):
    await message.answer("Please send your geo-location")
    await state.set_state(Location.waiting_location)


@router.message(Location.waiting_location, ContentTypesFilter(content_types=["location"]))
async def set_users_location(message: types.Message, state: FSMContext):
    with session() as s:
        user = s.query(User).filter_by(chat_id=message.from_user.id).first()
        lat = message.location.latitude
        lon = message.location.longitude
        city_name = get_city_by_coords(lat, lon)
        if city_name is None:
            await message.answer("Unable to determine your geolocation")
            return
        city = get_or_create(s, City, name=city_name)
        user.point = f"POINT({lat} {lon})"
        user.city = city
        s.add(user)

    await message.answer("Successful!")
    await state.clear()
