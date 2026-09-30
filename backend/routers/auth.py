from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import random
import time

from backend.database import get_db
from backend import models
from backend.auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory OTP store: {email: {"otp": str, "data": dict, "expires": float}}
otp_store = {}

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str = "customer"
    location: str = ""

class OTPRequest(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str = "customer"
    location: str = ""

class OTPVerify(BaseModel):
    email: str
    otp: str

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = None
    profile_image: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_name: Optional[str] = None
    bank_holder_name: Optional[str] = None
    upi_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

def user_to_dict(user: models.User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "phone": user.phone,
        "location": user.location,
        "language": user.language,
        "is_active": user.is_active,
        "profile_image": user.profile_image,
        "bank_account_no": user.bank_account_no,
        "bank_ifsc": user.bank_ifsc,
        "bank_name": user.bank_name,
        "bank_holder_name": user.bank_holder_name,
        "upi_id": user.upi_id,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        name=req.name, email=req.email, phone=req.phone,
        password=get_password_hash(req.password),
        role=req.role, location=req.location
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user_to_dict(user)}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account has been blocked")
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user_to_dict(user)}

@router.post("/send-otp")
def send_otp(req: OTPRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    otp = str(random.randint(100000, 999999))
    otp_store[req.email] = {
        "otp": otp,
        "data": req.dict(),
        "expires": time.time() + 600  # 10 minutes
    }
    print(f"\n{'='*40}\nOTP for {req.email}: {otp}\n{'='*40}\n")
    return {"message": "OTP sent successfully", "otp_demo": otp}

@router.post("/verify-otp")
def verify_otp(req: OTPVerify, db: Session = Depends(get_db)):
    stored = otp_store.get(req.email)
    if not stored:
        raise HTTPException(status_code=400, detail="No OTP found. Please request again.")
    if time.time() > stored["expires"]:
        del otp_store[req.email]
        raise HTTPException(status_code=400, detail="OTP expired. Please request again.")
    if stored["otp"] != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    data = stored["data"]
    del otp_store[req.email]
    
    user = models.User(
        name=data["name"], email=data["email"], phone=data["phone"],
        password=get_password_hash(data["password"]),
        role=data["role"], location=data.get("location", "")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user_to_dict(user), "message": "Registration successful"}

@router.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return user_to_dict(current_user)

@router.put("/profile")
def update_profile(req: ProfileUpdate, db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == current_user.id).first()
    for field, value in req.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user_to_dict(user)

@router.post("/upload-profile-image")
async def upload_profile_image(db: Session = Depends(get_db),
                                current_user: models.User = Depends(get_current_user)):
    # For demo, just return a placeholder
    return {"image_url": f"https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&q=80&fit=crop&auto=format"}
