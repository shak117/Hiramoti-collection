import subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture_admin(section_name, filename, port=9360):
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
            "params": {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False}
        }))
        ws.recv()

        ws.send(json.dumps({
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": "http://localhost:5000/admin/index.html"}
        }))
        time.sleep(2.5)

        # Login and navigate to section
        eval_code = f"""
        (async () => {{
            const res = await fetch('/api/admin/login', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{username: 'admin@hiramoti.com', password: 'Hiramoti@1987'}})
            }});
            const data = await res.json();
            if (data.token) {{
                localStorage.setItem('hm_admin_token', data.token);
                currentUser = data.user;
                showDashboardUI();
                showSection('{section_name}');
            }}
        }})();
        """
        ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": eval_code}
        }))
        ws.recv()
        time.sleep(2)

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
    capture_admin("categories", "verify_admin_categories_table.png", port=9361)
    capture_admin("discounts", "verify_admin_discounts_table.png", port=9362)
