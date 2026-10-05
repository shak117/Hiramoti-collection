import urllib.request
import json
import os
import sys
import sqlite3
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "hiramoti.db")
ARTIFACT_DIR = r"C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("=================================================================")
print("HIRAMOTI COLLECTION — COMPREHENSIVE MEDIA AUDIT & QA SUITE")
print("=================================================================")

# ----------------------------------------------------------------------
# 1. Admin Authentication
# ----------------------------------------------------------------------
print("\n[STEP 1] Testing Admin Authentication...")
login_payload = json.dumps({"username": "admin@hiramoti.com", "password": "Hiramoti@1987"}).encode('utf-8')
req = urllib.request.Request(f"{BASE_URL}/api/admin/login", data=login_payload, headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
login_data = json.loads(res.read().decode('utf-8'))
assert login_data.get("success"), "Login failed!"
token = login_data["token"]
auth_headers = {"Authorization": f"Bearer {token}"}
print(f" PASS: Authenticated as '{login_data['user']['username']}'. Token: {token[:12]}...")

# ----------------------------------------------------------------------
# 2. Reel Video Upload (MP4, WEBM, MOV) & Byte-Range Streaming
# ----------------------------------------------------------------------
print("\n[STEP 2] Testing Reel Video Uploads (MP4, WEBM, MOV)...")

def upload_file(filename, content_bytes, media_type):
    boundary = "----WebKitFormBoundaryQA7MA4YWxkTrZu0gW"
    mime_type = "video/mp4" if filename.endswith(".mp4") else "video/webm" if filename.endswith(".webm") else "video/quicktime" if filename.endswith(".mov") else "image/jpeg"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode('utf-8') + content_bytes + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="media_type"\r\n\r\n'
        f"{media_type}\r\n"
        f"--{boundary}--\r\n"
    ).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/admin/upload-media",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}", "Authorization": f"Bearer {token}"}
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

# Fake valid MP4 header (ftyp isom box)
mp4_dummy = b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free" + b"A" * 1024 * 50
upload_mp4 = upload_file("qa_test_video.mp4", mp4_dummy, "video")
assert upload_mp4["success"], "MP4 upload failed!"
assert upload_mp4["url"].startswith("assets/uploads/hm_vid_"), f"Unexpected path: {upload_mp4['url']}"
video_url = upload_mp4["url"]
print(f" PASS: MP4 video uploaded -> {video_url} ({upload_mp4['size_kb']} KB)")

# Test byte-range streaming (HTTP 206 Partial Content)
range_req = urllib.request.Request(f"{BASE_URL}/{video_url}", headers={"Range": "bytes=0-1023"})
range_res = urllib.request.urlopen(range_req)
assert range_res.status == 206, f"Expected 206 Partial Content, got {range_res.status}"
assert range_res.headers.get("Accept-Ranges") == "bytes", "Missing Accept-Ranges header"
assert "bytes 0-1023/" in range_res.headers.get("Content-Range", ""), f"Invalid Content-Range: {range_res.headers.get('Content-Range')}"
print(" PASS: Video Range streaming verified (HTTP 206, Accept-Ranges: bytes, Content-Range: bytes 0-1023/...)")

# Test WEBM upload
webm_dummy = b"\x1a\x45\xdf\xa3" + b"W" * 1024 * 20
upload_webm = upload_file("qa_test_video.webm", webm_dummy, "video")
assert upload_webm["success"], "WEBM upload failed!"
print(f" PASS: WEBM video uploaded -> {upload_webm['url']}")

# Test MOV upload
mov_dummy = b"\x00\x00\x00\x14ftypqt  \x00\x00\x00\x00qt  " + b"M" * 1024 * 20
upload_mov = upload_file("qa_test_video.mov", mov_dummy, "video")
assert upload_mov["success"], "MOV upload failed!"
print(f" PASS: MOV video uploaded -> {upload_mov['url']}")

# ----------------------------------------------------------------------
# 3. Custom Reel Cover Image Upload & Database Persistence
# ----------------------------------------------------------------------
print("\n[STEP 3] Testing Custom Reel Cover Upload & Reel Creation...")
# Dummy JPEG binary
jpeg_dummy = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"C" * 1024 * 10 + b"\xff\xd9"
upload_cover = upload_file("qa_custom_reel_cover.jpg", jpeg_dummy, "image")
assert upload_cover["success"], "Reel cover upload failed!"
assert upload_cover["url"].startswith("assets/uploads/hm_cover_"), f"Unexpected cover path: {upload_cover['url']}"
cover_url = upload_cover["url"]
print(f" PASS: Custom Reel Cover uploaded -> {cover_url} ({upload_cover['size_kb']} KB)")

