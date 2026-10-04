import urllib.request
import json

def test_api():
    base = "http://127.0.0.1:5000"
    endpoints = [
        "/api/products",
        "/api/categories",
        "/api/discounts",
        "/api/founder",
    ]
    for ep in endpoints:
        url = base + ep
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                print(f"OK: {ep} - Status {resp.status}")
                if ep == "/api/products":
                    print(f"  Total products: {data.get('count')}, Category counts: {data.get('category_counts')}")
                    # Check first technosport item
                    ts = [p for p in data.get('products', []) if p.get('brand') == 'TechnoSport']
                    if ts:
                        p0 = ts[0]
                        print(f"  TechnoSport Item: {p0['name']} Base: {p0.get('original_price')} -> Sale: {p0.get('price')} (Discount: {p0.get('discount')})")
                elif ep == "/api/categories":
                    cats = data.get('categories', [])
                    print(f"  Categories count: {len(cats)}, Slugs: {[c['slug'] for c in cats]}")
                elif ep == "/api/discounts":
                    rules = data.get('rules', [])
                    print(f"  Discounts count: {len(rules)}, Rules: {[r['id'] for r in rules]}")
                elif ep == "/api/founder":
                    milestones = data.get('founder', {}).get('milestones', [])
                    print(f"  Founder Milestones: {[m.get('year') for m in milestones]}")
        except Exception as e:
            print(f"ERROR: {ep} - {e}")

if __name__ == "__main__":
    test_api()
