import datetime
from sqlalchemy import Integer, String, ForeignKey, Column, BigInteger, DateTime
from sqlalchemy.orm import relationship
from .base import DeclarativeBase
from geoalchemy2 import Geometry


class City(DeclarativeBase):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    users = relationship("User", back_populates="city")
    products = relationship("ShopProduct", back_populates="city")
    requests = relationship("RequestCity", back_populates="city")


class RequestCity(DeclarativeBase):
    __tablename__ = "request_city"
    id = Column(Integer, primary_key=True)
    city_id = Column(ForeignKey('city.id'))
    request_id = Column(ForeignKey('request.id'))
    city = relationship("City", back_populates="requests")
    request = relationship("Request", back_populates="cities")
    date = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Request(DeclarativeBase):
    __tablename__ = "request"
    id = Column(Integer, primary_key=True)
    query = Column(String, unique=True)
    cities = relationship("RequestCity", back_populates="request")


class User(DeclarativeBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    point = Column(Geometry('POINT'), nullable=True)
    city_id = Column(Integer, ForeignKey('city.id'))
    city = relationship("City", back_populates="users")

    def __repr__(self):
        return f"chat_id: {self.chat_id}"


class ShopProduct(DeclarativeBase):
    __tablename__ = 'shop_product'
    id = Column(Integer, primary_key=True)
    shop_id = Column(ForeignKey('shop.id'))
    product_id = Column(ForeignKey('product.id'))
    city_id = Column(Integer, ForeignKey('city.id'))
    price = Column(String)
    address = Column(String)
    address_point = Column(Geometry('POINT'), nullable=True)
    shop = relationship("Shop", back_populates="products")
    product = relationship("Product", back_populates="shops")
    city = relationship("City", back_populates="products")


class Shop(DeclarativeBase):
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    products = relationship("ShopProduct", back_populates="shop")


class Product(DeclarativeBase):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    site_id = Column(BigInteger, unique=True)
    name = Column(String)
    image = Column(String)
    shops = relationship("ShopProduct", back_populates="product")
