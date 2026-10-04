import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

conn = sqlite3.connect("database/hiramoti.db")
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, username, email, password_hash, role FROM admin_users").fetchall()

passwords_to_test = [
    "Hiramoti@1987",
    "SuperAdmin@1987",
    "superadmin123",
    "SuperAdmin123",
    "admin123",
    "admin@1987",
    "superadmin@1987",
    "HiramotiSuper@1987",
    "12345678",
    "HiramotiAdmin@1987"
]

for r in rows:
    print(f"\nUser: {r['username']} ({r['email']}) Role: {r['role']}")
    matched = False
    for p in passwords_to_test:
        if check_password_hash(r["password_hash"], p):
            print(f"  MATCH FOUND: '{p}'")
            matched = True
            break
    if not matched:
        print("  NO MATCH in tested list. Hash starts with:", r["password_hash"][:20])

conn.close()
