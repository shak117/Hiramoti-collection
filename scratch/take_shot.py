import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

if len(sys.argv) < 3:
    print("Usage: python take_shot.py <url> <out_name> [port]")
    sys.exit(1)

url = sys.argv[1]
out_name = sys.argv[2]
port = int(sys.argv[3]) if len(sys.argv) > 3 else 9301

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'
out_path = os.path.join(brain_dir, out_name)

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
    ws = websocket.create_connection(ws_url, timeout=10)

    # 1. Emulation
    ws.send(json.dumps({
        "id": 1,
        "method": "Emulation.setDeviceMetricsOverride",
        "params": {
            "width": 375,
            "height": 812,
            "deviceScaleFactor": 2,
            "mobile": True
        }
    }))
    ws.recv()

    # 2. Navigate
    ws.send(json.dumps({
        "id": 2,
        "method": "Page.navigate",
        "params": {"url": url}
    }))
    time.sleep(2.5)

    # 3. Capture screenshot
    ws.send(json.dumps({
        "id": 3,
        "method": "Page.captureScreenshot",
        "params": {"format": "png"}
    }))

    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 3:
            img_data = base64.b64decode(msg["result"]["data"])
            with open(out_path, "wb") as f:
                f.write(img_data)
            print("Successfully saved:", out_path)
            break
    ws.close()
finally:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        pass
    shutil.rmtree(user_data, ignore_errors=True)
