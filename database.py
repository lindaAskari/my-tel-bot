# database.py
import sqlite3
from datetime import datetime

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
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول نمونه کارها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            image_path TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    cursor.execute('SELECT * FROM reservations WHERE user_id = ?', (user_id,))
    reservations = cursor.fetchall()
    conn.close()
    return reservations

def add_portfolio_item(category, image_path, caption=""):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO portfolio (category, image_path, caption)
        VALUES (?, ?, ?)
    ''', (category, image_path, caption))
    conn.commit()
    conn.close()

def get_all_categories():
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM portfolio ORDER BY category')
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_portfolio_by_category(category):
    conn = sqlite3.connect('reservations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT image_path, caption FROM portfolio WHERE category = ?', (category,))
    items = cursor.fetchall()
    conn.close()
    return items
