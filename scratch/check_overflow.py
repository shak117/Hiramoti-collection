import subprocess, time, json, urllib.request

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Launch edge with remote debugging
proc = subprocess.Popen([
    edge_path,
    '--headless',
    '--remote-debugging-port=9225',
    '--window-size=375,812',
    'http://localhost:5000/founder.html'
])
time.sleep(2)

try:
    tabs = json.loads(urllib.request.urlopen('http://localhost:9225/json').read().decode())
    target = tabs[0]
    ws_url = target['webSocketDebuggerUrl']
    
    # Simple websocket communication via basic socket
    import urllib.parse
    parsed = urllib.parse.urlparse(ws_url)
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((parsed.hostname, parsed.port))
    
    # Handshake
    key = "dGhlIHNhbXBsZSBub25jZQ=="
    req = (
        f"GET {parsed.path} HTTP/1.1\r\n"
        f"Host: {parsed.netloc}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    s.sendall(req.encode())
    resp = s.recv(1024).decode()
    if "101 Switching Protocols" in resp:
        # Send evaluate command
        js_code = """
        (() => {
            const docW = document.documentElement.clientWidth;
            const res = [];
            document.querySelectorAll('*').forEach(el => {
                const r = el.getBoundingClientRect();
                if (r.right > docW + 2) {
                    res.push({
                        tag: el.tagName,
                        cls: el.className,
                        id: el.id,
                        right: Math.round(r.right),
                        width: Math.round(r.width)
                    });
                }
            });
            return JSON.stringify({docW, count: res.length, items: res.slice(0, 10)});
        })()
        """
        payload = json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {"expression": js_code, "returnByValue": True}
        })
        
        # Frame
        data = payload.encode()
        frame = bytearray([0x81])
        length = len(data)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        mask = [0, 0, 0, 0]
        frame.extend(mask)
        frame.extend(data)
        s.sendall(frame)
        
        time.sleep(1)
        raw = s.recv(8192)
        # unmask or read payload
        print("Raw response received:", len(raw))
        # Find json in raw
        text = raw.decode('latin-1')
        print(text[text.find('{'):])
finally:
    proc.terminate()
