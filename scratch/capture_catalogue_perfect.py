import subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture(url, filename, width=1440, height=900, port=9400):
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

        # Wait for cards to render
        start = time.time()
        while time.time() - start < 10:
            time.sleep(0.5)
            ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {
                    "expression": "document.querySelectorAll('.ecommerce-product-card').length",
                    "returnByValue": True
                }
            }))
            res = json.loads(ws.recv())
            cards_count = res.get("result", {}).get("result", {}).get("value", 0)
            if cards_count > 0:
                print(f"Cards rendered: {cards_count}")
                break

        # Give images a brief moment to decode
        time.sleep(1.0)

        # Screenshot
        ws.send(json.dumps({
            "id": 4,
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        }))

        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 4:
                img_data = base64.b64decode(msg["result"]["data"])
                out_path = os.path.join(brain_dir, filename)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"Saved: {filename} ({len(img_data)} bytes)")
                break

        ws.close()
    finally:
        proc.terminate()
        proc.wait()
        try:
            shutil.rmtree(user_data, ignore_errors=True)
        except:
            pass

if __name__ == '__main__':
    print("1. Desktop All Collections...")
    capture("http://127.0.0.1:5000/collections.html", "verify_catalogue_desktop_perfect.png", width=1440, height=900, port=9401)
    
    print("2. Desktop Hosiery 10% OFF...")
    capture("http://127.0.0.1:5000/collections.html?category=hosiery", "verify_catalogue_hosiery_perfect.png", width=1440, height=900, port=9402)

    print("3. Mobile All Collections...")
    capture("http://127.0.0.1:5000/collections.html", "verify_catalogue_mobile_perfect.png", width=375, height=812, port=9403)

    print("4. Mobile Hosiery 10% OFF...")
    capture("http://127.0.0.1:5000/collections.html?category=hosiery", "verify_catalogue_hosiery_mobile_perfect.png", width=375, height=812, port=9404)
