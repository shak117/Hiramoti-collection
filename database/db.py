"""
Hiramoti Collection, Satara — SQLite Database Module & Seeder
Provides connection management, schema initialization, and initial seed data.
"""

import os
import sqlite3
import json
from werkzeug.security import generate_password_hash

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "hiramoti.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and seeds initial data if empty."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Admin Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            code TEXT,
            name TEXT NOT NULL,
            marathi_name TEXT,
            category TEXT NOT NULL,
            subtype TEXT NOT NULL,
            price REAL NOT NULL,
            original_price REAL,
            discount TEXT,
            badge TEXT,
            description TEXT,
            sizes TEXT,
            image TEXT,
            reel_url TEXT,
            stock INTEGER DEFAULT 15,
            status TEXT DEFAULT 'in_stock',
            is_featured INTEGER DEFAULT 0,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Product Images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            image_url TEXT NOT NULL,
            is_primary INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    """)

    # 4. Reels table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reels (
            id TEXT PRIMARY KEY,
            code TEXT,
            url TEXT NOT NULL,
            embed_url TEXT NOT NULL,
            title TEXT NOT NULL,
            marathi_title TEXT,
            caption TEXT,
            price TEXT,
            offer TEXT,
            category TEXT,
            image TEXT,
            display_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Gallery Items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gallery_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            subtitle TEXT,
            category TEXT NOT NULL,
            is_wide INTEGER DEFAULT 0,
            image TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 6. Customer Enquiries / Appointments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            area TEXT,
            visit_date TEXT,
            time_slot TEXT,
            style_interest TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Website Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    # Ensure reels table has video_url column
    try:
        cursor.execute("ALTER TABLE reels ADD COLUMN video_url TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()

    # Seed Admin User if none exists
    cursor.execute("SELECT COUNT(*) FROM admin_users")
    if cursor.fetchone()[0] == 0:
        default_pwd_hash = generate_password_hash("Hiramoti@1987", method="pbkdf2:sha256")
        cursor.execute("""
            INSERT INTO admin_users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("admin", "admin@hiramoti.com", default_pwd_hash, "superadmin"))
        print("[DB] Initialized default admin user (admin@hiramoti.com)")

    # Seed Products if none exists
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        seed_products = [
            {
                "id": "HM-JKT-01",
                "code": "HM-JKT-01",
                "name": "Dual-Tone Reversible Bomber Jacket",
                "marathi_name": "रिव्हर्सिबल बॉम्बर जॅकेट",
                "category": "mens",
                "subtype": "jackets",
                "price": 699,
                "original_price": 1299,
                "discount": "46% OFF",
                "badge": "Viral Reel",
                "image": "assets/images/real_reel_DaiL4H0zCqV.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DaiL4H0zCqV/",
                "description": "Featured in our viral Instagram reel! Reversible 2-in-1 bomber jacket with storm-rib cuffs, brass zippers, and deep pockets.",
                "sizes": "M, L, XL, XXL",
                "stock": 18,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 1
            },
            {
                "id": "HM-JKT-02",
                "code": "HM-JKT-02",
                "name": "TPU Weatherproof Windcheater Jacket",
                "marathi_name": "टीपीयू ऑल-वेदर जॅकेट",
                "category": "mens",
                "subtype": "jackets",
                "price": 399,
                "original_price": 799,
                "discount": "50% OFF",
                "badge": "Mega Offer",
                "image": "assets/images/real_reel_Dcp2loUTRWp.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/Dcp2loUTRWp/",
                "description": "Special offer ₹399/- only! Wind and rain resistant TPU lightweight jacket, ideal for Satara rides and travel wear.",
                "sizes": "M, L, XL",
                "stock": 24,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 2
            },
            {
                "id": "HM-JKT-03",
                "code": "HM-JKT-03",
                "name": "Imported Premium Leather Jacket",
                "marathi_name": "इम्पोर्टेड लेदर जॅकेट (६ कलर्स)",
                "category": "mens",
                "subtype": "jackets",
                "price": 1499,
                "original_price": 2499,
                "discount": "40% OFF",
                "badge": "Imported",
                "image": "assets/images/real_reel_DcX8iP-zOb_.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DcX8iP-zOb_/",
                "description": "Top-grade imported leather jacket available in 6 stunning shades. Premium metal hardware with satin inner lining.",
                "sizes": "M, L, XL, XXL",
                "stock": 10,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 3
            },
            {
                "id": "HM-SHT-01",
                "code": "HM-SHT-01",
                "name": "Executive Cotton Double-Pocket Branded Shirt",
                "marathi_name": "डबल पॉकेट कॉटन ब्रँडेड शर्ट",
                "category": "mens",
                "subtype": "formal_shirts",
                "price": 799,
                "original_price": 1299,
                "discount": "38% OFF",
                "badge": "Reel Bestseller",
                "image": "assets/images/real_reel_DcqiOSIzvCQ.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DcqiOSIzvCQ/",
                "description": "Available from M to 3XL! Heavy-duty pure cotton, structured collar, and utility double pockets.",
                "sizes": "M, L, XL, XXL, 3XL",
                "stock": 35,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 4
            },
            {
                "id": "HM-SHT-02",
                "code": "HM-SHT-02",
                "name": "Signature Restocked Favourite Cotton Shirt",
                "marathi_name": "फेव्हरेट कॉटन शर्ट री-स्टॉक",
                "category": "mens",
                "subtype": "formal_shirts",
                "price": 799,
                "original_price": 1199,
                "discount": "33% OFF",
                "badge": "Restocked",
                "image": "assets/images/real_reel_DdL4HYAzqZK.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DdL4HYAzqZK/",
                "description": "Satara's favorite shirt back in stock! Soft breathable fabric, wrinkle-resistant twill finish.",
                "sizes": "38, 40, 42, 44",
                "stock": 28,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 5
            },
            {
                "id": "HM-SHT-03",
                "code": "HM-SHT-03",
                "name": "Trendy Cuban-Collar Printed Half Shirt",
                "marathi_name": "क्युबन कॉलर प्रिंटेड हाफ शर्ट",
                "category": "mens",
                "subtype": "party_wear",
                "price": 799,
                "original_price": 1299,
                "discount": "38% OFF",
                "badge": "Trending",
                "image": "assets/images/real_reel_Dcd2dn2NKZ9.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/Dcd2dn2NKZ9/",
                "description": "Hundreds of fresh prints! Relaxed holiday and party fit, double-washed pure cotton.",
                "sizes": "M, L, XL",
                "stock": 20,
                "status": "in_stock",
                "is_featured": 0,
                "display_order": 6
            },
            {
                "id": "HM-CAS-01",
                "code": "HM-CAS-01",
                "name": "Ganesh Utsav Combo: T-Shirt & Track Pant (3 for ₹800)",
                "marathi_name": "टी-शर्ट व ट्रॅक पँट कॉम्बो (३ साठी ₹८००)",
                "category": "mens",
                "subtype": "casual_denim",
                "price": 800,
                "original_price": 1500,
                "discount": "3 for ₹800",
                "badge": "Festive Offer",
                "image": "assets/images/real_reel_DdQyFX4Tv4t.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DdQyFX4Tv4t/",
                "description": "Any 3 pieces of premium cotton round-neck t-shirts or four-way stretch track pants for just ₹800!",
                "sizes": "M, L, XL, XXL",
                "stock": 40,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 7
            },
            {
                "id": "HM-SHT-04",
                "code": "HM-SHT-04",
                "name": "Tropical Summer Floral Party Shirt",
                "marathi_name": "ट्रॉपिकल फ्लोरल पार्टी शर्ट",
                "category": "mens",
                "subtype": "party_wear",
                "price": 799,
                "original_price": 1199,
                "discount": "33% OFF",
                "badge": "Club Favorite",
                "image": "assets/images/real_reel_DcdL5uwTPTs.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/reel/DcdL5uwTPTs/",
                "description": "Vibrant botanical prints on featherlight cotton. Pair with shorts or chinos for an effortless look.",
                "sizes": "M, L, XL",
                "stock": 15,
                "status": "in_stock",
                "is_featured": 0,
                "display_order": 8
            },
            {
                "id": "HM-DNM-01",
                "code": "HM-DNM-01",
                "name": "Branded Comfort Stretch Denim Jeans",
                "marathi_name": "ब्रँडेड कम्फर्ट स्ट्रेच डेनिम",
                "category": "mens",
                "subtype": "denim",
                "price": 999,
                "original_price": 1699,
                "discount": "41% OFF",
                "badge": "Showroom Hit",
                "image": "assets/images/real_store_jeans.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/",
                "description": "Heavy ring-spun cotton denim with 2% elastane for maximum movement. Available in light wash, mid-blue, and black.",
                "sizes": "28, 30, 32, 34, 36, 38, 40",
                "stock": 30,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 9
            },
            {
                "id": "HM-DNM-02",
                "code": "HM-DNM-02",
                "name": "Tailored Smart Fit Chinos & Trousers",
                "marathi_name": "स्मार्ट फिट कॉटन ट्राउझर्स",
                "category": "mens",
                "subtype": "denim",
                "price": 899,
                "original_price": 1499,
                "discount": "40% OFF",
                "badge": "Daily Wear",
                "image": "assets/images/real_store_center.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/",
                "description": "Wrinkle-free combed cotton stretch chinos with clean pocket detailing. Colors: Khaki, Navy, Charcoal, Olive.",
                "sizes": "30, 32, 34, 36, 38",
                "stock": 25,
                "status": "in_stock",
                "is_featured": 0,
                "display_order": 10
            },
            {
                "id": "HM-ETH-01",
                "code": "HM-ETH-01",
                "name": "Royal Heritage Festive Kurta & Bundi Jacket",
                "marathi_name": "हेरिटेज फेस्टिव्ह कुर्ता व जॅकेट",
                "category": "mens",
                "subtype": "ethnic",
                "price": 1899,
                "original_price": 2999,
                "discount": "37% OFF",
                "badge": "Celebration",
                "image": "assets/images/hiramoti_founder_home.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/",
                "description": "Handcrafted festive ensemble featuring raw silk texture and subtle antique gold button accents for Satara weddings.",
                "sizes": "38, 40, 42, 44",
                "stock": 8,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 11
            },
            {
                "id": "HM-ETH-02",
                "code": "HM-ETH-02",
                "name": "Silk Blend Indo-Western Modi Jacket",
                "marathi_name": "सिल्क ब्लेन्ड मोदी जॅकेट",
                "category": "mens",
                "subtype": "ethnic",
                "price": 1299,
                "original_price": 1999,
                "discount": "35% OFF",
                "badge": "Wedding Edit",
                "image": "assets/images/hiramoti_interior_reception.jpg",
                "reel_url": "https://www.instagram.com/hiramoticollection/",
                "description": "Rich jacquard textured sleeveless Nehru jacket. Pairs effortlessly over plain linen or cotton kurtas.",
                "sizes": "M, L, XL, XXL",
                "stock": 12,
                "status": "in_stock",
                "is_featured": 1,
                "display_order": 12
            }
        ]

        for p in seed_products:
            cursor.execute("""
                INSERT INTO products (
                    id, code, name, marathi_name, category, subtype, price, original_price,
                    discount, badge, description, sizes, image, reel_url, stock, status, is_featured, display_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                p["id"], p["code"], p["name"], p["marathi_name"], p["category"], p["subtype"],
                p["price"], p["original_price"], p["discount"], p["badge"], p["description"],
                p["sizes"], p["image"], p["reel_url"], p["stock"], p["status"], p["is_featured"], p["display_order"]
            ))
            cursor.execute("""
                INSERT INTO product_images (product_id, image_url, is_primary)
                VALUES (?, ?, 1)
            """, (p["id"], p["image"]))
        print(f"[DB] Seeded {len(seed_products)} initial products")

    # Seed Reels if none exists
    cursor.execute("SELECT COUNT(*) FROM reels")
    if cursor.fetchone()[0] == 0:
        seed_reels = [
            {
                "id": "reel-1",
                "code": "DaiL4H0zCqV",
                "url": "https://www.instagram.com/hiramoticollection/reel/DaiL4H0zCqV/",
                "embed_url": "https://www.instagram.com/reel/DaiL4H0zCqV/embed/",
                "title": "Bomber Jacket Sale Live — Only ₹699/-",
                "marathi_title": "बॉम्बर जॅकेट स्पेशल ऑफर — फक्त ₹६९९/-",
                "caption": "Upgrade your wardrobe with latest Men’s & Women’s Bomber Jackets! Premium Quality, Trendy & Stylish Designs, Comfortable Fit. Rajatsagar Complex, Opp. Rajdhani Satara Selfie Point, Powai Naka.",
                "price": "₹699",
                "offer": "LIMITED DEAL",
                "category": "jackets",
                "image": "assets/images/real_reel_DaiL4H0zCqV.jpg",
                "display_order": 1
            },
            {
                "id": "reel-2",
                "code": "DdQyFX4Tv4t",
                "url": "https://www.instagram.com/hiramoticollection/reel/DdQyFX4Tv4t/",
                "embed_url": "https://www.instagram.com/reel/DdQyFX4Tv4t/embed/",
                "title": "T-Shirt & Track Pant — ₹800 मध्ये 3!",
                "marathi_title": "टी-शर्ट व ट्रॅक पँट — ₹८०० मध्ये ३!",
                "caption": "काहीही घ्या — ₹800 मध्ये 3! गणेश उत्सव स्पेशल ऑफरचा फायदा घ्या आणि स्टाईलमध्ये साजरा करा बाप्पाचा उत्सव! Hiramoti Collection, Satara.",
                "price": "₹800 for 3",
                "offer": "FESTIVE OFFER",
                "category": "casual",
                "image": "assets/images/real_reel_DdQyFX4Tv4t.jpg",
                "display_order": 2
            },
            {
                "id": "reel-3",
                "code": "DdL4HYAzqZK",
                "url": "https://www.instagram.com/hiramoticollection/reel/DdL4HYAzqZK/",
                "embed_url": "https://www.instagram.com/reel/DdL4HYAzqZK/embed/",
                "title": "Favourite Shirts Restock Alert — ₹799/-",
                "marathi_title": "फेव्हरेट शर्ट्स पुन्हा स्टॉक मध्ये — फक्त ₹७९९/-",
                "caption": "SHIRT RESTOCK ALERT! तुमचा Favourite Shirt पुन्हा STOCK मध्ये! Trendy Look, Premium Feel, Limited Stock. Powai Naka Satara.",
                "price": "₹799",
                "offer": "RESTOCK HIT",
                "category": "shirts",
                "image": "assets/images/real_reel_DdL4HYAzqZK.jpg",
                "display_order": 3
            },
            {
                "id": "reel-4",
                "code": "DcqiOSIzvCQ",
                "url": "https://www.instagram.com/hiramoticollection/reel/DcqiOSIzvCQ/",
                "embed_url": "https://www.instagram.com/reel/DcqiOSIzvCQ/embed/",
                "title": "Branded Denim, Cotton & Checks Shirts",
                "marathi_title": "ब्रँडेड डेनिम व कॉटन शर्ट्स — ₹७९९/-",
                "caption": "BRANDED SHIRTS @ JUST ₹799/-! Denim, Cotton, Checks, Double Pocket. Size Available: M to 3XL. Best Quality • Premium Collection • Perfect Fit.",
                "price": "₹799",
                "offer": "SIZES M-3XL",
                "category": "shirts",
                "image": "assets/images/real_reel_DcqiOSIzvCQ.jpg",
                "display_order": 4
            },
            {
                "id": "reel-5",
                "code": "Dcp2loUTRWp",
                "url": "https://www.instagram.com/hiramoticollection/reel/Dcp2loUTRWp/",
                "embed_url": "https://www.instagram.com/reel/Dcp2loUTRWp/embed/",
                "title": "TPU Weatherproof & Bomber Jacket @ ₹399/-",
                "marathi_title": "टीपीयू व बॉम्बर जॅकेट महाबचत — ₹३९९/-",
                "caption": "499/- चे TPU & BOMBER JACKET आता फक्त ₹399/- मध्ये! धमाकेदार ऑफर! आजच खरेदी करा आणि ₹100 ची बचत करा. Hiramoti Collection, Powai Naka.",
                "price": "₹399",
                "offer": "SAVE ₹100",
                "category": "jackets",
                "image": "assets/images/real_reel_Dcp2loUTRWp.jpg",
                "display_order": 5
            },
            {
                "id": "reel-6",
                "code": "Dcd2dn2NKZ9",
                "url": "https://www.instagram.com/hiramoticollection/reel/Dcd2dn2NKZ9/",
                "embed_url": "https://www.instagram.com/reel/Dcd2dn2NKZ9/embed/",
                "title": "Trendy Printed Half Shirts @ ₹799/-",
                "marathi_title": "ट्रेंडी प्रिंटेड हाफ शर्ट्स — ₹७९९/-",
                "caption": "TRENDY PRINTED HALF SHIRTS! Upgrade Your Style! Trendy Prints, Stylish & Comfortable. Pick Your Print, Rock Your Style. Available at Powai Naka Satara.",
                "price": "₹799",
                "offer": "MANY PRINTS",
                "category": "shirts",
                "image": "assets/images/real_reel_Dcd2dn2NKZ9.jpg",
                "display_order": 6
            },
            {
                "id": "reel-7",
                "code": "DcdL5uwTPTs",
                "url": "https://www.instagram.com/hiramoticollection/reel/DcdL5uwTPTs/",
                "embed_url": "https://www.instagram.com/reel/DcdL5uwTPTs/embed/",
                "title": "Designer Floral & Tropical Printed Shirts",
                "marathi_title": "डिझायनर फ्लोरल व प्रिंटेड शर्ट्स",
                "caption": "Rock Your Style! Hundreds of fresh prints in breathable pure cotton. Limited Stock — Grab Yours Now at Hiramoti Collection Satara.",
                "price": "₹799",
                "offer": "HOT SELLER",
                "category": "shirts",
                "image": "assets/images/real_reel_DcdL5uwTPTs.jpg",
                "display_order": 7
            },
            {
                "id": "reel-8",
                "code": "DcX8iP-zOb_",
                "url": "https://www.instagram.com/hiramoticollection/reel/DcX8iP-zOb_/",
                "embed_url": "https://www.instagram.com/reel/DcX8iP-zOb_/embed/",
                "title": "Imported Leather Jackets in 6 Colours",
                "marathi_title": "इम्पोर्टेड लेदर जॅकेट्स (६ कलर्स)",
                "caption": "IMPORTED LEATHER JACKET! Premium Imported Collection in 6 Stunning Colours. High Quality & Premium Finish. Choose Your Colour, Own Your Style!",
                "price": "₹1,499",
                "offer": "6 COLOURS",
                "category": "jackets",
                "image": "assets/images/real_reel_DcX8iP-zOb_.jpg",
                "display_order": 8
            }
        ]

        for r in seed_reels:
            cursor.execute("""
                INSERT INTO reels (
                    id, code, url, embed_url, title, marathi_title, caption, price,
                    offer, category, image, display_order, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                r["id"], r["code"], r["url"], r["embed_url"], r["title"], r["marathi_title"],
                r["caption"], r["price"], r["offer"], r["category"], r["image"], r["display_order"]
            ))
        print(f"[DB] Seeded {len(seed_reels)} initial Instagram reels")

    # Seed Gallery Items if none exists
    cursor.execute("SELECT COUNT(*) FROM gallery_items")
    if cursor.fetchone()[0] == 0:
        seed_gallery = [
            {"id": "gal-1", "title": "Grand Interior Reception & Royal HMC Wall", "subtitle": "Opp. Rajdhani Satara Selfie Point, Powai Naka Satara", "category": "showroom", "is_wide": 1, "image": "assets/images/hiramoti_interior_reception.jpg", "display_order": 1},
            {"id": "gal-2", "title": "Showroom Entrance & Red Neon Signboard", "subtitle": "Powai Naka entrance with grand floral celebration archway", "category": "showroom", "is_wide": 1, "image": "assets/images/hiramoti_exterior_entrance.jpg", "display_order": 2},
            {"id": "gal-3", "title": "Hiramoti Collection Founder — Pankaj Rathi", "subtitle": "परंपरा, भरोसा और स्टाइल – 39 सालों से आपके साथ", "category": "showroom", "is_wide": 0, "image": "assets/images/hiramoti_founder_home.jpg", "display_order": 3},
            {"id": "gal-4", "title": "Two-Story Glass Facade at Night", "subtitle": "Illuminated showroom glass display at Powai Naka", "category": "showroom", "is_wide": 0, "image": "assets/images/hiramoti_exterior_facade.jpg", "display_order": 4},
            {"id": "gal-5", "title": "Branded Cotton & Lycra Shirts Shelf", "subtitle": "Over 500+ Shirt Designs in Stock", "category": "shirts", "is_wide": 0, "image": "assets/images/real_store_shirts.jpg", "display_order": 5},
            {"id": "gal-6", "title": "Premium Stretch Denim & Trousers Counter", "subtitle": "Heavy Ring-Spun Denim Sizes 28 to 42", "category": "jeans", "is_wide": 0, "image": "assets/images/real_store_jeans.jpg", "display_order": 6},
            {"id": "gal-7", "title": "Central Shopping Aisles & Customer Trial Experience", "subtitle": "Spacious boutique shopping at Powai Naka", "category": "showroom", "is_wide": 0, "image": "assets/images/real_store_center.jpg", "display_order": 7},
            {"id": "gal-8", "title": "Hiramoti Fashion Hub Display", "subtitle": "Satara's Trusted Clothing Destination", "category": "showroom", "is_wide": 0, "image": "assets/images/hiramoti_real_store_2.png", "display_order": 8}
        ]
        for g in seed_gallery:
            cursor.execute("""
                INSERT INTO gallery_items (id, title, subtitle, category, is_wide, image, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (g["id"], g["title"], g["subtitle"], g["category"], g["is_wide"], g["image"], g["display_order"]))
        print(f"[DB] Seeded {len(seed_gallery)} gallery items")

    # Seed Founder & Legacy setting if not exists
    cursor.execute("SELECT value FROM settings WHERE key = 'founder_legacy'")
    if not cursor.fetchone():
        founder_default = {
            "founder": {
                "name": "Late Shri Ujwal Rathi",
                "designation": "Founder, Hiramoti Collection",
                "photo": "assets/images/hiramoti_founder_home.jpg",
                "quote": "Trust is not given — it is earned, stitch by stitch, customer by customer.",
                "quote_author": "Late Shri Ujwal Rathi",
                "biography": "Late Shri Ujwal Rathi laid the cornerstone of Hiramoti Collection in 1987 with a heartfelt vision: to provide the people of Satara with exquisite garments, genuine hospitality, and unquestionable trust. Under his dedicated leadership, Hiramoti Collection became far more than a clothing store — it became an enduring institution in the historic heart of Satara.\n\nHis commitment to welcoming every customer as family and ensuring fair pricing without compromising on fabric quality established standards that guide the showroom to this very day."
            },
            "milestones": [
                {
                    "year": "1987",
                    "badge_sub": "Origin",
                    "tag": "The Beginning • Vision • Trust",
                    "title": "The Beginning",
                    "description": "Hiramoti Collection was founded in 1987 with a singular vision — to bring premium-quality clothing, honest pricing, and genuine trust to the people of Satara. From humble beginnings, it was built on deep relationships with every customer who walked through the doors.",
                    "quote": "Where trust and honest craftsmanship were first woven into our story.",
                    "image": "assets/images/hiramoti_real_store_2.png",
                    "caption": "Hiramoti Collection — Established 1987"
                },
                {
                    "year": "2012",
                    "badge_sub": "Evolution",
                    "tag": "The First Renovation • Showroom Evolution",
                    "title": "The First Renovation",
                    "description": "To serve our growing family of customers better, Hiramoti Collection underwent its first major showroom renovation in 2012. Modern retail displays, expanded clothing collections, and a refined shopping experience were introduced — while preserving the warmth, personal attention, and trust that defined the brand from day one.",
                    "quote": "Preserving our warmth while evolving to serve growing generations.",
                    "image": "assets/images/hiramoti_store_interior.jpg",
                    "caption": "Showroom Transformation — 2012"
                },
                {
                    "year": "2026",
                    "badge_sub": "New Chapter",
                    "tag": "The Second Renovation • A New Chapter",
                    "title": "The Second Renovation",
                    "description": "In 2026, Hiramoti Collection unveiled a grand, state-of-the-art showroom renovation. Featuring contemporary lighting, premium display sections for suits, sherwanis, jackets, and everyday essentials, and an elevated shopping ambiance — designed to serve the next generation while honouring the legacy of the past.",
                    "quote": "Honouring the past. Building for the future.",
                    "image": "assets/images/hiramoti_exterior_entrance.jpg",
                    "caption": "The New Hiramoti Collection Showroom — 2026"
                }
            ]
        }
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("founder_legacy", json.dumps(founder_default)))
        print("[DB] Initialized founder & legacy data")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[DB] Database initialization complete.")
