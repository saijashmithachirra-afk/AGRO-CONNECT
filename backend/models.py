from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="customer")  # farmer/customer/admin
    phone = Column(String, default="")
    location = Column(String, default="")
    language = Column(String, default="en")
    is_active = Column(Boolean, default=True)
    profile_image = Column(String, default="")
    bank_account_no = Column(String, default="")
    bank_ifsc = Column(String, default="")
    bank_name = Column(String, default="")
    bank_holder_name = Column(String, default="")
    upi_id = Column(String, default="")
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="farmer", foreign_keys="Product.farmer_id")
    orders_as_customer = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    orders_as_farmer = relationship("Order", back_populates="farmer", foreign_keys="Order.farmer_id")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    name_hi = Column(String, default="")
    name_ta = Column(String, default="")
    name_te = Column(String, default="")
    icon = Column(String, default="🌿")

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    ai_suggested_price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    unit = Column(String, default="kg")
    category_id = Column(Integer, ForeignKey("categories.id"))
    farmer_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String, default="")
    is_pre_harvest = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    demand_factor = Column(Float, default=1.0)
    views = Column(Integer, default=0)
    harvest_date = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    farmer = relationship("User", back_populates="products", foreign_keys=[farmer_id])
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    farmer_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    coupon_code = Column(String, default="")
    status = Column(String, default="pending")
    payment_verified = Column(Boolean, default=False)
    payment_id = Column(String, default="")
    payment_method = Column(String, default="")
    delivery_address = Column(Text, default="")
    delivery_lat = Column(Float, default=0.0)
    delivery_lng = Column(Float, default=0.0)
    tracking_status = Column(String, default="")
    tracking_location = Column(String, default="")
    tracking_updated_at = Column(DateTime, default=datetime.utcnow)
    estimated_delivery = Column(String, default="")
    review_prompted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("User", back_populates="orders_as_customer", foreign_keys=[customer_id])
    farmer = relationship("User", back_populates="orders_as_farmer", foreign_keys=[farmer_id])
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=1.0)
    price_at_purchase = Column(Float, default=0.0)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer, default=5)
    comment = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Float, default=1.0)

    product = relationship("Product")

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    discount_percent = Column(Float, default=0.0)
    is_first_order_only = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

class SupportMessage(Base):
    __tablename__ = "support_messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    is_admin_reply = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
