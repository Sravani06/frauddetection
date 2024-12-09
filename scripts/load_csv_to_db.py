import sqlite3
import pandas as pd
import os

# Path to the database
db_path = "db/claims.db"

# Dictionary mapping CSV files to database tables
csv_to_table = {
    "data/POLICY_DETAILS.csv": "POLICY_DETAILS",
    "data/CUSTOMER_DETAILS.csv": "CUSTOMER_DETAILS",
    "data/CLAIM_DETAILS.csv": "CLAIM_DETAILS",
    "data/CLAIM_STATUS.csv": "CLAIM_STATUS",
    "data/CLAIM_PARTICIPANT.csv": "CLAIM_PARTICIPANT",
    "data/CLAIM_ADDITIONAL_DETAILS.csv": "CLAIM_ADDITIONAL_DETAILS",
    "data/PAYMENT_DETAILS.csv": "PAYMENT_DETAILS",
    "data/CLAIM_INJURY_DETAILS.csv": "CLAIM_INJURY_DETAILS"
}


def load_csv_to_db():
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support

    for csv_file, table_name in csv_to_table.items():
        if os.path.exists(csv_file):
            try:
                print(f"Loading {csv_file} into {table_name}...")
                # Load CSV into DataFrame
                df = pd.read_csv(csv_file)

                # Write DataFrame to SQLite table
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"Table {table_name} loaded successfully.")
            except Exception as e:
                print(f"Error loading {csv_file} into {table_name}: {e}")
        else:
            print(f"File {csv_file} not found. Skipping.")

    # Close the connection
    conn.close()
    print("All CSV files processed.")


if __name__ == "__main__":
    load_csv_to_db()
