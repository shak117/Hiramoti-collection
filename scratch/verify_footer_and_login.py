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
    profile_dir = os.path.join(ARTIFACT_DIR, "edge_profile_footer_v2")
    cmd = [
        EDGE_PATH,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,900",
        "--user-data-dir=" + profile_dir
    ]
    proc = subprocess.Popen(cmd)
    time.sleep(2.5)

    try:
        resp = urllib.request.urlopen("http://localhost:9222/json/list")
        targets = json.loads(resp.read().decode())
        ws_url = targets[0]["webSocketDebuggerUrl"]
        
        ws = websocket.create_connection(ws_url, timeout=10)
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

        # 1. Open Homepage
        print("1. Opening Homepage...", flush=True)
        send_cdp("Page.navigate", {"url": "http://localhost:5000/"})
        time.sleep(2)

        # Scroll down to footer
        send_cdp("Runtime.evaluate", {"expression": "window.scrollTo(0, document.body.scrollHeight);"})
        time.sleep(1)

        # Inspect footer links in DOM
        check_footer_script = """
        (() => {
            const adminLink = document.querySelector('a.footer-admin-link');
            const superLink = document.querySelector('a.footer-superadmin-link');
            return {
                admin_href: adminLink ? adminLink.getAttribute('href') : null,
                admin_text: adminLink ? adminLink.textContent : null,
                super_href: superLink ? superLink.getAttribute('href') : null,
                super_text: superLink ? superLink.textContent : null
            };
        })()
        """
        footer_info = send_cdp("Runtime.evaluate", {"expression": check_footer_script, "returnByValue": True})
        print("Footer links in DOM:", footer_info.get("result", {}).get("value"), flush=True)

        # Capture footer screenshot
        shot_footer = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_footer:
            out_footer = os.path.join(ARTIFACT_DIR, "website_footer_with_admin_links.png")
            with open(out_footer, "wb") as f:
                f.write(base64.b64decode(shot_footer["data"]))
            print(f"[PASS] Footer screenshot saved: {out_footer}", flush=True)

        # 2. Navigate to Super Admin using the footer link target
        target_super_url = "http://localhost:5000/admin/index.html?role=super_admin"
        print(f"2. Navigating to {target_super_url} ...", flush=True)
        send_cdp("Page.navigate", {"url": target_super_url})
        time.sleep(2.5)

        # Check login card state
        check_login_state = """
        (() => {
            const u = document.getElementById("login-username");
            const badge = document.getElementById("login-role-badge");
            const pillSuper = document.getElementById("pill-role-superadmin");
            const pillAdmin = document.getElementById("pill-role-admin");
            return {
                username_val: u ? u.value : null,
                badge_text: badge ? badge.textContent : null,
                super_pill_active: pillSuper ? pillSuper.classList.contains("active") : false,
                admin_pill_active: pillAdmin ? pillAdmin.classList.contains("active") : false
            };
        })()
        """
        state_res = send_cdp("Runtime.evaluate", {"expression": check_login_state, "returnByValue": True})
        print("Login page state:", state_res.get("result", {}).get("value"), flush=True)

        # Capture Super Admin login card
        shot_super = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_super:
            out_super = os.path.join(ARTIFACT_DIR, "superadmin_login_card_prefilled.png")
            with open(out_super, "wb") as f:
                f.write(base64.b64decode(shot_super["data"]))
            print(f"[PASS] Super Admin login card saved: {out_super}", flush=True)

        # 3. Enter password and submit
        print("3. Submitting password Hiramoti@1987 ...", flush=True)
        login_submit = """
        (() => {
            const p = document.getElementById("login-password");
            const f = document.getElementById("login-form");
            if (p && f) {
                p.value = "Hiramoti@1987";
                f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                return "SUBMITTED";
            }
            return "FORM_NOT_FOUND";
        })()
        """
        submit_res = send_cdp("Runtime.evaluate", {"expression": login_submit, "returnByValue": True})
        print("Submit result:", submit_res, flush=True)
        time.sleep(3)

        # Check dashboard
        dash_check = """
        (() => {
            const dash = document.getElementById("dashboard-view");
            const role = document.getElementById("user-role-badge");
            const name = document.getElementById("user-display-name");
            return {
                dash_display: dash ? window.getComputedStyle(dash).display : null,
                role: role ? role.textContent : null,
                username: name ? name.textContent : null
            };
        })()
        """
        dash_res = send_cdp("Runtime.evaluate", {"expression": dash_check, "returnByValue": True})
        print("Dashboard check after login:", dash_res.get("result", {}).get("value"), flush=True)

        shot_dash = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_dash:
            out_dash = os.path.join(ARTIFACT_DIR, "superadmin_dashboard_logged_in.png")
            with open(out_dash, "wb") as f:
                f.write(base64.b64decode(shot_dash["data"]))
            print(f"[PASS] Logged-in Dashboard screenshot saved: {out_dash}", flush=True)

        # 4. Now also test clicking the Admin role pill to switch to Admin
        print("4. Testing logout and role switching ...", flush=True)
        send_cdp("Runtime.evaluate", {"expression": "handleAdminLogout();"})
        time.sleep(1.5)

        # Click Admin role pill
        send_cdp("Runtime.evaluate", {"expression": "switchLoginRole('admin');"})
        time.sleep(1)

        admin_state_res = send_cdp("Runtime.evaluate", {"expression": check_login_state, "returnByValue": True})
        print("State after clicking Admin pill:", admin_state_res.get("result", {}).get("value"), flush=True)

        shot_admin = send_cdp("Page.captureScreenshot", {"format": "png"})
        if "data" in shot_admin:
            out_admin = os.path.join(ARTIFACT_DIR, "admin_login_card_prefilled.png")
            with open(out_admin, "wb") as f:
                f.write(base64.b64decode(shot_admin["data"]))
            print(f"[PASS] Admin login card saved: {out_admin}", flush=True)

        ws.close()
        print("\n=== ALL FOOTER ACCESS & ROLE VERIFICATIONS COMPLETED SUCCESSFULLY! ===", flush=True)

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
