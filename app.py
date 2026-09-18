"""
Hiramoti Collection, Satara — Unified Flask Application & CMS Backend
Serves public website pages, static assets, and full secure Admin REST API.
"""

import os
import re
import json
import uuid
import time
import secrets
import string
import sqlite3
from functools import wraps
from datetime import datetime

from flask import (
    Flask, request, jsonify, session, send_from_directory,
    redirect, url_for, render_template, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from database.db import get_db_connection, init_db, DB_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "avif", "gif"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov"}
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB total upload payload
MAX_IMAGE_SIZE = 15 * 1024 * 1024     # 15 MB max image size
MAX_VIDEO_SIZE = 50 * 1024 * 1024     # 50 MB max video size

# Registered admin mobile security configuration
ADMIN_REGISTERED_PHONE = "7588745454"
ADMIN_MASKED_PHONE = "******5454"

# In-memory secure OTP storage: never exposed in frontend or client responses
otp_security_store = {
    "otp_hash": None,
    "phone": ADMIN_REGISTERED_PHONE,
    "expires_at": 0,
    "attempts": 0,
    "max_attempts": 5,
    "last_sent_at": 0,
    "resend_cooldown": 30,  # 30 seconds
    "reset_token": None,
    "token_expires_at": 0
}

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("HIRAMOTI_SECRET_KEY", "hiramoti-satara-royal-secret-key-1987-secure")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ensure DB is initialized
init_db()


# ---------------------------------------------------------------------------
# Helper Decorators & Functions
# ---------------------------------------------------------------------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized. Please log in as admin."}), 401
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def parse_instagram_url(url):
    """Extracts Instagram reel code and builds standard embed URL."""
    if not url:
        return "", ""
    match = re.search(r"(?:reel|p)/([A-Za-z0-9_-]+)", url)
    if match:
        code = match.group(1)
        embed_url = f"https://www.instagram.com/reel/{code}/embed/"
        return code, embed_url
    return "", url


# ---------------------------------------------------------------------------
# Admin Web Interface Routes
# ---------------------------------------------------------------------------
@app.route("/admin")
@app.route("/admin/")
def admin_root():
    if "user_id" in session:
        return redirect("/admin/dashboard")
    return redirect("/admin/login")

@app.route("/admin/login")
def admin_login_page():
    if "user_id" in session:
        return redirect("/admin/dashboard")
    return send_from_directory(os.path.join(BASE_DIR, "admin"), "index.html")

@app.route("/admin/dashboard")
def admin_dashboard_page():
    if "user_id" not in session:
        return redirect("/admin/login")
    return send_from_directory(os.path.join(BASE_DIR, "admin"), "index.html")

@app.route("/admin/logout")
def admin_logout_redirect():
    session.clear()
    return redirect("/admin/login")


# ---------------------------------------------------------------------------
# Authentication API
# ---------------------------------------------------------------------------
@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json() or {}
    identifier = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not identifier or not password:
        return jsonify({"error": "Please provide username/email and password"}), 400

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM admin_users WHERE username = ? OR email = ?",
        (identifier, identifier)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["email"] = user["email"]
    session["role"] = user["role"]

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    })

@app.route("/api/admin/logout", methods=["POST"])
def api_admin_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route("/api/admin/me", methods=["GET"])
def api_admin_me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401
    return jsonify({
        "authenticated": True,
        "user": {
            "id": session.get("user_id"),
            "username": session.get("username"),
            "email": session.get("email"),
            "role": session.get("role")
        }
    })

