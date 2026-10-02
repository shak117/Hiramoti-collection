import urllib.request
import urllib.parse
import json
import http.cookiejar
import sys

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with opener.open(req, timeout=5) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

def get(url):
    req = urllib.request.Request(url)
    try:
        with opener.open(req, timeout=5) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

print("=== TEST 1: Admin Login ===")
c, d = post("http://127.0.0.1:5000/api/admin/login", {"username": "admin@hiramoti.com", "password": "Hiramoti@1987"})
print("Status:", c)
print("User:", d.get("user"))
assert c == 200, f"Expected 200, got {c}"
assert d.get("user", {}).get("role") == "admin"

print("\n=== TEST 2: Check Session (/api/admin/me) ===")
c, d = get("http://127.0.0.1:5000/api/admin/me")
print("Status:", c)
print("Authenticated:", d.get("authenticated"))
print("Current User:", d.get("user"))
assert c == 200 and d.get("authenticated") is True

print("\n=== TEST 3: Admin Users List (/api/admin/users) ===")
c, d = get("http://127.0.0.1:5000/api/admin/users")
print("Status:", c)
print("Users:", [(u["username"], u["role"], u["is_active"]) for u in d.get("users", [])])
assert c == 200 and len(d.get("users", [])) >= 2

print("\n=== TEST 4: Super Admin Login ===")
c, d = post("http://127.0.0.1:5000/api/admin/login", {"username": "superadmin@hiramoti.com", "password": "Hiramoti@1987"})
print("Status:", c)
print("User:", d.get("user"))
assert c == 200 and d.get("user", {}).get("role") == "super_admin"

print("\n=== TEST 5: Invalid Password ===")
c, d = post("http://127.0.0.1:5000/api/admin/login", {"username": "admin@hiramoti.com", "password": "WrongPassword"})
print("Status:", c, "Response:", d)
assert c == 401

print("\n=== TEST 6: Logout & Guard ===")
c, d = post("http://127.0.0.1:5000/api/admin/logout", {})
print("Status:", c, "Response:", d)
c, d = get("http://127.0.0.1:5000/api/admin/me")
print("After logout /me status:", c)
assert c == 401

print("\n=== ALL AUTH TESTS PASSED SUCCESSFULLY! ===")
