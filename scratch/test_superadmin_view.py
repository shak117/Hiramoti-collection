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
    cmd = [
        EDGE_PATH,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,900",
        "--user-data-dir=" + os.path.join(ARTIFACT_DIR, "edge_profile_super")
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2)

    try:
        resp = urllib.request.urlopen("http://localhost:9222/json/list")
        targets = json.loads(resp.read().decode())
        ws_url = targets[0]["webSocketDebuggerUrl"]
        
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

        send_cdp("Page.navigate", {"url": "http://localhost:5000/admin/login"})
        time.sleep(2)

        # Login as superadmin
        login_script = """
        (() => {
            const u = document.getElementById("login-username");
            const p = document.getElementById("login-password");
            const f = document.getElementById("login-form");
            if (u && p && f) {
                u.value = "superadmin@hiramoti.com";
                p.value = "Hiramoti@1987";
                f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                return "SUBMITTED";
            }
            return "NOT_FOUND";
        })()
        """
        send_cdp("Runtime.evaluate", {"expression": login_script})
        time.sleep(2.5)

        check_script = """
        (() => {
            const role = document.getElementById("user-role-badge");
            const name = document.getElementById("user-display-name");
            return {
                role: role ? role.textContent : null,
                roleClass: role ? role.className : null,
                username: name ? name.textContent : null
            };
        })()
        """
        check_res = send_cdp("Runtime.evaluate", {"expression": check_script, "returnByValue": True})
        print("Super admin check result:", check_res)

        shot = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot:
            out_path = os.path.join(ARTIFACT_DIR, "dashboard_superadmin_1440px.png")
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"[PASS] Saved: {out_path}")

        ws.close()

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
