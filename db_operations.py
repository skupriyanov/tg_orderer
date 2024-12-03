import sqlite3

from logging_config import logger


def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            desc TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            contact TEXT,
            item TEXT,
            quantity INTEGER,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_products():
    logger.info("Запрос списка продуктов")
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def add_product(name, price):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()
    conn.close()

def update_product_price(product_id, new_price):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, product_id))
    conn.commit()
    conn.close()

def update_product_desc(product_id, new_desc):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET desc = ? WHERE id = ?", (new_desc, product_id))
    conn.commit()
    conn.close()

def update_product_name(product_id, new_name):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ? WHERE id = ?", (new_name, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_product_description(product_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT desc FROM products where id = ?",(product_id,))
    desc = cursor.fetchone()
    conn.close()
    return  desc[0]

def get_product_name(product_id):
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products where id = ?",(product_id,))
    desc = cursor.fetchone()
    conn.close()
    return  desc[0]