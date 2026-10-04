import sqlite3

conn = sqlite3.connect("database/hiramoti.db")
conn.row_factory = sqlite3.Row
rules = conn.execute("SELECT * FROM promotional_rules").fetchall()
print("Rules:")
for r in rules:
    print(dict(r))

categories = conn.execute("SELECT * FROM categories").fetchall()
print("\nCategories:")
for c in categories:
    print(dict(c))
conn.close()
