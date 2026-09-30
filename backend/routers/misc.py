from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend import models
from backend.auth import get_current_user, get_current_user_optional, require_admin

router = APIRouter(tags=["misc"])

# ─── Categories ───────────────────────────────────────────────────────────────

@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    cats = db.query(models.Category).all()
    return [{"id": c.id, "name": c.name, "name_hi": c.name_hi,
             "name_ta": c.name_ta, "name_te": c.name_te, "icon": c.icon}
            for c in cats]

# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItem(BaseModel):
    product_id: int
    quantity: float = 1.0

@router.get("/api/cart")
def get_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    items = db.query(models.Cart).filter(models.Cart.customer_id == current_user.id).all()
    result = []
    for item in items:
        p = item.product
        if p:
            result.append({
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product_name": p.name,
                "product_price": p.price,
                "product_unit": p.unit,
                "product_image": p.image_url,
                "product_available": p.is_available,
                "farmer_name": p.farmer.name if p.farmer else "",
            })
    return result

@router.post("/api/cart")
def add_to_cart(req: CartItem, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    existing = db.query(models.Cart).filter(
        models.Cart.customer_id == current_user.id,
        models.Cart.product_id == req.product_id
    ).first()
    if existing:
        existing.quantity += req.quantity
        db.commit()
        return {"message": "Cart updated"}
    cart_item = models.Cart(customer_id=current_user.id,
                             product_id=req.product_id, quantity=req.quantity)
    db.add(cart_item)
    db.commit()
    return {"message": "Added to cart"}

@router.put("/api/cart/{item_id}")
def update_cart(item_id: int, req: CartItem, db: Session = Depends(get_db),
                current_user = Depends(get_current_user)):
    item = db.query(models.Cart).filter(
        models.Cart.id == item_id, models.Cart.customer_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = req.quantity
    db.commit()
    return {"message": "Updated"}

@router.delete("/api/cart/{item_id}")
def remove_from_cart(item_id: int, db: Session = Depends(get_db),
                     current_user = Depends(get_current_user)):
    item = db.query(models.Cart).filter(
        models.Cart.id == item_id, models.Cart.customer_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed"}

@router.delete("/api/cart")
def clear_cart(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db.query(models.Cart).filter(models.Cart.customer_id == current_user.id).delete()
    db.commit()
    return {"message": "Cart cleared"}

# ─── Wishlist ─────────────────────────────────────────────────────────────────

@router.get("/api/wishlist")
def get_wishlist(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    items = db.query(models.Wishlist).filter(models.Wishlist.customer_id == current_user.id).all()
    return [{"id": i.id, "product_id": i.product_id} for i in items]

@router.post("/api/wishlist")
def toggle_wishlist(req: CartItem, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    existing = db.query(models.Wishlist).filter(
        models.Wishlist.customer_id == current_user.id,
        models.Wishlist.product_id == req.product_id
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"action": "removed"}
    item = models.Wishlist(customer_id=current_user.id, product_id=req.product_id)
    db.add(item)
    db.commit()
    return {"action": "added"}

# ─── Reviews ─────────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    product_id: int
    order_id: int
    rating: int
    comment: str = ""

@router.post("/api/reviews")
def submit_review(req: ReviewCreate, db: Session = Depends(get_db),
                  current_user = Depends(get_current_user)):
    existing = db.query(models.Review).filter(
        models.Review.product_id == req.product_id,
        models.Review.customer_id == current_user.id,
        models.Review.order_id == req.order_id
    ).first()
    if existing:
        existing.rating = req.rating
        existing.comment = req.comment
        db.commit()
        return {"message": "Review updated"}
    review = models.Review(
        product_id=req.product_id, customer_id=current_user.id,
        order_id=req.order_id, rating=req.rating, comment=req.comment
    )
    db.add(review)
    db.commit()
    return {"message": "Review submitted"}

@router.get("/api/reviews/{product_id}")
def get_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(models.Review).filter(models.Review.product_id == product_id).all()
    return [{
        "id": r.id,
        "customer_name": r.customer.name if r.customer else "Customer",
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at.isoformat() if r.created_at else None
    } for r in reviews]

# ─── Coupon ───────────────────────────────────────────────────────────────────

class CouponValidate(BaseModel):
    code: str
    customer_id: Optional[int] = None

@router.post("/api/coupon/validate")
def validate_coupon(req: CouponValidate, db: Session = Depends(get_db),
                    current_user = Depends(get_current_user)):
    coupon = db.query(models.Coupon).filter(
        models.Coupon.code == req.code.upper(),
        models.Coupon.is_active == True
    ).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid or expired coupon")
    if coupon.is_first_order_only:
        existing_orders = db.query(models.Order).filter(
            models.Order.customer_id == current_user.id
        ).count()
        if existing_orders > 0:
            raise HTTPException(status_code=400, detail="Coupon valid for first order only")
    return {"code": coupon.code, "discount_percent": coupon.discount_percent,
            "message": f"{int(coupon.discount_percent)}% discount applied!"}

# ─── Analytics ────────────────────────────────────────────────────────────────

@router.get("/api/analytics/farmer")
def farmer_analytics(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "farmer":
        raise HTTPException(status_code=403, detail="Farmer access required")
    orders = db.query(models.Order).filter(models.Order.farmer_id == current_user.id).all()
    products = db.query(models.Product).filter(models.Product.farmer_id == current_user.id).all()
    total_revenue = sum(o.total_amount for o in orders)
    pending = sum(1 for o in orders if o.status in ["pending", "confirmed"])
    return {
        "total_revenue": round(total_revenue, 2),
        "total_orders": len(orders),
        "active_products": sum(1 for p in products if p.is_available),
        "pending_orders": pending,
        "recent_orders": [],
        "monthly_revenue": []
    }

# ─── Support ──────────────────────────────────────────────────────────────────

class SupportMsg(BaseModel):
    message: str

@router.post("/api/support/send")
def send_support(req: SupportMsg, db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    msg = models.SupportMessage(sender_id=current_user.id, message=req.message)
    db.add(msg)
    db.commit()
    return {"message": "Message sent"}

@router.get("/api/support/my-messages")
def my_messages(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    msgs = db.query(models.SupportMessage).filter(
        (models.SupportMessage.sender_id == current_user.id) |
        (models.SupportMessage.receiver_id == current_user.id)
    ).order_by(models.SupportMessage.created_at.asc()).all()
    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "sender_name": m.sender.name if m.sender else "",
        "message": m.message,
        "is_admin_reply": m.is_admin_reply,
        "is_read": m.is_read,
        "created_at": m.created_at.isoformat() if m.created_at else None
    } for m in msgs]

@router.get("/api/support/all")
def all_support(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    users_with_msgs = db.query(models.User).join(
        models.SupportMessage, models.User.id == models.SupportMessage.sender_id
    ).filter(models.User.role != "admin").distinct().all()
    result = []
    for user in users_with_msgs:
        msgs = db.query(models.SupportMessage).filter(
            (models.SupportMessage.sender_id == user.id) |
            (models.SupportMessage.receiver_id == user.id)
        ).all()
        unread = sum(1 for m in msgs if not m.is_read and not m.is_admin_reply)
        result.append({
            "user_id": user.id,
            "user_name": user.name,
            "user_email": user.email,
            "unread_count": unread,
            "last_message": msgs[-1].message if msgs else "",
        })
    return result

class AdminReply(BaseModel):
    user_id: int
    message: str

@router.post("/api/support/reply")
def admin_reply(req: AdminReply, db: Session = Depends(get_db),
                current_user = Depends(require_admin)):
    msg = models.SupportMessage(
        sender_id=current_user.id,
        receiver_id=req.user_id,
        message=req.message,
        is_admin_reply=True
    )
    db.add(msg)
    db.commit()
    return {"message": "Reply sent"}

@router.get("/api/support/conversation/{user_id}")
def get_conversation(user_id: int, db: Session = Depends(get_db),
                     current_user = Depends(require_admin)):
    msgs = db.query(models.SupportMessage).filter(
        (models.SupportMessage.sender_id == user_id) |
        (models.SupportMessage.receiver_id == user_id)
    ).order_by(models.SupportMessage.created_at.asc()).all()
    # Mark as read
    for m in msgs:
        if not m.is_admin_reply:
            m.is_read = True
    db.commit()
    return [{
        "id": m.id,
        "sender_id": m.sender_id,
        "sender_name": m.sender.name if m.sender else "",
        "message": m.message,
        "is_admin_reply": m.is_admin_reply,
        "created_at": m.created_at.isoformat() if m.created_at else None
    } for m in msgs]

@router.put("/api/support/mark-read/{user_id}")
def mark_read(user_id: int, db: Session = Depends(get_db),
              current_user = Depends(require_admin)):
    db.query(models.SupportMessage).filter(
        models.SupportMessage.sender_id == user_id,
        models.SupportMessage.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "Marked as read"}

# ─── Admin ────────────────────────────────────────────────────────────────────

@router.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    users = db.query(models.User).all()
    orders = db.query(models.Order).all()
    products = db.query(models.Product).all()
    return {
        "total_users": len(users),
        "farmers": sum(1 for u in users if u.role == "farmer"),
        "customers": sum(1 for u in users if u.role == "customer"),
        "total_products": len(products),
        "total_orders": len(orders),
        "total_revenue": round(sum(o.total_amount for o in orders), 2)
    }

@router.get("/api/admin/users")
def admin_users(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    users = db.query(models.User).all()
    return [{
        "id": u.id, "name": u.name, "email": u.email, "role": u.role,
        "location": u.location, "is_active": u.is_active,
        "phone": u.phone,
        "created_at": u.created_at.isoformat() if u.created_at else None
    } for u in users]

@router.put("/api/admin/users/{user_id}/toggle")
def toggle_user(user_id: int, db: Session = Depends(get_db),
                current_user = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot block admin")
    user.is_active = not user.is_active
    db.commit()
    return {"is_active": user.is_active}

@router.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db),
                current_user = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete admin")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.get("/api/admin/products")
def admin_products(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    products = db.query(models.Product).all()
    return [{
        "id": p.id, "name": p.name, "price": p.price, "quantity": p.quantity,
        "unit": p.unit, "is_available": p.is_available,
        "image_url": p.image_url,
        "category_name": p.category.name if p.category else "",
        "farmer_name": p.farmer.name if p.farmer else "",
        "farmer_id": p.farmer_id,
    } for p in products]

class AdminProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    is_available: Optional[bool] = None

@router.put("/api/admin/products/{product_id}")
def admin_update_product(product_id: int, req: AdminProductUpdate,
                          db: Session = Depends(get_db),
                          current_user = Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in req.dict(exclude_unset=True).items():
        if value is not None:
            setattr(product, field, value)
    db.commit()
    return {"message": "Updated"}

@router.delete("/api/admin/products/{product_id}")
def admin_delete_product(product_id: int, db: Session = Depends(get_db),
                          current_user = Depends(require_admin)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Deleted"}

class AdminProductCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    quantity: float
    unit: str = "kg"
    category_id: int
    farmer_id: int
    image_url: Optional[str] = None
    is_pre_harvest: bool = False
    demand_factor: float = 1.0

@router.post("/api/admin/products")
def admin_create_product(req: AdminProductCreate, db: Session = Depends(get_db),
                          current_user = Depends(require_admin)):
    from backend.image_engine import get_product_image
    from backend.ai_engine import get_ai_price
    
    if not req.image_url:
        cat = db.query(models.Category).filter(models.Category.id == req.category_id).first()
        img = get_product_image(req.name, cat.name if cat else "")
        image_url = img["url"]
    else:
        image_url = req.image_url
    
    farmer = db.query(models.User).filter(models.User.id == req.farmer_id).first()
    ai = get_ai_price(req.name, req.price, req.quantity, req.demand_factor,
                       req.is_pre_harvest, farmer.location if farmer else "")
    
    product = models.Product(
        name=req.name, description=req.description, price=req.price,
        ai_suggested_price=ai["suggested_price"],
        quantity=req.quantity, unit=req.unit, category_id=req.category_id,
        farmer_id=req.farmer_id, image_url=image_url,
        is_pre_harvest=req.is_pre_harvest, demand_factor=req.demand_factor
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "Product added", "id": product.id}

@router.get("/api/admin/farmers")
def admin_farmers(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    farmers = db.query(models.User).filter(models.User.role == "farmer").all()
    return [{"id": f.id, "name": f.name, "location": f.location} for f in farmers]
