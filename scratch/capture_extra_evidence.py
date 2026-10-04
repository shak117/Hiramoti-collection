import sys, subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

def capture_page(url, filename, width=1440, height=900, scroll_to=0, eval_code=None, port=9350):
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
            time.sleep(1.5)

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
    print("Capturing Founder Milestones 1987 & 2006...")
    capture_page("http://localhost:5000/founder.html", "verify_founder_milestones_1987_2006.png", width=1440, height=900, scroll_to=1050, port=9351)

    print("Capturing Founder Milestone 2026 & Footer...")
    capture_page("http://localhost:5000/founder.html", "verify_founder_milestones_2026.png", width=1440, height=900, scroll_to=1850, port=9352)

    # Log in to admin and view categories
    admin_login_eval = """
    (async () => {
        const res = await fetch('/api/admin/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: 'admin@hiramoti.com', password: 'Hiramoti@1987'})
        });
        const data = await res.json();
        if (data.token) {
            localStorage.setItem('hm_admin_token', data.token);
            window.location.reload();
        }
    })();
    """
    print("Capturing Admin Dashboard...")
    capture_page("http://localhost:5000/admin/index.html", "verify_admin_categories_view.png", width=1440, height=900, scroll_to=0, eval_code=admin_login_eval, port=9353)

    print("Extra evidence capture complete!")
