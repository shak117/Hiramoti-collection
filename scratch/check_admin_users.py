import sqlite3

conn = sqlite3.connect("database/hiramoti.db")
conn.row_factory = sqlite3.Row
info = conn.execute("PRAGMA table_info(admin_users)").fetchall()
print("Columns:", [dict(col)['name'] for col in info])
rows = conn.execute("SELECT * FROM admin_users").fetchall()
for r in rows:
    d = dict(r)
    d.pop("password_hash", None)
    print(d)
conn.close()
