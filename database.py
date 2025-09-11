# database.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    
    # جدول رزروها (همون قبلی)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ✅ جدول جدید: نمونه کارها (Portfolio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,      -- دسته‌بندی: "بافت هلندی", "بافت خورشیدی", ...
            image_path TEXT NOT NULL,    -- مسیر فایل عکس (مثلاً "static/portfolio/holland_1.jpg")
            caption TEXT,                -- کپشن: "بافت هلندی برای موی بلند — مشتری: مریم جان 💖"
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# ... (بقیه توابع add_reservation و get_user_reservations بدون تغییر می‌مونن)

# ✅ تابع جدید: افزودن نمونه کار
def add_portfolio_item(category, image_path, caption=""):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO portfolio (category, image_path, caption)
        VALUES (?, ?, ?)
    ''', (category, image_path, caption))
    conn.commit()
    conn.close()

# ✅ تابع جدید: دریافت همه دسته‌بندی‌های منحصر به فرد
def get_all_categories():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM portfolio ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

# ✅ تابع جدید: دریافت همه نمونه کارهای یک دسته‌بندی
def get_portfolio_by_category(category):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image_path, caption FROM portfolio WHERE category = ?', (category,))
    items = cursor.fetchall()  # لیستی از تاپل‌ها: [('path1.jpg', 'caption1'), ...]
    conn.close()
    return items