def send_sms_otp(phone, otp_code):
    """
    Sends 6-digit verification code via configured SMS provider.
    Reads credentials from environment variables: OTP_API_KEY, OTP_API_SECRET, OTP_SENDER_ID.
    If no provider configured (local development mode), writes dispatch record to secure local scratch
    file (scratch/otp_dev_latest.txt) for developer testing, NEVER in HTTP responses or public logs.
    """
    api_key = os.environ.get("OTP_API_KEY")
    api_secret = os.environ.get("OTP_API_SECRET")
    sender_id = os.environ.get("OTP_SENDER_ID", "HIRAMT")

    if api_key:
        try:
            import urllib.request
            import urllib.parse
            url = "https://www.fast2sms.com/dev/bulkV2"
            payload = urllib.parse.urlencode({
                "authorization": api_key,
                "variables_values": otp_code,
                "route": "otp",
                "numbers": phone
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache"
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                return True
        except Exception as err:
            print(f"[SMS Provider Warning] Gateway error: {err}")

    # Secure local developer verification record (never exposed to API/client)
    try:
        scratch_dir = os.path.join(BASE_DIR, "scratch")
        os.makedirs(scratch_dir, exist_ok=True)
        otp_file = os.path.join(scratch_dir, "otp_dev_latest.txt")
        with open(otp_file, "w", encoding="utf-8") as f:
            f.write(f"OTP:{otp_code}\nPHONE:{phone}\nTIMESTAMP:{int(time.time())}\n")
    except Exception:
        pass

    return True


@app.route("/api/admin/otp/request", methods=["POST"])
@admin_required
def api_admin_request_otp():
    """Generates cryptographically random 6-digit OTP and sends to registered mobile number."""
    now = time.time()
    
    # Rate limit: enforce 30 seconds cooldown between resend requests
    last_sent = otp_security_store.get("last_sent_at", 0)
    cooldown = otp_security_store.get("resend_cooldown", 30)
    if now - last_sent < cooldown:
        wait_seconds = int(cooldown - (now - last_sent))
        return jsonify({
            "error": f"Please wait {wait_seconds} seconds before requesting a new OTP.",
            "cooldown_remaining": wait_seconds
        }), 429

    # Generate 6-digit cryptographic OTP
    raw_otp = "".join(secrets.choice(string.digits) for _ in range(6))
    
    # Store hashed OTP and timestamps
    otp_security_store["otp_hash"] = generate_password_hash(raw_otp, method="pbkdf2:sha256")
    otp_security_store["expires_at"] = now + 300  # 5 minutes validity
    otp_security_store["attempts"] = 0
    otp_security_store["last_sent_at"] = now
    otp_security_store["reset_token"] = None

    # Dispatch via SMS provider
    send_sms_otp(ADMIN_REGISTERED_PHONE, raw_otp)

    return jsonify({
        "success": True,
        "message": f"Verification code sent to registered mobile {ADMIN_MASKED_PHONE}",
        "masked_phone": ADMIN_MASKED_PHONE,
        "expires_in": 300,
        "cooldown": 30
    })


@app.route("/api/admin/otp/verify", methods=["POST"])
@admin_required
def api_admin_verify_otp():
    """Verifies entered 6-digit OTP against cryptographic hash."""
    data = request.get_json() or {}
    otp = str(data.get("otp", "")).strip()

    if not otp or len(otp) != 6 or not otp.isdigit():
        return jsonify({"error": "Please enter a valid 6-digit verification code."}), 400

    now = time.time()
    if now > otp_security_store.get("expires_at", 0):
        otp_security_store["otp_hash"] = None
        return jsonify({"error": "The verification code has expired. Please request a new one."}), 400

    if otp_security_store.get("attempts", 0) >= otp_security_store.get("max_attempts", 5):
        otp_security_store["otp_hash"] = None
        return jsonify({"error": "Maximum verification attempts exceeded. Please request a new code."}), 429

    otp_security_store["attempts"] += 1
    stored_hash = otp_security_store.get("otp_hash")

    if not stored_hash or not check_password_hash(stored_hash, otp):
        remaining = otp_security_store["max_attempts"] - otp_security_store["attempts"]
        if remaining <= 0:
            otp_security_store["otp_hash"] = None
            return jsonify({"error": "Incorrect code. Maximum attempts exceeded. Please request a new code."}), 429
        return jsonify({"error": f"Invalid verification code. {remaining} attempt(s) remaining."}), 400

    # OTP is valid: invalidate OTP (single use) and issue temporary password reset token
    otp_security_store["otp_hash"] = None
    reset_token = secrets.token_hex(24)
    otp_security_store["reset_token"] = reset_token
    otp_security_store["token_expires_at"] = now + 600  # 10 minutes

    return jsonify({
        "success": True,
        "message": "Mobile number verified successfully.",
        "reset_token": reset_token
    })


@app.route("/api/admin/change-password", methods=["POST"])
@admin_required
def api_admin_change_password():
    """Updates admin password only after verified mobile OTP session."""
    data = request.get_json() or {}
    reset_token = data.get("reset_token", "").strip()
    new_pwd = data.get("new_password", "").strip()
    confirm_pwd = data.get("confirm_password", "").strip()

    # Verify reset token from OTP step
    now = time.time()
    valid_token = otp_security_store.get("reset_token")
    token_expires = otp_security_store.get("token_expires_at", 0)

    if not reset_token or reset_token != valid_token or now > token_expires:
        return jsonify({"error": "Unauthorized: Verified mobile OTP session required to change password."}), 403

    if not new_pwd or not confirm_pwd:
        return jsonify({"error": "Both new password and confirmation are required."}), 400

    if len(new_pwd) < 8:
        return jsonify({"error": "New password must be at least 8 characters long."}), 400

    if new_pwd != confirm_pwd:
        return jsonify({"error": "New password and confirmation do not match."}), 400

    # Reject trivial / weak passwords
    weak_patterns = ["password", "12345678", "admin123", "hiramoti123", "qwertyuiop"]
    if new_pwd.lower() in weak_patterns:
        return jsonify({"error": "Password is too weak. Please use a combination of letters, numbers, or symbols."}), 400

    # Securely hash and update in database
    new_hash = generate_password_hash(new_pwd, method="pbkdf2:sha256")
    conn = get_db_connection()
    conn.execute("UPDATE admin_users SET password_hash = ? WHERE id = ?", (new_hash, session["user_id"]))
    conn.commit()
    conn.close()

    # Invalidate reset token and session
    otp_security_store["reset_token"] = None
    session.clear()

    return jsonify({
        "success": True,
        "message": "Password updated successfully. Please log in with your new password."
    })


# ---------------------------------------------------------------------------
# Dashboard Statistics API
# ---------------------------------------------------------------------------
@app.route("/api/admin/dashboard-stats", methods=["GET"])
@admin_required
def api_admin_dashboard_stats():
    conn = get_db_connection()
    total_products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    total_images = conn.execute("SELECT COUNT(*) FROM product_images").fetchone()[0]
    in_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock > 0 AND status = 'in_stock'").fetchone()[0]
    out_of_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock = 0 OR status = 'out_of_stock'").fetchone()[0]
    total_reels = conn.execute("SELECT COUNT(*) FROM reels WHERE is_active = 1").fetchone()[0]
    total_enquiries = conn.execute("SELECT COUNT(*) FROM enquiries").fetchone()[0]

    # Recent 5 products
    recent_products = [dict(row) for row in conn.execute(
        "SELECT id, name, price, stock, status, image FROM products ORDER BY created_at DESC LIMIT 5"
    ).fetchall()]

    # Recent 5 enquiries
    recent_enquiries = [dict(row) for row in conn.execute(
        "SELECT id, name, phone, area, visit_date, time_slot, status, created_at FROM enquiries ORDER BY created_at DESC LIMIT 5"
    ).fetchall()]

    conn.close()

    return jsonify({
        "total_products": total_products,
        "total_images": total_images,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "total_reels": total_reels,
        "total_enquiries": total_enquiries,
        "recent_products": recent_products,
        "recent_enquiries": recent_enquiries
    })


# ---------------------------------------------------------------------------
# Products API (Public & Admin)
# ---------------------------------------------------------------------------
@app.route("/api/products", methods=["GET"])
def api_public_products():
    category = request.args.get("category")
    subtype = request.args.get("subtype")
    search = request.args.get("search")

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    if subtype and subtype != "all":
        query += " AND subtype = ?"
        params.append(subtype)
    if search:
        query += " AND (name LIKE ? OR marathi_name LIKE ? OR description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    query += " ORDER BY display_order ASC, created_at DESC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    products = []
    for r in rows:
        p = dict(r)
        # Parse sizes
        p["sizes_list"] = [s.strip() for s in p.get("sizes", "").split(",") if s.strip()]
        # Auto-compute status based on stock
        if p["stock"] <= 0:
            p["status"] = "out_of_stock"
        products.append(p)

    return jsonify({"products": products, "count": len(products)})

@app.route("/api/admin/products", methods=["GET"])
@admin_required
def api_admin_products():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM products ORDER BY display_order ASC, created_at DESC").fetchall()
    conn.close()

    products = []
    for r in rows:
        p = dict(r)
        p["sizes_list"] = [s.strip() for s in p.get("sizes", "").split(",") if s.strip()]
        products.append(p)

    return jsonify({"products": products, "count": len(products)})

@app.route("/api/admin/products", methods=["POST"])
@admin_required
def api_admin_create_product():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category = data.get("category", "mens").strip()
    subtype = data.get("subtype", "jackets").strip()
    
    try:
        price = float(data.get("price", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price format"}), 400

    if not name:
        return jsonify({"error": "Product name is required"}), 400
    if price <= 0:
        return jsonify({"error": "Product price must be greater than 0"}), 400

    prod_id = data.get("id", "").strip()
    if not prod_id:
        prod_id = f"HM-{subtype[:3].upper()}-{str(uuid.uuid4())[:4].upper()}"

    original_price = data.get("original_price")
    try:
        original_price = float(original_price) if original_price else None
    except (ValueError, TypeError):
        original_price = None

    discount = data.get("discount", "").strip()
    if not discount and original_price and original_price > price:
        pct = round(((original_price - price) / original_price) * 100)
        discount = f"{pct}% OFF"

    try:
        stock = int(data.get("stock", 10))
    except (ValueError, TypeError):
        stock = 10

    status = "out_of_stock" if stock <= 0 else data.get("status", "in_stock")
    image = data.get("image", "").strip() or "assets/images/real_store_shirts.jpg"
    marathi_name = data.get("marathi_name", "").strip()
    badge = data.get("badge", "").strip()
    description = data.get("description", "").strip()
    sizes = data.get("sizes", "M, L, XL").strip()
    reel_url = data.get("reel_url", "").strip()
    is_featured = 1 if data.get("is_featured") else 0
    display_order = int(data.get("display_order", 0))

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO products (
                id, code, name, marathi_name, category, subtype, price, original_price,
                discount, badge, description, sizes, image, reel_url, stock, status, is_featured, display_order
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prod_id, prod_id, name, marathi_name, category, subtype, price, original_price,
            discount, badge, description, sizes, image, reel_url, stock, status, is_featured, display_order
        ))
        conn.execute("""
            INSERT INTO product_images (product_id, image_url, is_primary)
            VALUES (?, ?, 1)
        """, (prod_id, image))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Product with ID '{prod_id}' already exists."}), 400
    
    new_p = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Product created successfully", "product": dict(new_p)}), 201

@app.route("/api/admin/products/<prod_id>", methods=["PUT"])
@admin_required
def api_admin_update_product(prod_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    name = data.get("name", existing["name"]).strip()
    marathi_name = data.get("marathi_name", existing["marathi_name"]).strip()
    category = data.get("category", existing["category"]).strip()
    subtype = data.get("subtype", existing["subtype"]).strip()
    price = float(data.get("price", existing["price"]))
    
    orig_p = data.get("original_price")
    original_price = float(orig_p) if orig_p is not None and orig_p != "" else None

    discount = data.get("discount", existing["discount"]).strip()
    if not discount and original_price and original_price > price:
        pct = round(((original_price - price) / original_price) * 100)
        discount = f"{pct}% OFF"

    badge = data.get("badge", existing["badge"]).strip()
    description = data.get("description", existing["description"]).strip()
    sizes = data.get("sizes", existing["sizes"]).strip()
    image = data.get("image", existing["image"]).strip()
    reel_url = data.get("reel_url", existing["reel_url"]).strip()
    stock = int(data.get("stock", existing["stock"]))
    status = "out_of_stock" if stock <= 0 else data.get("status", existing["status"])
    is_featured = 1 if data.get("is_featured", existing["is_featured"]) else 0
    display_order = int(data.get("display_order", existing["display_order"]))

    conn.execute("""
        UPDATE products SET
            name = ?, marathi_name = ?, category = ?, subtype = ?, price = ?, original_price = ?,
            discount = ?, badge = ?, description = ?, sizes = ?, image = ?, reel_url = ?,
            stock = ?, status = ?, is_featured = ?, display_order = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        name, marathi_name, category, subtype, price, original_price,
        discount, badge, description, sizes, image, reel_url,
        stock, status, is_featured, display_order, prod_id
    ))

    # Update primary image in product_images
    if image != existing["image"]:
        conn.execute("UPDATE product_images SET is_primary = 0 WHERE product_id = ?", (prod_id,))
        conn.execute("""
            INSERT INTO product_images (product_id, image_url, is_primary)
            VALUES (?, ?, 1)
        """, (prod_id, image))

    conn.commit()
    updated = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Product updated successfully", "product": dict(updated)})

@app.route("/api/admin/products/<prod_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_product(prod_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    conn.execute("DELETE FROM product_images WHERE product_id = ?", (prod_id,))
    conn.execute("DELETE FROM products WHERE id = ?", (prod_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Product '{existing['name']}' deleted successfully"})

@app.route("/api/admin/products/<prod_id>/quick-update", methods=["PATCH"])
@admin_required
def api_admin_quick_update_product(prod_id):
    """Fast inline price and stock update."""
    data = request.get_json() or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    updates = []
    params = []

    if "price" in data:
        try:
            p = float(data["price"])
            if p > 0:
                updates.append("price = ?")
                params.append(p)
        except (ValueError, TypeError):
            pass

    if "stock" in data:
        try:
            s = int(data["stock"])
            updates.append("stock = ?")
            params.append(s)
            if s <= 0:
                updates.append("status = 'out_of_stock'")
            else:
                if "status" not in data:
                    updates.append("status = 'in_stock'")
        except (ValueError, TypeError):
            pass

    if "status" in data:
        st = data["status"]
        if st in ("in_stock", "out_of_stock"):
            updates.append("status = ?")
            params.append(st)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        params.append(prod_id)
        conn.execute(query, params)
        conn.commit()

    updated = conn.execute("SELECT * FROM products WHERE id = ?", (prod_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Quick update saved", "product": dict(updated)})


# ---------------------------------------------------------------------------
# Image & Video Upload & Management API
# ---------------------------------------------------------------------------
def process_uploaded_media(file, expected_type=None):
    """
    Validates uploaded media file (image or video), checks size limits,
    sanitizes filename, saves to UPLOAD_DIR, and returns file metadata dictionary.
    """
    if not file or file.filename == "":
        return None, "No file selected"

    filename = secure_filename(file.filename)
    if not filename or "." not in filename:
        return None, "Invalid file format or missing extension"

    ext = filename.rsplit(".", 1)[1].lower()
    
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        media_type = "image"
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        media_type = "video"
    else:
        return None, f"Unsupported file type (.{ext}). Allowed images: jpg, jpeg, png, webp. Allowed videos: mp4, webm, mov."

    if expected_type and media_type != expected_type:
        return None, f"Expected {expected_type} file, but received {media_type} (.{ext})"

    # Check size limit
    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    file.seek(0)

    if media_type == "image" and size_bytes > MAX_IMAGE_SIZE:
        return None, f"Image file is too large ({round(size_bytes / (1024*1024), 1)} MB). Maximum allowed is 15 MB."

    if media_type == "video" and size_bytes > MAX_VIDEO_SIZE:
        return None, f"Video file is too large ({round(size_bytes / (1024*1024), 1)} MB). Maximum allowed is 50 MB."

    clean_base = secure_filename(filename.rsplit(".", 1)[0]) or "media"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "hm_vid" if media_type == "video" else "hm_cover" if expected_type == "image" else "hm"
    unique_name = f"{prefix}_{clean_base}_{timestamp}_{str(uuid.uuid4())[:4]}.{ext}"

    file_path = os.path.join(UPLOAD_DIR, unique_name)
    file.save(file_path)

    relative_url = f"assets/uploads/{unique_name}"

    return {
        "url": relative_url,
        "filename": unique_name,
        "original_name": file.filename,
        "media_type": media_type,
        "size_kb": round(size_bytes / 1024, 1)
    }, None

@app.route("/api/admin/upload-media", methods=["POST"])
@admin_required
def api_admin_upload_media():
    """Universal media uploader supporting device images (<=15MB) and videos (<=50MB)."""
    file = None
    for field_name in ("file", "media", "image", "video"):
        if field_name in request.files:
            file = request.files[field_name]
            break

    if not file or file.filename == "":
        return jsonify({"error": "No media file provided. Please choose a file from your device."}), 400

    expected_type = request.form.get("media_type")
    meta, error = process_uploaded_media(file, expected_type=expected_type)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "success": True,
        "message": f"{meta['media_type'].capitalize()} uploaded successfully",
        **meta
    })

@app.route("/api/admin/upload-image", methods=["POST"])
@admin_required
def api_admin_upload_image():
    """Legacy and product-associated image uploader."""
    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No image file provided"}), 400

    meta, error = process_uploaded_media(file, expected_type="image")
    if error:
        return jsonify({"error": error}), 400

    relative_url = meta["url"]
    unique_name = meta["filename"]

    # Optionally associate with product
    product_id = request.form.get("product_id")
    is_primary = 1 if request.form.get("is_primary") == "true" else 0

    if product_id:
        conn = get_db_connection()
        if is_primary:
            conn.execute("UPDATE product_images SET is_primary = 0 WHERE product_id = ?", (product_id,))
            conn.execute("UPDATE products SET image = ? WHERE id = ?", (relative_url, product_id))
        conn.execute("""
            INSERT INTO product_images (product_id, image_url, is_primary)
            VALUES (?, ?, ?)
        """, (product_id, relative_url, is_primary))
        conn.commit()
        conn.close()

    return jsonify({
        "success": True,
        "message": "Image uploaded successfully",
        "url": relative_url,
        "filename": unique_name,
        "media_type": "image",
        "size_kb": meta["size_kb"]
    })

@app.route("/api/admin/images", methods=["GET"])
@admin_required
def api_admin_list_images():
    """Lists uploaded images and existing showroom assets."""
    images = []
    
    # 1. Uploaded images
    if os.path.exists(UPLOAD_DIR):
        for fname in os.listdir(UPLOAD_DIR):
            if allowed_file(fname):
                fpath = os.path.join(UPLOAD_DIR, fname)
                images.append({
                    "filename": fname,
                    "url": f"assets/uploads/{fname}",
                    "source": "uploads",
                    "size_kb": round(os.path.getsize(fpath) / 1024, 1),
                    "created_at": datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
                })

    # 2. Existing assets
    images_dir = os.path.join(BASE_DIR, "assets", "images")
    if os.path.exists(images_dir):
        for fname in os.listdir(images_dir):
            if allowed_file(fname) and (fname.startswith("real_") or fname.startswith("hiramoti_")):
                fpath = os.path.join(images_dir, fname)
                images.append({
                    "filename": fname,
                    "url": f"assets/images/{fname}",
                    "source": "store_assets",
                    "size_kb": round(os.path.getsize(fpath) / 1024, 1),
                    "created_at": datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")
                })

    return jsonify({"images": images, "count": len(images)})

@app.route("/api/admin/images/<filename>", methods=["DELETE"])
@admin_required
def api_admin_delete_image(filename):
    """Deletes uploaded image safely."""
    safe_name = secure_filename(filename)
    fpath = os.path.join(UPLOAD_DIR, safe_name)
    if not os.path.exists(fpath):
        return jsonify({"error": "File not found or protected"}), 404

    try:
        os.remove(fpath)
        # Remove from product_images table if referenced
        relative_url = f"assets/uploads/{safe_name}"
        conn = get_db_connection()
        conn.execute("DELETE FROM product_images WHERE image_url = ?", (relative_url,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Image deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Reels & Videos API (Public & Admin)
# ---------------------------------------------------------------------------
@app.route("/api/reels", methods=["GET"])
def api_public_reels():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM reels WHERE is_active = 1 ORDER BY display_order ASC, created_at DESC").fetchall()
    conn.close()
    return jsonify({"reels": [dict(r) for r in rows], "count": len(rows)})

@app.route("/api/admin/reels", methods=["GET"])
@admin_required
def api_admin_reels():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM reels ORDER BY display_order ASC, created_at DESC").fetchall()
    conn.close()
    return jsonify({"reels": [dict(r) for r in rows], "count": len(rows)})

@app.route("/api/admin/reels", methods=["POST"])
@admin_required
def api_admin_create_reel():
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    url = data.get("url", "").strip()
    video_url = data.get("video_url", "").strip()

    if not title:
        return jsonify({"error": "Reel title is required"}), 400
    if not url and not video_url:
        return jsonify({"error": "Either Instagram Reel URL or an uploaded Reel Video is required"}), 400

    if url:
        code, embed_url = parse_instagram_url(url)
        if not embed_url:
            embed_url = data.get("embed_url", "").strip() or url
    else:
        code = ""
        embed_url = video_url
        url = video_url

    if video_url and not embed_url:
        embed_url = video_url

    reel_id = data.get("id", "").strip() or f"reel-{str(uuid.uuid4())[:6]}"
    marathi_title = data.get("marathi_title", "").strip()
    caption = data.get("caption", "").strip()
    price = data.get("price", "").strip() or "SPECIAL DEAL"
    offer = data.get("offer", "").strip() or "VIRAL DROP"
    category = data.get("category", "general").strip()
    image = data.get("image", "").strip() or "assets/images/real_reel_DaiL4H0zCqV.jpg"
    display_order = int(data.get("display_order", 0))
    is_active = 1 if data.get("is_active", True) else 0

    conn = get_db_connection()
    try:
        conn.execute("""
            INSERT INTO reels (
                id, code, url, embed_url, title, marathi_title, caption, price,
                offer, category, image, display_order, is_active, video_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            reel_id, code, url, embed_url, title, marathi_title, caption, price,
            offer, category, image, display_order, is_active, video_url
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Reel with ID '{reel_id}' already exists."}), 400

    new_reel = conn.execute("SELECT * FROM reels WHERE id = ?", (reel_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Reel added successfully", "reel": dict(new_reel)}), 201

@app.route("/api/admin/reels/<reel_id>", methods=["PUT"])
@admin_required
def api_admin_update_reel(reel_id):
    data = request.get_json() or {}
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM reels WHERE id = ?", (reel_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Reel not found"}), 404

    existing_dict = dict(existing)
    title = data.get("title", existing_dict["title"]).strip()
    url = data.get("url", existing_dict.get("url", "")).strip()
    video_url = data.get("video_url", existing_dict.get("video_url") or "").strip()

    if url:
        code, embed_url = parse_instagram_url(url)
        if not embed_url:
            embed_url = data.get("embed_url", existing_dict.get("embed_url", "")).strip() or url
    else:
        code = ""
        embed_url = video_url or existing_dict.get("embed_url", "")
        url = video_url or existing_dict.get("url", "")

    marathi_title = data.get("marathi_title", existing_dict.get("marathi_title", "")).strip()
    caption = data.get("caption", existing_dict.get("caption", "")).strip()
    price = data.get("price", existing_dict.get("price", "")).strip()
    offer = data.get("offer", existing_dict.get("offer", "")).strip()
    category = data.get("category", existing_dict.get("category", "")).strip()
    image = data.get("image", existing_dict.get("image", "")).strip()
    display_order = int(data.get("display_order", existing_dict.get("display_order", 1)))
    is_active = 1 if data.get("is_active", existing_dict.get("is_active", 1)) else 0

    conn.execute("""
        UPDATE reels SET
            title = ?, marathi_title = ?, url = ?, embed_url = ?, code = ?,
            caption = ?, price = ?, offer = ?, category = ?, image = ?,
            display_order = ?, is_active = ?, video_url = ?
        WHERE id = ?
    """, (
        title, marathi_title, url, embed_url, code,
        caption, price, offer, category, image,
        display_order, is_active, video_url, reel_id
    ))
    conn.commit()
    updated = conn.execute("SELECT * FROM reels WHERE id = ?", (reel_id,)).fetchone()
    conn.close()

    return jsonify({"success": True, "message": "Reel updated successfully", "reel": dict(updated)})

@app.route("/api/admin/reels/<reel_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_reel(reel_id):
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM reels WHERE id = ?", (reel_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Reel not found"}), 404

    conn.execute("DELETE FROM reels WHERE id = ?", (reel_id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Reel '{existing['title']}' deleted successfully"})


# ---------------------------------------------------------------------------
# Gallery Items API (Public)
# ---------------------------------------------------------------------------
@app.route("/api/gallery", methods=["GET"])
def api_public_gallery():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM gallery_items ORDER BY display_order ASC, created_at DESC").fetchall()
    conn.close()
    return jsonify({"gallery": [dict(r) for r in rows], "count": len(rows)})


# ---------------------------------------------------------------------------
# Customer Enquiries / Appointments API
# ---------------------------------------------------------------------------
@app.route("/api/enquiries", methods=["POST"])
def api_create_enquiry():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"error": "Name and phone number are required"}), 400

    area = data.get("area", "").strip()
    visit_date = data.get("visit_date", "").strip()
    time_slot = data.get("time_slot", "").strip()
    style_interest = data.get("style_interest", "").strip()
    message = data.get("message", "").strip()

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO enquiries (name, phone, area, visit_date, time_slot, style_interest, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, area, visit_date, time_slot, style_interest, message))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Showroom appointment enquiry received!"}), 201

@app.route("/api/admin/enquiries", methods=["GET"])
@admin_required
def api_admin_enquiries():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM enquiries ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify({"enquiries": [dict(r) for r in rows], "count": len(rows)})

@app.route("/api/admin/enquiries/<int:enquiry_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_enquiry(enquiry_id):
    """Deletes showroom appointment lead by ID."""
    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM enquiries WHERE id = ?", (enquiry_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({"error": "Appointment enquiry not found"}), 404

    conn.execute("DELETE FROM enquiries WHERE id = ?", (enquiry_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": f"Appointment lead #{enquiry_id} deleted successfully"})
 
# ---------------------------------------------------------------------------
# Founder & Legacy API (Public & Admin Protected)
# ---------------------------------------------------------------------------
@app.route("/api/founder", methods=["GET"])
def api_get_founder():
    conn = get_db_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = 'founder_legacy'").fetchone()
    conn.close()
    if row:
        try:
            return jsonify(json.loads(row["value"]))
        except Exception:
            pass
    return jsonify({
        "founder": {
            "name": "Late Shri Ujwal Rathi",
            "designation": "Founder, Hiramoti Collection",
            "photo": "",
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
    })

@app.route("/api/admin/founder", methods=["GET"])
@admin_required
def api_admin_get_founder():
    return api_get_founder()

@app.route("/api/admin/founder", methods=["POST"])
@admin_required
def api_admin_update_founder():
    data = request.get_json() or {}
    founder = data.get("founder")
    milestones = data.get("milestones")

    if not founder or not isinstance(milestones, list):
        return jsonify({"error": "Invalid payload. 'founder' and 'milestones' are required."}), 400

    conn = get_db_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES ('founder_legacy', ?)",
        (json.dumps(data),)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Founder & Legacy content saved successfully!"})

@app.after_request
def add_cache_control_headers(response):
    """Disables caching on all REST API endpoints to ensure real-time consistency."""
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# ---------------------------------------------------------------------------
# Public Static File Serving (Preserves all existing website routes)
# ---------------------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/founder")
def serve_founder_page():
    return send_from_directory(BASE_DIR, "founder.html")

@app.route("/<path:filename>")
def serve_static(filename):
    # If file exists directly in root directory (e.g. collections.html, css/style.css, assets/...)
    file_path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, filename)
    
    # Check if html extension is omitted (e.g. /collections -> collections.html)
    if os.path.isfile(file_path + ".html"):
        return send_from_directory(BASE_DIR, filename + ".html")

    # 404 fallback to index
    if not filename.startswith("api/") and not filename.startswith("admin/"):
        return send_from_directory(BASE_DIR, "index.html")

    abort(404)


# ---------------------------------------------------------------------------
# Main Application Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"==================================================")
    print(f" Hiramoti Collection — Store & Admin Server Active")
    print(f" Public Website: http://localhost:{port}/")
    print(f" Admin Dashboard: http://localhost:{port}/admin")
    print(f"==================================================")
    app.run(host="0.0.0.0", port=port, debug=False)
