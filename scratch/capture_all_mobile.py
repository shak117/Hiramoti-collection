import subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

user_data = tempfile.mkdtemp()
port = 9240

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

    msg_id = 0
    def send_cdp(method, params=None):
        global msg_id
        msg_id += 1
        curr_id = msg_id
        ws.send(json.dumps({
            "id": curr_id,
            "method": method,
            "params": params or {}
        }))
        while True:
            resp = json.loads(ws.recv())
            if resp.get("id") == curr_id:
                return resp.get("result", {})

    # Set mobile viewport
    send_cdp("Emulation.setDeviceMetricsOverride", {
        "width": 375,
        "height": 812,
        "deviceScaleFactor": 2,
        "mobile": True
    })

    pages = [
        ('about.html', 'cdp_about_375.png'),
        ('collections.html', 'cdp_collections_375.png'),
        ('index.html', 'cdp_home_375.png'),
        ('contact.html', 'cdp_contact_375.png')
    ]

    for page_name, out_filename in pages:
        url = f'http://localhost:5000/{page_name}'
        send_cdp("Page.navigate", {"url": url})
        time.sleep(1.5)
        res = send_cdp("Page.captureScreenshot", {"format": "png"})
        img_data = base64.b64decode(res["data"])
        out_path = os.path.join(brain_dir, out_filename)
        with open(out_path, "wb") as f:
            f.write(img_data)
        print(f"Captured {page_name} -> {out_filename}", flush=True)

    ws.close()
finally:
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        pass
    shutil.rmtree(user_data, ignore_errors=True)

print("Done all captures!", flush=True)