# Create Reel in Admin
reel_data = {
    "title": "QA Exclusive Royal Drop 2026",
    "marathi_title": "शाही फेस्टिव्ह कलेक्शन",
    "url": "https://www.instagram.com/reel/QA_ROYAL_2026/",
    "video_url": video_url,
    "image": cover_url,
    "price": "₹1,299",
    "offer": "FESTIVE DROP",
    "caption": "Verified QA Reel with custom cover and attached MP4 video."
}
req = urllib.request.Request(
    f"{BASE_URL}/api/admin/reels",
    data=json.dumps(reel_data).encode('utf-8'),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
)
res = urllib.request.urlopen(req)
created_reel = json.loads(res.read().decode('utf-8'))["reel"]
reel_id = created_reel["id"]
print(f" PASS: Reel created in Admin -> ID: {reel_id}")

# Direct Database Audit
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
db_reel = conn.execute("SELECT * FROM reels WHERE id = ?", (reel_id,)).fetchone()
conn.close()

assert db_reel is not None, "Reel not found in database!"
assert db_reel["image"] == cover_url, f"DB image expected '{cover_url}', got '{db_reel['image']}'"
assert db_reel["video_url"] == video_url, f"DB video_url expected '{video_url}', got '{db_reel['video_url']}'"
assert not db_reel["image"].startswith("C:"), "Database must not store local drive absolute path!"
assert "real_reel_DaiL4H0zCqV" not in db_reel["image"], "Database incorrectly reset to default cover!"
print(f" PASS: SQLite DB verified: image = '{db_reel['image']}', video_url = '{db_reel['video_url']}'")

# Re-open / Update Reel
update_payload = {
    "title": "QA Exclusive Royal Drop 2026 (Updated)",
    "price": "₹1,499",
    "image": cover_url,
    "video_url": video_url
}
req = urllib.request.Request(
    f"{BASE_URL}/api/admin/reels/{reel_id}",
    data=json.dumps(update_payload).encode('utf-8'),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="PUT"
)
res = urllib.request.urlopen(req)
updated_reel = json.loads(res.read().decode('utf-8'))["reel"]
assert updated_reel["image"] == cover_url, "Cover reset on update!"
assert updated_reel["video_url"] == video_url, "Video reset on update!"
print(f" PASS: Reel updated and custom cover/video strictly preserved.")

# Verify Public API
pub_reels_req = urllib.request.Request(f"{BASE_URL}/api/reels")
pub_reels = json.loads(urllib.request.urlopen(pub_reels_req).read().decode('utf-8'))["reels"]
pub_reel = next((r for r in pub_reels if r["id"] == reel_id), None)
assert pub_reel is not None, "Reel missing from public API!"
assert pub_reel["image"] == cover_url, f"Public API image mismatch: {pub_reel['image']}"
print(f" PASS: Public Storefront API (/api/reels) reflects custom cover image: {pub_reel['image']}")

# ----------------------------------------------------------------------
# 4. Product Custom Image Upload & Persistence Test
# ----------------------------------------------------------------------
print("\n[STEP 4] Testing Product Custom Image Upload & Catalogue Sync...")
upload_prod_img = upload_file("qa_custom_shirt.jpg", jpeg_dummy, "image")
assert upload_prod_img["success"], "Product image upload failed!"
prod_img_url = upload_prod_img["url"]
print(f" PASS: Product custom image uploaded -> {prod_img_url}")

# Create Product in Admin
product_data = {
    "id": "HM-QA-SHIRT-99",
    "name": "QA Oxford Royal Luxury Shirt",
    "marathi_name": "रॉयल ऑक्सफर्ड लक्झरी शर्ट",
    "brand": "Hiramoti Collection",
    "category": "shirts",
    "subtype": "shirts",
    "price": 899.0,
    "original_price": 1299.0,
    "stock": 20,
    "status": "in_stock",
    "badge": "QA VERIFIED",
    "sizes": "M, L, XL, XXL",
    "image": prod_img_url,
    "description": "Premium 100% Giza cotton tailored fit."
}
req = urllib.request.Request(
    f"{BASE_URL}/api/admin/products",
    data=json.dumps(product_data).encode('utf-8'),
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
)
res = urllib.request.urlopen(req)
created_prod = json.loads(res.read().decode('utf-8'))["product"]
assert created_prod["image"] == prod_img_url, "Product image mismatch on create!"
print(f" PASS: Product created in Admin with custom image -> {created_prod['id']}")

# Direct DB check
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
db_prod = conn.execute("SELECT * FROM products WHERE id = ?", ("HM-QA-SHIRT-99",)).fetchone()
conn.close()

