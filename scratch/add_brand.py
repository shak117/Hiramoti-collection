import sqlite3

conn = sqlite3.connect('database/hiramoti.db')
cur = conn.cursor()
cols = [r[1] for r in cur.execute('PRAGMA table_info(products)').fetchall()]
if 'brand' not in cols:
    cur.execute("ALTER TABLE products ADD COLUMN brand TEXT DEFAULT 'Hiramoti Collection'")
    print("Added brand column to products")
else:
    print("Brand column already exists")

cur.execute("UPDATE products SET brand='TechnoSport' WHERE category='technosport' OR subtype='technosport'")
cur.execute("UPDATE products SET brand='Hiramoti Hosiery' WHERE category='hosiery' OR subtype='hosiery'")
conn.commit()
conn.close()
print("Brand updates complete")
