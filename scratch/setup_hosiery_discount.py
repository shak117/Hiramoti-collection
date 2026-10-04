import sqlite3

conn = sqlite3.connect("database/hiramoti.db")
cursor = conn.cursor()

# 1. Insert RULE-HOSIERY-10
cursor.execute("""
    INSERT OR REPLACE INTO promotional_rules (
        id, name, target_type, target_value, discount_type, discount_value,
        start_date, end_date, is_active, updated_at
    ) VALUES (
        'RULE-HOSIERY-10', 'Hosiery 10% Promotional Discount', 'category', 'hosiery',
        'percentage', 10.0, '2026-01-01', '2027-12-31', 1, CURRENT_TIMESTAMP
    )
""")

# 2. Update category tag to 10% OFF
cursor.execute("UPDATE categories SET tag = '10% OFF' WHERE slug = 'hosiery'")

conn.commit()
conn.close()
print("RULE-HOSIERY-10 and category tag successfully added.")
