import difflib

PHOTO_MAP = {
    "tomato": "photo-1546094096-0df4bcaaa337",
    "potato": "photo-1518977676601-b53f82aba655",
    "onion": "photo-1508747703725-719777637510",
    "garlic": "photo-1540148426945-6cf22a6b2383",
    "ginger": "photo-1593478428857-99a1c4dd3ea8",
    "spinach": "photo-1576045057995-568f588f82fb",
    "cabbage": "photo-1551754655-cd27e38d2076",
    "cauliflower": "photo-1568584711075-3d021a7c3ca3",
    "broccoli": "photo-1459411621453-7b03977f4bfc",
    "carrot": "photo-1598170845058-32b9d6a5da37",
    "radish": "photo-1597079910443-60c43fc4a729",
    "beetroot": "photo-1593105544559-ecb03bf76f82",
    "beet": "photo-1593105544559-ecb03bf76f82",
    "cucumber": "photo-1449300079323-02e209d9d3a6",
    "pumpkin": "photo-1570586437263-ab629fccc818",
    "bottle gourd": "photo-1518977822534-7049a61ee0c2",
    "lauki": "photo-1518977822534-7049a61ee0c2",
    "ridge gourd": "photo-1631207153680-0d0ec7a69caf",
    "bitter gourd": "photo-1631207153775-f0b69ef99948",
    "karela": "photo-1631207153775-f0b69ef99948",
    "lady finger": "photo-1601648764658-cf37e8c89b70",
    "okra": "photo-1601648764658-cf37e8c89b70",
    "bhindi": "photo-1601648764658-cf37e8c89b70",
    "eggplant": "photo-1613743983303-b3e89f8a2b80",
    "brinjal": "photo-1613743983303-b3e89f8a2b80",
    "baingan": "photo-1613743983303-b3e89f8a2b80",
    "capsicum": "photo-1563565375-f3fdfdbefa83",
    "bell pepper": "photo-1563565375-f3fdfdbefa83",
    "shimla mirch": "photo-1563565375-f3fdfdbefa83",
    "chilli": "photo-1583119022894-919a68a3d0e3",
    "green chilli": "photo-1583119022894-919a68a3d0e3",
    "mirch": "photo-1583119022894-919a68a3d0e3",
    "corn": "photo-1551754655-cd27e38d2076",
    "sweet corn": "photo-1551754655-cd27e38d2076",
    "peas": "photo-1592982537447-7440770cbfc9",
    "matar": "photo-1592982537447-7440770cbfc9",
    "beans": "photo-1567375698348-5d9d5ae99de0",
    "banana": "photo-1571771894821-ce9b6c11b08e",
    "kela": "photo-1571771894821-ce9b6c11b08e",
    "mango": "photo-1553279768-865429fa0078",
    "aam": "photo-1553279768-865429fa0078",
    "alphonso": "photo-1553279768-865429fa0078",
    "apple": "photo-1560806887-1e4cd0b6cbd6",
    "seb": "photo-1560806887-1e4cd0b6cbd6",
    "orange": "photo-1547514701-42782101795e",
    "santra": "photo-1547514701-42782101795e",
    "grapes": "photo-1537640538966-79f369143f8f",
    "angoor": "photo-1537640538966-79f369143f8f",
    "pomegranate": "photo-1541344999736-83eca272f6fc",
    "anar": "photo-1541344999736-83eca272f6fc",
    "papaya": "photo-1526318896980-cf78c088247c",
    "papita": "photo-1526318896980-cf78c088247c",
    "guava": "photo-1517282009859-f000ec3b26fe",
    "amrood": "photo-1517282009859-f000ec3b26fe",
    "watermelon": "photo-1563114773-84221bd62daa",
    "tarbooz": "photo-1563114773-84221bd62daa",
    "pineapple": "photo-1550258987-190a2d41a8ba",
    "coconut": "photo-1580984969071-a8da5656c2fb",
    "nariyal": "photo-1580984969071-a8da5656c2fb",
    "lemon": "photo-1587486913049-53fc88980cfc",
    "lime": "photo-1587486913049-53fc88980cfc",
    "nimbu": "photo-1587486913049-53fc88980cfc",
    "strawberry": "photo-1464965911861-746a04b4bca6",
    "rice": "photo-1586201375761-83865001e31c",
    "chawal": "photo-1586201375761-83865001e31c",
    "basmati": "photo-1536304993881-ff86e0c9b639",
    "wheat": "photo-1574323347407-f5e1ad6d020b",
    "gehu": "photo-1574323347407-f5e1ad6d020b",
    "maize": "photo-1551754655-cd27e38d2076",
    "jowar": "photo-1574323347407-f5e1ad6d020b",
    "bajra": "photo-1574323347407-f5e1ad6d020b",
    "ragi": "photo-1574323347407-f5e1ad6d020b",
    "dal": "photo-1515543904379-3d757dc1a93c",
    "lentil": "photo-1515543904379-3d757dc1a93c",
    "moong": "photo-1515543904379-3d757dc1a93c",
    "chana": "photo-1515543904379-3d757dc1a93c",
    "toor": "photo-1515543904379-3d757dc1a93c",
    "urad": "photo-1515543904379-3d757dc1a93c",
    "masoor": "photo-1515543904379-3d757dc1a93c",
    "rajma": "photo-1515543904379-3d757dc1a93c",
    "chickpea": "photo-1515543904379-3d757dc1a93c",
    "turmeric": "photo-1615485500704-8e990f9900f7",
    "haldi": "photo-1615485500704-8e990f9900f7",
    "cumin": "photo-1596040033229-a9821ebd058d",
    "jeera": "photo-1596040033229-a9821ebd058d",
    "coriander": "photo-1608831541541-b4a7a6a0a8c2",
    "dhania": "photo-1608831541541-b4a7a6a0a8c2",
    "cardamom": "photo-1596040033229-a9821ebd058d",
    "elaichi": "photo-1596040033229-a9821ebd058d",
    "black pepper": "photo-1596040033229-a9821ebd058d",
    "kali mirch": "photo-1596040033229-a9821ebd058d",
    "cinnamon": "photo-1569596082827-c7a1e4b0a7a3",
    "dalchini": "photo-1569596082827-c7a1e4b0a7a3",
    "milk": "photo-1550583724-b2692b85b150",
    "doodh": "photo-1550583724-b2692b85b150",
    "curd": "photo-1571091718767-18b5b1457add",
    "dahi": "photo-1571091718767-18b5b1457add",
    "paneer": "photo-1631452180519-c014fe946bc7",
    "ghee": "photo-1558642452-9d2a7deb7f62",
    "butter": "photo-1589985270826-4b7bb135bc9d",
    "makhan": "photo-1589985270826-4b7bb135bc9d",
    "mushroom": "photo-1518977956812-cd3dbadaaf31",
    "pear": "photo-1514756331096-242fdeb70d4a",
    "peach": "photo-1529084507571-3b0a75ea7a62",
    "plum": "photo-1566842600175-97dca3c5ad83",
    "litchi": "photo-1586093021955-c7d66e5e9bfb",
    "jackfruit": "photo-1602733670-2e45e8e5eed2",
    "tamarind": "photo-1564894809611-1742fc40ed80",
    "drumstick": "photo-1631207153680-0d0ec7a69caf",
    "moringa": "photo-1631207153680-0d0ec7a69caf",
}

