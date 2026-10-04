import urllib.request
import json

url = "http://127.0.0.1:5000/api/founder"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode())
    print("Keys in /api/founder:", list(data.keys()))
    print("Milestones count:", len(data.get("milestones", [])))
    for m in data.get("milestones", []):
        print(" -", m.get("year"), m.get("title"))
