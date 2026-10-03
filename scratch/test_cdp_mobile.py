import subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

user_data = tempfile.mkdtemp()
port = 9235

proc = subprocess.Popen([
    edge_path,
    '--headless=new',
    '--disable-gpu',
    f'--user-data-dir={user_data}',
    '--remote-allow-origins=*',
    f'--remote-debugging-port={port}',
    'about:blank'
])

time.sleep(2)
try:
    tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json').read().decode())
    ws_url = tabs[0]['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url)
    
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

    pages = [
        ('about.html', 'cdp_about_375.png'),
        ('collections.html', 'cdp_collections_375.png'),
        ('index.html', 'cdp_home_375.png'),
        ('contact.html', 'cdp_contact_375.png')
    ]

    msg_id = 10
    for page_name, out_filename in pages:
        url = f'http://localhost:5000/{page_name}'
        msg_id += 1
        ws.send(json.dumps({
            "id": msg_id,
            "method": "Page.navigate",
            "params": {"url": url}
        }))
        # Wait a moment for page load
        time.sleep(1.5)
        
        # Take screenshot
        msg_id += 1
        shot_id = msg_id
        ws.send(json.dumps({
            "id": shot_id,
            "method": "Page.captureScreenshot",
            "params": {"format": "png"}
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == shot_id:
                img_data = base64.b64decode(resp["result"]["data"])
                out_path = os.path.join(brain_dir, out_filename)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"Successfully captured {page_name} to {out_filename}", flush=True)
                break
    ws.close()
finally:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        pass
    shutil.rmtree(user_data, ignore_errors=True)
print("All captures completed successfully!", flush=True)
