from aiogram import Dispatcher
from aiogram import types
from app.db.tables import Product, User
from app.db.base import session
from .utils import get_product_text_message


async def get_user_favorites(message: types.Message):
    with session() as s:
        user = s.query(User).filter_by(chat_id=message.from_user.id).first()
        products = s.query(Product).filter_by(user=user.id).all()
        for product in products:
            d = {}
            for column in product.__table__.columns:
                d[column.name] = str(getattr(product, column.name))
            text = get_product_text_message(d)
            await message.answer(text, parse_mode="HTML", disable_notification=True)


def register_favorites_handlers(dp: Dispatcher):
    dp.register_message_handler(get_user_favorites, commands="favorites", state="*")
