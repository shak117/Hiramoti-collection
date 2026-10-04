import subprocess, time, json, websocket, urllib.request, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = tempfile.mkdtemp()
proc = subprocess.Popen([
    edge_path,
    '--headless=new',
    '--disable-gpu',
    f'--user-data-dir={user_data}',
    '--remote-allow-origins=*',
    '--remote-debugging-port=9390',
    'about:blank'
])
time.sleep(2.5)

try:
    tabs = json.loads(urllib.request.urlopen('http://localhost:9390/json').read().decode())
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'], timeout=10)

    # Enable Console & Runtime
    ws.send(json.dumps({"id": 1, "method": "Console.enable"}))
    ws.recv()
    ws.send(json.dumps({"id": 2, "method": "Runtime.enable"}))
    ws.recv()

    # Navigate
    ws.send(json.dumps({
        "id": 3,
        "method": "Page.navigate",
        "params": {"url": "http://127.0.0.1:5000/collections.html"}
    }))

    start = time.time()
    while time.time() - start < 6:
        try:
            ws.settimeout(0.5)
            raw = ws.recv()
            msg = json.loads(raw)
            method = msg.get("method", "")
            if "Console" in method or "exception" in method or "Runtime" in method:
                print(f"EVENT [{method}]:", json.dumps(msg.get("params", {}), indent=2))
        except:
            pass

    # Now evaluate cards count
    ws.settimeout(5)
    ws.send(json.dumps({
        "id": 10,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "({ cards: document.querySelectorAll('.ecommerce-product-card').length, innerSnippet: document.getElementById('catalog-products-grid')?.innerHTML?.slice(0, 150) })",
            "returnByValue": True
        }
    }))
    while True:
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get("id") == 10:
            print("FINAL EVAL:", msg.get("result", {}).get("result", {}).get("value"))
            break
finally:
    proc.terminate()
    proc.wait()
    try:
        shutil.rmtree(user_data, ignore_errors=True)
    except:
        pass
