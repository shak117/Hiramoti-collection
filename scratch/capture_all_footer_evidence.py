import subprocess
import time
import json
import base64
import os
import sys
import urllib.request
import websocket

sys.stdout.reconfigure(line_buffering=True)
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ARTIFACT_DIR = r"C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12"

def main():
    profile = os.path.join(ARTIFACT_DIR, "edge_profile_evidence")
    cmd = [
        EDGE_PATH,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,900",
        "--user-data-dir=" + profile
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)

    try:
        resp = urllib.request.urlopen("http://localhost:9222/json/list")
        targets = json.loads(resp.read().decode())
        ws_url = targets[0]["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url, timeout=30)
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
        send_cdp("Emulation.setDeviceMetricsOverride", {
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        })

        # 1. Open homepage and capture footer
        print("1. Loading Homepage...")
        send_cdp("Page.navigate", {"url": "http://localhost:5000/"})
        for _ in range(20):
            res = send_cdp("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
            if res.get("result", {}).get("value") == "complete":
                break
            time.sleep(0.5)

        # Scroll to footer
        send_cdp("Runtime.evaluate", {"expression": "window.scrollTo(0, document.body.scrollHeight);"})
        time.sleep(1)

        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_file = os.path.join(ARTIFACT_DIR, "footer_with_admin_and_superadmin.png")
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Footer screenshot saved: {out_file}")

        # 2. Open Super Admin login page (as if clicked from footer)
        print("2. Opening Super Admin login page via footer link URL...")
        send_cdp("Page.navigate", {"url": "http://localhost:5000/admin/index.html?role=super_admin"})
        for _ in range(20):
            res = send_cdp("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
            if res.get("result", {}).get("value") == "complete":
                break
            time.sleep(0.5)
        time.sleep(1)

        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_file = os.path.join(ARTIFACT_DIR, "login_superadmin_role_prefilled.png")
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Super Admin login card saved: {out_file}")

        # 3. Enter password and submit
        print("3. Logging in as Super Admin...")
        submit_script = """
        (() => {
            const p = document.getElementById("login-password");
            const f = document.getElementById("login-form");
            p.value = "Hiramoti@1987";
            f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            return "OK";
        })()
        """
        send_cdp("Runtime.evaluate", {"expression": submit_script})
        time.sleep(2.5)

        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_file = os.path.join(ARTIFACT_DIR, "dashboard_superadmin_verified.png")
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Super Admin dashboard saved: {out_file}")

        # 4. Open Admin login page (as if clicked Admin from footer)
        print("4. Testing Admin login page via footer link URL...")
        # First logout
        send_cdp("Runtime.evaluate", {"expression": "handleAdminLogout();"})
        time.sleep(1)
        send_cdp("Page.navigate", {"url": "http://localhost:5000/admin/index.html?role=admin"})
        time.sleep(1.5)

        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_file = os.path.join(ARTIFACT_DIR, "login_admin_role_prefilled.png")
            with open(out_file, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Admin login card saved: {out_file}")

        ws.close()
        print("\nAll verification screenshots captured successfully!")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
