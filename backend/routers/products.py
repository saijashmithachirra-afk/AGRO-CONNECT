from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.database import get_db
from backend import models
from backend.auth import get_current_user, get_current_user_optional, require_farmer
from backend.ai_engine import get_ai_price
from backend.image_engine import get_product_image

router = APIRouter(prefix="/api/products", tags=["products"])

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    quantity: float
    unit: str = "kg"
    category_id: int
    image_url: Optional[str] = None
    is_pre_harvest: bool = False
    demand_factor: float = 1.0
    harvest_date: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    image_url: Optional[str] = None
    is_pre_harvest: Optional[bool] = None
    is_available: Optional[bool] = None
    demand_factor: Optional[float] = None

class AIPriceRequest(BaseModel):
    product_name: str
    current_price: float = 0
    quantity: float = 0
    demand_factor: float = 1.0
    is_pre_harvest: bool = False
    location: str = ""

class AutoImageRequest(BaseModel):
    name: str
    category: str = ""

def product_to_dict(p: models.Product, include_farmer=True):
    avg_rating = 0
    if p.reviews:
        avg_rating = round(sum(r.rating for r in p.reviews) / len(p.reviews), 1)
    d = {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "ai_suggested_price": p.ai_suggested_price,
        "quantity": p.quantity,
        "unit": p.unit,
        "category_id": p.category_id,
        "category_name": p.category.name if p.category else "",
        "farmer_id": p.farmer_id,
        "image_url": p.image_url,
        "is_pre_harvest": p.is_pre_harvest,
        "is_available": p.is_available,
        "demand_factor": p.demand_factor,
        "views": p.views,
        "harvest_date": p.harvest_date,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "avg_rating": avg_rating,
        "review_count": len(p.reviews) if p.reviews else 0,
    }
    if include_farmer and p.farmer:
        d["farmer_name"] = p.farmer.name
        d["farmer_location"] = p.farmer.location
    return d

@router.get("/")
def list_products(
    category: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort: Optional[str] = "latest",
    pre_harvest: Optional[bool] = None,
    page: int = 1,
    limit: int = 12,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_available == True)
    if category:
        query = query.filter(models.Product.category_id == category)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    if pre_harvest is not None:
        query = query.filter(models.Product.is_pre_harvest == pre_harvest)
    
    if sort == "price_low":
        query = query.order_by(models.Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(models.Product.price.desc())
    elif sort == "popular":
        query = query.order_by(models.Product.views.desc())
    else:
        query = query.order_by(models.Product.created_at.desc())
    
    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()
    return {
        "products": [product_to_dict(p) for p in products],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/farmer/my-products")
def my_products(db: Session = Depends(get_db), current_user = Depends(require_farmer)):
    products = db.query(models.Product).filter(models.Product.farmer_id == current_user.id).all()
    return [product_to_dict(p) for p in products]

@router.post("/ai-price")
def ai_price(req: AIPriceRequest, db: Session = Depends(get_db),
             current_user = Depends(get_current_user_optional)):
    location = req.location
    if not location and current_user:
        location = current_user.location or ""
    result = get_ai_price(req.product_name, req.current_price, req.quantity,
                          req.demand_factor, req.is_pre_harvest, location)
    return result

@router.post("/auto-image")
def auto_image(req: AutoImageRequest):
    result = get_product_image(req.name, req.category)
    return result

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    p.views += 1
    db.commit()
    return product_to_dict(p)

@router.post("/")
def create_product(req: ProductCreate, db: Session = Depends(get_db),
                   current_user = Depends(require_farmer)):
    if not current_user.bank_account_no and not current_user.upi_id:
        raise HTTPException(status_code=400, detail="Please add bank account or UPI ID in Profile first")
    
    if not req.image_url:
        cat = db.query(models.Category).filter(models.Category.id == req.category_id).first()
        cat_name = cat.name if cat else ""
        img_result = get_product_image(req.name, cat_name)
        image_url = img_result["url"]
    else:
        image_url = req.image_url
    
    ai_result = get_ai_price(req.name, req.price, req.quantity,
                              req.demand_factor, req.is_pre_harvest, current_user.location)
    
    product = models.Product(
        name=req.name, description=req.description, price=req.price,
        ai_suggested_price=ai_result["suggested_price"],
        quantity=req.quantity, unit=req.unit, category_id=req.category_id,
        farmer_id=current_user.id, image_url=image_url,
        is_pre_harvest=req.is_pre_harvest, demand_factor=req.demand_factor,
        harvest_date=req.harvest_date
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product_to_dict(product)

@router.put("/{product_id}")
def update_product(product_id: int, req: ProductUpdate, db: Session = Depends(get_db),
                   current_user = Depends(require_farmer)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.farmer_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in req.dict(exclude_unset=True).items():
        if value is not None:
            setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product_to_dict(product)

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db),
                   current_user = Depends(require_farmer)):
    product = db.query(models.Product).filter(
        models.Product.id == product_id,
        models.Product.farmer_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
