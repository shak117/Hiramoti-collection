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
    proc = subprocess.Popen([
        EDGE_PATH,
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--headless=new",
        "--disable-gpu",
        "--window-size=1440,1200",
        "--user-data-dir=" + os.path.join(ARTIFACT_DIR, "edge_footer_clip")
    ])
    time.sleep(2)
    try:
        resp = urllib.request.urlopen("http://localhost:9222/json/list")
        ws_url = json.loads(resp.read().decode())[0]["webSocketDebuggerUrl"]
        ws = websocket.create_connection(ws_url, timeout=30)
        
        msg_id = 1
        def send(method, params=None):
            nonlocal msg_id
            m = {"id": msg_id, "method": method, "params": params or {}}
            msg_id += 1
            ws.send(json.dumps(m))
            while True:
                r = json.loads(ws.recv())
                if r.get("id") == m["id"]:
                    return r.get("result", {})
                    
        send("Page.enable")
        send("Runtime.enable")
        send("Page.navigate", {"url": "http://localhost:5000/"})
        time.sleep(2.5)

        # Scroll right to footer
        send("Runtime.evaluate", {"expression": "document.querySelector('.footer-bottom').scrollIntoView();"})
        time.sleep(1)

        # Get rect of footer-bottom
        rect_res = send("Runtime.evaluate", {
            "expression": """
            (() => {
                const f = document.querySelector('footer');
                const r = f.getBoundingClientRect();
                return { x: r.left, y: r.top, width: r.width, height: r.height };
            })()
            """,
            "returnByValue": True
        })
        rect = rect_res.get("result", {}).get("value")
        print("Footer rect:", rect)

        # Capture screenshot
        shot = send("Page.captureScreenshot", {"format": "png"})
        out_path = os.path.join(ARTIFACT_DIR, "website_footer_full_view.png")
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(shot["data"]))
        print("[PASS] Saved:", out_path)
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
