import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    clicks INTEGER DEFAULT 0,
    gems INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()
