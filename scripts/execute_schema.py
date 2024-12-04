import sqlite3

# Connect to the database
conn = sqlite3.connect('db/claims.db')
conn.execute("PRAGMA foreign_keys = ON;")

# Read and execute the schema
with open('db/schema.sql', 'r') as schema_file:
    conn.executescript(schema_file.read())

print("Tables with relationships created successfully.")
conn.close()
