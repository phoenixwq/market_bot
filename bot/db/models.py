from sqlalchemy import Integer, Float, String, ForeignKey, Column
from sqlalchemy.orm import relationship
from .base import DeclarativeBase
from geoalchemy2 import Geometry


class User(DeclarativeBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    point = Column(Geometry('POINT'))

    def __repr__(self):
        return f"chat_id: {self.chat_id}"


class Shop(DeclarativeBase):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship("ShopProduct", back_populates="shop")


class Product(DeclarativeBase):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    photo = Column(String)
    shops = relationship("ShopProduct", back_populates="product")

    def __repr__(self):
        return f"{self.title}"


class ShopProduct(DeclarativeBase):
    __tablename__ = 'shop_product'
    id = Column(Integer, primary_key=True)
    shop_id = Column(ForeignKey('shop.id'))
    product_id = Column(ForeignKey('product.id'))
    price = Column(Float)
    address = Column(String)
    address_point = Column(Geometry('POINT'))
    shop = relationship("Shop", back_populates="shop")
    product = relationship("Product", back_populates="product")
