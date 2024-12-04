import sqlite3

# Connect to SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('db/claims.db')
conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support
conn.close()
print("Database initialized.")
