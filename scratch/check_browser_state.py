import subprocess, time, json, websocket, urllib.request, tempfile, shutil

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
user_data = tempfile.mkdtemp()
proc = subprocess.Popen([
    edge_path,
    '--headless=new',
    '--disable-gpu',
    f'--user-data-dir={user_data}',
    '--remote-allow-origins=*',
    '--remote-debugging-port=9385',
    'http://127.0.0.1:5000/collections.html'
])
time.sleep(3)

try:
    tabs = json.loads(urllib.request.urlopen('http://localhost:9385/json').read().decode())
    ws = websocket.create_connection(tabs[0]['webSocketDebuggerUrl'], timeout=10)

    # Enable Log & Runtime
    ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
    ws.recv()

    time.sleep(2)

    expr = """
    (() => {
        const grid = document.getElementById('catalog-products-grid');
        return {
            title: document.getElementById('catalog-title')?.textContent,
            countText: document.getElementById('catalog-count-display')?.textContent,
            gridChildren: grid?.children.length,
            firstCard: document.querySelector('.ecommerce-product-card')?.outerHTML.substring(0, 300),
            gridHTMLSnippet: grid?.innerHTML.substring(0, 300)
        };
    })()
    """
    ws.send(json.dumps({
        "id": 2,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expr,
            "returnByValue": True
        }
    }))

    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 2:
            print("Evaluation Result:", json.dumps(msg.get("result", {}), indent=2))
            break
finally:
    proc.terminate()
    proc.wait()
    try:
        shutil.rmtree(user_data, ignore_errors=True)
    except:
        pass
