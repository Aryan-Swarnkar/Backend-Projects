from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductResponse, ProductCreate, ProductWithCategoriesResponse, CategoryResponse, CategoryCreate, ProductUpdate, CartItemResponse, AddToCartRequest
from app.models import Product, Category, CartItem, Cart
from decimal import Decimal

app = FastAPI()

@app.get("/")
def index():
    return {
        "message": "Hello World !"
    }

@app.post("/product", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_prod = Product(
    name=product.name,
    price=product.price,
    stock_quantity=product.stock_quantity,
)
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    
    return new_prod

@app.get("/products", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    category_id: int | None = Query(None),
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    name: str | None = Query(None, min_length=1),
    in_stock: bool | None = Query(None),
    skip: int | None = Query(None, ge=0),
    limit: int | None = Query(20, ge=0, le=100)
):
    query = db.query(Product)
    
    if category_id is not None:
        query = query.join(Product.categories).filter(Category.id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= min_price)
    if name is not None:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if in_stock is not None:
        query = query.filter(Product.stock_quantity > 0) if in_stock else query.filter(Product.stock_quantity == 0)
    
    return query.offset(skip).limit(limit).all()
        

@app.get("/products/{product_id}", response_model=ProductWithCategoriesResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    return product

@app.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product(product_id: int, updates: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}/categories/{category_id}", response_model=ProductWithCategoriesResponse)
def remove_category_from_product(product_id: int, category_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")

    category = next((c for c in product.categories if c.id == category_id), None)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not linked to this product.")

    product.categories.remove(category)
    db.commit()
    db.refresh(product)
    return product

@app.post("/products/{product_id}/categories/{category_id}", response_model=ProductWithCategoriesResponse)
def add_category_to_product(product_id: int, category_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    category = db.query(Category).filter(Category.id == category_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found.")
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {category_id} not found.")

    if category not in product.categories:
        product.categories.append(category)
        db.commit()
        db.refresh(product)
    return product


@app.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@app.post("/add_to_cart", response_model=CartItemResponse)
def add_to_cart(
    request: AddToCartRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == request.product_id
    ).first()

    if existing_item:
        existing_item.quantity += request.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    
    new_item = CartItem(
        cart_id=cart.id,
        product_id=request.product_id,
        quantity=request.quantity
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item