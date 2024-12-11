import sqlite3

# Connect to the database
conn = sqlite3.connect('db/claims.db')  # Replace with your database file name
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM main.sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

conn.close()