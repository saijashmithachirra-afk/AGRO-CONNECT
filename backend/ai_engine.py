from datetime import datetime

MARKET_PRICES = {
    "tomato": 30, "potato": 20, "onion": 25, "garlic": 120, "ginger": 100,
    "spinach": 40, "cabbage": 20, "cauliflower": 30, "broccoli": 60,
    "carrot": 35, "radish": 20, "beetroot": 30, "cucumber": 25, "pumpkin": 18,
    "bottle gourd": 20, "ridge gourd": 25, "bitter gourd": 40, "lady finger": 35,
    "okra": 35, "eggplant": 25, "brinjal": 25, "capsicum": 60, "chilli": 80,
    "green chilli": 60, "corn": 20, "sweet corn": 30, "peas": 60, "beans": 50,
    "cluster beans": 40, "banana": 25, "mango": 80, "apple": 120, "orange": 60,
    "grapes": 80, "pomegranate": 120, "papaya": 30, "guava": 40, "watermelon": 15,
    "pineapple": 40, "coconut": 35, "lemon": 60, "lime": 50, "strawberry": 200,
    "rice": 45, "wheat": 22, "basmati rice": 80, "jowar": 25, "bajra": 22,
    "maize": 18, "barley": 28, "oats": 50, "ragi": 35, "quinoa": 250,
    "dal": 80, "lentil": 90, "moong dal": 85, "chana dal": 70, "toor dal": 90,
    "urad dal": 95, "masoor dal": 80, "rajma": 100, "chickpeas": 75, "soybean": 40,
    "turmeric": 150, "cumin": 200, "coriander": 120, "cardamom": 1200,
    "cloves": 600, "black pepper": 500, "cinnamon": 300, "fenugreek": 80,
    "mustard seeds": 60, "ajwain": 150, "saffron": 3000, "fennel": 100,
    "milk": 55, "curd": 60, "paneer": 280, "ghee": 500, "butter": 400,
    "cheese": 350, "cream": 200, "lassi": 40, "buttermilk": 30,
    "fresh tomatoes": 30, "organic potatoes": 25, "alphonso mangoes": 150,
    "fresh spinach": 40, "alphonso mango": 150,
}

LOCATION_FACTORS = {
    "mumbai": 1.25, "delhi": 1.15, "bangalore": 1.20, "bengaluru": 1.20,
    "chennai": 1.10, "hyderabad": 1.12, "pune": 1.15, "kolkata": 1.08,
    "ahmedabad": 1.05, "surat": 1.05, "jaipur": 1.00, "lucknow": 0.98,
    "chandigarh": 1.02, "punjab": 0.92, "haryana": 0.94, "gujarat": 0.96,
    "maharashtra": 1.18, "karnataka": 1.10, "tamil nadu": 1.08,
    "andhra pradesh": 1.00, "telangana": 1.05, "rajasthan": 0.95,
    "uttar pradesh": 0.95, "bihar": 0.88, "west bengal": 1.02,
    "kerala": 1.12, "goa": 1.20, "default": 1.00
}

SEASONAL_PRICES = {
    "mango": {4: 1.0, 5: 0.85, 6: 0.75, 7: 0.80, 8: 0.90, 9: 1.3, 10: 1.5, 11: 1.6, 12: 1.7, 1: 1.8, 2: 1.7, 3: 1.3},
    "tomato": {1: 1.2, 2: 1.1, 3: 0.9, 4: 0.85, 5: 0.8, 6: 1.1, 7: 1.3, 8: 1.4, 9: 1.2, 10: 1.0, 11: 1.0, 12: 1.1},
    "onion": {1: 1.3, 2: 1.4, 3: 1.2, 4: 0.8, 5: 0.7, 6: 0.8, 7: 0.9, 8: 1.0, 9: 1.1, 10: 1.0, 11: 0.9, 12: 1.1},
    "strawberry": {11: 1.0, 12: 0.9, 1: 0.85, 2: 0.9, 3: 1.1, 4: 1.4, 5: 1.6, 6: 1.8, 7: 2.0, 8: 1.9, 9: 1.7, 10: 1.3},
}

def get_ai_price(product_name: str, current_price: float, quantity: float,
                 demand_factor: float, is_pre_harvest: bool, location: str):
    name_lower = product_name.lower().strip()
    month = datetime.now().month

    market_price = None
    for key, price in MARKET_PRICES.items():
        if key in name_lower or name_lower in key:
            market_price = price
            break

    if market_price is None:
        market_price = current_price * 0.85 if current_price > 0 else 50.0

    loc_lower = location.lower().strip() if location else "default"
    location_factor = 1.0
    location_label = location or "India"
    for loc, factor in LOCATION_FACTORS.items():
        if loc in loc_lower or loc_lower in loc:
            location_factor = factor
            location_label = loc.title()
            break

    seasonal_factor = 1.0
    for crop, seasons in SEASONAL_PRICES.items():
        if crop in name_lower:
            seasonal_factor = seasons.get(month, 1.0)
            break

    demand_mult = 0.8 + (demand_factor * 0.4)
    pre_harvest_discount = 0.9 if is_pre_harvest else 1.0

    suggested = round(market_price * location_factor * seasonal_factor * demand_mult * pre_harvest_discount, 1)

    price_low = round(suggested * 0.85, 1)
    price_high = round(suggested * 1.20, 1)

    reasons = []
    if location_factor > 1.05:
        reasons.append(f"📍 Urban market premium ({location_label})")
    elif location_factor < 0.95:
        reasons.append(f"📍 Rural farm-gate price ({location_label})")
    if seasonal_factor < 0.9:
        reasons.append("🌸 Peak season — supply high")
    elif seasonal_factor > 1.2:
        reasons.append("❄️ Off-season — premium pricing")
    if demand_factor > 1.2:
        reasons.append("📈 High demand detected")
    elif demand_factor < 0.8:
        reasons.append("📉 Low demand — consider reducing")
    if is_pre_harvest:
        reasons.append("🌱 Pre-harvest discount applied")
    if quantity > 500:
        reasons.append("📦 Bulk quantity — competitive rate")
    if not reasons:
        reasons.append("✅ Market-aligned pricing")

    insight = f"Based on current Indian mandi rates for {product_name}, adjusted for {location_label} market conditions."

    confidence = "High" if market_price else "Medium"

    return {
        "suggested_price": suggested,
        "market_price": market_price,
        "price_range": {"low": price_low, "high": price_high},
        "location_label": location_label,
        "location_factor": location_factor,
        "seasonal_factor": seasonal_factor,
        "demand_factor": demand_factor,
        "reasons": reasons,
        "confidence": confidence,
        "insight": insight
    }
