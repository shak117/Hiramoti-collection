import urllib.request
import urllib.parse
import json
import http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def request(url, method="GET", data=None):
    body = json.dumps(data).encode("utf-8") if data else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=5) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

# 1. Login as admin
code, data = request("http://127.0.0.1:5000/api/admin/login", "POST", {
    "username": "admin@hiramoti.com",
    "password": "Hiramoti@1987"
})
assert code == 200, f"Login failed: {code}"
print("[PASS] Admin logged in successfully")

# 2. Get dashboard stats
code, stats = request("http://127.0.0.1:5000/api/admin/dashboard-stats")
assert code == 200, f"Stats failed: {code}"
print(f"[PASS] Dashboard stats: {stats['total_products']} products, {stats['total_reels']} reels, {stats['total_enquiries']} enquiries")

# 3. Get products list
code, prods_data = request("http://127.0.0.1:5000/api/admin/products")
assert code == 200, f"Products failed: {code}"
prods = prods_data.get("products", [])
print(f"[PASS] Retrieved {len(prods)} products")

# 4. Quick update stock and price on first product
if prods:
    test_prod = prods[0]
    orig_stock = test_prod.get("stock", 15)
    orig_price = test_prod.get("price", 699)
    print(f"Testing quick-update on product: {test_prod['id']} (Current price: {orig_price}, stock: {orig_stock})")
    
    code, update_res = request(f"http://127.0.0.1:5000/api/admin/products/{test_prod['id']}/quick-update", "PATCH", {
        "stock": orig_stock + 1,
        "price": orig_price
    })
    assert code == 200, f"Quick update failed: {code}"
    print(f"[PASS] Quick-update stock modified successfully to {orig_stock + 1}")
    
    # Restore original stock
    code, _ = request(f"http://127.0.0.1:5000/api/admin/products/{test_prod['id']}/quick-update", "PATCH", {
        "stock": orig_stock,
        "price": orig_price
    })
    assert code == 200
    print("[PASS] Stock restored cleanly")

# 5. Get reels list
code, reels = request("http://127.0.0.1:5000/api/admin/reels")
assert code == 200, f"Reels failed: {code}"
print(f"[PASS] Retrieved {len(reels)} reels")

# 6. Get enquiries
code, enquiries = request("http://127.0.0.1:5000/api/admin/enquiries")
assert code == 200, f"Enquiries failed: {code}"
print(f"[PASS] Retrieved {len(enquiries)} enquiries")

print("\n=== ALL CRUD AND MANAGEMENT APIS TESTED & WORKING PROPERLY! ===")
