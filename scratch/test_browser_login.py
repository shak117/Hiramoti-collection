import subprocess
import time
import json
import base64
import os
import urllib.request
import websocket

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ARTIFACT_DIR = r"C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12"

def main():
    # 1. Launch Edge with remote debugging
    cmd = [
        EDGE_PATH,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,900",
        "--user-data-dir=" + os.path.join(ARTIFACT_DIR, "edge_profile")
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)

    try:
        # 2. Get WebSocket debugger URL
        try:
            resp = urllib.request.urlopen("http://localhost:9222/json/list")
            targets = json.loads(resp.read().decode())
            ws_url = targets[0]["webSocketDebuggerUrl"]
        except Exception:
            req = urllib.request.Request("http://localhost:9222/json/new", method="PUT")
            resp = urllib.request.urlopen(req)
            target = json.loads(resp.read().decode())
            ws_url = target["webSocketDebuggerUrl"]
        
        ws = websocket.create_connection(ws_url)
        msg_id = 1

        def send_cdp(method, params=None):
            nonlocal msg_id
            m = {"id": msg_id, "method": method, "params": params or {}}
            msg_id += 1
            ws.send(json.dumps(m))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == m["id"]:
                    return r.get("result", {})

        send_cdp("Page.enable")
        send_cdp("Runtime.enable")

        # 3. Navigate to admin login
        send_cdp("Page.navigate", {"url": "http://localhost:5000/admin/login"})
        time.sleep(2)

        # 4. Fill credentials and click submit
        login_script = """
        (() => {
            const u = document.getElementById("login-username");
            const p = document.getElementById("login-password");
            const f = document.getElementById("login-form");
            if (u && p && f) {
                u.value = "admin@hiramoti.com";
                p.value = "Hiramoti@1987";
                f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                return "SUBMITTED";
            }
            return "NOT_FOUND";
        })()
        """
        res = send_cdp("Runtime.evaluate", {"expression": login_script, "returnByValue": True})
        print("Login script evaluation:", res)

        time.sleep(2.5)

        # Check if dashboard is visible
        check_script = """
        (() => {
            const d = document.getElementById("dashboard-view");
            const role = document.getElementById("user-role-badge");
            const name = document.getElementById("user-display-name");
            return {
                dashboard_display: d ? window.getComputedStyle(d).display : null,
                role: role ? role.textContent : null,
                username: name ? name.textContent : null
            };
        })()
        """
        check_res = send_cdp("Runtime.evaluate", {"expression": check_script, "returnByValue": True})
        print("Dashboard check result:", check_res)

        # 5. Capture Desktop Screenshot (1440x900)
        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_path = os.path.join(ARTIFACT_DIR, "dashboard_desktop_1440px.png")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Saved: {out_path}")

        # 6. Capture Mobile Screenshot (375x812)
        send_cdp("Emulation.setDeviceMetricsOverride", {
            "width": 375,
            "height": 812,
            "deviceScaleFactor": 2,
            "mobile": True
        })
        time.sleep(1)
        shot_mobile = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_mobile:
            out_path_mobile = os.path.join(ARTIFACT_DIR, "dashboard_mobile_375px.png")
            with open(out_path_mobile, "wb") as f:
                f.write(base64.b64decode(shot_mobile["data"]))
            print(f"[PASS] Saved: {out_path_mobile}")

        # 7. Test open edit product modal and take screenshot
        edit_script = """
        (() => {
            showSection('products');
            setTimeout(() => {
                if (cachedProducts && cachedProducts.length > 0) {
                    openEditProductModal(cachedProducts[0].id);
                }
            }, 500);
        })()
        """
        send_cdp("Runtime.evaluate", {"expression": edit_script})
        time.sleep(1.5)

        shot_modal = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_modal:
            out_path_modal = os.path.join(ARTIFACT_DIR, "product_modal_mobile_375px.png")
            with open(out_path_modal, "wb") as f:
                f.write(base64.b64decode(shot_modal["data"]))
            print(f"[PASS] Saved: {out_path_modal}")

        ws.close()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
