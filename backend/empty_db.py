import sqlite3

DB_FILE = r"backend\db.sqlite"

def empty_database():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM submissions;")
    c.execute("DELETE FROM feedback;")
    conn.commit()
    conn.close()
    print("Database emptied successfully!")

if __name__ == "__main__":
    empty_database()
