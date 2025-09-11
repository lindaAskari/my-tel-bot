import sqlite3

def init_db():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()

    # جدول رزروها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول پورتفولیو (نمونه کارها)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            image_path TEXT NOT NULL,
            caption TEXT
        )
    ''')

    conn.commit()
    conn.close()

def add_reservation(user_id, name, phone, service, date, time_slot):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reservations (user_id, name, phone, service, date, time_slot)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, phone, service, date, time_slot))
    conn.commit()
    conn.close()

def get_user_reservations(user_id):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT service, date, time_slot, name, phone
        FROM reservations
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 🖼️ تابع جدید: همیشه لیست کامل دسته‌بندی‌های پیش‌فرض رو برمی‌گردونه
def get_all_categories():
    # ✅ ثابت نگه داشتن لیست کامل — بدون وابستگی به دیتابیس
    return [
        "بافت هلندی",
        "بافت خورشیدی",
        "بافت کراس",
        "بافت افریقایی",
        "بافت مرواریدی",
        "بافت تلی",
        "بافت کویین",
        "بافت تیغ ماهی"
    ]

# 🖼️ بازیابی عکس‌های یک دسته‌بندی خاص از دیتابیس
def get_portfolio_by_category(category):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT image_path, caption
        FROM portfolio
        WHERE category = ?
    ''', (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 🖼️ اضافه کردن یک آیتم پورتفولیو به دیتابیس
def add_portfolio_item(category, image_path, caption):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO portfolio (category, image_path, caption)
        VALUES (?, ?, ?)
    ''', (category, image_path, caption))
    conn.commit()
    conn.close()
