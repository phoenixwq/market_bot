from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters.content_types import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from bot.db.base import session
from bot.db.models import User
from aiogram import types

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
        user.latitude = message.location.latitude
        user.longitude = message.location.longitude
        s.add(user)

    await message.answer("Successful!")
    await state.clear()
