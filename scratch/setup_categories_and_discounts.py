import sqlite3, json

conn = sqlite3.connect('database/hiramoti.db')
cur = conn.cursor()

# 1. Create categories table
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    marathi_name TEXT,
    slug TEXT UNIQUE NOT NULL,
    icon TEXT,
    tag TEXT,
    display_order INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Default categories
default_categories = [
    ("all", "All Collections", "सर्व कलेक्शन्स", "all", "✨", "50+ Styles", 1, 1),
    ("jackets", "Bomber & TPU Jackets", "बॉम्बर व टीपीयू जॅकेट्स", "jackets", "🧥", "From ₹399", 2, 1),
    ("shirts", "Cotton & Printed Shirts", "कॉटन व प्रिंटेड शर्ट्स", "shirts", "👔", "₹799", 3, 1),
    ("casual", "T-Shirts & Track Combos", "टी-शर्ट व ट्रॅक कॉम्बो", "casual", "👕", "3 for ₹800", 4, 1),
    ("denim", "Denim & Trousers", "डेनिम व ट्राउझर्स", "denim", "👖", "M to 3XL", 5, 1),
    ("ethnic", "Festive & Ethnic Wear", "पारंपरिक व सणासुदीचे कपडे", "ethnic", "👑", "Royal", 6, 1),
    ("technosport", "TechnoSport", "टेक्नोस्पोर्ट", "technosport", "⚡", "10% OFF", 7, 1),
    ("hosiery", "Hosiery", "होझियरी", "hosiery", "🧦", "Essentials", 8, 1),
]

for cat in default_categories:
    cur.execute("""
    INSERT OR REPLACE INTO categories (id, name, marathi_name, slug, icon, tag, display_order, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, cat)

# 2. Create promotional_rules table
cur.execute("""
CREATE TABLE IF NOT EXISTS promotional_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_value TEXT NOT NULL,
    discount_type TEXT DEFAULT 'percentage',
    discount_value REAL NOT NULL,
    start_date TEXT,
    end_date TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Default TechnoSport 10% promotional rule
cur.execute("""
INSERT OR REPLACE INTO promotional_rules (id, name, target_type, target_value, discount_type, discount_value, start_date, end_date, is_active)
VALUES (
    'RULE-TECHNO-10',
    'TechnoSport 10% Promotional Discount',
    'category',
    'technosport',
    'percentage',
    10.0,
    '2026-01-01',
    '2027-12-31',
    1
)
""")

# 3. Add initial verified TechnoSport and Hosiery products if not already present
initial_products = [
    # TechnoSport
    (
        "HM-TS-01", "HM-TS-01", "TechnoSport O-Dry Active Training T-Shirt", "टेक्नोस्पोर्ट ट्रेनिंग टी-शर्ट",
        "technosport", "technosport", 539.0, 599.0, "10% OFF", "10% OFF",
        "Engineered with O-Dry micro-filament technology, UPF 50+ UV shield, and anti-static sweat management. Superior comfort for gym, running, and daily active lifestyle.",
        "M, L, XL, XXL", "assets/images/real_store_shirts.jpg", "", 25, "in_stock", 1, 13
    ),
    (
        "HM-TS-02", "HM-TS-02", "TechnoSport Performance Stretch Track Pant", "टेक्नोस्पोर्ट ट्रॅक पॅन्ट",
        "technosport", "technosport", 899.0, 999.0, "10% OFF", "10% OFF",
        "4-way stretch techno-performance fabric with breathable knee vents and secure brass zip pockets. Engineered for athletic movement and Satara travel comfort.",
        "M, L, XL, XXL", "assets/images/real_store_jeans.jpg", "", 18, "in_stock", 1, 14
    ),
    (
        "HM-TS-03", "HM-TS-03", "TechnoSport Breathable Honeycomb Polo Tee", "टेक्नोस्पोर्ट पोलो टी-शर्ट",
        "technosport", "technosport", 719.0, 799.0, "10% OFF", "10% OFF",
        "Quick-cool honeycomb jacquard knit with ribbed collar and anti-pilling wash resistance. Sporty elegance tailored for distinguished active gentlemen.",
        "L, XL, XXL", "assets/images/real_store_center.jpg", "", 14, "in_stock", 1, 15
    ),
    # Hosiery
    (
        "HM-HOS-01", "HM-HOS-01", "Hiramoti Combed Cotton Cushion Crew Socks (Pack of 3)", "कॉटन सॉक्स (३ पॅक)",
        "hosiery", "hosiery", 249.0, 349.0, "29% OFF", "Pack of 3",
        "100% pure combed cotton with reinforced heel and toe cushioning. Odour-resistant breathable weave designed for all-day comfort.",
        "Free Size", "assets/images/real_store_shirts.jpg", "", 40, "in_stock", 1, 16
    ),
    (
        "HM-HOS-02", "HM-HOS-02", "Premium Ribbed Cotton Gym Vest (Pack of 2)", "कॉटन जिम बनियान (२ पॅक)",
        "hosiery", "hosiery", 399.0, 499.0, "20% OFF", "Pack of 2",
        "Super-soft combed cotton 1x1 rib knit vest with contoured sweat-absorbing armholes and flat seams for smooth inner comfort under shirts.",
        "80cm, 85cm, 90cm, 95cm, 100cm", "assets/images/real_store_shirts.jpg", "", 30, "in_stock", 1, 17
    ),
    (
        "HM-HOS-03", "HM-HOS-03", "All-Day Soft Touch Modal Stretch Trunk", "सॉफ्ट मोडल ट्रंक",
        "hosiery", "hosiery", 299.0, 399.0, "25% OFF", "Ultra Soft",
        "Micro-modal luxury stretch trunk with anti-chafing ergonomic pouch and brushed microfiber waistband. Unbeatable softness all day long.",
        "M, L, XL, XXL", "assets/images/real_store_jeans.jpg", "", 22, "in_stock", 1, 18
    ),
]

for p in initial_products:
    cur.execute("""
    INSERT OR REPLACE INTO products (
        id, code, name, marathi_name, category, subtype, price, original_price,
        discount, badge, description, sizes, image, reel_url, stock, status, is_featured, display_order
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, p)
    # Ensure primary image in product_images
    cur.execute("DELETE FROM product_images WHERE product_id = ?", (p[0],))
    cur.execute("INSERT INTO product_images (product_id, image_url, is_primary) VALUES (?, ?, 1)", (p[0], p[12]))

conn.commit()
conn.close()
print("Categories, promotional rules, and initial TechnoSport & Hosiery products successfully seeded!")
