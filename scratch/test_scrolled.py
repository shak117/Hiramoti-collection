import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'
user_data = tempfile.mkdtemp()
port = 9330

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
    ws = websocket.create_connection(ws_url, timeout=10)

    # 1. Desktop Emulation
    ws.send(json.dumps({
        "id": 1,
        "method": "Emulation.setDeviceMetricsOverride",
        "params": {
            "width": 1440,
            "height": 900,
            "deviceScaleFactor": 1,
            "mobile": False
        }
    }))
    ws.recv()

    # 2. Navigate
    ws.send(json.dumps({
        "id": 2,
        "method": "Page.navigate",
        "params": {"url": "http://localhost:5000/gallery.html"}
    }))
    time.sleep(2)

    # 3. Scroll down 400px
    ws.send(json.dumps({
        "id": 3,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "window.scrollTo(0, 450);"
        }
    }))
    ws.recv()
    time.sleep(1)

    # 4. Capture screenshot
    ws.send(json.dumps({
        "id": 4,
        "method": "Page.captureScreenshot",
        "params": {"format": "png"}
    }))

    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 4:
            img_data = base64.b64decode(msg["result"]["data"])
            out_path = os.path.join(brain_dir, "desktop_gallery_scrolled.png")
            with open(out_path, "wb") as f:
                f.write(img_data)
            print("Successfully saved scrolled desktop:", out_path)
            break
    ws.close()
finally:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        pass
    shutil.rmtree(user_data, ignore_errors=True)
