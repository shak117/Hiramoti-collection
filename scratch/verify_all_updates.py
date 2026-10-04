import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture_page(url, filename, width=1440, height=900, scroll_to=0, eval_code=None, port=9340):
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

        # 3. Custom evaluation or scroll
        if eval_code:
            ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": eval_code}
            }))
            ws.recv()
            time.sleep(1)

        if scroll_to > 0:
            ws.send(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": f"window.scrollTo(0, {scroll_to});"}
            }))
            ws.recv()
            time.sleep(1.5)

        # 4. Capture screenshot
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
                print(f"[OK] Saved: {filename} -> {out_path}")
                break
        ws.close()
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass
        shutil.rmtree(user_data, ignore_errors=True)

if __name__ == "__main__":
    print("Capturing 1: Founder Timeline...")
    capture_page("http://localhost:5000/founder.html", "verify_founder_timeline.png", width=1440, height=900, scroll_to=650, port=9341)

    print("Capturing 2: Collections Catalog (All Products)...")
    capture_page("http://localhost:5000/collections.html", "verify_collections_catalog.png", width=1440, height=900, scroll_to=380, port=9342)

    print("Capturing 3: Collections TechnoSport 10% OFF...")
    capture_page("http://localhost:5000/collections.html?category=technosport", "verify_collections_technosport.png", width=1440, height=900, scroll_to=380, port=9343)

    print("Capturing 4: Collections Mobile 375px...")
    capture_page("http://localhost:5000/collections.html", "verify_collections_mobile.png", width=375, height=812, scroll_to=300, port=9344)

    print("Capturing 5: Admin Login Screen...")
    capture_page("http://localhost:5000/admin/login", "verify_admin_login.png", width=1440, height=900, scroll_to=0, port=9345)

    print("All captures completed!")
