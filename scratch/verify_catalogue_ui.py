import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture_page(url, filename, width=1440, height=900, scroll_to=0, eval_code=None, port=9360):
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

        # 1. Device metrics
        ws.send(json.dumps({
            "id": 1,
            "method": "Emulation.setDeviceMetricsOverride",
            "params": {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1 if width >= 1000 else 2,
                "mobile": width < 1000
            }
        }))
        ws.recv()

        # 2. Navigate
        ws.send(json.dumps({
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": url}
        }))
        time.sleep(3)

        # 3. Custom evaluation
        if eval_code:
            ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": eval_code}
            }))
            ws.recv()
            time.sleep(1.5)

        if scroll_to > 0:
            ws.send(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": f"window.scrollTo(0, {scroll_to});"}
            }))
            ws.recv()
            time.sleep(0.5)

        # 4. Screenshot
        ws.send(json.dumps({
            "id": 5,
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        }))

        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 5:
                img_data = base64.b64decode(msg["result"]["data"])
                out_path = os.path.join(brain_dir, filename)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"Captured: {out_path} ({len(img_data)} bytes)")
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
    # 1. Desktop: Catalogue main page directly opening to controls
    print("Capturing 1: Desktop catalogue top view...")
    capture_page("http://127.0.0.1:5000/collections.html", "verify_catalogue_direct_desktop.png", width=1440, height=900, port=9361)

    # 2. Desktop: Hosiery filtered view
    print("Capturing 2: Desktop Hosiery filtered view...")
    capture_page("http://127.0.0.1:5000/collections.html?category=hosiery", "verify_catalogue_hosiery_desktop.png", width=1440, height=900, port=9362)

    # 3. Mobile: Catalogue top view
    print("Capturing 3: Mobile catalogue view...")
    capture_page("http://127.0.0.1:5000/collections.html", "verify_catalogue_mobile_direct.png", width=375, height=812, port=9363)

    # 4. Mobile: Hosiery view
    print("Capturing 4: Mobile Hosiery view...")
    capture_page("http://127.0.0.1:5000/collections.html?category=hosiery", "verify_catalogue_hosiery_mobile.png", width=375, height=812, port=9364)
