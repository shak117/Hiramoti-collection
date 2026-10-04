import urllib.request, json

url = "http://localhost:5000/api/products?category=hosiery"
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print("Hosiery items count:", data.get("count"))
    for p in data.get("products", []):
        print(f"Item: {p['name']} | Base: {p.get('original_price')} -> Sale: {p.get('price')} | Discount: {p.get('discount')}")
