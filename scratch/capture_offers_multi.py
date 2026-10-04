import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture(w, h, filename, port=9480):
    user_data = tempfile.mkdtemp()
    proc = subprocess.Popen([
        edge_path,
        '--headless=new',
        '--disable-gpu',
        f'--user-data-dir={user_data}',
        '--remote-allow-origins=*',
        f'--remote-debugging-port={port}',
        'about:blank'
    ])
    time.sleep(2.5)
    try:
        tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json', timeout=5).read().decode())
        ws_url = tabs[0]['webSocketDebuggerUrl']
        ws = websocket.create_connection(ws_url, timeout=15)

        ws.send(json.dumps({
            "id": 1,
            "method": "Emulation.setDeviceMetricsOverride",
            "params": {
                "width": w,
                "height": h,
                "deviceScaleFactor": 1 if w >= 1000 else 2,
                "mobile": w < 1000
            }
        }))
        ws.recv()

        ws.send(json.dumps({
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": "http://127.0.0.1:5000/catalog.html"}
        }))
        time.sleep(3.0)

        # Check overflow
        ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "({ scrollWidth: document.documentElement.scrollWidth, innerWidth: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth })",
                "returnByValue": True
            }
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == 3:
                print(f"[{w}x{h}] Overflow check:", resp.get("result", {}).get("result", {}).get("value"))
                break

        ws.send(json.dumps({
            "id": 4,
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        }))

        while True:
            resp = json.loads(ws.recv())
            if "result" in resp and "data" in resp["result"]:
                out_path = os.path.join(brain_dir, filename)
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(resp["result"]["data"]))
                print(f"Successfully saved: {out_path}")
                break

        ws.close()
    finally:
        proc.terminate()
        proc.wait()
        try:
            shutil.rmtree(user_data, ignore_errors=True)
        except Exception:
            pass

if __name__ == '__main__':
    targets = [
        (1440, 900, "offers_desktop_1440.png", 9481),
        (1024, 768, "offers_tablet_1024.png", 9482),
        (768, 1024, "offers_tablet_768.png", 9483),
        (390, 844, "offers_mobile_390.png", 9484),
        (1920, 1080, "offers_desktop_1920.png", 9485),
    ]
    for w, h, fn, p in targets:
        print(f"Capturing {w}x{h} -> {fn}...")
        capture(w, h, fn, port=p)