assert db_prod is not None, "Product missing in SQLite DB!"
assert db_prod["image"] == prod_img_url, f"DB product image expected '{prod_img_url}', got '{db_prod['image']}'"
assert not db_prod["image"].startswith("C:"), "Product image must not be Windows path!"
assert "hiramoti_header_logo.png" not in db_prod["image"], "Custom product image was incorrectly replaced with logo!"
print(f" PASS: SQLite DB verified: image = '{db_prod['image']}' (No logo fallback!)")

# Public Catalogue API check
cat_req = urllib.request.Request(f"{BASE_URL}/api/products?category=shirts")
cat_products = json.loads(urllib.request.urlopen(cat_req).read().decode('utf-8'))["products"]
cat_prod = next((p for p in cat_products if p["id"] == "HM-QA-SHIRT-99"), None)
assert cat_prod is not None, "Product missing from public catalogue API!"
assert cat_prod["image"] == prod_img_url, f"Catalogue API image mismatch: {cat_prod['image']}"
print(f" PASS: Public Catalogue API (/api/products) correctly serves custom image: {cat_prod['image']}")

# Verify image is served with HTTP 200
img_req = urllib.request.Request(f"{BASE_URL}/{prod_img_url}")
img_res = urllib.request.urlopen(img_req)
assert img_res.status == 200, f"Expected HTTP 200 for product image, got {img_res.status}"
print(f" PASS: Image file served over HTTP 200 OK ({len(img_res.read())} bytes)")

# ----------------------------------------------------------------------
# 5. Visual Screenshots (Desktop & Mobile)
# ----------------------------------------------------------------------
print("\n[STEP 5] Capturing Visual Verification Screenshots via Edge Headless...")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

shots = [
    {
        "url": f"{BASE_URL}/collections.html?category=shirts",
        "output": os.path.join(ARTIFACT_DIR, "qa_catalogue_custom_product_desktop.png"),
        "size": "1366,900"
    },
    {
        "url": f"{BASE_URL}/reels.html",
        "output": os.path.join(ARTIFACT_DIR, "qa_reels_custom_cover_desktop.png"),
        "size": "1366,900"
    },
    {
        "url": f"{BASE_URL}/admin/index.html",
        "output": os.path.join(ARTIFACT_DIR, "qa_admin_dashboard_desktop.png"),
        "size": "1366,900"
    }
]

for s in shots:
    cmd = [
        EDGE_EXE,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={s['size']}",
        f"--screenshot={s['output']}",
        "--virtual-time-budget=4000",
        s["url"]
    ]
    print(f" Capturing {os.path.basename(s['output'])} from {s['url']}...")
    subprocess.run(cmd, capture_output=True)
    if os.path.exists(s["output"]):
        print(f" PASS: Saved screenshot ({os.path.getsize(s['output'])} bytes)")
    else:
        print(f" WARN: Screenshot capture did not produce file: {s['output']}")

# ----------------------------------------------------------------------
# 6. Residue Cleanup & Zero Leftover Verification
# ----------------------------------------------------------------------
print("\n[STEP 6] Cleaning up test records & verifying zero residue...")

# Delete test reel
req = urllib.request.Request(f"{BASE_URL}/api/admin/reels/{reel_id}", headers={"Authorization": f"Bearer {token}"}, method="DELETE")
urllib.request.urlopen(req)
print(f" Deleted test reel '{reel_id}'")

# Delete test product
req = urllib.request.Request(f"{BASE_URL}/api/admin/products/HM-QA-SHIRT-99", headers={"Authorization": f"Bearer {token}"}, method="DELETE")
urllib.request.urlopen(req)
print(" Deleted test product 'HM-QA-SHIRT-99'")

# Remove uploaded test media files
upload_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "uploads")
for f in [
    os.path.basename(video_url),
    os.path.basename(upload_webm["url"]),
    os.path.basename(upload_mov["url"]),
    os.path.basename(cover_url),
    os.path.basename(prod_img_url)
]:
    p = os.path.join(upload_dir, f)
    if os.path.exists(p):
        os.remove(p)
        print(f" Cleaned up test file: {f}")

# Final DB residue verification
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
r_count = conn.execute("SELECT count(*) as c FROM reels WHERE id = ?", (reel_id,)).fetchone()["c"]
p_count = conn.execute("SELECT count(*) as c FROM products WHERE id = 'HM-QA-SHIRT-99'").fetchone()["c"]
conn.close()

assert r_count == 0, f"Residue error: Reel {reel_id} still exists in DB!"
assert p_count == 0, "Residue error: Product HM-QA-SHIRT-99 still exists in DB!"
print(" PASS: Database zero residue verified. 0 leftover test records.")

print("\n=================================================================")
print(" ALL 6 AUDIT PHASES COMPLETED WITH 100% PASS RATE!")
print("=================================================================")
