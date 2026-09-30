from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random
import string

from backend.database import get_db
from backend import models
from backend.auth import get_current_user, require_farmer, require_admin

router = APIRouter(prefix="/api/orders", tags=["orders"])

class OrderItemIn(BaseModel):
    product_id: int
    quantity: float
    price_at_purchase: float

class OrderCreate(BaseModel):
    items: List[OrderItemIn]
    total_amount: float
    discount_amount: float = 0.0
    coupon_code: str = ""
    payment_method: str = "cod"
    payment_id: str = ""
    delivery_address: str
    delivery_lat: float = 0.0
    delivery_lng: float = 0.0

class StatusUpdate(BaseModel):
    status: str
    tracking_location: str = ""

def order_to_dict(o: models.Order):
    estimated = (o.created_at + timedelta(days=3)).strftime("%Y-%m-%d") if o.created_at else ""
    return {
        "id": o.id,
        "customer_id": o.customer_id,
        "customer_name": o.customer.name if o.customer else "",
        "farmer_id": o.farmer_id,
        "farmer_name": o.farmer.name if o.farmer else "",
        "total_amount": o.total_amount,
        "discount_amount": o.discount_amount,
        "coupon_code": o.coupon_code,
        "status": o.status,
        "payment_verified": o.payment_verified,
        "payment_id": o.payment_id,
        "payment_method": o.payment_method,
        "delivery_address": o.delivery_address,
        "delivery_lat": o.delivery_lat,
        "delivery_lng": o.delivery_lng,
        "tracking_status": o.tracking_status,
        "tracking_location": o.tracking_location,
        "tracking_updated_at": o.tracking_updated_at.isoformat() if o.tracking_updated_at else None,
        "estimated_delivery": o.estimated_delivery or estimated,
        "review_prompted": o.review_prompted,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "",
                "product_image": item.product.image_url if item.product else "",
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase
            }
            for item in o.items
        ]
    }

@router.post("/")
def create_order(req: OrderCreate, db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    if current_user.role not in ["customer", "admin"]:
        raise HTTPException(status_code=403, detail="Customer access required")
    
    if not req.delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address required")
    
    # Determine farmer from first item
    farmer_id = None
    for item_in in req.items:
        product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
        if product:
            farmer_id = product.farmer_id
            break
    
    payment_id = req.payment_id or "PAY_" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    estimated = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    order = models.Order(
        customer_id=current_user.id,
        farmer_id=farmer_id,
        total_amount=req.total_amount,
        discount_amount=req.discount_amount,
        coupon_code=req.coupon_code,
        status="confirmed",
        payment_verified=(req.payment_method != "cod"),
        payment_id=payment_id,
        payment_method=req.payment_method,
        delivery_address=req.delivery_address,
        delivery_lat=req.delivery_lat,
        delivery_lng=req.delivery_lng,
        tracking_status="Order Placed",
        tracking_location="Warehouse",
        estimated_delivery=estimated
    )
    db.add(order)
    db.flush()
    
    for item_in in req.items:
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            price_at_purchase=item_in.price_at_purchase
        )
        db.add(order_item)
        # Reduce quantity
        product = db.query(models.Product).filter(models.Product.id == item_in.product_id).first()
        if product:
            product.quantity = max(0, product.quantity - item_in.quantity)
    
    db.commit()
    db.refresh(order)
    return order_to_dict(order)

@router.get("/my-orders")
def my_orders(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    orders = db.query(models.Order).filter(
        models.Order.customer_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()
    return [order_to_dict(o) for o in orders]

@router.get("/farmer/received")
def farmer_orders(db: Session = Depends(get_db), current_user = Depends(require_farmer)):
    orders = db.query(models.Order).filter(
        models.Order.farmer_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()
    return [order_to_dict(o) for o in orders]

@router.get("/admin/all")
def admin_all_orders(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    orders = db.query(models.Order).order_by(models.Order.created_at.desc()).all()
    return [order_to_dict(o) for o in orders]

@router.get("/{order_id}/tracking")
def get_tracking(order_id: int, db: Session = Depends(get_db),
                 current_user = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    steps = ["pending", "confirmed", "shipped", "out_for_delivery", "delivered"]
    step_labels = ["Order Placed", "Confirmed", "Shipped", "Out for Delivery", "Delivered"]
    current_step = 0
    for i, s in enumerate(steps):
        if order.status == s:
            current_step = i
            break
    
    return {
        "order_id": order.id,
        "status": order.status,
        "steps": [{"key": s, "label": l, "done": i <= current_step}
                  for i, (s, l) in enumerate(zip(steps, step_labels))],
        "current_step": current_step,
        "tracking_location": order.tracking_location,
        "tracking_updated_at": order.tracking_updated_at.isoformat() if order.tracking_updated_at else None,
        "delivery_address": order.delivery_address,
        "delivery_lat": order.delivery_lat,
        "delivery_lng": order.delivery_lng,
        "estimated_delivery": order.estimated_delivery,
        "payment_method": order.payment_method,
        "payment_verified": order.payment_verified,
    }

@router.put("/{order_id}/status")
def update_status(order_id: int, req: StatusUpdate, db: Session = Depends(get_db),
                  current_user = Depends(require_farmer)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.farmer_id == current_user.id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = req.status
    order.tracking_status = req.status.replace("_", " ").title()
    if req.tracking_location:
        order.tracking_location = req.tracking_location
    order.tracking_updated_at = datetime.utcnow()
    db.commit()
    return order_to_dict(order)

@router.post("/{order_id}/verify-payment")
def verify_payment(order_id: int, db: Session = Depends(get_db),
                   current_user = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.payment_verified = True
    db.commit()
    return {"message": "Payment verified"}

@router.post("/{order_id}/prompt-review")
def prompt_review(order_id: int, db: Session = Depends(get_db),
                  current_user = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.review_prompted = True
    db.commit()
    return {"message": "Review prompted"}
