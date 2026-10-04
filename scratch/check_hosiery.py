import sqlite3, json

conn = sqlite3.connect("database/hiramoti.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, name, category, subtype, brand, price, original_price, discount FROM products WHERE category = 'hosiery' OR subtype = 'hosiery'").fetchall()
for r in rows:
    print(r["id"], "|", r["name"], "|", r["price"], "|", r["original_price"], "|", r["discount"])
conn.close()
