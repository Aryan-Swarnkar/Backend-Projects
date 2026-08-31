from typing import List
from app.database import Base
from sqlalchemy import Table, String, Column, ForeignKey, FLOAT, INTEGER
from sqlalchemy.orm import mapped_column, relationship, Mapped

product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", ForeignKey("product.id"), primary_key=True),
    Column("category_id", ForeignKey("category.id"), primary_key=True),
    
)

class Category(Base):
  __tablename__="category"
  id: Mapped[int] = mapped_column(primary_key=True)
  category_name: Mapped[str] = mapped_column(String(100))

  products: Mapped[List["Product"]] = relationship(
    "Product", secondary=product_category
  )
  
class Product(Base):
  __tablename__="product"
  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(100))
  price: Mapped[float] = mapped_column(FLOAT)
  stock_quantity: Mapped[int] = mapped_column(INTEGER)

  categories: Mapped[List["Category"]] = relationship(
    "Category", secondary=product_category
  )
  

