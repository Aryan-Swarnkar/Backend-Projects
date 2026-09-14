from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import List

class ProductCreate(BaseModel):
    name: str
    price: Decimal = Field(gt=0)
    stock_quantity: int = Field(gt=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)
    
class CategoryResponse(BaseModel):
    id: int
    category_name: str
    
    model_config = ConfigDict(from_attributes=True)

class ProductWithCategoriesResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    stock_quantity: int
    categories: List[CategoryResponse]
    
    model_config = ConfigDict(from_attributes=True)

class ProductUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = Field(None, gt=0)
    stock_quantity: int | None = Field(None, ge=0)
    
class CartItemResponse(BaseModel):
    id: int
    quantity: int
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]

    model_config = ConfigDict(from_attributes=True)

class OrderItemResponse(BaseModel):
    id: int
    quantity: int
    price_at_purchase: Decimal
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    category_name: str
    

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class CartItemInput(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class BulkAddToCartRequest(BaseModel):
    items: List[CartItemInput]