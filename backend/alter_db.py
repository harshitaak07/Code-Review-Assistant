import sqlite3

conn = sqlite3.connect("backend/db.sqlite")
c = conn.cursor()
c.execute("ALTER TABLE submissions ADD COLUMN code_hash TEXT;")
conn.commit()
conn.close()
