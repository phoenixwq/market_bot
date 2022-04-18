from sqlalchemy import Table, Integer, String, Float, ForeignKey, Column
from sqlalchemy.orm import relationship
from .base import DeclarativeBase


association_table = Table('association', DeclarativeBase.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('product_id', ForeignKey('product.id'), primary_key=True)
)


class User(DeclarativeBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    latitude = Column(Float, nullable=True, default=None)
    longitude = Column(Float, nullable=True, default=None)
    products = relationship("Product",
                            secondary="association",
                            backref="users")

    def __repr__(self):
        return f"chat_id: {self.chat_id}"


class Product(DeclarativeBase):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(String)
    shop = Column(String)
    url = Column(String, unique=True)
    image = Column(String)

    def __repr__(self):
        return f"{self.name}"
