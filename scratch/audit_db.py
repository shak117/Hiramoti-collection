import sqlite3

conn = sqlite3.connect("database/hiramoti.db")
cursor = conn.cursor()
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables in hiramoti.db:", tables)
for t in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {count} rows")

print("\nAdmin Users:")
for u in cursor.execute("SELECT id, username, email, role, is_active FROM admin_users").fetchall():
    print(" ", u)
