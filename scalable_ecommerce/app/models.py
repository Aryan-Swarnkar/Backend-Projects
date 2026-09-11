from typing import List
from app.database import Base
from sqlalchemy import Table, String, Column, ForeignKey, FLOAT, INTEGER, Numeric, UniqueConstraint
from decimal import Decimal
from sqlalchemy.orm import mapped_column, relationship, Mapped

product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True),
    Column("category_id", ForeignKey("category.id"), primary_key=True),
    
)

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

class Category(Base):
  __tablename__="category"
  id: Mapped[int] = mapped_column(primary_key=True)
  category_name: Mapped[str] = mapped_column(String(100))

  products: Mapped[List["Product"]] = relationship(
    "Product", secondary=product_category, back_populates="categories"
  )
  
class Product(Base):
  __tablename__="product"
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100))
  price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
  # price: Mapped[float] = mapped_column(FLOAT)
  stock_quantity: Mapped[int] = mapped_column(INTEGER)

  categories: Mapped[List["Category"]] = relationship(
    "Category", secondary=product_category, back_populates="products"
  )
  
class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    items: Mapped[List["CartItem"]] = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_item"
    __table_args__=(UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("cart.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    quantity: Mapped[int] = mapped_column(INTEGER)

    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
  
class Order(Base):
  __tablename__="order"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  
  user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
  items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
  
class OrderItem(Base):
  __tablename__="order_item"
  
  id: Mapped[int] = mapped_column(primary_key=True)
  product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
  order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
  quantity: Mapped[int] = mapped_column(INTEGER)
  price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2))

  order: Mapped["Order"] = relationship("Order", back_populates="items")
  product: Mapped["Product"] = relationship("Product")