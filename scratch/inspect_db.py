import sqlite3, json

conn = sqlite3.connect('database/hiramoti.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for t in tables:
    count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"Table {t}: {count} rows")

row = cur.execute("SELECT * FROM settings WHERE key='founder_legacy'").fetchone()
if row:
    print("founder_legacy:", row['value'])
else:
    print("No founder_legacy key in settings")

rows = cur.execute("SELECT * FROM categories").fetchall()
print("Categories:", [dict(r) for r in rows])

products = cur.execute("SELECT id, name, category, subtype, price, original_price, discount, stock, image FROM products").fetchall()
print(f"Total products: {len(products)}")
for p in products:
    print(dict(p))

discounts = cur.execute("SELECT * FROM promotional_discounts").fetchall() if 'promotional_discounts' in tables else []
print("Discounts table:", [dict(d) for d in discounts])
