import sqlite3

conn = sqlite3.connect('catalog')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS categories
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS item
(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    user TEXT NOT NULL
)

""")
conn.commit()
c.execute("""CREATE TABLE IF NOT EXISTS users
(
    username TEXT,
    email TEXT PRIMARY KEY
)""")
conn.commit()