CATEGORY_FALLBACKS = {
    "vegetables": "photo-1540420773420-3366772f4999",
    "fruits": "photo-1490885578174-acda8905c2c6",
    "grains": "photo-1586201375761-83865001e31c",
    "spices": "photo-1596040033229-a9821ebd058d",
    "dairy": "photo-1550583724-b2692b85b150",
    "pulses": "photo-1515543904379-3d757dc1a93c",
    "default": "photo-1540420773420-3366772f4999",
}

STOP_WORDS = {"fresh", "organic", "desi", "raw", "dried", "green", "red", "yellow",
               "black", "white", "baby", "mini", "big", "small", "large",
               "natural", "pure", "premium", "local", "seasonal"}

def get_unsplash_url(photo_id: str, width: int = 400) -> str:
    return f"https://images.unsplash.com/{photo_id}?w={width}&q=80&fit=crop&auto=format"

def get_product_image(name: str, category: str = "") -> dict:
    name_lower = name.lower().strip()

    # 1. Exact match
    if name_lower in PHOTO_MAP:
        return {"url": get_unsplash_url(PHOTO_MAP[name_lower]), "confidence": "high", "matched": name_lower}

    # 2. Strip stop words
    words = [w for w in name_lower.split() if w not in STOP_WORDS]
    stripped = " ".join(words)
    if stripped in PHOTO_MAP:
        return {"url": get_unsplash_url(PHOTO_MAP[stripped]), "confidence": "high", "matched": stripped}

    # 3. Word-by-word match
    for word in words:
        if word in PHOTO_MAP:
            return {"url": get_unsplash_url(PHOTO_MAP[word]), "confidence": "medium", "matched": word}

    # 4. Two-word combo match
    for i in range(len(words) - 1):
        combo = f"{words[i]} {words[i+1]}"
        if combo in PHOTO_MAP:
            return {"url": get_unsplash_url(PHOTO_MAP[combo]), "confidence": "medium", "matched": combo}

    # 5. Fuzzy match
    all_keys = list(PHOTO_MAP.keys())
    matches = difflib.get_close_matches(name_lower, all_keys, n=1, cutoff=0.70)
    if not matches:
        matches = difflib.get_close_matches(stripped, all_keys, n=1, cutoff=0.65)
    if matches:
        return {"url": get_unsplash_url(PHOTO_MAP[matches[0]]), "confidence": "low", "matched": matches[0]}

    # 6. Category fallback
    cat_lower = category.lower()
    for cat_key, photo_id in CATEGORY_FALLBACKS.items():
        if cat_key in cat_lower:
            return {"url": get_unsplash_url(photo_id), "confidence": "category", "matched": cat_key}

    # 7. Default
    return {"url": get_unsplash_url(CATEGORY_FALLBACKS["default"]), "confidence": "default", "matched": "default"}
