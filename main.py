import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, SessionLocal, Base
from backend import models
from backend.auth import get_password_hash
from backend.routers import auth, products, orders, misc

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgroConnect")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(misc.router)

# Static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# ─── Seed Data ────────────────────────────────────────────────────────────────

def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.User).count() > 0:
            return

        # Categories
        cats = [
            models.Category(name="Vegetables", name_hi="सब्जियां", name_ta="காய்கறிகள்", name_te="కూరగాయలు", icon="🥦"),
            models.Category(name="Fruits", name_hi="फल", name_ta="பழங்கள்", name_te="పండ్లు", icon="🍎"),
            models.Category(name="Grains", name_hi="अनाज", name_ta="தானியங்கள்", name_te="ధాన్యాలు", icon="🌾"),
            models.Category(name="Spices", name_hi="मसाले", name_ta="மசாலாப் பொருட்கள்", name_te="సుగంధ ద్రవ్యాలు", icon="🌶️"),
            models.Category(name="Dairy", name_hi="डेयरी", name_ta="பால் பொருட்கள்", name_te="పాల ఉత్పత్తులు", icon="🥛"),
            models.Category(name="Pulses", name_hi="दालें", name_ta="பருப்பு வகைகள்", name_te="పప్పుధాన్యాలు", icon="🫘"),
        ]
        for c in cats:
            db.add(c)
        db.flush()

        cat_veg = cats[0]
        cat_fruit = cats[1]
        cat_grain = cats[2]

        # Users
        admin = models.User(
            name="Admin User", email="admin@agroconnect.com",
            password=get_password_hash("admin123"), role="admin",
            phone="9000000001", location="Mumbai"
        )
        farmer1 = models.User(
            name="Ranjit Singh", email="farmer@agroconnect.com",
            password=get_password_hash("farmer123"), role="farmer",
            phone="9000000002", location="Punjab",
            bank_account_no="123456789012", bank_ifsc="PUNB0123456",
            bank_name="Punjab National Bank", bank_holder_name="Ranjit Singh",
            upi_id="ranjit@upi"
        )
        farmer2 = models.User(
            name="Priya Patel", email="farmer2@agroconnect.com",
            password=get_password_hash("farmer123"), role="farmer",
            phone="9000000003", location="Gujarat",
            bank_account_no="987654321098", bank_ifsc="SBIN0987654",
            bank_name="State Bank of India", bank_holder_name="Priya Patel",
            upi_id="priya@upi"
        )
        customer = models.User(
            name="Amit Kumar", email="customer@agroconnect.com",
            password=get_password_hash("customer123"), role="customer",
            phone="9000000004", location="Delhi"
        )
        for u in [admin, farmer1, farmer2, customer]:
            db.add(u)
        db.flush()

        # Products
        products_data = [
            {
                "name": "Fresh Tomatoes", "description": "Farm-fresh red tomatoes, organically grown",
                "price": 35, "quantity": 200, "unit": "kg", "category_id": cat_veg.id,
                "farmer_id": farmer1.id,
                "image_url": "https://images.unsplash.com/photo-1546094096-0df4bcaaa337?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 1.2
            },
            {
                "name": "Organic Potatoes", "description": "Organic potatoes from Punjab farms",
                "price": 22, "quantity": 500, "unit": "kg", "category_id": cat_veg.id,
                "farmer_id": farmer1.id,
                "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 1.0
            },
            {
                "name": "Alphonso Mangoes", "description": "Premium Alphonso mangoes from Ratnagiri",
                "price": 180, "quantity": 100, "unit": "kg", "category_id": cat_fruit.id,
                "farmer_id": farmer2.id,
                "image_url": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 1.5, "is_pre_harvest": True
            },
            {
                "name": "Basmati Rice", "description": "Long grain aged basmati rice from Punjab",
                "price": 90, "quantity": 1000, "unit": "kg", "category_id": cat_grain.id,
                "farmer_id": farmer1.id,
                "image_url": "https://images.unsplash.com/photo-1536304993881-ff86e0c9b639?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 1.1
            },
            {
                "name": "Fresh Spinach", "description": "Tender green spinach leaves, freshly harvested",
                "price": 45, "quantity": 80, "unit": "kg", "category_id": cat_veg.id,
                "farmer_id": farmer2.id,
                "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 0.9
            },
            {
                "name": "Bananas", "description": "Ripe yellow bananas, rich in potassium",
                "price": 30, "quantity": 300, "unit": "kg", "category_id": cat_fruit.id,
                "farmer_id": farmer2.id,
                "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&q=80&fit=crop&auto=format",
                "demand_factor": 1.0
            },
        ]
        for pd in products_data:
            p = models.Product(**pd, ai_suggested_price=pd["price"] * 1.05)
            db.add(p)

        # Coupon
        coupon = models.Coupon(code="FIRST25", discount_percent=25, is_first_order_only=True, is_active=True)
        db.add(coupon)

        db.commit()
        print("✅ Seed data created successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Seed error: {e}")
    finally:
        db.close()

seed_data()

# ─── Page Routes ──────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/marketplace", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse("marketplace.html", {"request": request})

@app.get("/farmer-dashboard", response_class=HTMLResponse)
async def farmer_dashboard(request: Request):
    return templates.TemplateResponse("farmer_dashboard.html", {"request": request})

@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
