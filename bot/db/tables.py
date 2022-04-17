# from sqlalchemy import Column
# from sqlalchemy import ForeignKey
# from sqlalchemy import BigInteger, Integer, String
# from sqlalchemy.orm import relationship
# from .base import DeclarativeBase
#
#
# class User(DeclarativeBase):
#     __tablename__ = "user"
#     id = Column(Integer, primary_key=True)
#     chat_id = Column(BigInteger, unique=True)
#     products = relationship("Product")
#
#     def __repr__(self):
#         return f"chat_id: {self.chat_id}"
#
#
# class Product(DeclarativeBase):
#     __tablename__ = "product"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     price = Column(String)
#     shop = Column(String)
#     url = Column(String)
#     user = Column(Integer, ForeignKey("user.id"), nullable=False)
#
#     def __repr__(self):
#         return f"{self.name}"
