import sqlite3

conn = sqlite3.connect("database/hiramoti.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, name, slug, tag, icon, is_active FROM categories").fetchall()
for r in rows:
    print(r["id"], "|", r["name"], "|", r["slug"], "|", r["tag"], "|", r["is_active"])
conn.close()
