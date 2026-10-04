import subprocess, time, json, websocket, base64, urllib.request, os, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
brain_dir = r'C:\Users\Admin1\.gemini\antigravity\brain\308e7e6e-37b1-432a-ae90-5d626e94ce12'

viewports = [
    (375, 812, "offers_375.png"),
    (390, 844, "offers_390.png"),
    (414, 896, "offers_414.png"),
    (768, 1024, "offers_768.png"),
    (1024, 768, "offers_1024.png"),
    (1280, 800, "offers_1280.png"),
    (1440, 900, "offers_1440.png"),
    (1920, 1080, "offers_1920.png")
]

def capture_viewport(w, h, filename, port=9450):
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
    time.sleep(2.2)
    try:
        tabs = json.loads(urllib.request.urlopen(f'http://localhost:{port}/json', timeout=5).read().decode())
        ws_url = tabs[0]['webSocketDebuggerUrl']
        ws = websocket.create_connection(ws_url, timeout=15)

        # 1. Device metrics
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

        # 2. Navigate
        ws.send(json.dumps({
            "id": 2,
            "method": "Page.navigate",
            "params": {"url": "http://127.0.0.1:5000/catalog.html"}
        }))
        time.sleep(2.5)

        # 3. Check overflow & get page info
        ws.send(json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {
                "expression": """
                (() => {
                    const scrollWidth = document.documentElement.scrollWidth;
                    const innerWidth = window.innerWidth;
                    const hasOverflow = scrollWidth > innerWidth + 1;
                    const offerCards = document.querySelectorAll('.offers-main-layout div[style*="border-radius"]').length;
                    const title = document.querySelector('.section-title')?.textContent;
                    return JSON.stringify({
                        viewport: `${window.innerWidth}x${window.innerHeight}`,
                        scrollWidth,
                        innerWidth,
                        hasOverflow,
                        title,
                        cardsFound: offerCards
                    });
                })()
                """,
                "returnByValue": True
            }
        }))
        eval_res = json.loads(ws.recv())
        val_str = eval_res.get("result", {}).get("result", {}).get("value", "{}")
        print(f"[{w}x{h}] Eval:", val_str)

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
                out_path = os.path.join(brain_dir, filename)
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"[{w}x{h}] Saved screenshot: {filename} ({len(img_data)} bytes)")
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
    for idx, (w, h, fn) in enumerate(viewports):
        port = 9450 + idx
        print(f"Testing viewport {w}x{h} -> {fn}...")
        capture_viewport(w, h, fn, port=port)
