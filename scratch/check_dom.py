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
    profile = os.path.join(ARTIFACT_DIR, "edge_profile_check")
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

        send_cdp("Page.navigate", {"url": "http://localhost:5000/"})
        # Wait until document.readyState is complete
        for _ in range(20):
            res = send_cdp("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
            if res.get("result", {}).get("value") == "complete":
                break
            time.sleep(0.5)

        eval_script = """
        (() => {
            const adminLinks = Array.from(document.querySelectorAll('a.footer-admin-link')).map(a => ({href: a.href, text: a.textContent}));
            const superLinks = Array.from(document.querySelectorAll('a.footer-superadmin-link')).map(a => ({href: a.href, text: a.textContent}));
            return {
                title: document.title,
                url: window.location.href,
                adminLinks,
                superLinks
            };
        })()
        """
        res = send_cdp("Runtime.evaluate", {"expression": eval_script, "returnByValue": True})
        print("DOM evaluation on http://localhost:5000/:", res.get("result", {}).get("value"))

        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
