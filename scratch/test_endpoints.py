import urllib.request, json

res = urllib.request.urlopen('http://localhost:5000/api/products?category=technosport')
data = json.loads(res.read().decode())
print('Technosport count:', data['count'])
for p in data['products']:
    print(p['name'], '| Orig:', p['original_price'], '| Sale:', p['price'], '| Disc:', p['discount'])
print('Category counts:', data['category_counts'])

res2 = urllib.request.urlopen('http://localhost:5000/api/products?category=hosiery')
data2 = json.loads(res2.read().decode())
print('Hosiery count:', data2['count'])
for p in data2['products']:
    print(p['name'], '| Orig:', p['original_price'], '| Sale:', p['price'], '| Disc:', p['discount'])

res3 = urllib.request.urlopen('http://localhost:5000/api/categories')
print('Categories:', json.loads(res3.read().decode())['categories'])
