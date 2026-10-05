import urllib.request
import json
import subprocess
import os

login_payload = json.dumps({"username": "admin@hiramoti.com", "password": "Hiramoti@1987"}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:5000/api/admin/login", data=login_payload, headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
token = json.loads(res.read().decode('utf-8'))["token"]

edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
art_dir = r"C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12"

shots = [
    {
        "url": f"http://127.0.0.1:5000/admin/index.html?token={token}&action=add-reel",
        "out": os.path.join(art_dir, "qa_admin_add_reel_modal.png")
    },
    {
        "url": f"http://127.0.0.1:5000/admin/index.html?token={token}&action=edit-reel&id=reel-1",
        "out": os.path.join(art_dir, "qa_admin_edit_reel_modal.png")
    },
    {
        "url": f"http://127.0.0.1:5000/admin/index.html?token={token}&action=add-product",
        "out": os.path.join(art_dir, "qa_admin_add_product_modal.png")
    }
]

for s in shots:
    cmd = [
        edge,
        "--headless=new",
        "--disable-gpu",
        "--window-size=1366,950",
        f"--screenshot={s['out']}",
        "--virtual-time-budget=5000",
        s["url"]
    ]
    subprocess.run(cmd, capture_output=True)
    print(os.path.basename(s["out"]), "->", os.path.exists(s["out"]), os.path.getsize(s["out"]) if os.path.exists(s["out"]) else 0)
