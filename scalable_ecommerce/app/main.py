from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ProductResponse, ProductCreate, ProductWithCategoriesResponse, CategoryResponse, CategoryCreate, ProductUpdate, CartItemResponse, AddToCartRequest, CartItemInput, BulkAddToCartRequest
from app.models import Product, Category, CartItem, Cart, Order, OrderItem
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
        query = query.filter(Product.price <= max_price)
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

@app.post("/add_to_cart/bulk", response_model=CartItemResponse)
def add_to_cart_bulk(request: BulkAddToCartRequest, user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()

    for item in request.items:
        existing_item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item.product_id
        ).first()

        if existing_item:
            existing_item.quantity += item.quantity
        else:
            db.add(CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity))

    db.commit()
    db.refresh(cart)
    return cart

@app.post("/checkout", response_model=ProductResponse)
def checkout(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        order = Order(user_id=user_id)
        db.add(order)
        db.flush()  # <-- new piece, explained below

        for item in cart.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} no longer exists")
            if product.stock_quantity < item.quantity:
                raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
            db.add(order_item)
            product.stock_quantity -= item.quantity
            db.delete(item)

        db.commit()
        db.refresh(order)
        return order

    except Exception:
        db.rollback()
        raise