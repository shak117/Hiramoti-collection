import urllib.request
import json

base = "http://127.0.0.1:5000"

def test_login(username, password):
    url = f"{base}/api/admin/login"
    payload = json.dumps({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Login SUCCESS for {username}: role={data.get('user', {}).get('role')}, token={bool(data.get('token'))}")
        return data.get("token")

if __name__ == "__main__":
    test_login("admin@hiramoti.com", "Hiramoti@1987")
    test_login("superadmin@hiramoti.com", "Hiramoti@1987")
